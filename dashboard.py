import time
import os
import shutil
import urllib.request
import json
import ssl 
import xml.etree.ElementTree as ET
import textwrap
import datetime
from PIL import Image, ImageDraw, ImageFont # type: ignore 

# edit LATITUDE and LONGITUDE based on your city
LATITUDE = 49.5986
LONGITUDE = 18.1449
WEATHER_CACHE_FILE = "/tmp/weather_cache.json"
CACHE_EXPIRY_SECONDS = 900  # reload weather data every 15min (900s)
NEWS_FEED_URL = "https://feeds.bbci.co.uk/news/rss.xml"
NEWS_CACHE_FILE = "/tmp/news_cache.json"
NEWS_FETCH_INTERVAL = 3600
CRYPTO_CACHE_FILE = "/tmp/crypto_cache.json"
CRYPTO_FETCH_INTERVAL = 900

weather_cache = {
    "temp": "--",
    "feels_like": "--",
    "condition": "NO DATA",
    "humidity": "--",
    "wind": "--",
    "last_fetch": 0
}

news_headlines = ["LOADING NEWS..."]
news_index = 0
last_news_fetch = 0

crypto_cache = {
    "BTC": {"price": "--", "change": "--"},
    "ETH": {"price": "--", "change": "--"},
    "XRP": {"price": "--", "change": "--"},
    "AAPL": {"price": "--", "change": "--"},
    "last_fetch": 0
}

def update_weather():
    global weather_cache
    now = time.time()
    
    if weather_cache["last_fetch"] == 0 and os.path.exists(WEATHER_CACHE_FILE):
        try:
            with open(WEATHER_CACHE_FILE, "r") as f:
                weather_cache = json.load(f)
        except:
            pass

    if now - weather_cache["last_fetch"] < CACHE_EXPIRY_SECONDS and weather_cache["condition"] != "NO DATA":
        return

    url = f"http://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m&wind_speed_unit=ms"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'KindleDashboard/2.0'})
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=10, context=context) as response:
            data = json.loads(response.read().decode())
            current = data.get("current", {})
            
            temp = current.get("temperature_2m", 0)
            feels = current.get("apparent_temperature", 0)
            humidity = current.get("relative_humidity_2m", 0)
            wind = current.get("wind_speed_10m", 0)
            code = current.get("weather_code", 0)
            
            # Weather Interpretation Codes for open meteo 
            mapping = {
                0: "CLEAR SKY",
                1: "MAINLY CLEAR", 2: "PARTLY CLOUDY", 3: "OVERCAST",
                45: "FOGGY", 48: "RIME FOG",
                51: "LIGHT DRIZZLE", 53: "DRIZZLE", 55: "DENSE DRIZZLE",
                61: "LIGHT RAIN", 63: "RAINY", 65: "HEAVY RAIN",
                71: "LIGHT SNOW", 73: "SNOWFALL", 75: "HEAVY SNOW",
                80: "LIGHT SHOWERS", 81: "SHOWERS", 82: "HEAVY SHOWERS",
                95: "THUNDERSTORM"
            }
            
            condition = mapping.get(code, "UNKNOWN")
            if condition == "UNKNOWN":
                if 50 <= code <= 59: condition = "DRIZZLE"
                elif 60 <= code <= 69: condition = "RAINY"
                elif 70 <= code <= 79: condition = "SNOWY"
                elif 80 <= code <= 89: condition = "SHOWERS"
                elif 90 <= code <= 99: condition = "STORM"
            
            weather_cache["temp"] = f"{round(temp)}*C"
            weather_cache["feels_like"] = f"{round(feels)}*C"
            weather_cache["condition"] = condition
            weather_cache["humidity"] = f"{humidity}%"
            weather_cache["wind"] = f"{wind:.1f} M/S"
            weather_cache["last_fetch"] = now
            
            with open(WEATHER_CACHE_FILE, "w") as f:
                json.dump(weather_cache, f)
    except:
        pass

def update_news():
    global news_headlines, last_news_fetch
    now = time.time()
    
    if last_news_fetch == 0 and os.path.exists(NEWS_CACHE_FILE):
        try:
            with open(NEWS_CACHE_FILE, "r") as f:
                data = json.load(f)
                news_headlines = data.get("headlines", ["LOADING NEWS..."])
                last_news_fetch = data.get("last_fetch", 0)
        except:
            pass

    if now - last_news_fetch < NEWS_FETCH_INTERVAL and len(news_headlines) > 1:
        return

    try:
        req = urllib.request.Request(NEWS_FEED_URL, headers={'User-Agent': 'KindleDashboard/2.0'})
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=10, context=context) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            items = root.findall(".//item")
            titles = []
            for item in items:
                title = item.find("title")
                if title is not None and title.text:
                    titles.append(title.text.strip())
            if titles:
                news_headlines = titles[:15]
                last_news_fetch = now
                with open(NEWS_CACHE_FILE, "w") as f:
                    json.dump({"headlines": news_headlines, "last_fetch": last_news_fetch}, f)
    except:
        pass

