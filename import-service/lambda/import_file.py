import os
import json
import boto3
import logging

s3 = boto3.client('s3')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    bucket_name = os.environ['BUCKET_NAME']
    
    try:
        file_name = event['queryStringParameters']['name']
        # Generate a presigned URL for uploading
        presigned_url = s3.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': f"uploaded/{file_name}"
            },
            ExpiresIn=3600  # URL expires in 1 hour
        )
        logging.info(f"Presigned URL: {presigned_url}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                "content-type": "*/*"
            },
            'body': presigned_url
        }
    except Exception as e:
        logger.error(
            "Error processing file %s. Here's why: %s",
            file_name,
            str(e),
        )
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    