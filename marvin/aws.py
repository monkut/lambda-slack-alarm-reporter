import boto3

from . import settings

SNS_CLIENT = boto3.client("sns", endpoint_url=settings.AWS_SERVICE_ENDPOINTS["sns"], region_name=settings.AWS_REGION)
LOGS_CLIENT = boto3.client("logs", endpoint_url=settings.AWS_SERVICE_ENDPOINTS["logs"])
