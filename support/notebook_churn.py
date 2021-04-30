## License:
## This sample code is made available under the MIT-0 license. See the LICENSE file.


#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!! Set your bucket name here !!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
bucket = 'mlbucketplaceholder'
prefix = 'sagemaker/sk-learn-sqlai'

# Define IAM role
import boto3
import re
import sagemaker
from sagemaker import get_execution_role

role = get_execution_role()
sess = sagemaker.Session()


# In[ ]:


import pandas as pd
import numpy as np

churn = pd.read_csv('./sample_churn_data.txt')
churn.columns = ['state', 'acc_length', 'area_code', 'phone', 'int_plan', 'vmail_plan',
                'vmail_msg', 'day_mins', 'day_calls', 'day_charge', 'eve_mins', 'eve_calls',
                'eve_charge', 'night_mins', 'night_calls', 'night_charge', 'int_mins',
                'int_calls', 'int_charge', 'cust_service_calls', 'churn']
churn.info()
# Save all data
churn.to_csv('data.csv', header=False, index=False)


# The last attribute, _churn_, is known as the target attribute–the attribute that we want the ML model to predict. Because the target attribute is binary, our model will be performing binary prediction, also known as binary classification.

# In[ ]:


# Preprocessing steps taken from the XGBoost notebook
# This steps will remove unneded features from the dataset. The goal is to start
# with a clean dataset, but we won't be doing any label encoding or imputation here
# that will be included in the actual algorithm code
churn = churn.drop('phone', axis=1)
churn['area_code'] = churn['area_code'].astype(object)
churn = churn.drop(['day_charge', 'eve_charge', 'night_charge', 'int_charge'], axis=1)

model_data = churn
model_data.info()

# Split 80/20 train/test
train_data, test_data = np.split(model_data.sample(frac=1, random_state=42), [int(0.8 * len(model_data))])
train_data.to_csv('train.csv', header=True, index=False)
test_data.to_csv('test.csv', header=True, index=False)
model_data.to_csv('data.csv', header=False, index=False)


# Let's now use this data to train SKLearn RanmdomCutForest to predict Customer churn. The following Python module will be used by the SKLearn framework container to perfrom training and inference. This code gets uploaded behind the scenes to S3, and its location is made available to the container via an environment variable ```SAGEMAKER_SUBMIT_DIRECTORY```. The SKLearn container download the code from S3 and executes it. At infernce time the same process takes place.

# In[ ]:


