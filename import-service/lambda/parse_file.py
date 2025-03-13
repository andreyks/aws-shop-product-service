import os
import json
import csv
import codecs
import boto3
import logging

s3 = boto3.client('s3')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    bucket_name = os.environ['BUCKET_NAME']

    for record in event['Records']:
        object_key = record['s3']['object']['key']

        try:
            # Get the object from S3
            logging.info(f"Process file {object_key} from Bucket {bucket_name}")
            data = s3.get_object(Bucket=bucket_name, Key=object_key)
            for row in csv.DictReader(codecs.getreader("utf-8")(data["Body"])):
                logging.info(f"Row: {row}")

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
