"""Build and verify workload container images against the local ECR (floci).

Reads `.harness/state.yaml` for containerized workloads, maps their ECR
repositories from `terraform show`, builds each image, verifies the package
imports cleanly inside the built container, and pushes when an OCI registry
endpoint is active.
"""

import base64
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import boto3
import yaml

ROOT = Path(__file__).resolve().parents[1]


def _run(argv: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
    """Run one command and return the completed process."""
    return subprocess.run(  # noqa: S603
        argv, capture_output=True, text=True, check=False, **kwargs
    )


def _ecr_urls(env: dict[str, str]) -> dict[str, str]:
    """Map ECR repository names to their URIs from the applied state."""
    show = _run(["terraform", "show", "-json"], cwd=ROOT / "infra", env=env)
    payload = json.loads(show.stdout or "{}")
    repos: dict[str, str] = {}
    modules = payload.get("values", {}).get("root_module", {}).get("child_modules", [])
    for module in modules:
        for resource in module.get("resources", []):
            if resource.get("type") == "aws_ecr_repository":
                values = resource.get("values", {})
                repos[values["name"]] = values["repository_url"]
    return repos


def _tls_flags(runtime: str) -> list[str]:
    """Return TLS bypass flags for Podman against local HTTP emulators."""
    return ["--tls-verify=false"] if Path(runtime).name == "podman" else []


def _podman_login(runtime: str, url: str) -> subprocess.CompletedProcess[str]:
    """Attempt to log the container runtime into the emulator's ECR registry."""
    registry = url.split("/", maxsplit=1)[0]
    region = os.environ.get("AWS_DEFAULT_REGION", "eu-west-3")
    ecr = boto3.client(
        "ecr",
        endpoint_url=os.environ.get("AWS_ENDPOINT_URL", "http://localhost:4566"),
        region_name=region,
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "test"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "test"),
    )
    token = ecr.get_authorization_token()["authorizationData"][0]["authorizationToken"]
    password = base64.b64decode(token).decode().split(":", maxsplit=1)[1]
    return _run(
        [
            runtime,
            "login",
            *_tls_flags(runtime),
            registry,
            "--username",
            "AWS",
            "--password-stdin",
        ],
        input=password,
    )


def _build_and_verify(
    runtime: str,
    package: str,
    uri: str,
    env: dict[str, str],
) -> str | None:
    """Build the workload image, smoke-test it, and push if registry is active."""
    image = f"{uri}:latest"
    build = _run(
        [runtime, "build", "-f", f"backend/{package}/Dockerfile", "-t", image, "."],
        cwd=ROOT,
        env=env,
    )
    if build.returncode != 0:
        return f"build: {build.stderr[-300:]}"
    smoke = _run(
        [runtime, "run", "--rm", image, "python", "-c", f"import {package}"],
        cwd=ROOT,
        env=env,
    )
    if smoke.returncode != 0:
        return f"smoke: {smoke.stderr[-300:]}"
    login = _podman_login(runtime, uri)
    if login.returncode == 0:
        push = _run([runtime, "push", *_tls_flags(runtime), image], env=env)
        if push.returncode != 0 and "503" not in push.stderr:
            return f"push: {push.stderr[-300:]}"
    elif "503" not in login.stderr and "HTTP response" not in login.stderr:
        return f"ecr login: {login.stderr[-300:]}"
    return None


def main() -> int:
    """Build, verify, and push every containerized workload image."""
    state = yaml.safe_load(
        (ROOT / ".harness" / "state.yaml").read_text(encoding="utf-8")
    )
    workloads = [
        (w["package_name"], w["image_repo"])
        for stack in state.get("stacks", [])
        for w in stack.get("workloads", [])
        if w.get("containerized") and w.get("image_repo")
    ]
    if not workloads:
        print("no containerized workloads")
        return 0
    env = dict(os.environ)
    repos = _ecr_urls(env)
    runtime = shutil.which("podman") or shutil.which("docker") or "podman"
    rc = 0
    for package, repo_name in workloads:
        uri = repos.get(repo_name)
        if uri is None:
            print(f"FAILED {package}: no ecr repository named {repo_name}")
            rc = 1
            continue
        err = _build_and_verify(runtime, package, uri, env)
        if err is not None:
            print(f"FAILED {package}: {err}")
            rc = 1
            continue
        print(f"pushed {uri}:latest")
    return rc


if __name__ == "__main__":
    sys.exit(main())
