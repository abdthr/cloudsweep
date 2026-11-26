import time

import boto3
import pytest
from moto import mock_aws

from cloudsweep.logs import find_log_groups_without_retention

REGION = "eu-north-1"


@pytest.fixture
def logs():
    """A fake CloudWatch Logs service. Nothing here touches real AWS."""
    with mock_aws():
        yield boto3.client("logs", region_name=REGION)


def add_log_data(logs, group_name, size_in_bytes):
    logs.create_log_stream(logGroupName=group_name, logStreamName="test")
    logs.put_log_events(
        logGroupName=group_name,
        logStreamName="test",
        logEvents=[{"timestamp": int(time.time() * 1000), "message": "x" * size_in_bytes}],
    )


def test_finds_log_group_that_never_expires(logs):
    logs.create_log_group(logGroupName="my-app")
    add_log_data(logs, "my-app", 5000)

    findings = find_log_groups_without_retention(REGION)

    assert len(findings) == 1
    assert findings[0]["id"] == "my-app"
    assert findings[0]["resource"] == "Log group"


def test_ignores_log_group_with_retention(logs):
    logs.create_log_group(logGroupName="my-app")
    add_log_data(logs, "my-app", 5000)
    logs.put_retention_policy(logGroupName="my-app", retentionInDays=30)

    assert find_log_groups_without_retention(REGION) == []


def test_ignores_empty_log_group(logs):
    logs.create_log_group(logGroupName="empty")

    assert find_log_groups_without_retention(REGION) == []