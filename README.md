# image2svg

一个本地运行的位图转 SVG 工具，提供 Streamlit 图形界面和 FastAPI 接口。默认使用 [VTracer](https://github.com/visioncortex/vtracer) 生成彩色 SVG；未安装 VTracer 时会回退到基础黑白轮廓转换。

## 特性

- 支持 PNG、JPG、JPEG 输入，以及 VTracer 的颜色、曲线和分层参数。
- 支持在浏览器中预览 SVG、编辑颜色与下载结果。
- 同时提供图形界面和 HTTP API。
- 运行数据存于 `.image2svg/`，不提交用户图片和转换结果。

## 要求

- Python 3.10 或更高版本。
- 可选但推荐：安装 VTracer 并确保 `vtracer` 在 `PATH` 中。也可通过 `VTRACER_PATH` 指向可执行文件。

VTracer 提供 Windows、macOS 和 Linux 的安装方式，请参考其官方仓库。项目不包含其二进制文件，因此不会将平台特定文件或第三方发布产物提交到 Git。

## 安装与运行

```bash
git clone https://github.com/yolloo888/image2svg.git
cd image2svg
python -m venv .venv
```

激活虚拟环境后安装：

```bash
pip install -e .
```

启动图形界面：

```bash
python -m streamlit run frontend/app.py
```

Windows 用户也可以运行 `./run_gui.ps1`。默认地址为 `http://localhost:8501`。

## HTTP API

```bash
uvicorn backend.api.app:app --reload
curl -F "file=@example.png" http://127.0.0.1:8000/convert
```

响应会返回任务 ID 和结果地址。轮询 `GET /result/{task_id}`；完成后将直接返回 SVG。默认单个上传最大 20 MiB，可用 `IMAGE2SVG_MAX_UPLOAD_BYTES` 调整。

## 配置

| 环境变量 | 用途 |
| --- | --- |
| `VTRACER_PATH` | VTracer 可执行文件的绝对或相对路径。 |
| `IMAGE2SVG_DATA_DIR` | 上传和输出目录，默认 `.image2svg/`。 |
| `IMAGE2SVG_MAX_UPLOAD_BYTES` | API 单个上传大小上限，默认 `20971520`。 |

公开部署 API 前，请在反向代理层配置认证、速率限制、文件清理和请求大小限制。该项目默认定位为本地工具。

## 开发

```bash
pip install -e ".[dev]"
pytest
```

欢迎阅读 [贡献指南](CONTRIBUTING.md)。项目以 [MIT](LICENSE) 协议发布；VTracer 及其他依赖分别遵循其自身许可证。
