from __future__ import annotations

import hashlib
import os
from pathlib import Path
from uuid import UUID, uuid4

from app.core.config import get_settings


def store_document(candidate_id: UUID, data: bytes) -> tuple[str, str]:
    root = Path(get_settings().document_storage_path)
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(root, 0o700)
    storage_key = f"{candidate_id}/{uuid4().hex}"
    path = root / storage_key
    path.parent.mkdir(mode=0o700, exist_ok=True)
    path.write_bytes(data)
    os.chmod(path, 0o600)
    return storage_key, hashlib.sha256(data).hexdigest()
