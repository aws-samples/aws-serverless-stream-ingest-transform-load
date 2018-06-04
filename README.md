## Serverless Stream Ingest Transform Load

In this pattern, data records are ingested and then modified with simple transformations such as field level substitutions and data enrichment from relatively small and static data sets. A Lambda function is invoked by Kinesis Data Firehose as records are received by the delivery stream. the Lambda function then performs a simple processing job and returns the transformed or enriched records back to Kinesis Data Firehose. Firehose then buffers and sends the modified records to the configured destinations. A copy of the source records is saved in S3 as a backup and for future analysis.

## License Summary

This sample code is made available under a modified MIT license. See the LICENSE file.
