/* jslint node: true */
'use strict'

// init grunt
var grunt = require('grunt')

// load modules
grunt.loadNpmTasks('grunt-exec')

// options
var env = grunt.option('env') || 'dev'
var bucket = grunt.option('bucket') || 's3bucket'
var region = grunt.option('region') || 'us-east-1'
var stack = grunt.option('cfnstack') || 'ams-labs-' + env

// define configuration
grunt.initConfig({
  pkg: grunt.file.readJSON('package.json'),
  exec: {
    clearBuild: {
      cmd: 'rm -rf ./build && mkdir ./build && mkdir ./build/website && mkdir ./build/infra'
    },
    pkgInfra: {
      cmd: 'aws cloudformation package --template-file ./website/template/site.yml --s3-bucket ' + bucket + ' --output-template-file ./build/infra/site.yml.packaged --region ' + region
    },
    buildInfra: {
      cmd: 'aws cloudformation deploy --template-file ./build/infra/site.yml.packaged --stack-name ' + stack  + ' --parameter-overrides tagEnvironment=' + env + ' --capabilities CAPABILITY_NAMED_IAM --region ' + region
    },
    buildSite: {
      cmd: 'mkdocs build -c -d ./build/website'
    },
    copySite: {
      cmd: 'aws s3 cp ./build/website s3://$(aws cloudformation describe-stacks --stack-name ' + stack  + ' --region ' + region + ' | jq -r \'.Stacks[0].Outputs[] | if .OutputKey == "ContentBucket" then .OutputValue else "" end\' | tr -d \'\\n\')/website/ --recursive'
    }
  }
})

// register tasks
grunt.registerTask('deploy-all', [ 'exec:clearBuild', 'exec:pkgInfra' , 'exec:buildInfra', 'exec:buildSite', 'exec:copySite' ])
