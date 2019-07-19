## Amazon Aurora Labs for MySQL

Workshop and lab content for Amazon Aurora MySQL compatible databases. This code will contain a series of templates, instructional guides and sample code to educate users on how to use Amazon Aurora features. The AWS CloudFormation templates will create the relevant resources in a user's account, the Bash and Python scripts will support the lab, by automating tasks, generating load or execute changes on resources created using AWS CloudFormation.

## Installation steps

MacOS (with homebrew):
```
brew install mkdocs
pip3 install mkdocs-material
pip3 install pymdown-extensions
pip3 install taskcat

brew install node
npm install -g npm
npm install -g grunt-cli
grunt deploy-all --region=us-east-1 --bucket=<your-s3-bucket>
```

For functions (each):
```
npm install
grunt lambda_package
```

## License Summary

This sample code is made available under the MIT-0 license. See the LICENSE file.
