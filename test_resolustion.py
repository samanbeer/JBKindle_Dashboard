# you can run this script on your kindle to see which resolution you have
import os
from PIL import Image, ImageDraw, ImageFont # type: ignore

def draw_calibration():
    width = 1264
    height = 1680
    
    image = Image.new("L", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    
    for x in range(100, width, 100):
        draw.line([(x, 0), (x, height)], fill="gray", width=1)
    for y in range(100, height, 100):
        draw.line([(0, y), (width, y)], fill="gray", width=1)
#you can add your own resolution if none of the basic types matches
    resolutions = [
        (1264, 1680),
        (1236, 1648),
        (1200, 1600),
        (1072, 1448), # this one i have on Kindle PaperWhite Gen11 
        (800, 1024)
    ]
    
    for w, h in resolutions:
        draw.rectangle((0, 0, w - 1, h - 1), outline="black", width=4)
        
        txt = f"{w}x{h}"
        txt_w = len(txt) * 6
        t_img = Image.new("L", (txt_w, 10), "white")
        t_draw = ImageDraw.Draw(t_img)
        t_draw.text((0, 0), txt, fill="black", font=font)
        t_img = t_img.resize((txt_w * 4, 40), Image.Resampling.NEAREST)
        
        image.paste(t_img, (w - (txt_w * 4) - 20, h - 60))
        image.paste(t_img, (20, h - 60))

    png_path = "/mnt/us/dashboard.png" # also if your kindle does not have "user" partition in /mnt/us/ you should edit it.
    image.save(png_path, "PNG")
    
    os.system("eips -c")
    os.system(f"eips -g {png_path}")

if __name__ == "__main__":
    os.system("lipc-set-prop com.lab126.powerd preventScreenSaver 1")
    draw_calibration()

