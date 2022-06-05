#!/usr/bin/env python3
"""
This module encompasses various functions used to call AWS services
"""

import os
import logging
import boto3
from src.lib.common import load_page

log = logging.getLogger(__name__)


def delete_message(receipt_handle):
    """Delete queue message from SQS"""
    try:
        log.info("Deleting Message in Queue")
        sqs = boto3.client("sqs", region_name=os.environ.get("SQS_REGION"))
        response = sqs.delete_message(
            QueueUrl="https://sqs.%s.amazonaws.com/827114851303/%s" % (os.environ.get("SQS_REGION"),
                                                                       os.environ.get("SQS_NAME")),
            ReceiptHandle=receipt_handle
        )
        return response
    except Exception as exception:
        log.error("Unable to delete message %s: %s", receipt_handle, exception)


def receive_message():
    """Get queue message from SQS"""
    try:
        sqs = boto3.client("sqs", region_name=os.environ.get("SQS_REGION"))
        response = sqs.receive_message(
            QueueUrl="https://sqs.%s.amazonaws.com/827114851303/%s" % (os.environ.get("SQS_REGION"),
                                                                       os.environ.get("SQS_NAME")),
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
            delete_message(receipt_handle)
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
            Source="Serpbot Support <support@serp.bot>",
            Destination={"ToAddresses": [recipient]},
            Message=message,
            ReplyToAddresses=["Serpbot Support <support@serp.bot>"])
        return True
    except Exception as exception:
        log.error("Unable to send email to %s: %s", recipient, exception)
        return False
