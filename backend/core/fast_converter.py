import cv2
import numpy as np
import svgwrite
import os
import subprocess
import shutil

class FastConverter:
    def __init__(self):
        # Check if vtracer is available in path or local directory
        self.vtracer_path = shutil.which("vtracer")
        if not self.vtracer_path and os.path.exists("vtracer.exe"):
            self.vtracer_path = os.path.abspath("vtracer.exe")
            
    def convert(self, image_path, output_path, callback=None, **kwargs):
        # Try VTracer first if available
        if self.vtracer_path:
            try:
                print(f"🚀 Executing VTracer: {self.vtracer_path}")
                
                # Extract VTracer parameters from kwargs with defaults
                colormode = kwargs.get('colormode', 'color')
                hierarchical = kwargs.get('hierarchical', 'stacked')
                mode = kwargs.get('mode', 'spline')
                filter_speckle = str(kwargs.get('filter_speckle', 4))
                color_precision = str(kwargs.get('color_precision', 6))
                gradient_step = str(kwargs.get('gradient_step', 64))
                corner_threshold = str(kwargs.get('corner_threshold', 60))
                segment_length = str(kwargs.get('segment_length', 4))
                splice_threshold = str(kwargs.get('splice_threshold', 45))
                
                # Construct command
                # Only use arguments supported by the current vtracer version
                cmd = [
                    self.vtracer_path,
                    "--input", image_path,
                    "--output", output_path,
                    "--colormode", colormode,
                    "--hierarchical", hierarchical,
                    "--mode", mode,
                    "--filter_speckle", filter_speckle,
                    "--color_precision", color_precision,
                    "--gradient_step", gradient_step,
                    "--corner_threshold", corner_threshold,
                    "--segment_length", segment_length,
                    "--splice_threshold", splice_threshold
                ]
                
                print(f"   Command: {' '.join(cmd)}")
                
                # Run command
                # Use shell=True on Windows if path has spaces or issues, but usually list is safer
                # Ensure paths are absolute
                process = subprocess.run(cmd, capture_output=True, text=True)
                
                if process.returncode == 0:
                    print("✅ VTracer success!")
                    if callback: callback(100, 100, 0)
                    return
                else:
                    error_msg = f"VTracer failed with code {process.returncode}:\n{process.stderr}"
                    print(f"❌ {error_msg}")
                    raise RuntimeError(error_msg) # Don't fallback silently
                    
            except Exception as e:
                print(f"❌ Error running VTracer: {e}")
                raise e # Re-raise to show in UI

        # Fallback: OpenCV Implementation (Only if VTracer not found)
        print("⚠️ VTracer not found. Using OpenCV fallback...")
        
        # Read image using numpy to support non-ASCII paths
        try:
            stream = np.fromfile(image_path, dtype=np.uint8)
            img = cv2.imdecode(stream, cv2.IMREAD_COLOR)
        except Exception:
            img = None
            
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
            
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Thresholding
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Create SVG
        h, w = img.shape[:2]
        dwg = svgwrite.Drawing(output_path, size=(w, h), profile='tiny')
        
        total_contours = len(contours)
        
        for i, contour in enumerate(contours):
            if callback and i % 10 == 0:
                callback(i, total_contours, 0)
                
            epsilon = 0.005 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Convert points to list of tuples with standard python types
            points = [(float(pt[0][0]), float(pt[0][1])) for pt in approx]
            
            if len(points) > 2:
                dwg.add(dwg.polygon(points=points, fill='black'))
                
        dwg.save()
