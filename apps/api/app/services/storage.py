from pathlib import Path
from uuid import uuid4

from app.config import settings


def store_upload(filename: str, content: bytes, owner_id: str | None = None) -> str:
    safe_name = Path(filename).name
    object_name = (owner_id + "/" if owner_id else "") + uuid4().hex + "-" + safe_name
    if settings.gcs_bucket and settings.google_cloud_project:
        from google.cloud import storage

        client = storage.Client(project=settings.google_cloud_project)
        blob = client.bucket(settings.gcs_bucket).blob(object_name)
        blob.upload_from_string(content)
        return "gs://" + settings.gcs_bucket + "/" + object_name
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    target = upload_dir / object_name
    if owner_id:
        target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    return str(target)
