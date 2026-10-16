"""Triggered by S3 uploads: runs Textract AnalyzeExpense and stores the result in DynamoDB."""
import os
import urllib.parse
from datetime import datetime, timezone

import boto3

textract = boto3.client("textract")
table = boto3.resource("dynamodb").Table(os.environ["TABLE"])


def parse_summary(response):
    """Pull vendor, total and date out of Textract's summary fields."""
    wanted = {"VENDOR_NAME": "vendor", "TOTAL": "total", "INVOICE_RECEIPT_DATE": "date"}
    result = {"vendor": "Unknown", "total": "0", "date": ""}
    for doc in response.get("ExpenseDocuments", []):
        for field in doc.get("SummaryFields", []):
            name = field.get("Type", {}).get("Text")
            value = field.get("ValueDetection", {}).get("Text")
            if name in wanted and value:
                result[wanted[name]] = value
    return result


def handler(event, context):
    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])
        user_id = key.split("/")[1]

        response = textract.analyze_expense(
            Document={"S3Object": {"Bucket": bucket, "Name": key}}
        )
        parsed = parse_summary(response)

        table.put_item(
            Item={
                "userId": user_id,
                "expenseId": key.split("/")[-1],
                "vendor": parsed["vendor"],
                "total": parsed["total"],
                "date": parsed["date"],
                "receiptKey": key,
                "createdAt": datetime.now(timezone.utc).isoformat(),
            }
        )
