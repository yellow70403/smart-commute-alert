import os
import requests


# =========================
# 基本設定
# =========================

LATITUDE = 24.9937
LONGITUDE = 121.2969

# 從 GitHub Secrets 取得 Telegram 資訊
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


# =========================
# 取得天氣資料
# =========================

weather_url = "https://api.open-meteo.com/v1/forecast"

weather_params = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "daily": "temperature_2m_max,precipitation_probability_max",
    "timezone": "Asia/Taipei",
    "forecast_days": 1
}

weather_response = requests.get(
    weather_url,
    params=weather_params,
    timeout=10
)

# 檢查 HTTP 狀態碼
weather_response.raise_for_status()

weather_data = weather_response.json()

max_temperature = weather_data["daily"]["temperature_2m_max"][0]
rain_probability = weather_data["daily"]["precipitation_probability_max"][0]


# =========================
# 取得 AQI 資料
# =========================

air_url = "https://air-quality-api.open-meteo.com/v1/air-quality"

air_params = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "hourly": "us_aqi",
    "timezone": "Asia/Taipei",
    "forecast_days": 1
}

air_response = requests.get(
    air_url,
    params=air_params,
    timeout=10
)

# 檢查 HTTP 狀態碼
air_response.raise_for_status()

air_data = air_response.json()

aqi_values = air_data["hourly"]["us_aqi"]

# 取得今天 AQI 最高值
aqi = max(aqi_values)


# =========================
# 顯示 API 資料
# =========================

print(f"最高溫度：{max_temperature}°C")
print(f"最高降雨機率：{rain_probability}%")
print(f"今日最高 AQI：{aqi}")


# =========================
# 產生通勤建議
# =========================

suggestions = []


# 條件 1：降雨機率達 60%
if rain_probability >= 60:
    suggestions.append("☔ 降雨機率達 60%，記得攜帶雨傘！")


# 條件 2：最高溫度達 33°C
if max_temperature >= 33:
    suggestions.append("☀️ 最高溫度達 33°C，記得防曬並補充水分！")


# 條件 3：AQI 達 100
if aqi >= 100:
    suggestions.append("😷 AQI 達 100，建議配戴口罩！")


# 如果沒有任何風險
if not suggestions:
    suggestions.append("✅ 今日天氣與空氣品質正常，適合外出通勤！")


# =========================
# 建立 Telegram 訊息
# =========================

message = f"""
🚗 智慧通勤風險通知

📍 地點：桃園

🌡️ 最高溫度：{max_temperature}°C
🌧️ 最高降雨機率：{rain_probability}%
🌫️ 今日最高 AQI：{aqi}

📢 通勤建議：
"""

message += "\n".join(suggestions)


# =========================
# 傳送 Telegram
# =========================

telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

telegram_data = {
    "chat_id": CHAT_ID,
    "text": message
}

telegram_response = requests.post(
    telegram_url,
    data=telegram_data,
    timeout=10
)

# 檢查 Telegram API 狀態
telegram_response.raise_for_status()

telegram_result = telegram_response.json()

# 檢查 Telegram API 是否真的成功
if not telegram_result.get("ok"):
    raise Exception(f"Telegram 發送失敗：{telegram_result}")

print("✅ Telegram 通知發送成功！")
