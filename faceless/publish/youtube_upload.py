from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime

from faceless.config import get_settings
from faceless.niches.base import Niche

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


@dataclass
class UploadResult:
    video_id: str
    url: str


def _get_credentials():
    """Load cached OAuth creds, refreshing or running the consent flow as needed."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    settings = get_settings()
    token_file = settings.youtube_token_file
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.youtube_client_secret_file, SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(token_file, "w") as f:
            f.write(creds.to_json())
    return creds


def upload_to_youtube(
    video_path: str,
    title: str,
    description: str,
    tags: list[str],
    niche: Niche,
    *,
    publish_at: datetime | None = None,
    dry_run: bool = False,
) -> UploadResult:
    """Upload a video as private (or scheduled), with the niche's policy flags.

    Sets selfDeclaredMadeForKids and the altered/synthetic-content disclosure per
    the niche's PublishConfig. Note quota: videos.insert costs ~1600 units, so the
    default 10k/day quota allows ~6 uploads/day — request an increase for 5-10/day.
    """
    if dry_run:
        return UploadResult(video_id="DRYRUN_VIDEO_ID", url="https://youtu.be/DRYRUN_VIDEO_ID")

    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    youtube = build("youtube", "v3", credentials=_get_credentials())

    status = {
        "privacyStatus": "private",
        "selfDeclaredMadeForKids": niche.publish.made_for_kids,
        "containsSyntheticMedia": niche.publish.synthetic_content_disclosure,
    }
    if publish_at:
        status["publishAt"] = publish_at.isoformat()

    body = {
        "snippet": {"title": title[:100], "description": description, "tags": tags},
        "status": status,
    }
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        _status, response = request.next_chunk()
    vid = response["id"]
    return UploadResult(video_id=vid, url=f"https://youtu.be/{vid}")
