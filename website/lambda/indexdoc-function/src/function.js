/* jslint node: true */
'use strict'

/*
Amazon Aurora Labs for MySQL
AWS Lambda function to expand directory requests to an index.html file for CloudFront

Dependencies:
none

License:
This sample code is made available under the MIT-0 license. See the LICENSE file.
*/

// lambda function handler
exports.handler = (event, context, callback) => {

    // extract the request from the CloudFront event that is sent to Lambda@Edge
    var response = event.Records[0].cf.request

    // Extract the URI from the request
    var olduri = response.uri

    // match any '/' that occurs at the end of a URI, replace it with a default index
    var newuri = olduri.replace(/\/$/, '\/index.html')

    // replace the received URI with the URI that includes the index page
    response.uri = newuri

    // return to CloudFront
    callback(null, response)
};
