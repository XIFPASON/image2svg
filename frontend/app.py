import streamlit as st
import os
import sys
import time
import base64
from PIL import Image

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.core.fast_converter import FastConverter

st.set_page_config(page_title="位图转 SVG 工具", layout="wide")

st.title("位图转 SVG 工具 (VTracer)")
st.markdown("基于 VTracer 的高性能矢量化工具。")

# Sidebar for configuration
st.sidebar.header("配置选项")

# Check for VTracer
vtracer_path = "vtracer.exe" if os.path.exists("vtracer.exe") else None

if not vtracer_path:
    st.error("❌ 未检测到 vtracer.exe！")
    st.info("请下载 vtracer.exe 并放置在项目根目录下。")
    st.stop()

st.sidebar.success("✅ VTracer 已就绪")

# VTracer Parameters
st.sidebar.markdown("### 基础设置")
colormode = st.sidebar.selectbox("颜色模式", ["color (彩色)", "binary (黑白)"], index=0)
colormode_val = "color" if "color" in colormode else "binary"

color_precision = st.sidebar.slider("颜色精度", 1, 8, 6, help="数值越高颜色越准，但文件越大")
filter_speckle = st.sidebar.slider("噪点过滤", 0, 128, 4, help="过滤掉小于此像素值的噪点区域")

# Advanced Settings
with st.sidebar.expander("高级设置"):
    mode = st.sidebar.selectbox("曲线模式", ["spline (平滑曲线)", "polygon (直线)", "none (无)"], index=0)
    mode_val = mode.split(" ")[0]
    
    hierarchical = st.sidebar.selectbox("分层模式", ["stacked (堆叠)", "cutout (剪切)"], index=0, help="堆叠：形状互相覆盖；剪切：形状互不重叠")
    hierarchical_val = hierarchical.split(" ")[0]
    
    gradient_step = st.sidebar.slider("梯度阈值", 0, 255, 64, help="用于梯度检测的阈值")
    corner_threshold = st.sidebar.slider("拐角阈值", 0, 180, 60, help="识别为拐角的角度阈值")
    segment_length = st.sidebar.slider("最小线段长度", 3, 20, 4, help="线段的最小长度")
    splice_threshold = st.sidebar.slider("拼接阈值", 0, 180, 45, help="曲线拼接的角度阈值")

uploaded_file = st.file_uploader("上传图片", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("原始图片")
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
        
        # Save uploaded file temporarily
        temp_input_path = os.path.join("uploads", f"temp_{uploaded_file.name}")
        os.makedirs("uploads", exist_ok=True)
        with open(temp_input_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

    if st.button("开始转换"):
        with col2:
            st.subheader("生成的 SVG")
            
            # Progress and Status Elements
            status_text = st.empty()
            progress_bar = st.progress(0)
            timer_text = st.empty()
            
            # Use timestamp for unique filename
            timestamp = int(time.time())
            output_filename = f"result_{timestamp}_{uploaded_file.name}.svg"
            output_path = os.path.join("outputs", output_filename)
            os.makedirs("outputs", exist_ok=True)
            
            start_time = time.time()
            
            try:
                converter = FastConverter()
                status_text.text("正在运行 VTracer...")
                
                def update_progress(current, total, _):
                    progress = min(current / max(total, 1), 1.0)
                    progress_bar.progress(progress)
                
                converter.convert(
                    temp_input_path, 
                    output_path, 
                    callback=update_progress,
                    colormode=colormode_val,
                    filter_speckle=filter_speckle,
                    color_precision=color_precision,
                    mode=mode_val,
                    hierarchical=hierarchical_val,
                    gradient_step=gradient_step,
                    corner_threshold=corner_threshold,
                    segment_length=segment_length,
                    splice_threshold=splice_threshold
                )
                
                # Finalize
                end_time = time.time()
                duration = end_time - start_time
                progress_bar.progress(100)
                status_text.text("完成！")
                timer_text.markdown(f"✅ **总耗时:** {duration:.2f}秒")
                
                # Display SVG Preview
                st.markdown("### 预览")
                with open(output_path, "r") as f:
                    svg_content = f.read()
                    b64 = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
                    html = f'<img src="data:image/svg+xml;base64,{b64}" style="width: 100%; max-width: 800px; border: 1px solid #ddd; border-radius: 5px;"/>'
                    st.markdown(html, unsafe_allow_html=True)
                
                # Download Button
                with open(output_path, "rb") as f:
                    st.download_button(
                        label=f"下载 SVG ({duration:.2f}s)",
                        data=f,
                        file_name=output_filename,
                        mime="image/svg+xml"
                    )

                st.success(f"转换成功！耗时 {duration:.2f}秒")
                
            except Exception as e:
                st.error(f"发生错误: {e}")

# History Section
st.sidebar.markdown("---")
st.sidebar.header("历史记录")
if os.path.exists("outputs"):
    files = sorted(os.listdir("outputs"), reverse=True)
    svg_files = [f for f in files if f.endswith(".svg")]
    
    if svg_files:
        selected_file = st.sidebar.selectbox("选择之前的转换结果", ["无"] + svg_files)
        
        if selected_file != "无":
            file_path = os.path.join("outputs", selected_file)
            st.sidebar.markdown(f"**预览: {selected_file}**")
            with open(file_path, "r") as f:
                svg_content = f.read()
                b64 = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
                html = f'<img src="data:image/svg+xml;base64,{b64}" style="width: 100%; border: 1px solid #ddd; border-radius: 5px; background: white;"/>'
                st.sidebar.markdown(html, unsafe_allow_html=True)
                
            with open(file_path, "rb") as f:
                st.sidebar.download_button(
                    label="下载",
                    data=f,
                    file_name=selected_file,
                    mime="image/svg+xml"
                )
    else:
        st.sidebar.text("暂无历史记录")