def update_crypto():
    global crypto_cache
    now = time.time()
    
    if crypto_cache["last_fetch"] == 0 and os.path.exists(CRYPTO_CACHE_FILE):
        try:
            with open(CRYPTO_CACHE_FILE, "r") as f:
                crypto_cache = json.load(f)
        except:
            pass

    if now - crypto_cache["last_fetch"] < CRYPTO_FETCH_INTERVAL and crypto_cache["BTC"]["price"] != "--" and "AAPL" in crypto_cache:
        return

    url = 'https://api.binance.com/api/v3/ticker/24hr?symbols=["BTCUSDT","ETHUSDT","XRPUSDT"]'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'KindleDashboard/2.0'})
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=10, context=context) as response:
            data = json.loads(response.read().decode())
            for item in data:
                sym = item.get("symbol", "")
                last_price = float(item.get("lastPrice", 0))
                change_pct = float(item.get("priceChangePercent", 0))
                
                if last_price >= 1000:
                    price_str = f"${last_price:,.0f}"
                elif last_price >= 1:
                    price_str = f"${last_price:,.2f}"
                else:
                    price_str = f"${last_price:,.4f}"
                    
                change_str = f"{change_pct:+.2f}%"
                
                if sym == "BTCUSDT":
                    crypto_cache["BTC"] = {"price": price_str, "change": change_str}
                elif sym == "ETHUSDT":
                    crypto_cache["ETH"] = {"price": price_str, "change": change_str}
                elif sym == "XRPUSDT":
                    crypto_cache["XRP"] = {"price": price_str, "change": change_str}
    except:
        pass

    url_aapl = 'https://query1.finance.yahoo.com/v8/finance/chart/AAPL'
    try:
        req = urllib.request.Request(url_aapl, headers={'User-Agent': 'KindleDashboard/2.0'})
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=10, context=context) as response:
            res_data = json.loads(response.read().decode())
            meta = res_data["chart"]["result"][0]["meta"]
            price = meta.get("regularMarketPrice", 0.0)
            prev = meta.get("chartPreviousClose", 0.0)
            if prev:
                change_pct = ((price - prev) / prev) * 100
            else:
                change_pct = 0.0
            
            price_str = f"${price:,.2f}"
            change_str = f"{change_pct:+.2f}%"
            
            crypto_cache["AAPL"] = {"price": price_str, "change": change_str}
    except:
        pass

    crypto_cache["last_fetch"] = now
    with open(CRYPTO_CACHE_FILE, "w") as f:
        json.dump(crypto_cache, f)

def read_file_stripped(path):
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except:
        return None

def get_battery():
    ps_dir = "/sys/class/power_supply" # this path should work on all kindles but if not, you should edit it

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
            else:
                f.seek(0)
                for line in f:
                    if "MemFree" in line:
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
    margin_x, margin_y = 40, 90
    gap_x, gap_y = 30, 30
    box_w = (width - 2 * margin_x - gap_x) // 2
    box_h = (height - margin_y - 40 - gap_y) // 2
    
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
    
    if align == "center":
        px = x - scaled_w // 2
    elif align == "right":
        px = x - scaled_w
    else:
        px = x
    py = y - scaled_h // 2
    image.paste(t_img, (int(px), int(py)))

