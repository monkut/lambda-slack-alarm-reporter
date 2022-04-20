import datetime
import json
from pathlib import Path
from unittest import TestCase

from botocore.exceptions import ClientError

from marvin.aws import LOGS_CLIENT
from marvin.handlers.functions import get_lambda_logs

from .utils import get_logstream_dummy_events

FIXTURES_DIRECTORY = Path(__file__).parent / "fixtures"


class HandlersFunctionsTestCase(TestCase):
    def setUp(self) -> None:
        alarm_sample_filepath = FIXTURES_DIRECTORY / "alarm-sample.json"
        alarm_sample_filepath.exists()
        with alarm_sample_filepath.open("r") as json_in:
            self.alarm = json.load(json_in)

        # prepare logs
        # - create log group
        self.log_group_name = "/aws/lambda/LAMBDA-FUNCTION-NAME"
        try:
            response = LOGS_CLIENT.create_log_group(
                logGroupName=self.log_group_name,
                kmsKeyId="kmskey1",
            )
        except ClientError as e:
            if e.__class__.__name__ != "ResourceAlreadyExistsException":
                raise

        # - create log stream
        self.log_stream_name = "HandlersFunctionsTestCase-logstream-1"
        try:
            response = LOGS_CLIENT.create_log_stream(
                logGroupName=self.log_group_name,
                logStreamName=self.log_stream_name,
            )
        except ClientError as e:
            if e.__class__.__name__ != "ResourceAlreadyExistsException":
                raise

        # - create test logs
        events = get_logstream_dummy_events(count=5)
        try:
            response = LOGS_CLIENT.put_log_events(logGroupName=self.log_group_name, logStreamName=self.log_stream_name, logEvents=events)
        except ClientError as e:
            if e.__class__.__name__ != "ResourceAlreadyExistsException":
                raise

    def test_get_lambda_logs(self):
        state_change_time = datetime.datetime.now(datetime.timezone.utc)
        alarm_event = {
            "AlarmName": "MyLambdaFunctionErrorsAlarm-stage",
            "AlarmDescription": "",
            "AWSAccountId": "xxx",
            "NewStateValue": "ALARM",
            "NewStateReason": "Threshold Crossed: 1 datapoint [1.0 (23/08/21 11:22:00)] was greater than or equal to the threshold (1.0).",
            "StateChangeTime": state_change_time.isoformat(),
            "Region": "Asia Pacific (Tokyo)",
            "AlarmArn": "arn:aws:cloudwatch:ap-northeast-1:xxx:alarm:MyLambdaFunctionErrorsAlarm-stage",
            "OldStateValue": "OK",
            "Trigger": {
                "MetricName": "Errors",
                "Namespace": "AWS/Lambda",
                "StatisticType": "Statistic",
                "Statistic": "MAXIMUM",
                "Unit": "",
                "Dimensions": [{"value": "LAMBDA-FUNCTION-NAME", "name": "FunctionName"}],
                "Period": 60,
                "EvaluationPeriods": 1,
                "ComparisonOperator": "GreaterThanOrEqualToThreshold",
                "Threshold": 1.0,
                "TreatMissingData": "- TreatMissingData: notBreaching",
                "EvaluateLowSampleCountPercentile": "",
            },
        }
        events = get_lambda_logs(alarm_event=alarm_event)
        self.assertTrue(events)
