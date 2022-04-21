import datetime
import logging
import os
from distutils.util import strtobool

DEFAULT_LOG_LEVEL = "DEBUG"
VALID_LOG_LEVELS = ("WARNING", "INFO", "CRITICAL", "ERROR", "DEBUG")
LOG_LEVEL = os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL)
assert LOG_LEVEL in VALID_LOG_LEVELS, f"{LOG_LEVEL} not in {VALID_LOG_LEVELS}"
LOG_LEVEL = getattr(logging, LOG_LEVEL)  # get log level number for logging

# reduce output from noisy packages
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("botocore").setLevel(logging.WARNING)
logging.getLogger("boto3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

DEFAULT_SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/"
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", DEFAULT_SLACK_WEBHOOK_URL)

DEFAULT_ENABLE_POSTTOSLACK = "True"
ENABLE_POSTTOSLACK = bool(strtobool(os.getenv("ENABLE_POSTTOSLACK", DEFAULT_ENABLE_POSTTOSLACK)))

DEFAULT_POST_SNS_ALARM = "False"
POST_SNS_ALARM = bool(strtobool(os.getenv("POST_SNS_ALARM", DEFAULT_POST_SNS_ALARM)))

APP_VERSION = os.getenv("APP_VERSION", "UNKNOWN")
logger.info(f"APP_VERSION={APP_VERSION}")

AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "ap-northeast-1")

DEFAULT_SNS_SERVICE_ENDPOINT = f"https://sns.{AWS_REGION}.amazonaws.com"
DEFAULT_LOGS_SERVICE_ENDPOINT = f"https://logs.{AWS_REGION}.amazonaws.com"

AWS_SERVICE_ENDPOINTS = {
    "sns": os.getenv("SNS_SERVICE_ENDPOINT", DEFAULT_SNS_SERVICE_ENDPOINT),
    "logs": os.getenv("LOGS_SERVICE_ENDPOINT", DEFAULT_LOGS_SERVICE_ENDPOINT),
}

DEFAULT_ERROR_CAPTURE_BUFFER_SECONDS = 150
ERROR_CAPTURE_BUFFER_SECONDS = int(os.getenv("ERROR_CAPTURE_BUFFER_SECONDS ", DEFAULT_ERROR_CAPTURE_BUFFER_SECONDS))

DEFAULT_UTC_OFFSET = 9  # 9 - JST (Asia/Tokyo)
UTC_OFFSET = int(os.getenv("UTC_OFFSET"), DEFAULT_UTC_OFFSET)
TIMEZONE = datetime.timezone(datetime.timedelta(hours=UTC_OFFSET))

DEFAULT_FUNCTION_NAMES = "/aws/lambda/LAMBDA-FUNCTION-NAME"
FUNCTION_NAMES = os.getenv("FUNCTION_NAMES").split(",")  # Can be provided by envars
