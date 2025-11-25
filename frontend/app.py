import streamlit as st
import os
import sys
import time
import base64
from PIL import Image

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.core.fast_converter import FastConverter
from backend.core.color_manager import SVGColorManager

st.set_page_config(page_title="位图转 SVG 工具", layout="wide", page_icon="🎨")

# Custom CSS for better UI
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
    .color-box {
        width: 25px; 
        height: 25px; 
        border-radius: 50%; 
        display: inline-block; 
        margin-right: 5px; 
        border: 2px solid #eee;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #333;
        margin-bottom: 1rem;
    }
    .history-card {
        background-color: white;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #eee;
        margin-bottom: 10px;
        text-align: center;
        transition: transform 0.2s;
    }
# ... (previous CSS)
    .history-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* 右侧固定栏样式 Hack */
    /* 选中主布局的 Columns 容器 */
    section[data-testid="stMain"] > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] {
        align-items: flex-start; /* 顶部对齐 */
    }
    
    /* 强制固定右侧列 (第二个 Column) */
    section[data-testid="stMain"] > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) {
        position: fixed !important;
        top: 3.75rem; /* 避开 Header */
        right: 0;
        width: 320px !important; /* 固定宽度 */
        height: calc(100vh - 3.75rem);
        overflow-y: auto;
        background-color: #ffffff;
        border-left: 1px solid #e0e0e0;
        padding: 20px;
        z-index: 990;
        box-shadow: -2px 0 10px rgba(0,0,0,0.02);
    }
    
    /* 调整左侧列 (第一个 Column) 以适应右侧固定栏 */
    section[data-testid="stMain"] > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1) {
        margin-right: 340px; /* 留出右侧栏宽度 + 间隙 */
        width: auto !important;
        min-width: 0; /* 防止 flex 子项溢出 */
    }
    
    /* 隐藏右侧列在移动端的固定效果 (可选) */
    @media (max-width: 768px) {
        section[data-testid="stMain"] > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) {
            position: static !important;
            width: 100% !important;
            height: auto;
            border-left: none;
            box-shadow: none;
        }
        section[data-testid="stMain"] > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1) {
            margin-right: 0;
        }
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🎨 位图转 SVG 工具 (VTracer)</div>', unsafe_allow_html=True)

# Initialize Session State for Advanced Settings
default_settings = {
    "adv_mode": "spline (平滑曲线)",
    "adv_hierarchical": "stacked (堆叠)",
    "adv_gradient_step": 64,
    "adv_corner_threshold": 60,
    "adv_segment_length": 4,
    "adv_splice_threshold": 45
}

for key, val in default_settings.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Define History Dialog
@st.dialog("📜 历史记录", width="large")
def show_history_dialog():
    st.markdown("""
    <style>
        .history-card {
            background-color: #f8f9fa;
            border: 1px solid #eee;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
            transition: transform 0.2s;
            margin-bottom: 10px;
        }
        .history-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-color: #ddd;
        }
        .history-filename {
            font-size: 0.8em;
            color: #666;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-top: 5px;
        }
    </style>
    """, unsafe_allow_html=True)

    if os.path.exists("outputs"):
        files = sorted(os.listdir("outputs"), reverse=True)
        svg_files = [f for f in files if f.endswith(".svg") and "edited" not in f]
        
        if not svg_files:
            st.info("暂无历史记录")
        else:
            # Grid Layout for Dialog
            cols_per_row = 4
            rows = [svg_files[i:i + cols_per_row] for i in range(0, len(svg_files), cols_per_row)]
            
            for row in rows:
                cols = st.columns(cols_per_row)
                for idx, filename in enumerate(row):
                    file_path = os.path.join("outputs", filename)
                    with cols[idx]:
                        try:
                            with open(file_path, "r") as f:
                                svg_content = f.read()
                                b64 = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
                            
                            # Thumbnail
                            html = f'''
                            <div class="history-card">
                                <a href="data:image/svg+xml;base64,{b64}" download="{filename}" style="text-decoration: none; color: inherit; display: block;">
                                    <img src="data:image/svg+xml;base64,{b64}" style="width: 100%; height: 80px; object-fit: contain;" title="{filename}"/>
                                    <div class="history-filename">{filename}</div>
                                </a>
                            </div>
                            '''
                            st.markdown(html, unsafe_allow_html=True)
                            
                            # Buttons
                            c1, c2 = st.columns(2)
                            with c1:
                                if st.button("📂", key=f"l_{filename}", help="加载"):
                                    st.session_state['current_svg_path'] = file_path
                                    st.session_state['original_svg_path'] = file_path
                                    st.rerun()
                            with c2:
                                if st.button("🗑️", key=f"d_{filename}", help="删除"):
                                    try:
                                        os.remove(file_path)
                                        st.rerun()
                                    except:
                                        pass
                        except:
                            pass

