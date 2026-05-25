from __future__ import annotations

import mimetypes
from functools import lru_cache

from faceless.config import get_settings


def is_configured() -> bool:
    return get_settings().storage_configured


@lru_cache
def _client():
    import boto3

    s = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=s.require("storage_endpoint_url"),
        aws_access_key_id=s.require("storage_access_key_id"),
        aws_secret_access_key=s.require("storage_secret_access_key"),
        region_name=s.storage_region,
    )


def upload_file(local_path: str, key: str, *, dry_run: bool = False) -> str:
    """Upload a file to S3-compatible storage (e.g. Cloudflare R2). Returns its
    public URL (STORAGE_PUBLIC_BASE_URL + key)."""
    s = get_settings()
    if dry_run:
        base = (s.storage_public_base_url or "https://media.example.invalid").rstrip("/")
        return f"{base}/{key}"

    content_type = mimetypes.guess_type(local_path)[0] or "application/octet-stream"
    _client().upload_file(
        local_path,
        s.require("storage_bucket"),
        key,
        ExtraArgs={"ContentType": content_type},
    )
    return f"{s.require('storage_public_base_url').rstrip('/')}/{key}"
