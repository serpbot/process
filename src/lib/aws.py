#!/usr/bin/env python3
"""
This module empasses various functions used to call AWS services
"""

import logging
import boto3
from src.lib.common import load_page

log = logging.getLogger(__name__)


def delete_message(sqs_name, sqs_region, receiptHandle):
    """Delete queue message from SQS"""
    try:
        log.info("Deleting Message in Queue")
        sqs = boto3.client("sqs", region_name=sqs_region)
        response = sqs.delete_message(
            QueueUrl="https://sqs.%s.amazonaws.com/827114851303/%s" % (sqs_region, sqs_name),
            ReceiptHandle=receiptHandle
        )
        return response
    except Exception as exception:
        log.error("Unable to delete message %s: %s", receiptHandle, exception)


def receive_message(sqs_name, sqs_region):
    """Get queue message from SQS"""
    try:
        sqs = boto3.client("sqs", region_name=sqs_region)
        response = sqs.receive_message(
            QueueUrl="https://sqs.%s.amazonaws.com/827114851303/%s" % (sqs_region, sqs_name),
            AttributeNames=[
                "SentTimestamp"
            ],
            MaxNumberOfMessages=1,
            MessageAttributeNames=[
                "All"
            ],
            VisibilityTimeout=0,
            WaitTimeSeconds=10
        )
        if "Messages" in response:
            message = response["Messages"][0]
            receipt_handle = message["ReceiptHandle"]
            delete_message(sqs_name, sqs_region, receipt_handle)
            return message
        return None
    except Exception as exception:
        log.error("Unable to queue message: %s", exception)


def send_email(recipient, template="trend_report", **kwargs):
    """Send email to client using SES"""
    try:
        client = boto3.client("ses", region_name="us-west-2")
        message = {"Subject": {"Data": "Your latest trend report!"},
                   "Body": {"Text": {"Data": "This is your latest trend report... "},
                            "Html": {"Data": load_page(template, **kwargs)}}}
        client.send_email(
            Source="Serpbot Support <support@serpbot.co>",
            Destination={"ToAddresses": [recipient]},
            Message=message,
            ReplyToAddresses=["Serpbot Support <support@serpbot.co>"])
        return True
    except Exception as exception:
        log.error("Unable to send email to %s: %s", recipient, exception)
        return False
