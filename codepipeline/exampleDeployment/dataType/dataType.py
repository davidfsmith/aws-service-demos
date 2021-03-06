import boto3
import json
import os

if os.environ['S3_ENDPOINT'] != '':
    endpoint_url = os.environ['S3_ENDPOINT']
else:
    endpoint_url = None

s3 = boto3.client('s3', endpoint_url=endpoint_url)

def readHead(event):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    response = s3.head_object(
    Bucket=bucket,
    Key=key)
    return response['ResponseMetadata']['HTTPHeaders']['content-type']

def lambda_handler(event, context):
    typeText = { 'dataType': readHead(event) }
    return typeText, event
