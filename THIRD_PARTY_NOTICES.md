# 第三方项目致谢与声明

`image2svg` 是一个整合工具，并不声称拥有其依赖项目的算法、框架或实现。

## 核心矢量化引擎

- [VTracer](https://github.com/visioncortex/vtracer)，由 VisionCortex 开发，提供本项目默认使用的位图到彩色 SVG 矢量化能力。本项目通过命令行调用 VTracer，不包含或修改 VTracer 的源代码及二进制发布物。VTracer 采用 MIT 许可证；详见其上游仓库的许可证文件。

## 直接依赖

| 项目 | 在本项目中的用途 | 上游许可证与来源 |
| --- | --- | --- |
| [FastAPI](https://github.com/fastapi/fastapi) | HTTP API | MIT |
| [Streamlit](https://github.com/streamlit/streamlit) | 本地图形界面 | Apache-2.0 |
| [Pillow](https://github.com/python-pillow/Pillow) | 图片读取与校验 | HPND / PIL Software License |
| [NumPy](https://github.com/numpy/numpy) | 图像数组处理 | BSD-3-Clause |
| [OpenCV](https://github.com/opencv/opencv)（经 `opencv-python-headless` 分发） | 基础轮廓转换回退实现 | Apache-2.0 |
| [svgwrite](https://github.com/mozman/svgwrite) | SVG 输出 | MIT |
| [python-multipart](https://github.com/Kludex/python-multipart) | API 文件上传解析 | Apache-2.0 |
| [Uvicorn](https://github.com/Kludex/uvicorn) | ASGI 服务运行 | BSD-3-Clause |

开发依赖（如 `pytest`、`httpx`）同样各自受其上游许可证约束。

## 许可证适用范围

本仓库自身代码以 [MIT License](LICENSE) 发布。第三方项目仍分别受其各自许可证约束；本文件是归属说明而非这些许可证文本的替代品。安装、分发或部署时，请以对应版本上游发布物中附带的完整许可证和版权声明为准。
