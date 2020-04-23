## Amazon Aurora Labs for MySQL

Workshop and lab content for Amazon Aurora MySQL compatible databases. This code will contain a series of templates, instructional guides and sample code to educate users on how to use Amazon Aurora features. The AWS CloudFormation templates will create the relevant resources in a user's account, the Bash and Python scripts will support the lab, by automating tasks, generating load or execute changes on resources created using AWS CloudFormation.

To run and use the labs, visit the website at: https://awsauroralabsmy.com

The instructional guides are packaged into a website that can be deployed using AWS CloudFormantion, Amazon CloudFront, Amazon S3 and AWS Lambda. If you wish to contribute to the project follow the installation and deployment steps below.

**NOTE: This project is currently under active development. If you encounter any inaccuracies in the instructions below, please report them to us via Issues**


## Installation

The website is built using the [mkdocs](https://www.mkdocs.org/) project and supporting libraries. We use [node.js](https://nodejs.org/en/), [grunt](https://gruntjs.com/) and [Python 3](https://www.python.org/) throughout the project, therefore these dependencies also need to be installed. The AWS CloudFormation templates are tested using [taskcat](https://github.com/aws-quickstart/taskcat).

### Get Started on MacOS with Homebrew

Install dependencies:

```
brew install python3
brew install mkdocs
brew install node
brew install jq
pip3 install -r requirements.txt

npm install -g npm
npm install -g grunt-cli
```

Install project dependencies (from [project root] folder):

```
npm install
```

Install dependencies for the individual AWS Lambda functions. For each function in `[project root]/website/lambda/[function name]/src/` run

```
npm install
```

### Build and Deploy the Project

To build the website only, locally, from the root folder of the project run:

```
mkdocs serve
```

To build the project assets and deploy them in AWS, run the following commands from the root of the project folder.

**NOTE:** The website has to be deployed in the us-east-1 region due to dependencies on AWS Lambda@Edge.

Build the full project for development:

```
grunt deploy-all --region-us-east-1 --bucket=<your_bucket> --cfnstack=<your_name_letters_and_dashes_only>
```

Build the project but skip changing (or redeploying the website infrastructure):

```
grunt deploy-skipinfra --region-us-east-1 --bucket=<your_bucket> --cfnstack=<your_name_letters_and_dashes_only>
```

### Testing the AWS CloudFormation Lab Templates

The AWS CloudFormation templates for the labs are located in the `[project root]/templates/` folder. They contain placeholder expressions (such as `[[website]]`) that are replaced by the build process above, with the final URIs of the website you deploy in AWS. Final build versions of these templates are placed in the folder: `[project root]/build/templates/`

Taskcat assets are located in `[project root]/taskcat/ci`. Because the templates have hardcoded resource names to satisfy requirements with external tools, you cannot test more than one template at a time via taskcat. It is therefore necessary to customize the `[project root]/taskcat/ci/taskcat.yml` config file to indicate which template to test.

Once the config file is changed appropriately, from the root of the project folder run:

```
grunt run-taskcat --region-us-east-1 --bucket=<your_bucket> --cfnstack=<your_name_letters_and_dashes_only>
```

## License Summary

This sample code is made available under the MIT-0 license. See the LICENSE file.

Additionally, this project installs the following software for the purposes of deploying and running the labs into the lab environment:

* [mysql-client](https://dev.mysql.com/doc/refman/5.6/en/programs-client.html) package. MySQL open source software is provided under the GPL License.
* [sysbench](https://github.com/akopytov/sysbench) available using the GPL License.
* [test_db](https://github.com/datacharmer/test_db) available using the Creative Commons Attribution-Share Alike 3.0 Unported License.
* [percona sysbench-tpcc](https://github.com/Percona-Lab/sysbench-tpcc) available using the Apache License 2.0.
