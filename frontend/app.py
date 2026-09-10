import streamlit as st
import os
import sys
import base64
from PIL import Image

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.core.fast_converter import FastConverter
from backend.core.color_manager import SVGColorManager
from backend.core.config import OUTPUT_DIR, new_output_path, new_upload_path

st.set_page_config(page_title="Image to SVG", layout="wide", page_icon="🎨")

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
    
    /* Fixed right-panel layout */
    /* Align the main column container at the top. */
    section[data-testid="stMain"] > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] {
        align-items: flex-start;
    }
    
    /* Pin the second column as the right panel. */
    section[data-testid="stMain"] > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) {
        position: fixed !important;
        top: 3.75rem;
        right: 0;
        width: 320px !important;
        height: calc(100vh - 3.75rem);
        overflow-y: auto;
        background-color: #ffffff;
        border-left: 1px solid #e0e0e0;
        padding: 20px;
        z-index: 990;
        box-shadow: -2px 0 10px rgba(0,0,0,0.02);
    }
    
    /* Reserve room for the fixed right panel. */
    section[data-testid="stMain"] > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1) {
        margin-right: 340px;
        width: auto !important;
        min-width: 0;
    }
    
    /* Restore normal column flow on narrow screens. */
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

st.markdown('<div class="main-header">🎨 Image to SVG (VTracer)</div>', unsafe_allow_html=True)

# Initialize Session State for Advanced Settings
default_settings = {
    "adv_mode": "spline (Smooth)",
    "adv_hierarchical": "stacked (Stacked)",
    "adv_gradient_step": 64,
    "adv_corner_threshold": 60,
    "adv_segment_length": 4,
    "adv_splice_threshold": 45
}

for key, val in default_settings.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Initialize History Stack
if 'history_stack' not in st.session_state:
    st.session_state['history_stack'] = []
if 'history_pointer' not in st.session_state:
    st.session_state['history_pointer'] = -1

def push_to_history(path):
    # Truncate if we are in the middle of the stack
    if st.session_state['history_pointer'] < len(st.session_state['history_stack']) - 1:
        st.session_state['history_stack'] = st.session_state['history_stack'][:st.session_state['history_pointer']+1]
    
    # Avoid pushing duplicates if it's the same as current
    if not st.session_state['history_stack'] or st.session_state['history_stack'][-1] != path:
        st.session_state['history_stack'].append(path)
        st.session_state['history_pointer'] += 1

# Define History Dialog
@st.dialog("📜 History", width="large")
def show_history_dialog():
    # ... (existing code for history dialog)
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

    if OUTPUT_DIR.exists():
        files = sorted(OUTPUT_DIR.iterdir(), reverse=True)
        svg_files = [f for f in files if f.suffix == ".svg"]
        
        if not svg_files:
            st.info("No conversion history yet.")
        else:
            # Grid Layout for Dialog
            cols_per_row = 4
            rows = [svg_files[i:i + cols_per_row] for i in range(0, len(svg_files), cols_per_row)]
            
            for row in rows:
                cols = st.columns(cols_per_row)
                for idx, file_path in enumerate(row):
                    filename = file_path.name
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
                                if st.button("📂", key=f"l_{filename}", help="Load"):
                                    st.session_state['current_svg_path'] = str(file_path)
                                    st.session_state['original_svg_path'] = str(file_path)
                                    push_to_history(file_path) # Add loaded file to history
                                    st.rerun()
                            with c2:
                                if st.button("🗑️", key=f"d_{filename}", help="Delete"):
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
    if not FastConverter().is_vtracer_available:
        st.warning("VTracer was not found. Basic monochrome contour tracing will be used. Install VTracer for high-quality color output.")

    # History Button
    if st.button("📜 History", use_container_width=True):
        show_history_dialog()

    st.markdown("---")
    st.subheader("Basic Settings")
    colormode = st.selectbox("Color Mode", ["color", "binary"], index=0, help="Choose color or monochrome output.")
    colormode_val = "color" if "color" in colormode else "binary"
    
    color_precision = st.slider("Color Precision", 1, 8, 6, help="Higher values preserve more colors but create larger files. Default: 6.")
    filter_speckle = st.slider("Speckle Filter", 0, 128, 4, help="Remove small noisy regions. Default: 4.")

    # Advanced Settings in Sidebar (Default Expanded)
    with st.expander("🛠️ Advanced Settings", expanded=True):
        st.selectbox(
            "Curve Mode",
            ["spline (Smooth)", "polygon (Straight)", "none (None)"],
            key="adv_mode",
            index=["spline", "polygon", "none"].index(st.session_state['adv_mode'].split(" ")[0]),
            help="Controls path geometry. Spline is smoother; polygon is sharper."
        )
        
        st.selectbox(
            "Layering Mode",
            ["stacked (Stacked)", "cutout (Cutout)"],
            key="adv_hierarchical",
            index=["stacked", "cutout"].index(st.session_state['adv_hierarchical'].split(" ")[0]),
            help="Stacked layers shapes. Cutout creates non-overlapping shapes."
        )
        
        st.slider("Gradient Step", 0, 255, key="adv_gradient_step", value=st.session_state['adv_gradient_step'], help="Color-gradient quantization step. Default: 64.")
        st.slider("Corner Threshold", 0, 180, key="adv_corner_threshold", value=st.session_state['adv_corner_threshold'], help="Corner-angle threshold for smooth curves. Default: 60.")
        st.slider("Minimum Segment Length", 3, 20, key="adv_segment_length", value=st.session_state['adv_segment_length'], help="Ignore segments shorter than this value. Default: 4.")
        st.slider("Splice Threshold", 0, 180, key="adv_splice_threshold", value=st.session_state['adv_splice_threshold'], help="Angle threshold for joining consecutive segments. Default: 45.")
        
        def reset_params():
            for key, val in default_settings.items():
                st.session_state[key] = val

        st.button("↺ Reset Settings", use_container_width=True, on_click=reset_params)

