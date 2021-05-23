import boto3
import os

os.environ['AWS_SHARED_CREDENTIALS_FILE']='./web/.aws/credentials'

s3 = boto3.resource('s3')
content_object = s3.Object('pihistory', 'data.txt')
file_content = content_object.get()['Body'].read().decode('utf-8')
print(file_content)