def draw_dashboard():
    global news_index
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

    current_date = datetime.date(now.tm_year, now.tm_mon, now.tm_mday)
    target_date = datetime.date(now.tm_year, 8, 31)
    days_left = (target_date - current_date).days
    if days_left >= 0:
        days_left_str = f"{days_left} DAYS OF HOLIDAYS LEFT"
    else:
        days_left_str = "HOLIDAYS ENDED"

    b1_cx = (b1[0] + b1[2]) // 2
    b1_cy = (b1[1] + b1[3]) // 2
    draw_text(image, time_str, font, b1_cx, b1_cy - 50, 14)
    draw_text(image, full_date_line, font, b1_cx, b1_cy + 70, 4)
    draw_text(image, days_left_str, font, b1_cx, b1_cy + 130, 3)
    
    #  weather
    update_weather()
    b2_cx = (b2[0] + b2[2]) // 2
    b2_x = b2[0]
    b2_y = b2[1]
    
    draw_text(image, "WEATHER", font, b2_cx, b2_y + 45, 5, align="center")
    draw.line([(b2_x + 50, b2_y + 80), (b2[2] - 50, b2_y + 80)], fill="black", width=2)
    
    draw_text(image, weather_cache["temp"], font, b2_cx, b2_y + 160, 14, align="center")
    draw_text(image, weather_cache["condition"], font, b2_cx, b2_y + 245, 5, align="center")
    
    details_y = b2_y + 310
    weather_items = [
        ("FEELS LIKE", weather_cache["feels_like"]),
        ("HUMIDITY", weather_cache["humidity"]),
        ("WIND SPEED", weather_cache["wind"])
    ]
    for i, (label, val) in enumerate(weather_items):
        row_y = details_y + (i * 50)
        draw_text(image, label, font, b2_x + 50, row_y, 4, align="left")
        draw_text(image, val, font, b2_x + 320, row_y, 4, align="left")
    
    update_news()
    b3_cx = (b3[0] + b3[2]) // 2
    b3_x = b3[0]
    b3_y = b3[1]
    
    draw_text(image, "NEWS", font, b3_cx, b3_y + 45, 5, align="center")
    draw.line([(b3_x + 50, b3_y + 80), (b3[2] - 50, b3_y + 80)], fill="black", width=2)
    
    if news_headlines:
        current_headline = news_headlines[news_index % len(news_headlines)]
        news_index = (news_index + 1) % len(news_headlines)
    else:
        current_headline = "NO NEWS AVAILABLE"
        
    wrapped_lines = textwrap.wrap(current_headline, width=28)
    wrapped_lines = wrapped_lines[:6]
    start_y = b3_y + 120 + (280 - len(wrapped_lines) * 40) // 2
    for idx, line in enumerate(wrapped_lines):
        draw_text(image, line, font, b3_cx, start_y + (idx * 40), 4, align="center")
    
    update_crypto()
    b4_cx = (b4[0] + b4[2]) // 2
    b4_x = b4[0]
    b4_y = b4[1]
    
    draw_text(image, "MARKETS", font, b4_cx, b4_y + 45, 5, align="center")
    draw.line([(b4_x + 50, b4_y + 80), (b4[2] - 50, b4_y + 80)], fill="black", width=2)
    
    crypto_assets = [
        ("BTC", crypto_cache["BTC"]),
        ("ETH", crypto_cache["ETH"]),
        ("XRP", crypto_cache["XRP"]),
        ("AAPL", crypto_cache["AAPL"])
    ]
    
    for i, (symbol, info) in enumerate(crypto_assets):
        row_y = b4_y + 125 + (i * 80)
        draw_text(image, symbol, font, b4_x + 50, row_y, 5, align="left")
        draw_text(image, info["price"], font, b4_x + 220, row_y, 5, align="left")
        draw_text(image, info["change"], font, b4[2] - 50, row_y, 4, align="right")
        
        if i < 3:
            div_y = row_y + 40
            draw.line([(b4_x + 50, div_y), (b4[2] - 50, div_y)], fill="black", width=1)
            
    stats = get_system_stats()
    status_items = [
        f"BATTERY: {stats['battery']}%",
        f"WI-FI: {stats['wifi']}%",
        f"DISK: {stats['storage_gb']:.1f}GB FREE",
        f"RAM: {stats['ram_mb']}MB FREE",
        f"UPTIME: {stats['uptime']}"
    ]
    
    item_widths = [len(item) * 18 for item in status_items]
    total_text_width = sum(item_widths)
    start_x = 40
    end_x = 1408
    available_width = end_x - start_x
    gap = (available_width - total_text_width) // 4
    current_x = start_x
    positions = []
    for w in item_widths:
        text_start = current_x
        text_end = current_x + w
        text_center = text_start + w // 2
        positions.append((text_start, text_end, text_center))
        current_x = text_end + gap
        
    for i, item in enumerate(status_items):
        draw_text(image, item, font, positions[i][2], 45, 3, align="center")
        if i < 4:
            sep_x = int(positions[i][1] + gap // 2)
            draw.line([(sep_x, 25), (sep_x, 65)], fill="black", width=2)
                    
    rotated_image = image.rotate(270, expand=True)
    png_path = "/mnt/us/dashboard.png"
    rotated_image.save(png_path, "PNG")

    os.system("eips -c")
    os.system(f"eips -g {png_path}")
    os.system("eips -f")

# at start of dashboard it kill kindle processes that are distrupting our dashboard, like printing system clocks at the top
if __name__ == "__main__":
    os.system("stop pillow")
    os.system("stop lab126_gui")
    os.system("lipc-set-prop com.lab126.powerd preventScreenSaver 1")
    try:
        while True:
            draw_dashboard()
            time.sleep(60)

#this part below is pretty important as when you turn off the dashboard process in ssh it must start again the kindle processes so you dont need to restart the kindle
    except KeyboardInterrupt:
        print(f"Wait for shutdown! Starting up kindle processes. This could take like 30s or 1m , WAIT!")
        os.system("start lab126_gui")
        os.system("start pillow")
        os.system("lipc-set-prop com.lab126.powerd preventScreenSaver 0")