# Main Layout
# Use columns to create the layout structure, CSS will handle the positioning
col_main, col_right = st.columns([1, 1]) # Ratio doesn't matter much due to CSS override, but keeping 1:1 is safe

with col_main:
    st.subheader("📤 Upload Image")
    
    # Initialize uploader key for reset functionality
    if 'uploader_key' not in st.session_state:
        st.session_state['uploader_key'] = 0

    # File Uploader
    uploaded_file = st.file_uploader(
        "Drag and drop or click to upload",
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
        temp_input_path = new_upload_path(uploaded_file.name)
        with temp_input_path.open("wb") as f:
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
                st.caption("✨ Adjust settings in the sidebar to update the preview.")
                
            with c3:
                # Placeholder for alignment, or we can remove this column if not needed
                st.empty()
                
            with c4:
                # Delete Button
                if st.button("✕", help="Remove image"):
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
        file_id = f"{uploaded_file.name}_{uploaded_file.size}_{hash(uploaded_file.getvalue())}"
        last_params = st.session_state.get('last_params', {})
        last_file_id = st.session_state.get('last_file_id', None)
        
        should_convert = (
            'current_svg_path' not in st.session_state or 
            not os.path.exists(st.session_state['current_svg_path']) or
            file_id != last_file_id or
            current_params != last_params
        )

        if should_convert:
            with st.spinner("Converting..."):
                output_path = new_output_path()
                
                try:
                    converter = FastConverter()
                    converter.convert(
                        str(temp_input_path), str(output_path),
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
                    st.session_state['current_svg_path'] = str(output_path)
                    st.session_state['original_svg_path'] = str(output_path)
                    st.session_state['last_params'] = current_params
                    st.session_state['last_file_id'] = file_id
                    
                    push_to_history(output_path) # Add to history
                    
                    # Force rerun to update the preview immediately
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Conversion failed: {e}")

    # Display Result (if exists)
    if 'current_svg_path' in st.session_state and os.path.exists(st.session_state['current_svg_path']):
        st.markdown("---")
        st.subheader("SVG Preview")
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
                label="⬇️ Download SVG",
                data=f,
                file_name=file_name,
                mime="image/svg+xml",
                type="primary"
            )
    else:
        if not uploaded_file:
            st.info("👈 Upload an image to start vectorization automatically.")

# Right Sidebar (Column) for Color Palette
with col_right:
    if 'current_svg_path' in st.session_state and os.path.exists(st.session_state['current_svg_path']):
        
        # Undo/Redo Buttons
        ur_col1, ur_col2 = st.columns(2)
        with ur_col1:
            if st.button("↩️ Undo", use_container_width=True, disabled=st.session_state['history_pointer'] <= 0, help="Keyboard shortcuts are unavailable in Streamlit."):
                if st.session_state['history_pointer'] > 0:
                    st.session_state['history_pointer'] -= 1
                    st.session_state['current_svg_path'] = st.session_state['history_stack'][st.session_state['history_pointer']]
                    st.rerun()
        with ur_col2:
            if st.button("↪️ Redo", use_container_width=True, disabled=st.session_state['history_pointer'] >= len(st.session_state['history_stack']) - 1):
                if st.session_state['history_pointer'] < len(st.session_state['history_stack']) - 1:
                    st.session_state['history_pointer'] += 1
                    st.session_state['current_svg_path'] = st.session_state['history_stack'][st.session_state['history_pointer']]
                    st.rerun()

        st.subheader("🎨 Smart Palette")
        
        # Initialize Color Manager
        if 'color_manager' not in st.session_state or st.session_state.get('cm_svg_path') != st.session_state['current_svg_path']:
            st.session_state['color_manager'] = SVGColorManager(st.session_state['current_svg_path'])
            st.session_state['cm_svg_path'] = st.session_state['current_svg_path']
        
        cm = st.session_state['color_manager']
        unique_colors = cm.get_unique_colors()
        
        st.caption(f"{len(unique_colors)} colors found")
        
        # Tolerance Slider
        tolerance = st.slider("Merge Tolerance", 0, 100, 10, key="sidebar_tolerance")
        groups = cm.group_similar_colors(tolerance)
        
        # Color Editing Form
        with st.form("sidebar_color_editor"):
            changes_map = {}
            
            # List layout for color groups
            for i, (main_color, similar_colors) in enumerate(groups.items()):
                with st.container(border=True):
                    c_col1, c_col2 = st.columns([3, 1])
                    with c_col1:
                        st.markdown(f"**Group {i+1}** ({len(similar_colors)})")
                        swatches = "".join([f'<div class="color-box" style="background-color:{c}; width:15px; height:15px;" title="{c}"></div>' for c in similar_colors])
                        st.markdown(swatches, unsafe_allow_html=True)
                    with c_col2:
                        # Ensure main_color is valid hex
                        new_color = st.color_picker("Edit", value=main_color, key=f"cp_sb_{i}", label_visibility="collapsed")
                    
                    for original in similar_colors:
                        if original != new_color:
                            changes_map[original] = new_color
            
            apply_btn = st.form_submit_button("✨ Apply Changes", type="primary")
            
            if apply_btn:
                if changes_map:
                    edited_output_path = new_output_path()
                    cm.apply_changes(changes_map, str(edited_output_path))

                    st.session_state['current_svg_path'] = str(edited_output_path)
                    push_to_history(str(edited_output_path)) # Add edit to history
                    st.rerun()
