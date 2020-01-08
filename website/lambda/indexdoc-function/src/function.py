"""
Amazon Aurora Labs for MySQL
AWS Lambda function to expand directory requests to an index.html file for CloudFront

NOTICE:
For testing only, the actual code is inline in the CloudFormation template
(see ../../../template/site.yml).

Dependencies:
none

License:
This sample code is made available under the MIT-0 license. See the LICENSE file.
"""

# Lambda function handler
def lambda_handler(event, context):
    # Request is the response, too
    request = event['Records'][0]['cf']['request']

    # Check if the URI ends with '/', then append 'index.html' to it
    if request['uri'].endswith('/'):
        request['uri'] = request['uri'] + 'index.html'

    # Return modified request
    return request
