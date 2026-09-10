# Third-Party Notices

`image2svg` is an integration tool. It does not claim ownership of the algorithms, frameworks, or implementations provided by its dependencies.

## Core Vectorization Engine

- [VTracer](https://github.com/visioncortex/vtracer), developed by VisionCortex, provides the default bitmap-to-color-SVG vectorization engine. This project invokes VTracer as a command-line executable; it does not include or modify VTracer source code or binary releases. VTracer is licensed under MIT; refer to its upstream repository for the full license text.

## Direct Dependencies

| Project | Role in image2svg | Upstream license |
| --- | --- | --- |
| [FastAPI](https://github.com/fastapi/fastapi) | HTTP API | MIT |
| [Streamlit](https://github.com/streamlit/streamlit) | Local graphical interface | Apache-2.0 |
| [Pillow](https://github.com/python-pillow/Pillow) | Image loading and validation | HPND / PIL Software License |
| [NumPy](https://github.com/numpy/numpy) | Image-array processing | BSD-3-Clause |
| [OpenCV](https://github.com/opencv/opencv), distributed through `opencv-python-headless` | Fallback contour tracing | Apache-2.0 |
| [svgwrite](https://github.com/mozman/svgwrite) | SVG output | MIT |
| [python-multipart](https://github.com/Kludex/python-multipart) | API upload parsing | Apache-2.0 |
| [Uvicorn](https://github.com/Kludex/uvicorn) | ASGI server | BSD-3-Clause |

Development dependencies, including `pytest` and `httpx`, remain subject to their own upstream licenses.

## License Scope

Code authored for this repository is released under the [MIT License](LICENSE). Every third-party component remains governed by its own license. This notice is an attribution summary, not a replacement for any upstream license text; use the full copyright and license notices shipped with the applicable upstream release when installing, distributing, or deploying this project.
