import datetime
import logging
from typing import Generator, List, Optional

from .. import settings
from ..aws import LOGS_CLIENT

logger = logging.getLogger(__name__)
logger.setLevel(settings.LOG_LEVEL)


def get_logstream_events(log_group_name: str, log_stream_name: str, from_datetime: datetime.datetime) -> Generator:
    """collect logstream events"""
    # first request
    logger.info(f"retrieving log events {log_group_name} {log_stream_name} from_datetime={from_datetime}")
    response = LOGS_CLIENT.get_log_events(logGroupName=log_group_name, logStreamName=log_stream_name, startFromHead=True)
    for event in response["events"]:
        event_datetime = datetime.datetime.fromtimestamp(event["timestamp"] / 1000).replace(tzinfo=datetime.timezone.utc)
        if event_datetime >= from_datetime:
            event["datetime"] = event_datetime
            yield event

    # remaining
    while True:
        prev_token = response["nextForwardToken"]
        logger.info(f"retrieving log events {log_group_name} {log_stream_name} from_datetime={from_datetime} -- {prev_token}")
        response = LOGS_CLIENT.get_log_events(logGroupName=log_group_name, logStreamName=log_stream_name, nextToken=prev_token)
        # same token then break
        if response["nextForwardToken"] == prev_token:
            break
        for event in response["events"]:
            event_datetime = datetime.datetime.fromtimestamp(event["timestamp"] / 1000).replace(tzinfo=datetime.timezone.utc)
            if event_datetime >= from_datetime:
                event["datetime"] = event_datetime
                yield event
    logger.info(f"retrieving log events {log_group_name} {log_stream_name} from_datetime={from_datetime} -- DONE")


def get_lambda_logs(alarm_event: dict) -> List[Optional[str]]:
    """
    Sample alarm_event:
    {
       "AlarmName": "MyLambdaFunctionErrorsAlarm-stage",
       "AlarmDescription": null,
       "AWSAccountId": "xxx",
       "NewStateValue": "ALARM",
       "NewStateReason": "Threshold Crossed: 1 datapoint [1.0 (23/08/21 11:22:00)] was greater than or equal to the threshold (1.0).",
       "StateChangeTime": "2021-08-23T11:23:24.588+0000",
       "Region": "Asia Pacific (Tokyo)",
       "AlarmArn": "arn:aws:cloudwatch:ap-northeast-1:xxx:alarm:MyLambdaFunctionErrorsAlarm-stage",
       "OldStateValue": "OK",
       "Trigger": {
           "MetricName": "Errors",
           "Namespace": "AWS/Lambda",
           "StatisticType": "Statistic",
           "Statistic": "MAXIMUM",
           "Unit": null,
           "Dimensions": [
               {
                   "value": "LAMBDA-FUNCTION-NAME",
                   "name": "FunctionName"
               }
           ],
           "Period": 60,
           "EvaluationPeriods": 1,
           "ComparisonOperator": "GreaterThanOrEqualToThreshold",
           "Threshold": 1.0,
           "TreatMissingData": "- TreatMissingData:                    notBreaching",
           "EvaluateLowSampleCountPercentile": ""
       }
    }
    """
    assert alarm_event["Trigger"]["Namespace"] == "AWS/Lambda"
    function_name = None
    for dimension in alarm_event["Trigger"]["Dimensions"]:
        if dimension["name"] == "FunctionName":
            function_name = dimension["value"]
    assert function_name

    alarm_isoformat = alarm_event["StateChangeTime"]
    # convert to python supported isoformat
    alarm_datetime = datetime.datetime.fromisoformat(alarm_isoformat.replace("+0000", "+00:00"))   # convert to datetime parsable value
    logger.debug(f"ERROR_CAPTURE_BUFFER_SECONDS={settings.ERROR_CAPTURE_BUFFER_SECONDS}")
    error_buffered_datetime = alarm_datetime - datetime.timedelta(seconds=settings.ERROR_CAPTURE_BUFFER_SECONDS)
    logger.debug(f"alarm_datetime={alarm_datetime}")
    logger.debug(f"error_buffered_datetime={error_buffered_datetime}")

    formatted_events = []
    for function_name in settings.FUNCTION_NAMES:
        log_group = f"/aws/lambda/{function_name}"
        logger.info(f"describe_log_streams {log_group} ...")
        response = LOGS_CLIENT.describe_log_streams(logGroupName=log_group, orderBy="LastEventTime", descending=True)
        logger.info(f"describe_log_streams {log_group} ... DONE")

        for stream in response["logStreams"]:
            last_event_timestamp = stream["lastEventTimestamp"] / 1000  # convert to datetime parsable value
            last_event_datetime = datetime.datetime.fromtimestamp(last_event_timestamp)
            last_event_datetime = last_event_datetime.replace(tzinfo=datetime.timezone.utc)
            logger.debug(f"last_event_datetime={last_event_datetime}")
            if last_event_datetime >= error_buffered_datetime:
                logger.debug("-- get_logstream_events")
                for event in get_logstream_events(
                    log_group_name=log_group, log_stream_name=stream["logStreamName"], from_datetime=error_buffered_datetime
                ):
                    logger.debug(f"event={event}")
                    event_datetime = event["datetime"]
                    event_datetime_in_desired_timezone = event_datetime.astimezone(settings.TIMEZONE)  # settings.TIMEZONE = datetime.timezone(datetime.timedelta(hours=XXX))
                    formatted_event = f"[{event_datetime_in_desired_timezone.isoformat()}] {event['message']}"
                    formatted_events.append(formatted_event)
    return formatted_events
