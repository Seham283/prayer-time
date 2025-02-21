import streamlit as st
import requests
import json
from datetime import datetime

st.title("🕌 تحديد مواقيت الأذان 🕌")

# 🛰️ دالة جلب الموقع الجغرافي تلقائيًا
def get_location():
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        lat, lon = map(float, data["loc"].split(","))
        timezone = data["timezone"]
        return lat, lon, timezone
    except:
        return None, None, None

# ⛰️ دالة حساب الارتفاع عن سطح البحر
def get_altitude(lat, lon):
    try:
        url = f"https://api.opentopodata.org/v1/etopo1?locations={lat},{lon}"
        response = requests.get(url)
        data = response.json()
        altitude = data["results"][0]["elevation"]
        return altitude
    except:
        return 0  # لو فشل، نعتبره 0

# محاولة تحديد الموقع تلقائيًا
lat, lon, timezone = get_location()

# عرض الإحداثيات التي تم تحديدها
st.write("📍 **إحداثيات موقعك الحالي:**")
st.write(f"🌍 **خط العرض:** `{lat if lat else 'غير متوفر'}`")
st.write(f"🌍 **خط الطول:** `{lon if lon else 'غير متوفر'}`")
st.write(f"⏳ **المنطقة الزمنية:** `{timezone if timezone else 'غير متوفر'}`")

# حساب الارتفاع وإظهاره
if lat and lon:
    altitude = get_altitude(lat, lon)
    st.write(f"🗻 **الارتفاع عن سطح البحر:** `{altitude:.2f}` متر")
else:
    altitude = 0
    st.warning("⚠️ لم يتم تحديد الموقع تلقائيًا!")

# ✅ زر لتمكين الإدخال اليدوي عند الحاجة فقط
manual_entry = st.checkbox("🔧 إدخال الإحداثيات يدويًا")

if manual_entry:
    lat = st.number_input("🌍 أدخل خط العرض (Latitude):", format="%.6f", value=lat or 0.0)
    lon = st.number_input("🌍 أدخل خط الطول (Longitude):", format="%.6f", value=lon or 0.0)
    timezone = st.text_input("⏳ أدخل اسم المنطقة الزمنية:", value=timezone or "UTC")

# اختيار طريقة الحساب
methods = {
    "Muslim World League": 2,
    "Islamic Society of North America": 3,
    "Egyptian General Authority of Survey": 5,
    "Umm Al-Qura University, Makkah": 4,
    "University of Islamic Sciences, Karachi": 1,
    "Institute of Geophysics, University of Tehran": 7,
    "Shia Ithna-Ashari, Leva Institute, Qum": 0
}
method_name = st.selectbox("📋 اختر طريقة الحساب:", list(methods.keys()))
method_id = methods[method_name]

# زر لحساب المواقيت
if st.button("📅 حساب مواقيت الصلاة"):
    if lat and lon and timezone:
        try:
            # جلب مواقيت الصلاة
            api_url = f"http://api.aladhan.com/v1/timings/{datetime.now().strftime('%d-%m-%Y')}?latitude={lat}&longitude={lon}&method={method_id}&timezonestring={timezone}"
            response = requests.get(api_url)
            data = response.json()
            prayer_times = data["data"]["timings"]

            # تصحيح الارتفاع عن سطح البحر
            correction = round(altitude / 900, 2)  # كل 900 متر بتأثر بدقيقة واحدة
            
            # عرض المواقيت بعد التصحيح
            st.success(f"🛠 **طريقة الحساب:** `{method_name}`")
            st.write("🕌 **مواقيت الصلاة (مع تعديل الارتفاع إن وجد):**")
            for prayer, time in prayer_times.items():
                time_hour, time_minute = map(int, time.split(":"))
                if prayer in ["Fajr", "Maghrib", "Isha"] and altitude > 0:
                    corrected_minute = time_minute - correction
                    if corrected_minute < 0:
                        time_hour -= 1
                        corrected_minute += 60
                    corrected_time = f"{int(time_hour):02d}:{int(corrected_minute):02d}"
                    st.write(f"🕒 {prayer}: {corrected_time} _(متأثر بالارتفاع)_")
                else:
                    st.write(f"🕒 {prayer}: {time}")

        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء الحساب: {e}")
    else:
        st.warning("⚠️ يرجى إدخال الموقع يدويًا!")