get_ipython().run_cell_magic('writefile', 'script.py', '\nimport argparse\nimport os\nimport pickle\n\nimport numpy as np\nimport pandas as pd\nfrom sklearn.preprocessing import LabelEncoder\nfrom sklearn.ensemble import RandomForestClassifier\nfrom sklearn.externals import joblib\n\n# This needs to be inluded for the XXXYYY_fn method overrides to work. See\n# https://sagemaker.readthedocs.io/en/stable/using_sklearn.html#preparing-the-scikit-learn-training-script\n# for more details\nfrom sagemaker_containers.beta.framework import (\n    content_types, encoders, env, modules, transformer, worker)\n\nimport sys\nif sys.version_info[0] < 3: \n    from StringIO import StringIO\nelse:\n    from io import StringIO\n\n# Columns that need to be encoded as integers\n# TODO: Receive this as a hyperparameter\nCOLS = [\'state\', \'churn\', \'area_code\', \'int_plan\', \'vmail_plan\']\n\n\ndef input_fn(request_body, request_content_type):\n    """Override the default input_fn.\n    \n    Here we make sure we can handle text/csv, and load the data into\n    a pandas DataFrame.\n    """\n    if request_content_type != "text/csv":\n        raise ValueError("Invalid content type {}. Only text/csv is supported".format(request_content_type))\n    input_string = StringIO(request_body)\n    return pd.read_csv(input_string, header=None)\n\n\ndef predict_fn(data, model):\n    """Override the default predict_fn.\n    \n    This function takes as input the output of input_fn, and the deserialized model.\n    \n    :param data: Pandas DataFrame. The return of input_fn\n    :param model: The return of model_fn\n    :return: NDArray of shape (samples, 1)\n    """\n    encoders = model[\'encoders\']\n    model = model[\'model\']\n    encode_with(data, encoders, skip_target=True)\n    return encoders[0][1].inverse_transform(model.predict(data))\n\n\ndef model_fn(model_dir):\n    """Override the default model_fn\n    \n    The model is a pickled dictionary:\n    \n    {\'encoders\': List<Typle<idx, sklearn.LabelEncoder>>,\n     \'model\': sklearn.RandomForestClassifier}\n    \n    :param model_dir: str. The directory where the model artifact is being copied from S3\n    :return: The unpickled model as described above\n    """\n    print("Loading the model")\n    path = os.path.join(model_dir, "model.pkl")\n    model = pickle.load(open(path, \'rb\'))\n    return model\n\n\ndef encode(data, targets, target_col):\n    """Apply LabelEncoder to named columns.\n    \n    In order to make the encoders usable at inference time, this function\n    records the index to which each encoder must be applied, and returns a\n    List<Tuple<idx, LabelEncoder>>.\n    \n    The target_col encoder is guaranteed to be the first one in the list\n    \n    :param data: Pandas DataFrame.\n    :param targets: List<str>. The names of the columns that need to be encoded\n    :param target_col: str. Column to be predicted.\n    :return: List<Tuple<idx, LabelEncoder>>. The encoders list suitable for use during inference\n    """\n    encoders = []\n    \n    # Fit and savel target_col encoder\n    le = LabelEncoder()\n    le.fit(data[target_col])\n    encoders.append((data.columns.get_loc(target_col), le))\n    data[target_col] = le.transform(data[target_col])\n    \n    targets.remove(target_col)\n    \n    for target in targets:\n        print(target, data.columns.get_loc(target))\n        le = LabelEncoder()\n        le.fit(data[target])\n        encoders.append((data.columns.get_loc(target), le))\n        data[target] = le.transform(data[target])\n    return encoders\n\n\ndef encode_with(data, encoders, skip_target=False):\n    """Apply trained LabelEncoders to data\n    \n    Each encoder is associated with an integer index, corresponding\n    to the column in data to which it is to be applied. The data\n    DataFrame is updated in place.\n    \n    :param data: Pandas DataFrame.\n    :param encoders: List<Tuple<idx, LabelEncoder>>\n    :return: None\n    """\n    if skip_target:\n        enc = encoders[1:]\n    else:\n        enc = encoders\n    for (idx, encoder) in enc:\n        data.iloc[:, idx] = encoder.transform(data.iloc[:, idx])\n\n\n###################################################################\n# Training code starts here\n###################################################################\nif __name__ ==\'__main__\':\n\n    print(\'Extracting arguments\')\n    parser = argparse.ArgumentParser()\n\n    # hyperparameters sent by the client are passed as command-line arguments to the script.\n    # to simplify the demo we don\'t use all sklearn RandomForest hyperparameters\n    parser.add_argument(\'--n-estimators\', type=int, default=10)\n    parser.add_argument(\'--min-samples-leaf\', type=int, default=3)\n\n    # Data, model, and output directories\n    parser.add_argument(\'--model-dir\', type=str, default=os.environ.get(\'SM_MODEL_DIR\'))\n    parser.add_argument(\'--train\', type=str, default=os.environ.get(\'SM_CHANNEL_TRAIN\'))\n    parser.add_argument(\'--test\', type=str, default=os.environ.get(\'SM_CHANNEL_TEST\'))\n    parser.add_argument(\'--train-file\', type=str, default=\'train.csv\')\n    parser.add_argument(\'--test-file\', type=str, default=\'test.csv\')\n    parser.add_argument(\'--target\', type=str) # in this script we ask user to explicitly name the target\n\n    args, _ = parser.parse_known_args()\n\n    print(\'Preparing data\')\n    train_df = pd.read_csv(os.path.join(args.train, args.train_file))\n    test_df = pd.read_csv(os.path.join(args.test, args.test_file))\n    \n    # Encode the training data, and use the trained encoders to process\n    # the test data\n    encoders = encode(train_df, COLS, args.target)\n    encode_with(test_df, encoders)\n\n    print(\'Building training and testing datasets\')\n    X_train = train_df\n    X_test = test_df\n    y_train = train_df[args.target]\n    y_test = test_df[args.target]\n    \n    X_train = X_train.drop(\'churn\', axis=1)\n    X_test = X_test.drop(\'churn\', axis=1)\n\n    print(\'Training model\')\n    model = RandomForestClassifier(\n        n_estimators=args.n_estimators,\n        min_samples_leaf=args.min_samples_leaf,\n        n_jobs=-1)\n    model.fit(X_train, y_train)\n\n    # print abs error\n    print(\'validating model\')\n    abs_err = np.abs(model.predict(X_test) - y_test)\n    print(abs_err.sum())\n\n    # print couple perf metrics\n    for q in [10, 50, 90]:\n        print(\'AE-at-\' + str(q) + \'th-percentile: \'\n              + str(np.percentile(a=abs_err, q=q)))\n        \n    # Persist model as pickle\n    m  = {\'encoders\': encoders,\n          \'model\': model}\n    \n    path = os.path.join(args.model_dir, "model.pkl")\n    pickle.dump(m, open(path, \'wb\'))\n    print(\'Model persisted at \' + path)\n    print(args.min_samples_leaf)')


