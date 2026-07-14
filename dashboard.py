import time
import os
import shutil
from PIL import Image, ImageDraw, ImageFont

def read_file_stripped(path):
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except:
        return None

def get_battery():
    ps_dir = "/sys/class/power_supply"
    if os.path.exists(ps_dir):
        for folder in os.listdir(ps_dir):
            val = read_file_stripped(f"{ps_dir}/{folder}/capacity")
            if val and val.isdigit():
                return int(val)
    try:
        with os.popen("lipc-get-prop com.lab126.powerd batteryLevel") as f:
            val = f.read().strip()
            if val.isdigit():
                return int(val)
    except:
        pass
    return 0

def get_wifi_signal():
    try:
        with os.popen("wpa_cli -i wlan0 signal_poll 2>/dev/null") as f:
            for line in f:
                if "RSSI=" in line:
                    rssi = int(line.split("=")[1].strip())
                    return min(100, max(0, int(2 * (rssi + 100))))
    except:
        pass
    
    try:
        with open("/proc/net/wireless", "r") as f:
            for line in f:
                if ":" in line:
                    parts = line.split()
                    link_val = int(float(parts[2].rstrip('.')))
                    if link_val > 0:
                        return min(100, max(0, int((link_val / 70.0) * 100) if link_val <= 70 else link_val))
    except:
        pass
        
    try:
        with os.popen("lipc-get-prop com.lab126.wifid signal") as f:
            val = f.read().strip()
            if val.isdigit():
                sig = int(val)
                return sig * 20 if sig <= 5 else sig
    except:
        pass
    return 0

def get_system_stats():
    stats = {
        "battery": get_battery(),
        "wifi": get_wifi_signal(),
        "storage_gb": 0.0,
        "ram_mb": 0,
        "uptime": "0m"
    }
    
    try:
        total, used, free = shutil.disk_usage("/mnt/us")
        stats["storage_gb"] = free / (1024**3)
    except:
        pass
        
    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if "MemAvailable" in line or "MemFree" in line:
                    stats["ram_mb"] = int(line.split()[1]) // 1024
                    break
    except:
        pass
        
    try:
        with open("/proc/uptime", "r") as f:
            up_sec = float(f.readline().split()[0])
            days = int(up_sec // 86400)
            hours = int((up_sec % 86400) // 3600)
            minutes = int((up_sec % 3600) // 60)
            if days > 0:
                stats["uptime"] = f"{days}d {hours}h"
            elif hours > 0:
                stats["uptime"] = f"{hours}h {minutes}m"
            else:
                stats["uptime"] = f"{minutes}m"
    except:
        pass
        
    return stats

def get_grid_boxes(width, height):
    margin_x, margin_y = 40, 40
    gap_x, gap_y = 30, 30
    box_w = (width - 2 * margin_x - gap_x) // 2
    box_h = (height - 2 * margin_y - gap_y) // 2
    
    boxes = []
    for row in range(2):
        for col in range(2):
            x1 = margin_x + col * (box_w + gap_x)
            y1 = margin_y + row * (box_h + gap_y)
            x2 = x1 + box_w
            y2 = y1 + box_h
            boxes.append((x1, y1, x2, y2))
    return boxes

def draw_text(image, text, font, x, y, scale, align="center"):
    txt_w, txt_h = len(text) * 6, 10
    t_img = Image.new("L", (txt_w, txt_h), "white")
    t_draw = ImageDraw.Draw(t_img)
    t_draw.text((0, 0), text, fill="black", font=font)
    scaled_w, scaled_h = txt_w * scale, txt_h * scale
    t_img = t_img.resize((scaled_w, scaled_h), Image.Resampling.NEAREST)
    
    px = x - scaled_w // 2 if align == "center" else x
    py = y - scaled_h // 2 if align == "center" else y
    image.paste(t_img, (px, py))

def draw_dashboard():
    width = 1448
    height = 1072
    
    image = Image.new("L", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    
    boxes = get_grid_boxes(width, height)
    for box in boxes:
        draw.rectangle(box, outline="black", width=5)
        
    b1, b2, b3, b4 = boxes
    
    now = time.localtime()
    time_str = time.strftime("%H:%M", now)
    full_date_line = time.strftime("%d.%m.%Y %A", now).upper()

    b1_cx = (b1[0] + b1[2]) // 2
    b1_cy = (b1[1] + b1[3]) // 2
    draw_text(image, time_str, font, b1_cx, b1_cy - 50, 14)
    draw_text(image, full_date_line, font, b1_cx, b1_cy + 70, 4)
    b2_cx = (b2[0] + b2[2]) // 2
    b2_cy = (b2[1] + b2[3]) // 2
    draw_text(image, "WEATHER", font, b2_cx, b2_cy, 6)
    
    b3_cx = (b3[0] + b3[2]) // 2
    b3_cy = (b3[1] + b3[3]) // 2
    draw_text(image, "NEWS", font, b3_cx, b3_cy, 6)
    
    stats = get_system_stats()
    b4_cx = (b4[0] + b4[2]) // 2
    b4_x = b4[0]
    b4_y = b4[1]
    
    draw_text(image, "SYSTEM INFO", font, b4_cx, b4_y + 45, 5, align="center")
    draw.line([(b4_x + 50, b4_y + 80), (b4[2] - 50, b4_y + 80)], fill="black", width=2)
    
    items = [
        ("BATTERY", f"{stats['battery']}%", stats["battery"]),
        ("WI-FI", f"{stats['wifi']}%", stats["wifi"]),
        ("DISK", f"{stats['storage_gb']:.1f} GB FREE", None),
        ("RAM", f"{stats['ram_mb']} MB FREE", None),
        ("UPTIME", stats["uptime"], None)
    ]
    
    for i, (label, val_str, progress) in enumerate(items):
        row_y = b4_y + 120 + (i * 65)
        draw_text(image, label, font, b4_x + 50, row_y, 4, align="left")
        
        if progress is not None:
            draw.rectangle([b4_x + 240, row_y + 3, b4_x + 440, row_y + 23], outline="black", width=3)
            fill_w = int(200 * (progress / 100.0))
            if fill_w > 0:
                draw.rectangle([b4_x + 243, row_y + 6, b4_x + 243 + fill_w - 6, row_y + 20], fill="black")
            draw_text(image, val_str, font, b4_x + 460, row_y, 4, align="left")
        else:
            draw_text(image, val_str, font, b4_x + 240, row_y, 4, align="left")
            
    rotated_image = image.rotate(270, expand=True)
    
    png_path = "/mnt/us/dashboard.png"
    rotated_image.save(png_path, "PNG")
    
    os.system("eips -c")
    os.system(f"eips -g {png_path}")
    os.system("eips -f")

if __name__ == "__main__":
    os.system("stop pillow")
    os.system("stop lab126_gui")
    os.system("lipc-set-prop com.lab126.powerd preventScreenSaver 1")
    try:
        while True:
            draw_dashboard()
            time.sleep(60)
    except KeyboardInterrupt:
        os.system("start lab126_gui")
        os.system("start pillow")
        os.system("lipc-set-prop com.lab126.powerd preventScreenSaver 0")
66