"""Fixtures for integration tests against the local AWS emulator (floci)."""

import os
from collections.abc import Callable
from typing import Any

import boto3
import pytest

ENDPOINT = os.environ.get("AWS_ENDPOINT_URL", "http://localhost:4566")
REGION = os.environ.get("AWS_DEFAULT_REGION", "eu-west-3")


@pytest.fixture
def aws_client() -> Callable[[str], Any]:
    """Return a factory creating boto3 clients pinned to the local endpoint."""
    factory: Any = boto3.client

    def make(service: str) -> Any:
        """Create a client for one service with test credentials."""
        return factory(
            service,
            endpoint_url=ENDPOINT,
            region_name=REGION,
            aws_access_key_id="test",
            aws_secret_access_key="test",
        )

    return make
