/* jslint node: true */
'use strict'

/*
Amazon Aurora Labs for MySQL
Grunt build specification for the indexdoc function

Dependencies:
grunt, grunt-exec

License:
This sample code is made available under the MIT-0 license. See the LICENSE file.
*/

// init grunt
var grunt = require('grunt')

// load modules
grunt.loadNpmTasks('grunt-aws-lambda')

// define configuration
grunt.initConfig({
  pkg: grunt.file.readJSON('package.json'),
  lambda_invoke: {
    default: {
      options: {
        file_name: 'function.js',
        handler: 'handler',
        event: 'event.json'
      }
    }
  },
  lambda_package: {
    default: {
      options: {
        include_files: [],
        include_time: false,
        include_version: false,
        package_folder: './',
        dist_folder: '../dist'
      }
    }
  }
})
