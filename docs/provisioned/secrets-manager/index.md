# Manage database credentials with AWS Secrets Manager

This lab will walk you through the steps of securely managing Amazon Aurora database credentials using <a href="https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html"target="_blank">AWS Secrets Manager</a>. The service enables you to easily rotate, manage, and retrieve database credentials, as well as managing access to secrets using fine-grained policies.

<span class="image">![Basic scenario of using AWS Secrets Manager](0-basic-secrets-manager-scenario.png?raw=true)</span>

With steps 1 and 2 the admin creates credentials and places them in the AWS Secrets Manager. An application with sufficient permissions then can access the credentials in steps 3 and 4 to use them in step 5 to access the database.

Currently, we already have one secret `secretClusterAdminUser` that is used for the admin user.

This lab contains the following tasks:

1. Create new database user and grant permissions

2. Create new secret for the created user

3. Manage access to the new secret using IAM policies

4. Enable rotation for the secret

5. Verify DB Cluster connection

6. Audit usage of the secret

7. Cleanup

This lab requires the following lab modules to be completed first:

* [Get Started](/prereqs/environment/) (you do not need to provision a DB cluster automatically)
* [Connect to the Session Manager Workstation](/prereqs/connect/) (needed for task \#5)

## 1. Create new database user and grant permissions
You will connect to the Aurora database just like you would do with any other MySQL-based database, using a compatible client tool like `mysql`. To find the clusterEndpoint see [Retrieve the DB cluster endpoints](/provisioned/create/#2-retrieve-the-db-cluster-endpoints).

If you have not already opened a terminal window in the Cloud9 Desktop in a previous lab, please [follow these instructions](/prereqs/connect/) to do so now.

!!! warning "Check for correct cluster endpoint"
    Make sure you take the endpoint of the **cluster** and not of the writer or reader instances.

During this lab we will use a secure connection to ensure encryption in transit. If you haven't setup this up in a previous lab, let's do this now and download the certificates. Use the following command to download the RDS-related certificates as bundle into the current directory:

```
wget https://s3.amazonaws.com/rds-downloads/rds-combined-ca-bundle.pem
```

To connect to the cluster you can use the next command. The environment variables were already set during the cluster setup:

```
mysql -h[clusterEndpoint] -u$DBUSER -p"$DBPASS" --ssl-ca=rds-combined-ca-bundle.pem
```

Once connected to the Aurora database, use the code below to create a database user account that uses a secure password. In this lab we will use `demouser` as dbusername, but you can use a different name accordingly. Run the following SQL query:

```
CREATE USER demouser IDENTIFIED BY 'securePassword';
```


Run the following command to allow the just created database user account to connect to the cluster from anywhere but require using SSL:

```
GRANT USAGE ON *.* TO 'demouser'@'%' REQUIRE SSL;
```

Now grant the user some permissions to create or drop tables, insert and select records within the database `mylab`. This will be needed later on for some testing.

```
GRANT CREATE, INSERT, SELECT, DROP ON mylab.* TO 'demouser'@'%';
```

<span class="image">![Create database user account](1-database-create-user-account.png?raw=true)</span>

You can now quit the connection
```
\q
```

## 2. Create new secret for the new created user

Now, we'll create the secret, that will hold the credential information. Open the <a href="https://console.aws.amazon.com/secretsmanager/home" target="_blank">Secrets Manager console</a>.

!!! warning "Region Check"
    Ensure you are still working in the correct region, especially if you are following the links above to open the service console at the right screen.

Click **Store a new secret** to start the configuration process.

<span class="image">![Store new Secret](2-store-new-secret.png?raw=true)</span>

In the **Select secret type** section, choose **Credentials for RDS database**, then input the **User name** `demouser` and **Password** that was just setup in the step before `securePassword`.

Next, in the **Select which RDS database this secret will access** section, choose the DB cluster identifier you assigned to your cluster (e.g. `auroralab-mysql-cluster`). Click **Next**.

??? tip "What is the encryption key used for?"
    The secret information is encrypted using encryption keys that you can manage by using AWS KMS. For most cases you can encrypt by using the AWS managed key that AWS Secrets Manager creates on your behalf (aws/secretsmanager), or you can use a customer managed key that you've created in AWS KMS.

    If you use a customer managed key, then the IAM user or role who needs to read the secret later must have the permission "kms:Decrypt" for that KMS key.

    You're not billed for using the AWS managed key that AWS Secrets Manager creates for you. You're billed for any KMS keys that you create.

Leave the **Encryption key** as it is and click **Next**.

<span class="image">![Configure Secret](2-config-secret.png?raw=true)</span>

Name the secret `secret_Demouser` and provide a meaningful description `Demouser credentials for 'aurora-lab-mysql-cluster'` for the secret, then click **Next**.

<span class="image">![Name Secret](2-name-secret.png?raw=true)</span>

Choose **Next**.

(Optional) On the Secret rotation page, keep rotation off for now. We'll turn it in a later step. Click **Next**.

On the Review page, review your secret details and recognize the provided code samples in different programming languages. Then choose **Store**.

<span class="image">![Review Secret](2-review-secret.png?raw=true)</span>

Hit the refresh button and click on the newly created secret. Make note of the secrets ARN, since we will need it for further reference.

<span class="image">![Review Secret](2-note-secret-arn.png?raw=true)</span>

## 3. Manage access to the new secret using policies

To allow an identity like user, role or group accessing the secret an IAM policy is required. Follow the steps to create an IAM policy, that grants the `secretsmanager:GetSecretValue` action.

Open the <a href="https://console.aws.amazon.com/iamv2/home" target="_blank">IAM console</a>.

Choose **Policies** from the left navigation pane.

Click **Create Policy**

<span class="image">![Create policy to allow connecting to the database](3-create-policy.png?raw=true)</span>

Select the JSON tab, past in the following policy and replace the parameter

* [ ] `SecretARN`

with the value you have copied in the step before.

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "<SecretARN>"
    }
  ]
}
```

Click **Next: Tags**

<span class="image">![Input JSON for policy to allow acessing the secret](3-create-policy-json.png?raw=true)</span>

Click **Next: Review**

For **Name** enter a policy name, e.g. `auroralab-iam-access-secret` and click **Create policy**

<span class="image">![Name the policy and create](3-create-policy-name.png?raw=true)</span>

This policy now can be attached to a user or role in order to allow accessing the secret to retrieve its values.

??? tip "How to improve the access of Secrets Manager Secret via the public internet?"
    So, permissions are set, the secret information is encrypted and the traffic is encrypted as well. However, the traffic leaves the AWS network and traverses the public internet. In order to avoid that, we recommend to call the Secrets Manager API directly without having to leave your private network. This can be done using an <a href="https://docs.aws.amazon.com/secretsmanager/latest/userguide/vpc-endpoint-overview.html" target="_blank">interface VPC Endpoint for Secrets Manager</a>. In addition it allows you to deny any access to the secret information by requests that don't originate from your VPC.

## 4. Verify DB Cluster connection

Now, that we have created the database user, the secret and a policy to give permission to access the secret, let us check accessing the database.

For this verification, we will use the Cloud9 environment. But it well could be any other Service running the desired application, like AWS Lambda function or container image running in Amazon ECS or EKS. However, the current role of the instance already has permissions to access secrets. For our verification, we will therefore use a different role.

Let's create a role, that we can assign to the Cloud9 instance.

Open the <a href="https://console.aws.amazon.com/iamv2/home" target="_blank">IAM console</a>.

Choose **Roles** from the left navigation pane.

Click **Create Role**

<span class="image">![Create role for EC2 instance](4-create-role.png?raw=true)</span>

Select the common use case EC2 since we want to allow the EC2 instance to access the AWS Secrets Manager on our behalf. Then click **Next**

<span class="image">![Select EC2 use case](4-select-ec2-use-case.png?raw=true)</span>

Here we select the policies that should be attached to this new role. Please add them one by one. First filter by name and then activate the checkbox and clear the filter.

* [ ] `auroralab-iam-access-secret`

Click **Next**

<span class="image">![Select EC2 use case](4-role-add-permission.png?raw=true)</span>

Give the role a name, e.g. `auroralab-ec2-db-secret-access-role`, review the two added policies and click **Create role**

<span class="image">![Enter name for role](4-role-name.png?raw=true)</span>

You have created a role that can be assumed by an user or by a service like Amazon EC2. Now you will assign this role to the instance where the Cloud9 instance is running. Open the <a href="https://console.aws.amazon.com/ec2/home" target="_blank">EC2 console</a>, click instances on the left menu and select the instance with the name starting with `aws-cloud9-auroralab-client-ide`.

<span class="image">![EC2 console selecting instance](4-ec2-console-instances.png?raw=true)</span>

Then click **Actions**, choose **Security** and finally click **Modify IAM role**

<span class="image">![Modify IAM role of EC2 instance](4-ec2-modify-iam-role.png?raw=true)</span>

Select the just created role `auroralab-ec2-db-secret-access-role` and click **Update IAM role**

<span class="image">![Update IAM role of EC2 instance](4-ec2-update-iam-role.png?raw=true)</span>

The Cloud9 instance now assumes this role to call any AWS services on our behalf as we can see by issuing the follwoing command in an open terminal in the Cloud9 environment.

```
aws sts get-caller-identity
```

You should see a similar output like follows:
```
{
    "UserId": "AROAWHAQA2INSHSUGHBSL:i-04584130d15f50154",
    "Account": "123456789000",
    "Arn": "arn:aws:sts::123456789000:assumed-role/auroralab-ec2-db-secret-access-role/i-04584130d15f50154"
}
```

There is already a small script `db_access_test.py` connecting to the database cluster using the previously created secret without having stored the credentials somewhere in the code or environment variables. Open the file and examine its content. What it does is using the AWS SDK to create a client for the Session Manager and retrieves a secret by the name given via the command line argument. Then it uses the secret to extract host, username and password to access the cluster and execute a small query showing existing tables in the mylab database.

Okay, now try executing the script with the follwoing command with the previously created secrets name `secret_Demouser`
```
python db_access_test.py -s secret_Demouser
```

The output should look like the following
<span class="image">![Output of script db_access_test.py](4-output-db-test.png?raw=true)</span>

Well, but how do we know the access of the secret is only possible because we have granted access? We could remove the policy from the role and see what happens.

Open the <a href="https://console.aws.amazon.com/iamv2/home" target="_blank">IAM console</a>.

Choose **Roles** from the left navigation pane.

Click on the role `auroralab-ec2-db-secret-access-role`

Activate the checkbox of the `auroralab-iam-access-secret` policy and click **Remove**

<span class="image">![Remove policy](4-remove-policy.png?raw=true)</span>

Give it a couple of moments to be propagated and then try executing the script again
```
python db_access_test.py -s secret_Demouser
```

You should see a similar output like follows:
```
An error occurred (AccessDeniedException) when calling the GetSecretValue operation: User: arn:aws:sts::123456789000:assumed-role/auroralab-ec2-db-secret-access-role/i-04584130d15f50154 is not authorized to perform: secretsmanager:GetSecretValue on resource: secret_Demouser because no identity-based policy allows the secretsmanager:GetSecretValue action

