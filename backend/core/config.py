"""Shared paths and input validation for local and web entry points."""

from __future__ import annotations

import os
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.environ.get("IMAGE2SVG_DATA_DIR", PROJECT_ROOT / ".image2svg")).expanduser()
UPLOAD_DIR = DATA_DIR / "uploads"
OUTPUT_DIR = DATA_DIR / "outputs"
ALLOWED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}


def ensure_data_directories() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def new_upload_path(filename: str) -> Path:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_IMAGE_SUFFIXES:
        raise ValueError("Only PNG and JPEG images are supported.")
    ensure_data_directories()
    return UPLOAD_DIR / f"{uuid.uuid4().hex}{suffix}"


def new_output_path() -> Path:
    ensure_data_directories()
    return OUTPUT_DIR / f"{uuid.uuid4().hex}.svg"
