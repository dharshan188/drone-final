import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import random

# Page Config
st.set_page_config(page_title="Neon Drone Dashboard", layout="wide")

# Neon CSS
st.markdown("""
    <style>
    body {
        background-color: #000814;
        color: #00f7ff;
    }
    .stApp {
        background-color: #000814;
    }
    .stMetric, .stButton>button, .css-18e3th9 {
        background-color: #001d3d;
        color: #00f7ff;
        border-radius: 10px;
        border: 1px solid #00f7ff;
        box-shadow: 0 0 15px #00f7ff;
    }
    .stButton>button {
        padding: 0.5rem 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Telemetry Generator
def generate_telemetry():
    return {
        "mode": random.choice(["Auto", "Manual", "RTL", "Loiter"]),
        "battery": round(random.uniform(8.5, 12.6), 2),
        "signal": random.randint(-90, -50),
        "altitude": round(random.uniform(100, 250), 2),
        "temperature": round(random.uniform(18, 30), 2),
        "pressure": round(random.uniform(960, 1025), 2),
        "roll": round(random.uniform(-10, 10), 2),
        "pitch": round(random.uniform(-30, 30), 2),
        "yaw": round(random.uniform(0, 360), 2),
        "lat": round(random.uniform(29.13, 29.14), 6),
        "lon": round(random.uniform(77.22, 77.23), 6),
        "speed": round(random.uniform(5, 25), 2)
    }

telemetry = generate_telemetry()

# Alert
if telemetry["battery"] < 9.0:
    st.error("Battery Critical!", icon="⚠")

# Layout Start
col1, col2, col3 = st.columns([1, 2, 1])

# Controls
with col1:
    st.markdown("### Controls")
    st.slider("Simulation Speed", 0.5, 3.0, 1.0)
    st.toggle("IMU Sensor", True)
    st.toggle("GPS Sensor", True)
    st.toggle("Environmental Sensor", False)
    st.button("Pause")

# 3D Drone View
with col2:
    st.markdown("### 3D Drone View")
    fig = go.Figure()

    # Body
    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers',
        marker=dict(size=10, color='cyan'),
        name="Body"
    ))

    # Arms (X Shape)
    arms = [
        ([0, 1], [0, 1], [0, 0]),   # Arm 1
        ([0, -1], [0, 1], [0, 0]),  # Arm 2
        ([0, -1], [0, -1], [0, 0]), # Arm 3
        ([0, 1], [0, -1], [0, 0])   # Arm 4
    ]
    for x, y, z in arms:
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode='lines',
            line=dict(color='aqua', width=5)
        ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor='black'
    )
    st.plotly_chart(fig, use_container_width=True)

# Map
with col3:
    st.markdown("### Map")
    st.map(pd.DataFrame({'lat': [telemetry['lat']], 'lon': [telemetry['lon']]}))
    st.markdown(f"**Coordinates:** {telemetry['lat']}, {telemetry['lon']}")

# Speedometer Gauges
st.markdown("### Speedometers")
g1, g2, g3, g4 = st.columns(4)

def create_gauge(value, title, max_val):
    return go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={
            'axis': {'range': [None, max_val]},
            'bar': {'color': "aqua"},
            'bgcolor': "black",
            'borderwidth': 2,
            'bordercolor': "cyan"
        },
        domain={'x': [0, 1], 'y': [0, 1]}
    )).update_layout(paper_bgcolor="black", font=dict(color="aqua"))

g1.plotly_chart(create_gauge(telemetry["speed"], "Speed (m/s)", 50), use_container_width=True)
g2.plotly_chart(create_gauge(telemetry["altitude"], "Altitude (m)", 300), use_container_width=True)
g3.plotly_chart(create_gauge(telemetry["battery"], "Battery (V)", 13), use_container_width=True)
g4.plotly_chart(create_gauge(abs(telemetry["signal"]), "Signal (dBm)", 100), use_container_width=True)

# Detailed Telemetry
st.markdown("### Telemetry Readings")
t1, t2, t3, t4 = st.columns(4)
t1.metric("Roll", telemetry["roll"])
t2.metric("Pitch", telemetry["pitch"])
t3.metric("Yaw", telemetry["yaw"])
t4.metric("Temperature", f"{telemetry['temperature']}°C")

t1.metric("Pressure", f"{telemetry['pressure']} hPa")
t2.metric("Flight Mode", telemetry["mode"])

# Telemetry Trend
st.markdown("### Live Telemetry Trends")
time_range = pd.date_range(end=pd.Timestamp.now(), periods=30, freq="s")
data = pd.DataFrame({
    "Time": time_range,
    "Altitude": np.random.normal(telemetry["altitude"], 5, size=30),
    "Temperature": np.random.normal(telemetry["temperature"], 1, size=30),
    "Speed": np.random.normal(telemetry["speed"], 1.5, size=30)
})

fig = go.Figure()
fig.add_trace(go.Scatter(x=data["Time"], y=data["Altitude"], name="Altitude", line=dict(color="cyan")))
fig.add_trace(go.Scatter(x=data["Time"], y=data["Temperature"], name="Temp", line=dict(color="magenta")))
fig.add_trace(go.Scatter(x=data["Time"], y=data["Speed"], name="Speed", line=dict(color="lime")))

fig.update_layout(
    plot_bgcolor='black',
    paper_bgcolor='black',
    font=dict(color='aqua'),
    margin=dict(l=20, r=20, t=40, b=20),
)

st.plotly_chart(fig, use_container_width=True)
