from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from backend.api.app import app, tasks


def test_rejects_unsupported_upload() -> None:
    client = TestClient(app)
    response = client.post("/convert", files={"file": ("notes.txt", b"hello", "text/plain")})
    assert response.status_code == 415


def test_unknown_task_returns_404() -> None:
    client = TestClient(app)
    response = client.get("/result/not-a-task")
    assert response.status_code == 404


def test_upload_paths_do_not_include_user_filename() -> None:
    from backend.core.config import new_upload_path

    path = new_upload_path("../../unsafe.png")
    assert path.parent.name == "uploads"
    assert path.name.endswith(".png")
    assert "unsafe" not in path.name


def test_valid_png_converts_and_returns_svg() -> None:
    image_bytes = BytesIO()
    Image.new("RGB", (4, 4), "red").save(image_bytes, format="PNG")

    client = TestClient(app)
    response = client.post(
        "/convert",
        files={"file": ("sample.png", image_bytes.getvalue(), "image/png")},
    )

    assert response.status_code == 200
    task_id = response.json()["task_id"]
    try:
        result = client.get(response.json()["output_url"])
        assert result.status_code == 200
        assert result.headers["content-type"].startswith("image/svg+xml")
    finally:
        output_path = Path(tasks.pop(task_id)["output_path"])
        output_path.unlink(missing_ok=True)