Unexpected error encountered.
```

As you can see, it is not possible to access the secret and therefore connecting to the db cluster without sufficient permissions.

To proceed with further steps, let's quickly set the IAM role for the Cloud9 instance back to what it was.

Open the <a href="https://console.aws.amazon.com/ec2/home" target="_blank">EC2 console</a>, click instances on the left menu and select the instance with the name starting with `aws-cloud9-auroralab-client-ide`.

Then click **Actions**, choose **Security** and finally click **Modify IAM role**

Select the original role starting with `auroralab-ide` and click **Update IAM role**

If you check on the Security tab for the instance, it should state the correct IAM role

<span class="image">![Check IAM role for the ide instance in the security tab](4-ec2-security-iam-role.png?raw=true)</span>


??? tip "Do I need to retrieve the secret every time I need it in my application?"
    Well, it is up to you. While it is possible to retrieve the secret with 'GetSecretValue' every time you need it, we <a href="https://docs.aws.amazon.com/secretsmanager/latest/userguide/retrieving-secrets.html" target="_blank">recommended caching the secret values</a> by using client-side caching. There are caching components available in many SDKs.

## 5. Enable rotation for the secret

You now have an option to avoid storing the credentials inside the code or within environment variables. But there is a problem that still remains. Usually, it is required or at least strongly recommended to periodically change or rotate credentials. This is the moment where the AWS Secrets Manager can help even more by providing a fully automated feature to rotate your Amazon RDS, Amazon DocumentDB, and Amazon Redshift secrets.

??? tip "Can I also use the rotation feature for different types of secrets?"
    Yes, you can also <a href="https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotate-secrets_turn-on-for-other.html" target="_blank">rotate other types of secrets</a>.

To enable the rotation, open the <a href="https://console.aws.amazon.com/secretsmanager/home" target="_blank">Secrets Manager console</a>

On the Secrets page, choose the previously created secret `secret_Demouser`
<span class="image">![Select secret](5-select-secret.png?raw=true)</span>

On the Secret details page, in the **Rotation configuration** section, choose **Edit rotation**
<span class="image">![Edit rotation for secret](5-edit-rotation.png?raw=true)</span>

In the Edit rotation configuration dialog box, do the following:

Under **Configure automatic rotation**, turn on `Automatic rotation`

In the **Rotation Schedule** set `Time unit` to `30` days and leave the remaining values as is. Especially the `Rotate immediately when the secret is stored. The next rotation will begin on your schedule.` needs to be remain enabled, as we want to see the first rotation immediately.

Under **Rotation function** enter a function name, e.g. `aurora-rotation-lambda`

Click **Save**

<span class="image">![Configure rotation](5-configure-rotation.png?raw=true)</span>

??? tip "What happens behind the scene?"
    What happens now is that Secrets Manager will create and deploy a CloudFormation script to create a Lambda function, to actually perform the rotation, and a SecretRotationSchedule to invoke the Lambda function at the specified interval. The function updates the password in the database as well as in the Secrets Manager.

In the **Rotation configuration** the status field tells us the rotation is being enabled.

Now, let's check in the <a href="https://console.aws.amazon.com/cloudformation/home" target="_blank">CloudFormation console</a> when the stack creation is completed. Once the stack creation is finished. It can take approximately five minutes to complete.

<span class="image">![Check completed stack in CloudFormation](5-cloudformation.png?raw=true)</span>

Once the stack has been created, we can check the secret to be updated.

Go back to the <a href="https://console.aws.amazon.com/secretsmanager/home" target="_blank">Secrets Manager console</a>, select the secret `secret_Demouser` and retrieve secret value. You can see the details of the rotation like status, interval and function. On the top right corner you may also recognize a new button allowing you to perform an immediate rotation.

<span class="image">![Rotation is enabled](5-rotation-enabled.png?raw=true)</span>

To see if it also was changed on the database, execute the script again. You don't need to change the IAM roles for the instance, since the current role already has the rights to access secrets throughout this account.

```
python db_access_test.py -s secret_Demouser
```

Congratulations, you have just setup a highly secure and fully automated way to use periodically rotated credentials in any application. This does not only remove the undifferentiated heavy lifting, it also helps us minimizing our attack surface as well as being compliant.

## 6. Audit usage of the secret

Sometimes it might be necessary to audit the usage of the secret. As you might already know API calls can be collected in the audit trail. This is also the case for the `GetSecretValue` operation.

Open the <a href="https://console.aws.amazon.com/cloudtrail/home" target="_blank">Cloudtrail console</a>

Choose **Event history** and filter for `GetSecretValue`

You should see different calls. Some made by the Cloud9 instance, when we issued the test script. Some calls came from the Rotation function. And there might also be calls from your curently logged in user, when you retrieved the secret via the console.

<span class="image">![Audit access to secret on CloudTrail](6-cloudtrail.png?raw=true)</span>

Depending on the roles you will create and the secrets being setup you are able to exactly track and audit when who accessed a specific secret.

## 7. Cleanup Ressources
To remove all resources from this lab open a terminal in the Cloud9 environment and execute the following statements.
```
# 'Removing db user...'
mysql -h`aws rds describe-db-cluster-endpoints --query "DBClusterEndpoints[?EndpointType=='WRITER'].Endpoint" --output text | grep auroralab-mysql-cluster` -u$DBUSER -p"$DBPASS" --ssl-ca=rds-combined-ca-bundle.pem <<'EOF'
DROP USER 'demouser'@'%';
EOF

# 'Deleting role...'
aws iam delete-role --role-name auroralab-ec2-db-secret-access-role

# 'Deleting policy...'
aws iam delete-policy --policy-arn arn:aws:iam::`aws sts get-caller-identity --query Account --output text`:policy/auroralab-iam-access-secret

# 'Deleting secret in 7 days (minimal recovery window)...'
aws secretsmanager delete-secret --recovery-window-in-days 7 --secret-id secret_Demouser
```