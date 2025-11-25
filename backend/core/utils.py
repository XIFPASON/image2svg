import torch
import numpy as np
from PIL import Image
import skimage.io

def load_image(path, max_width=256):
    img = Image.open(path).convert('RGBA')
    w, h = img.size
    if w > max_width:
        h = int(h * max_width / w)
        w = max_width
        img = img.resize((w, h), Image.LANCZOS)
    img = np.array(img)
    img = img.astype(np.float32) / 255.0
    # Pre-multiply alpha
    img[:, :, :3] = img[:, :, :3] * img[:, :, 3:4]
    return torch.tensor(img).permute(2, 0, 1) # C, H, W

def save_svg(shapes, shape_groups, width, height, filename):
    import pydiffvg
    pydiffvg.save_svg(filename, width, height, shapes, shape_groups)
