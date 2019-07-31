/* jslint node: true */
'use strict'

/*
Amazon Aurora Labs for MySQL
AWS Lambda function to restrict access to the site based on IP addresses

Dependencies:
ipcheck module

License:
This sample code is made available under the MIT-0 license. See the LICENSE file.
*/

// init module
var ipcheck = require('./node_modules/ipcheck')

// CIDR whitelist
const allowedIpRanges = "***REMOVED***".split(',')

// Lambda function handler
exports.handler = (event, context, callback) => {
	// get the IP address of the client
	const clientIp = event.Records[0].cf.request.clientIp

  // get the requested URI
  const requestedUri = event.Records[0].cf.request.uri

  // generate the default response
  var response = event.Records[0].cf.request

	// search for CIDR blocks that contain the client IP address
	const foundItem = allowedIpRanges.find(function (item) { return ipcheck.match(clientIp, item) })

  // if the IP address is not found, mark as forbidden
  if (foundItem === undefined && !requestedUri.startsWith('/scripts/')) {
    response = {
			status: '403',
			statusDescription: 'Forbidden'
		}
	}

	// return
	callback(null, response)
}
