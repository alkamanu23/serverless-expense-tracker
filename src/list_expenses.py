"""GET /expenses -> returns the signed-in user's expenses."""
import json
import os

import boto3
from boto3.dynamodb.conditions import Key

table = boto3.resource("dynamodb").Table(os.environ["TABLE"])


def handler(event, context):
    user_id = event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
    result = table.query(KeyConditionExpression=Key("userId").eq(user_id))
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"expenses": result["Items"]}),
    }
  
