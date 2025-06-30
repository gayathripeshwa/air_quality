import streamlit as st
import pandas as pd
import joblib
import requests
import os

# --- Page Config ---
st.set_page_config(page_title="AQI & Weather App", layout="wide")

# --- City Coordinates ---
city_data = {
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Delhi": {"lat": 28.6139, "lon": 77.2090},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639},
    "Kochi": {"lat": 9.9312, "lon": 76.2673}
}

# --- Load Model Metadata ---
model_df = pd.read_csv("random_forest_model_scores.csv")
model_paths = dict(zip(model_df["City"], model_df["Model_File"]))

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["🏠 AQI Predictor", "🌤️ Weather Forecast", "📊 Compare Cities"])

# ========================= TAB 1: AQI Predictor ========================= #
with tab1:
    st.title("🌫️ AQI Predictor")
    city = st.selectbox("Select City", list(city_data.keys()), key="predict_city")
    coords = city_data[city]

    model_path = model_paths.get(city)
    if not model_path or not os.path.exists(model_path):
        st.error(f"❌ Model not found for {city}: {model_path}")
        st.stop()
    model = joblib.load(model_path)

    st.subheader("📥 Fetch Weather")
    if st.button("🌤️ Fetch Weather", key="fetch_btn"):
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
                "timezone": "Asia/Kolkata"
            }
            res = requests.get(url, params=params)
            data = res.json()
            st.session_state.weather_data = {
                "temperature_2m_max": data["daily"]["temperature_2m_max"][0],
                "temperature_2m_min": data["daily"]["temperature_2m_min"][0],
                "precipitation_sum": data["daily"]["precipitation_sum"][0],
                "windspeed_10m_max": data["daily"]["windspeed_10m_max"][0]
            }
            st.success("✅ Weather fetched successfully")
        except Exception as e:
            st.error(f"❌ Failed to fetch weather: {e}")

    weather = st.session_state.get("weather_data", {})

    use_weather = st.checkbox("☁️ Use Fetched Weather", value=True)
    include_lag = st.checkbox("📊 Include Previous Day's AQI", value=False)

    with st.form("predict_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            temp_max = st.number_input("🌡️ Max Temp (°C)", value=weather.get("temperature_2m_max", 34.0) if use_weather else 34.0)
        with col2:
            temp_min = st.number_input("🌡️ Min Temp (°C)", value=weather.get("temperature_2m_min", 26.0) if use_weather else 26.0)
        with col3:
            precipitation = st.number_input("🌧️ Precipitation (mm)", value=weather.get("precipitation_sum", 0.0) if use_weather else 0.0)

        col4, col5 = st.columns(2)
        with col4:
            wind_speed = st.number_input("🌬️ Wind Speed (km/h)", value=weather.get("windspeed_10m_max", 14.0) if use_weather else 14.0)
        with col5:
            aqi_lag = st.number_input("📊 Previous Day's AQI", value=90.0, disabled=not include_lag)

        if city == "Chennai":
            humidity = st.number_input("💧 Relative Humidity (%)", value=70.0)

        submitted = st.form_submit_button("🔮 Predict AQI")

    if submitted:
        try:
            if city == "Chennai":
                input_data = pd.DataFrame([{
                    "temperature_2m_max": temp_max,
                    "temperature_2m_min": temp_min,
                    "wind_speed_10m_max": wind_speed,
                    "precipitation_sum": precipitation,
                    "relative_humidity_2m_mean": humidity,
                    "AQI_lag1": aqi_lag if include_lag else 90.0
                }])[['temperature_2m_max', 'temperature_2m_min', 'wind_speed_10m_max', 'precipitation_sum', 'relative_humidity_2m_mean', 'AQI_lag1']]
            else:
                input_data = pd.DataFrame([{
                    "temperature_2m_max": temp_max,
                    "temperature_2m_min": temp_min,
                    "precipitation_sum": precipitation,
                    "windspeed_10m_max": wind_speed
                }])[['temperature_2m_max', 'temperature_2m_min', 'precipitation_sum', 'windspeed_10m_max']]

            prediction = model.predict(input_data)[0]

            def get_aqi_category(aqi):
                if aqi <= 50: return "🟢 Good"
                elif aqi <= 100: return "🟡 Moderate"
                elif aqi <= 200: return "🟠 Poor"
                elif aqi <= 300: return "🔴 Unhealthy"
                else: return "🟣 Very Unhealthy"

            st.success(f"📈 Predicted AQI for {city}: `{prediction:.2f}`")
            st.markdown(f"**Category:** {get_aqi_category(prediction)}")
        except Exception as e:
            st.error(f"⚠️ Prediction failed: {e}")

# ======================== TAB 2: Weather Forecast ======================= #
with tab2:
    st.title("🌤️ 7-Day Weather Forecast")
    city = st.selectbox("Select City", list(city_data.keys()), key="weather_city")
    coords = city_data[city]

    if st.button("📡 Get Forecast"):
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
                "timezone": "Asia/Kolkata"
            }
            res = requests.get(url, params=params)
            data = res.json()

            forecast_df = pd.DataFrame({
                "Date": data["daily"]["time"],
                "Temp Max (°C)": data["daily"]["temperature_2m_max"],
                "Temp Min (°C)": data["daily"]["temperature_2m_min"],
                "Precipitation (mm)": data["daily"]["precipitation_sum"],
                "Wind Speed (km/h)": data["daily"]["windspeed_10m_max"]
            })

            st.dataframe(forecast_df.set_index("Date"))
        except Exception as e:
            st.error(f"Error fetching forecast: {e}")

# ======================= TAB 3: Compare Cities ========================== #
with tab3:
    st.title("📊 Compare AQI Across Cities")

    selected_cities = st.multiselect("Select Cities to Compare", list(city_data.keys()), default=["Delhi", "Mumbai"])

    if st.button("🔍 Compare AQI Predictions") and selected_cities:
        comparison_results = []

        for city in selected_cities:
            coords = city_data[city]
            model_path = model_paths.get(city)
            if not model_path or not os.path.exists(model_path):
                comparison_results.append({"City": city, "Error": "Model not found"})
                continue

            try:
                model = joblib.load(model_path)
                if city == "Chennai":
                    input_data = {
                        "temperature_2m_max": 34.0,
                        "temperature_2m_min": 26.0,
                        "wind_speed_10m_max": 14.0,
                        "precipitation_sum": 0.0,
                        "relative_humidity_2m_mean": 70.0,
                        "AQI_lag1": 90.0
                    }
                    df = pd.DataFrame([input_data])[list(input_data.keys())]
                else:
                    input_data = {
                        "temperature_2m_max": 34.0,
                        "temperature_2m_min": 26.0,
                        "precipitation_sum": 0.0,
                        "windspeed_10m_max": 14.0
                    }
                    df = pd.DataFrame([input_data])[list(input_data.keys())]

                aqi = model.predict(df)[0]
                comparison_results.append({"City": city, "Predicted AQI": round(aqi, 2)})

            except Exception as e:
                comparison_results.append({"City": city, "Error": str(e)})

        st.dataframe(pd.DataFrame(comparison_results))