# Sidebar for configuration
with st.sidebar:
    # Check for VTracer (Silent check)
    vtracer_path = "vtracer.exe" if os.path.exists("vtracer.exe") else None
    if not vtracer_path:
        st.error("❌ 未检测到 vtracer.exe")
        st.info("请下载 vtracer.exe 并放置在项目根目录下。")
        st.stop()

    # History Button
    if st.button("📜 历史记录", use_container_width=True):
        show_history_dialog()

    st.markdown("---")
    st.subheader("基础设置")
    colormode = st.selectbox("颜色模式", ["color (彩色)", "binary (黑白)"], index=0)
    colormode_val = "color" if "color" in colormode else "binary"
    
    color_precision = st.slider("颜色精度", 1, 8, 6, help="数值越高颜色越准，但文件越大")
    filter_speckle = st.slider("噪点过滤", 0, 128, 4, help="过滤掉小于此像素值的噪点区域")

    # Advanced Settings in Sidebar (Default Expanded)
    with st.expander("🛠️ 高级设置", expanded=True):
        st.selectbox(
            "曲线模式", 
            ["spline (平滑曲线)", "polygon (直线)", "none (无)"], 
            key="adv_mode",
            index=["spline", "polygon", "none"].index(st.session_state['adv_mode'].split(" ")[0])
        )
        
        st.selectbox(
            "分层模式", 
            ["stacked (堆叠)", "cutout (剪切)"], 
            key="adv_hierarchical",
            index=["stacked", "cutout"].index(st.session_state['adv_hierarchical'].split(" ")[0])
        )
        
        st.slider("梯度阈值", 0, 255, key="adv_gradient_step", value=st.session_state['adv_gradient_step'])
        st.slider("拐角阈值", 0, 180, key="adv_corner_threshold", value=st.session_state['adv_corner_threshold'])
        st.slider("最小线段长度", 3, 20, key="adv_segment_length", value=st.session_state['adv_segment_length'])
        st.slider("拼接阈值", 0, 180, key="adv_splice_threshold", value=st.session_state['adv_splice_threshold'])

# Main Layout
# Use columns to create the layout structure, CSS will handle the positioning
col_main, col_right = st.columns([1, 1]) # Ratio doesn't matter much due to CSS override, but keeping 1:1 is safe

