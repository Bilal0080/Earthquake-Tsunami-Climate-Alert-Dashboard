import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from twilio.rest import Client
import smtplib
from email.message import EmailMessage

# ------------------- CONFIG -------------------
st.set_page_config(page_title="🌍 Earthquake, Tsunami & Climate Alert", layout="wide")
st.title("🌍 Earthquake, Tsunami & Climate Alert Dashboard")

TWILIO_SID = "your_twilio_account_sid"
TWILIO_TOKEN = "your_twilio_auth_token"
TWILIO_FROM = "+1234567890"
TWILIO_TO = "+923001234567"

EMAIL_SENDER = "youremail@gmail.com"
EMAIL_PASSWORD = "your_app_password"
EMAIL_RECEIVER = "receiver@example.com"

API_KEY = "c79c6b0f125a16c353e1567ffc7c9d4b"
CITY_NAME = "Karachi"

# ------------------- FUNCTIONS -------------------
def get_earthquake_data():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    try:
        res = requests.get(url).json()
        records = []
        for feature in res["features"]:
            prop = feature["properties"]
            coords = feature["geometry"]["coordinates"]
            records.append({
                "Place": prop["place"],
                "Magnitude": prop["mag"],
                "Time": datetime.utcfromtimestamp(prop["time"] / 1000),
                "Longitude": coords[0],
                "Latitude": coords[1],
                "Tsunami Alert": "⚠️ Possible" if prop["mag"] and prop["mag"] >= 6.5 else "No"
            })
        return pd.DataFrame(records)
    except Exception as e:
        st.error("Error fetching earthquake data.")
        return pd.DataFrame()

def get_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY_NAME}&appid={API_KEY}&units=metric"
    try:
        res = requests.get(url).json()
        return {
            "temperature": f"{res['main']['temp']}°C",
            "humidity": f"{res['main']['humidity']}%",
            "wind_speed": f"{res['wind']['speed']} km/h",
            "condition": res['weather'][0]['description'].title()
        }
    except:
        return {
            "temperature": "N/A",
            "humidity": "N/A",
            "wind_speed": "N/A",
            "condition": "N/A"
        }

def get_hourly_rain_forecast(city):
    try:
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
        geo_data = requests.get(geo_url).json()
        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]

        onecall_url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=current,minutely,daily,alerts&units=metric&appid={API_KEY}"
        data = requests.get(onecall_url).json()

        rainfall_data = []
        for hour in data["hourly"][:12]:
            timestamp = datetime.utcfromtimestamp(hour["dt"]).strftime("%I %p")
            rain = hour.get("rain", {}).get("1h", 0)
            rainfall_data.append({"Hour": timestamp, "Rainfall (mm)": rain})

        return pd.DataFrame(rainfall_data)
    except:
        return pd.DataFrame()

def send_sms_alert(message):
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(body=message, from_=TWILIO_FROM, to=TWILIO_TO)
    except Exception as e:
        st.warning("SMS alert failed. Check credentials.")

def send_email_alert(subject, message):
    try:
        email = EmailMessage()
        email['Subject'] = subject
        email['From'] = EMAIL_SENDER
        email['To'] = EMAIL_RECEIVER
        email.set_content(message)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(email)
    except Exception as e:
        st.warning("Email alert failed. Check credentials.")

# ------------------- MAIN LOGIC -------------------
df = get_earthquake_data()
weather = get_weather()

left, right = st.columns([2, 1])
with left:
    st.subheader("🛑 Latest Earthquakes Today")
    if not df.empty:
        map_df = df.rename(columns={"Latitude": "latitude", "Longitude": "longitude"})
        st.map(map_df[["latitude", "longitude"]], zoom=1)
        st.dataframe(df.sort_values("Magnitude", ascending=False), use_container_width=True)
    else:
        st.warning("No earthquake data available right now.")

with right:
    st.subheader("🌦 Real-Time Weather")
    st.metric("Temperature", weather["temperature"])
    st.metric("Humidity", weather["humidity"])
    st.metric("Wind Speed", weather["wind_speed"])
    st.info(f"Condition: {weather['condition']}")

    st.subheader("🌧 Rainfall Forecast (Next 12 Hours)")
    rain_df = get_hourly_rain_forecast(CITY_NAME)
    if not rain_df.empty:
        st.bar_chart(rain_df.set_index("Hour"))
    else:
        st.warning("No rainfall data available.")

    st.subheader("🛰️ Live Weather Radar (Windy)")
    lat = 24.8607  # Karachi Latitude
    lon = 67.0011  # Karachi Longitude

    radar_iframe = f"""
    <iframe width="100%" height="400" src="https://embed.windy.com/embed2.html?lat={lat}&lon={lon}&detailLat={lat}&detailLon={lon}&width=650&height=450&zoom=6&level=surface&overlay=rain&menu=&message=true" frameborder="0"></iframe>
    """
    st.markdown(radar_iframe, unsafe_allow_html=True)

    st.subheader("🌊 Tsunami Risk")
    tsunami_df = df[df["Magnitude"] >= 6.5]
    if not tsunami_df.empty:
        st.error(f"⚠️ {len(tsunami_df)} High-magnitude earthquakes detected!")
        st.dataframe(tsunami_df[["Place", "Magnitude", "Time"]])

        alert_message = f"{len(tsunami_df)} strong earthquakes detected with tsunami risk.\nCheck dashboard for live updates."
        send_sms_alert(alert_message)
        send_email_alert("Tsunami Alert ⚠️", alert_message)
    else:
        st.success("✅ No tsunami risk detected today.")

st.caption("🔁 Auto-refresh every few minutes. Live data from USGS & OpenWeatherMap.")
