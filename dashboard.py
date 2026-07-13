import time
import os
from PIL import Image, ImageDraw, ImageFont

def draw_clock():
    # this can be modified for any kindle screen
    width = 1100
    height = 1500
    image = Image.new("L", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    current_time = time.strftime("%H:%M")
    text_bbox = draw.textbbox((0, 0), current_time, font=font)
    font_w = text_bbox[2] - text_bbox[0]
    font_h = text_bbox[3] - text_bbox[1]
    scale = 12
    scaled_w = font_w * scale
    scaled_h = font_h * scale
    
    txt_img = Image.new("L", (font_w, font_h), "white")
    txt_draw = ImageDraw.Draw(txt_img)
    txt_draw.text((0, 0), current_time, fill="black", font=font)
    
    txt_img = txt_img.resize((scaled_w, scaled_h), Image.Resampling.NEAREST)
    
    x = (width - scaled_w) // 2         #divided by 2 coz we want it at center :)
    y = (height - scaled_h) // 2
    image.paste(txt_img, (x, y))
    png_path = "/mnt/us/dashboard.png"
    image.save(png_path, "PNG")    
    os.system("eips -c")
    os.system(f"eips -g {png_path}")

if __name__ == "__main__":
    os.system("lipc-set-prop com.lab126.powerd preventScreenSaver 1")
    try:
        while True:
            draw_clock()
            time.sleep(60)
    except KeyboardInterrupt:
        os.system("lipc-set-prop com.lab126.powerd preventScreenSaver 0")
