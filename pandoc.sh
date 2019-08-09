#!/bin/bash

cp docs/assets/images/* temp/pandoc
pandoc -f markdown -t html docs/index.md > temp/pandoc/output.html
pandoc -f markdown -t html docs/modules/index.md >> temp/pandoc/output.html

for MODULE in prerequisites create connect clone backtrack perf-insights create-serverless
do
cp docs/modules/$MODULE/*.png temp/pandoc/ && pandoc -f markdown -t html docs/modules/$MODULE/index.md >> temp/pandoc/output.html
done

pandoc -f markdown -t html docs/related/labs/index.md >> temp/pandoc/output.html
pandoc -f markdown -t html docs/contribute.md >> temp/pandoc/output.html
pandoc -f markdown -t html docs/license.md >> temp/pandoc/output.html