with col_main:
    st.subheader("📤 上传图片")
    
    # Initialize uploader key for reset functionality
    if 'uploader_key' not in st.session_state:
        st.session_state['uploader_key'] = 0

    # File Uploader
    uploaded_file = st.file_uploader(
        "拖拽或点击上传", 
        type=["png", "jpg", "jpeg"], 
        key=f"uploader_{st.session_state['uploader_key']}"
    )

    if uploaded_file:
        # CSS to hide the native uploaded file list
        st.markdown("""
        <style>
            div[data-testid='stFileUploader'] section[data-testid='stFileUploaderDropzone'] + div {
                display: none;
            }
            div[data-testid='stFileUploader'] ul {
                display: none;
            }
        </style>
        """, unsafe_allow_html=True)

        image = Image.open(uploaded_file)
        
        # Save temp
        temp_input_path = os.path.join("uploads", f"temp_{uploaded_file.name}")
        os.makedirs("uploads", exist_ok=True)
        with open(temp_input_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Custom Uploaded File Row
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([1, 3, 2, 0.5])
            
            with c1:
                # Thumbnail
                st.image(image, use_container_width=True)
            
            with c2:
                # File Info
                st.markdown(f"**{uploaded_file.name}**")
                st.caption(f"{uploaded_file.size / 1024:.1f} KB")
                st.caption("✨ 调整左侧参数可实时预览")
                
            with c3:
                # Placeholder for alignment, or we can remove this column if not needed
                st.empty()
                
            with c4:
                # Delete Button
                if st.button("✕", help="移除图片"):
                    st.session_state['uploader_key'] += 1
                    # Clear session state related to current file
                    keys_to_clear = ['current_svg_path', 'original_svg_path', 'last_params', 'last_file_id']
                    for k in keys_to_clear:
                        if k in st.session_state:
                            del st.session_state[k]
                    st.rerun()

        # --- Real-time Conversion Logic ---
        
        # 1. Collect current parameters
        current_params = {
            "colormode": colormode_val,
            "filter_speckle": filter_speckle,
            "color_precision": color_precision,
            "mode": st.session_state['adv_mode'].split(" ")[0],
            "hierarchical": st.session_state['adv_hierarchical'].split(" ")[0],
            "gradient_step": st.session_state['adv_gradient_step'],
            "corner_threshold": st.session_state['adv_corner_threshold'],
            "segment_length": st.session_state['adv_segment_length'],
            "splice_threshold": st.session_state['adv_splice_threshold']
        }
        
        # 2. Check if conversion is needed
        file_id = f"{uploaded_file.name}_{uploaded_file.size}"
        last_params = st.session_state.get('last_params', {})
        last_file_id = st.session_state.get('last_file_id', None)
        
        should_convert = (
            'current_svg_path' not in st.session_state or 
            not os.path.exists(st.session_state['current_svg_path']) or
            file_id != last_file_id or
            current_params != last_params
        )

        if should_convert:
            with st.spinner("正在实时转换..."):
                timestamp = int(time.time())
                output_filename = f"result_{timestamp}_{uploaded_file.name}.svg"
                output_path = os.path.join("outputs", output_filename)
                os.makedirs("outputs", exist_ok=True)
                
                try:
                    converter = FastConverter()
                    converter.convert(
                        temp_input_path, output_path,
                        colormode=current_params['colormode'],
                        filter_speckle=current_params['filter_speckle'],
                        color_precision=current_params['color_precision'],
                        mode=current_params['mode'],
                        hierarchical=current_params['hierarchical'],
                        gradient_step=current_params['gradient_step'],
                        corner_threshold=current_params['corner_threshold'],
                        segment_length=current_params['segment_length'],
                        splice_threshold=current_params['splice_threshold']
                    )
                    
                    # Update State
                    st.session_state['current_svg_path'] = output_path
                    st.session_state['original_svg_path'] = output_path
                    st.session_state['last_params'] = current_params
                    st.session_state['last_file_id'] = file_id
                    
                    # Force rerun to update the preview immediately
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"转换失败: {e}")

    # Display Result (if exists)
    if 'current_svg_path' in st.session_state and os.path.exists(st.session_state['current_svg_path']):
        st.markdown("---")
        st.subheader("SVG 预览")
        current_path = st.session_state['current_svg_path']
        
        # Display SVG
        with open(current_path, "r") as f:
            svg_content = f.read()
            b64 = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
            html = f'''
            <div style="background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #ddd; text-align: center;">
                <img src="data:image/svg+xml;base64,{b64}" style="max-width: 100%; max-height: 600px;"/>
            </div>
            '''
            st.markdown(html, unsafe_allow_html=True)
        
        st.markdown("###") 
        
        # Download Button
        with open(current_path, "rb") as f:
            file_name = os.path.basename(current_path)
            st.download_button(
                label="⬇️ 下载 SVG 文件",
                data=f,
                file_name=file_name,
                mime="image/svg+xml",
                type="primary"
            )
    else:
        if not uploaded_file:
            st.info("👈 请先上传图片，系统将自动进行矢量化转换")

# Right Sidebar (Column) for Color Palette
with col_right:
    if 'current_svg_path' in st.session_state and os.path.exists(st.session_state['current_svg_path']):
        st.subheader("🎨 智能调色板")
        
        # Initialize Color Manager
        if 'color_manager' not in st.session_state or st.session_state.get('cm_svg_path') != st.session_state['current_svg_path']:
            st.session_state['color_manager'] = SVGColorManager(st.session_state['current_svg_path'])
            st.session_state['cm_svg_path'] = st.session_state['current_svg_path']
        
        cm = st.session_state['color_manager']
        unique_colors = cm.get_unique_colors()
        
        st.caption(f"共 {len(unique_colors)} 种颜色")
        
        # Tolerance Slider
        tolerance = st.slider("合并容差", 0, 100, 10, key="sidebar_tolerance")
        groups = cm.group_similar_colors(tolerance)
        
        # Color Editing Form
        with st.form("sidebar_color_editor"):
            changes_map = {}
            
            # List layout for color groups
            for i, (main_color, similar_colors) in enumerate(groups.items()):
                with st.container(border=True):
                    c_col1, c_col2 = st.columns([3, 1])
                    with c_col1:
                        st.markdown(f"**组 {i+1}** ({len(similar_colors)})")
                        swatches = "".join([f'<div class="color-box" style="background-color:{c}; width:15px; height:15px;" title="{c}"></div>' for c in similar_colors])
                        st.markdown(swatches, unsafe_allow_html=True)
                    with c_col2:
                        new_color = st.color_picker("修改", value=main_color, key=f"cp_sb_{i}", label_visibility="collapsed")
                    
                    for original in similar_colors:
                        if original != new_color:
                            changes_map[original] = new_color
            
            apply_btn = st.form_submit_button("✨ 应用更改", type="primary")
            
            if apply_btn:
                if changes_map:
                    new_filename = f"edited_{int(time.time())}.svg"
                    new_output_path = os.path.join("outputs", new_filename)
                    cm.apply_changes(changes_map, new_output_path)
                    
                    st.session_state['current_svg_path'] = new_output_path
                    st.rerun()
