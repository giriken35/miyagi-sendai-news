import os
from PIL import Image, ImageDraw

def generate_masamune_icon():
    size = 4096
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    radius = int(size * 0.22)
    draw.rounded_rectangle((0, 0, size, size), radius=radius, fill=(15, 15, 20, 255))

    p0 = (717, 1800)
    p2 = (3379, 1300)
    p1_out = (1900, 4300)
    p1_in = (1600, 2000)

    points = []
    steps = 200
    for i in range(steps + 1):
        t = i / steps
        x = (1-t)**2 * p0[0] + 2*(1-t)*t * p1_out[0] + t**2 * p2[0]
        y = (1-t)**2 * p0[1] + 2*(1-t)*t * p1_out[1] + t**2 * p2[1]
        points.append((x, y))
        
    for i in range(steps + 1):
        t = i / steps
        x = (1-t)**2 * p2[0] + 2*(1-t)*t * p1_in[0] + t**2 * p0[0]
        y = (1-t)**2 * p2[1] + 2*(1-t)*t * p1_in[1] + t**2 * p0[1]
        points.append((x, y))

    draw.polygon(points, fill=(243, 198, 35, 255))

    out_dir = r"web\src\app"
    os.makedirs(out_dir, exist_ok=True)
    
    icon_png = img.resize((512, 512), Image.Resampling.LANCZOS)
    icon_png.save(os.path.join(out_dir, "icon.png"))
    
    apple_icon = img.resize((180, 180), Image.Resampling.LANCZOS)
    apple_bg = Image.new('RGB', (180, 180), (255, 255, 255))
    apple_bg.paste(apple_icon, (0, 0), apple_icon)
    apple_bg.save(os.path.join(out_dir, "apple-icon.png"))
    
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
    ico_img = img.resize((64, 64), Image.Resampling.LANCZOS)
    ico_img.save(os.path.join(out_dir, "favicon.ico"), format="ICO", sizes=sizes)
    print("Icons generated!")

if __name__ == "__main__":
    generate_masamune_icon()
