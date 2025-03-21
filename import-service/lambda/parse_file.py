import os
import json
import csv
import codecs
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    bucket_name = os.environ['BUCKET_NAME']
    queue_url = os.environ['QUEUE_URL']

    for record in event['Records']:
        object_key = record['s3']['object']['key']

        try:
            # Parse the CSV file from S3 as a stream
            logging.info(f"Process file {object_key} from Bucket {bucket_name}")
            s3 = boto3.client('s3')
            data = s3.get_object(Bucket=bucket_name, Key=object_key)
            rows = csv.DictReader(codecs.getreader("utf-8")(data["Body"]))

             # Initialize the SQS client
            sqs = boto3.client('sqs')
            logging.info(f"QueueUrl: {queue_url}")

            # Rows are sent to the queue in batch for cost optimization
            message_batch = []
            for row in rows:
                # Convert the row to JSON
                json_message = json.dumps(row)

                # Add the message to the batch
                message_batch.append({
                    'Id': str(len(message_batch) + 1),
                    'MessageBody': json_message
                })

                # Send the batch of messages when it reaches the maximum batch size (10 messages)
                if len(message_batch) == 10:
                    response = sqs.send_message_batch(
                        QueueUrl=queue_url,
                        Entries=message_batch
                    )
                    logging.info(f"Send message batch: {json.dumps(response)}")
                    message_batch = []

            # Send any remaining messages in the batch
            if message_batch:
                response = sqs.send_message_batch(
                    QueueUrl=queue_url,
                    Entries=message_batch
                )
                logging.info(f"Send message batch: {json.dumps(response)}")

            # Move file to processed directory (copy and delete)
            copy_source = {'Bucket': bucket_name, 'Key': object_key}
            target_key = object_key.replace('uploaded/', 'parsed/')
            logging.info(f"Copy file {copy_source} to {target_key}")
            s3.copy_object(
                CopySource = copy_source,
                Bucket = bucket_name,
                Key = target_key,
            )
            logging.info(f"Delete file {object_key} from Bucket {bucket_name}")
            if object_key != 'uploaded/':
                s3.delete_object(
                    Bucket = bucket_name,
                    Key = object_key,
                )
        except Exception as e:
            logger.error(
                "Error processing file %s. Here's why: %s",
                object_key,
                str(e),
            )
