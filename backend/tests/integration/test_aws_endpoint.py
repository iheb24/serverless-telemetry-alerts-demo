"""Smoke test: the local AWS endpoint (floci) is reachable and usable."""

import os
from typing import Any

import boto3

ENDPOINT = os.environ.get("AWS_ENDPOINT_URL", "http://localhost:4566")
REGION = os.environ.get("AWS_DEFAULT_REGION", "eu-west-3")


def build_ssm_client() -> Any:
    """Create an SSM client pinned to the local emulator endpoint."""
    return boto3.client(
        "ssm",
        endpoint_url=ENDPOINT,
        region_name=REGION,
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )


def test_ssm_parameter_round_trip() -> None:
    """A parameter written to the local stack reads back identically."""
    client = build_ssm_client()
    client.put_parameter(
        Name="/harness/smoke", Value="ok", Type="String", Overwrite=True
    )
    response = client.get_parameter(Name="/harness/smoke")
    assert response["Parameter"]["Value"] == "ok"
