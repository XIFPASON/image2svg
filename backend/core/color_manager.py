import xml.etree.ElementTree as ET
import math
import re

class SVGColorManager:
    def __init__(self, svg_path):
        self.svg_path = svg_path
        self.tree = ET.parse(svg_path)
        self.root = self.tree.getroot()
        # Namespace handling
        self.ns = {'svg': 'http://www.w3.org/2000/svg'}
        ET.register_namespace('', self.ns['svg'])
        
        self.colors = {} # Map of hex_color -> list of nodes
        self._extract_colors()

    def _extract_colors(self):
        """Parse SVG and find all unique colors"""
        self.colors = {}
        # Recursive search for all elements
        for elem in self.root.iter():
            # Check fill and stroke attributes
            for attr in ['fill', 'stroke']:
                color = elem.get(attr)
                if color and color != 'none' and color.startswith('#'):
                    # Normalize hex to 6 digits
                    if len(color) == 4:
                        color = '#' + color[1]*2 + color[2]*2 + color[3]*2
                    
                    if color not in self.colors:
                        self.colors[color] = []
                    self.colors[color].append((elem, attr))
                    
            # Also check style attribute
            style = elem.get('style')
            if style:
                styles = [s.strip().split(':') for s in style.split(';') if ':' in s]
                for key, val in styles:
                    key = key.strip()
                    val = val.strip()
                    if key in ['fill', 'stroke'] and val.startswith('#'):
                        if len(val) == 4:
                            val = '#' + val[1]*2 + val[2]*2 + val[3]*2
                        
                        if val not in self.colors:
                            self.colors[val] = []
                        self.colors[val].append((elem, 'style', key))

    def get_unique_colors(self):
        """Return list of unique hex colors found"""
        return list(self.colors.keys())

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(self, rgb):
        return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

    def color_distance(self, c1, c2):
        """Calculate Euclidean distance between two RGB colors"""
        r1, g1, b1 = self.hex_to_rgb(c1)
        r2, g2, b2 = self.hex_to_rgb(c2)
        return math.sqrt((r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2)

    def group_similar_colors(self, threshold):
        """
        Group colors based on similarity threshold (0-100).
        Returns a dict: { representative_color: [list of similar colors] }
        """
        # Convert threshold (0-100) to RGB distance (0-441 approx)
        # Max distance is sqrt(255^2 * 3) ≈ 441.6
        dist_threshold = (threshold / 100.0) * 442.0
        
        unique_colors = self.get_unique_colors()
        groups = {}
        processed = set()

        # Simple clustering
        for color in unique_colors:
            if color in processed:
                continue
                
            # Start a new group with this color
            current_group = [color]
            processed.add(color)
            
            # Find all other colors close to this one
            for other in unique_colors:
                if other not in processed:
                    if self.color_distance(color, other) <= dist_threshold:
                        current_group.append(other)
                        processed.add(other)
            
            # Find the dominant color in the group (most used)
            dominant_color = max(current_group, key=lambda c: len(self.colors[c]))
            
            groups[dominant_color] = current_group
            
        return groups

    def apply_changes(self, color_mapping, output_path):
        """
        Apply color replacements.
        color_mapping: { original_hex: new_hex }
        """
        # We need to re-parse or just update the nodes we stored
        # Since we stored references to elements, we can update them directly
        
        for original_hex, new_hex in color_mapping.items():
            if original_hex in self.colors:
                for item in self.colors[original_hex]:
                    elem = item[0]
                    attr_type = item[1]
                    
                    if attr_type == 'style':
                        # Update style string
                        style_key = item[2]
                        style_str = elem.get('style')
                        # Regex replace for safety in style string
                        # This is a bit simplistic, but robust enough for generated SVGs
                        new_style = re.sub(f"{style_key}\s*:\s*{original_hex}", f"{style_key}:{new_hex}", style_str)
                        elem.set('style', new_style)
                    else:
                        # Update attribute directly
                        elem.set(attr_type, new_hex)
        
        self.tree.write(output_path)
