#!/usr/bin/env bash
S3Bucket=BUCKET_NAME
REGION=REGION_NAME

FILE="$(uuidgen).yaml"
PREFIX=streamingitl

cd lambda/
pip3 install -r requirements.txt -t "$PWD" --upgrade
cd ..
aws cloudformation package --region $REGION --template-file streaming_ingest_transform_load.template --s3-bucket $S3Bucket --s3-prefix $PREFIX --output-template-file $FILE
aws cloudformation deploy --region $REGION --template-file $FILE --stack-name StreamingITL --capabilities CAPABILITY_NAMED_IAM
