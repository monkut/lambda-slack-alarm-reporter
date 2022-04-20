import json
import logging
from typing import List, Optional, Tuple

import requests

from .. import settings
from .functions import get_lambda_logs

logger = logging.getLogger(__name__)
logger.setLevel(settings.LOG_LEVEL)


def _extract_message_from_record(record) -> Tuple[str, Optional[str]]:
    """Extract the message to send to slack from alarm record"""
    logs_text = None
    try:
        logger.info("extracting sns message ...")
        message = json.loads(record["Sns"]["Message"])
        json_encoded_alarm = json.dumps(message, indent=4)
        logger.debug(f"message={message}")
        logger.info("extracting sns message ... DONE")
        message_namespace = message["Trigger"]["Namespace"]
        logger.debug(f"message_namespace={message_namespace}")
        if message_namespace == "AWS/Lambda":
            logger.debug("calling get_lambda_logs() ...")
            function_logs = get_lambda_logs(alarm_event=message)
            if function_logs:
                logs_text = "\n".join(function_logs)
            logger.debug("calling get_lambda_logs() ... DONE")
    except json.JSONDecodeError:
        logger.error("JSONDecodeError - unable to decode 'message' as JSON, returning raw message!")
        message = record["Sns"]["Message"]
        json_encoded_alarm = json.dumps(message, indent=4)
    return json_encoded_alarm, logs_text


def post_to_slack(event, context) -> List[int]:
    """Lambda handler for incoming SNS events.  SNS event 'Message' is posted to the configured SLACK_WEBHOOK_URL"""
    logger.debug(f"event={event}")
    logger.debug(f"context={context}")
    processed_record_status_codes = []
    if settings.ENABLE_POSTTOSLACK:
        logger.info(f"SLACK_WEBHOOK_URL={settings.SLACK_WEBHOOK_URL}")
        if "Records" in event:
            logger.debug(f"len(event['Records']={len(event['Records'])}")
            for record in event["Records"]:
                logger.debug(f"record={record}")
                json_encoded_alarm, logs_text = _extract_message_from_record(record=record)
                logger.debug(f"settings.POST_SNS_ALARM={settings.POST_SNS_ALARM}")
                if settings.POST_SNS_ALARM:
                    payload = {
                        "text": json_encoded_alarm,
                    }
                    response = requests.post(settings.SLACK_WEBHOOK_URL, json=payload)
                    logger.debug(f"response={response}")
                    logger.debug(f"response.status_code={response.status_code}")
                    processed_record_status_codes.append(response.status_code)
                if logs_text:
                    payload = {
                        "text": logs_text,
                    }
                    response = requests.post(settings.SLACK_WEBHOOK_URL, json=payload)
                    logger.debug(f"logs response={response}")
                    logger.debug(f"logs response.status_code={response.status_code}")
                    processed_record_status_codes.append(response.status_code)
                else:
                    logger.warning(f"No logs discovered: logs_text={logs_text}")
    else:
        logger.warning(f"ENABLE_POSTTOSLACK=False, Will not post to {settings.SLACK_WEBHOOK_URL}")
    return processed_record_status_codes
