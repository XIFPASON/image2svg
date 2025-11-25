# 位图转 SVG 工具 (VTracer 版)

这是一个基于 **VTracer** 的高性能位图转矢量图工具。它能够快速将 PNG/JPG 图片转换为高质量的 SVG 矢量图。

## ✨ 功能特性

- 🚀 **极速转换**: 基于 Rust 编写的 VTracer 引擎，毫秒级转换速度。
- 🎨 **全彩支持**: 完美还原图片颜色，支持彩色和黑白模式。
- 🔧 **参数丰富**: 提供颜色精度、噪点过滤、平滑度等多种调节选项。
- 🖥️ **中文界面**: 简洁直观的 Streamlit 图形界面。
- 📂 **历史记录**: 自动保存并可随时查看之前的转换结果。

## 📦 安装与运行

### 1. 准备环境

确保已安装 Python 3.8+。

```bash
pip install -r requirements.txt
```

### 2. 下载 VTracer

本工具依赖 `vtracer.exe`。
请下载 Windows 版本的 `vtracer.exe` 并将其放在项目根目录下。

### 3. 启动应用

```powershell
.\run_gui.ps1
```

浏览器将自动打开 `http://localhost:8501`。

## 🛠️ 参数说明

- **颜色模式**: 彩色或黑白。
- **颜色精度**: 控制生成的颜色数量，精度越高文件越大。
- **噪点过滤**: 过滤掉画面中的微小噪点。
- **曲线模式**: 平滑曲线 (Spline) 适合插画，直线 (Polygon) 适合几何图形。
- **分层模式**: 堆叠 (Stacked) 适合编辑，剪切 (Cutout) 适合切割。

## 📝 项目结构

- `frontend/app.py`: Streamlit 界面代码
- `backend/core/fast_converter.py`: 核心转换逻辑
- `vtracer.exe`: 转换引擎 (需手动下载)
- `outputs/`: 存放转换结果

---
*Powered by [VTracer](https://github.com/visioncortex/vtracer)*
