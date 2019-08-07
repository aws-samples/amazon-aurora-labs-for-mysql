/* jslint node: true */
'use strict'

/*
Amazon Aurora Labs for MySQL
Grunt build specification file

Dependencies:
grunt, grunt-exec

License:
This sample code is made available under the MIT-0 license. See the LICENSE file.
*/

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
      cmd: 'rm -rf ./build && mkdir ./build && mkdir ./build/infra && mkdir ./build/templates && mkdir ./build/docx'
    },
    clearTemp: {
      cmd: 'rm -rf ./temp  && mkdir ./temp && mkdir ./temp/pandoc'
    },
    buildIndexDocFunction: {
      cwd: './website/lambda/indexdoc-function/src',
      cmd: 'npm update && grunt lambda_package'
    },
    buildIpCheckFunction: {
      cwd: './website/lambda/ipcheck-function/src',
      cmd: 'npm update && grunt lambda_package'
    },
    pkgInfra: {
      cmd: 'aws cloudformation package --template-file ./website/template/site.yml --s3-bucket ' + bucket + ' --output-template-file ./build/infra/site.yml.packaged --region ' + region
    },
    buildInfra: {
      cmd: 'aws cloudformation deploy --template-file ./build/infra/site.yml.packaged --stack-name ' + stack  + ' --parameter-overrides tagEnvironment=' + env + ' --capabilities CAPABILITY_NAMED_IAM --region ' + region
    },
    buildSite: {
      cmd: 'BUCKET=$(aws cloudformation describe-stacks --stack-name ' + stack  + ' --region ' + region + ' | jq -r \'.Stacks[0].Outputs[] | if .OutputKey == "ContentBucket" then .OutputValue else "" end\' | tr -d "\\n") && DISTRO=$(aws cloudformation describe-stacks --stack-name ' + stack  + ' --region ' + region + ' | jq -r \'.Stacks[0].Outputs[] | if .OutputKey == "DistroEndpoint" then .OutputValue else "" end\' | tr -d "\\n") && mkdir ./temp/website && mkdocs build -c -d ./temp/website && find ./temp/website -type f -name "*.html" -exec sed -i "" "s/\\[\\[bucket\\]\\]/$BUCKET/g" {} + && find ./temp/website -type f -name "*.html" -exec sed -i "" "s/\\[\\[website\\]\\]/$DISTRO/g" {} + && mv ./temp/website ./build/website'
    },
    copySite: {
      cmd: 'BUCKET=$(aws cloudformation describe-stacks --stack-name ' + stack  + ' --region ' + region + ' | jq -r \'.Stacks[0].Outputs[] | if .OutputKey == "ContentBucket" then .OutputValue else "" end\' | tr -d "\\n") && aws s3 cp ./build/website s3://$BUCKET/website/ --recursive'
    },
    buildTemplates: {
      cmd: 'BUCKET=$(aws cloudformation describe-stacks --stack-name ' + stack  + ' --region ' + region + ' | jq -r \'.Stacks[0].Outputs[] | if .OutputKey == "ContentBucket" then .OutputValue else "" end\' | tr -d "\\n") && DISTRO=$(aws cloudformation describe-stacks --stack-name ' + stack  + ' --region ' + region + ' | jq -r \'.Stacks[0].Outputs[] | if .OutputKey == "DistroEndpoint" then .OutputValue else "" end\' | tr -d "\\n") && cp ./templates/*.yml ./temp/ && sed -i "" "s/\\[\\[website\\]\\]/$DISTRO/g" ./temp/*.yml && sed -i "" "s/\\[\\[bucket\\]\\]/$BUCKET/g" ./temp/*.yml && mv ./temp/*.yml ./build/templates/'
    },
    copyTemplates: {
      cmd: 'BUCKET=$(aws cloudformation describe-stacks --stack-name ' + stack  + ' --region ' + region + ' | jq -r \'.Stacks[0].Outputs[] | if .OutputKey == "ContentBucket" then .OutputValue else "" end\' | tr -d "\\n") && aws s3 cp ./build/templates s3://$BUCKET/templates/ --recursive --acl public-read'
    },
    copyScripts: {
      cmd: 'BUCKET=$(aws cloudformation describe-stacks --stack-name ' + stack  + ' --region ' + region + ' | jq -r \'.Stacks[0].Outputs[] | if .OutputKey == "ContentBucket" then .OutputValue else "" end\' | tr -d "\\n") && aws s3 cp ./scripts s3://$BUCKET/scripts/ --recursive'
    },
    buildDocHtmlIntermediate: {
      cmd: 'BUCKET=$(aws cloudformation describe-stacks --stack-name ' + stack  + ' --region ' + region + ' | jq -r \'.Stacks[0].Outputs[] | if .OutputKey == "ContentBucket" then .OutputValue else "" end\' | tr -d "\\n") && DISTRO=$(aws cloudformation describe-stacks --stack-name ' + stack  + ' --region ' + region + ' | jq -r \'.Stacks[0].Outputs[] | if .OutputKey == "DistroEndpoint" then .OutputValue else "" end\' | tr -d "\\n") && ./pandoc.sh && find ./temp/pandoc -type f -name "*.html" -exec sed -i "" "s/\\[\\[bucket\\]\\]/$BUCKET/g" {} + && find ./temp/pandoc -type f -name "*.html" -exec sed -i "" "s/\\[\\[website\\]\\]/$DISTRO/g" {} + && find ./temp/pandoc -type f -name "*.html" -exec sed -i "" "s/\%5B\%5Bbucket\%5D\%5D/$BUCKET/g" {} + && find ./temp/pandoc -type f -name "*.html" -exec sed -i "" "s/\%5B\%5Bwebsite\%5D\%5D/$DISTRO/g" {} +'
    },
    buildDocFinal: {
      cmd: 'sed -i "" "s/\\/assets\\/images\\///g" ./temp/pandoc/output.html && pandoc -o ./build/docx/aurora-labs-mysql.docx -f html -t docx --resource-path ./temp/pandoc/ ./temp/pandoc/output.html --toc --toc-depth 2'
    }
  }
})

// register tasks
grunt.registerTask('build-doc', [ 'exec:clearTemp', 'exec:buildDocHtmlIntermediate', 'exec:buildDocFinal' ])
grunt.registerTask('build-functions', [ 'exec:buildIndexDocFunction', 'exec:buildIpCheckFunction' ])
grunt.registerTask('deploy-all', [ 'exec:clearBuild', 'exec:clearTemp', 'build-functions', 'exec:pkgInfra', 'exec:buildInfra', 'exec:buildSite', 'exec:buildTemplates', 'exec:copySite', 'exec:copyTemplates', 'exec:copyScripts' ])
grunt.registerTask('deploy-skipinfra', [ 'exec:clearBuild', 'exec:clearTemp', 'build-functions', 'exec:pkgInfra', 'exec:buildSite', 'exec:buildTemplates', 'exec:copySite', 'exec:copyTemplates', 'exec:copyScripts' ])