# In[ ]:


get_ipython().system(" python script.py --n-estimators 100                    --min-samples-leaf 2                    --model-dir /home/ec2-user/SageMaker                    --train /home/ec2-user/SageMaker                    --train-file train.csv                     --test-file test.csv                     --test /home/ec2-user/SageMaker                    --target 'churn'")


# We are ready to train the model in SageMaker

# In[ ]:


# We use the Estimator from the SageMaker Python SDK
from sagemaker.sklearn.estimator import SKLearn

# send data to S3. SageMaker will take training data from s3
trainpath = sess.upload_data(
    path='train.csv', bucket=bucket,
    key_prefix=prefix)

testpath = sess.upload_data(
    path='test.csv', bucket=bucket,
    key_prefix=prefix)

sklearn_estimator = SKLearn(
    entry_point='script.py',
    role = get_execution_role(),
    train_instance_count=1,
    train_instance_type='ml.m4.xlarge',
    framework_version='0.20.0',
    metric_definitions=[
        {'Name': 'median-AE',
         'Regex': "AE-at-50th-percentile: ([0-9.]+).*$"}],
    hyperparameters = {'n-estimators': 100,
                       'min-samples-leaf': 2,
                       'target': 'churn'})
sklearn_estimator.fit({'train':trainpath, 'test': testpath}, wait=True)


# And now we are ready to host the model

# In[ ]:


sm_boto3 = boto3.client('sagemaker')
artifact = sm_boto3.describe_training_job(
    TrainingJobName=sklearn_estimator.latest_training_job.name)['ModelArtifacts']['S3ModelArtifacts']

print('Model artifact persisted at ' + artifact)


# In[ ]:


from sagemaker.sklearn.model import SKLearnModel

model = SKLearnModel(
    model_data=artifact,
    role=get_execution_role(),
    framework_version='0.20.0',
    entry_point='script.py')

endpoint_name = 'auroraml-churn-endpoint'

predictor = model.deploy(
    instance_type='ml.c5.large',
    initial_instance_count=1,
    endpoint_name=endpoint_name)


# In[ ]:
import boto3
import sagemaker
runtime = boto3.client('sagemaker-runtime')

test_data = test_data.drop("churn", axis=1)
train_data = train_data.drop("churn", axis=1)

response_test_data = runtime.invoke_endpoint(
    EndpointName=predictor.endpoint,
    Body=test_data.to_csv(header=False, index=False).encode('utf-8'),
    ContentType='text/csv')

print(response_test_data['Body'].read())

response_train_data = runtime.invoke_endpoint(
    EndpointName=predictor.endpoint,
    Body=train_data.to_csv(header=False, index=False).encode('utf-8'),
    ContentType='text/csv')

print(response_train_data['Body'].read())
