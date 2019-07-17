/* jslint node: true */
'use strict'

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
