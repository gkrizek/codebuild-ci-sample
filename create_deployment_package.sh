#!/bin/bash

set -e

echo "Creating Lambda Deployment Package..."

# Remove old export directory if it exists
EXPORT_DIR="./lambda/export"
if [ -d "$EXPORT_DIR" ]
then
  rm -rf $EXPORT_DIR
fi
# Make new export directory
mkdir -p ./lambda/export
# Copy our code
cp ./lambda/index.py ./lambda/export
# Install our modules
pip3 install -r ./lambda/requirements.txt -t ./lambda/export
# Create ZIP file
cd ./lambda/export
zip -r ../../codebuild-ci-lambda.zip .
cd -
# Clean Up export
rm -rf ./lambda/export

echo "Create Deployment Package: 'codebuild-ci-lambda.zip'"
