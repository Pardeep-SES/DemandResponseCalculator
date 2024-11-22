import streamlit as st
import numpy as np
import plotly.graph_objects as go
from numpy import trapezoid

# Function to generate a typical heating load profile
def typical_heating_load(time_scale):
    time = np.linspace(0, time_scale, 100)
    load_profile = np.piecewise(
        time,
        [time <= 15, (time > 15) & (time <= 40), time > 40],
        [lambda t: 7 * t,  # Morning ramp-up
         lambda t: 100 + 20 * np.sin(2 * np.pi * (t - 15) / 20),  # Midday fluctuation
         lambda t: 100 * np.exp(-0.05 * (t - 40))]  # Evening decline
    )
    return time, load_profile

# PI Controller implementation
def pi_controller(load_profile, time, kp, ki):
    response = np.zeros_like(load_profile)
    integral = 0

    for i in range(1, len(load_profile)):
        error = load_profile[i] - response[i-1]
        integral += error * (time[i] - time[i-1])
        response[i] = kp * error + ki * integral
        response[i] = max(0, response[i])
    return response

# SES Logo and Title
logo_path = "assets/SES_Logo+Tag_CMYK.png"  # Path set to Git repo's assets folder
st.markdown(
    f"""
    <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 20px;">
        <img src="data:image/png;base64,{open(logo_path, "rb").read().encode("base64").decode()}" 
             style="max-width: 80%; height: auto;" />
    </div>
    """,
    unsafe_allow_html=True,
)

st.title("Chiller Demand Response Simulation with PI Controller")
st.markdown(
    """
    This simulation models how a chiller responds to varying building cooling demands. Adjust the sliders to 
    fine-tune proportional and integral gains for efficient energy use. Hover over the chart to view integrated 
    energy required and overperformance values.
    """
)

# User Inputs
time_scale = st.slider("Timebase (minutes)", 1, 120, 30)
kp = st.slider("Proportional Gain (Kp)", 0.0, 2.0, 1.0, step=0.01)
ki = st.slider("Integral Gain (Ki)", 0.0, 2.0, 0.5, step=0.01)
custom_load = st.text_input("Custom Load Profile (comma-separated kW values)")

# Load Profile
if custom_load.strip():
    try:
        load_profile = np.array([float(x) for x in custom_load.split(",")])
        time = np.linspace(0, time_scale, len(load_profile))
    except ValueError:
        st.error("Invalid custom load profile. Please provide comma-separated numeric values.")
        load_profile, time = None, None
else:
    time, load_profile = typical_heating_load(time_scale)

if load_profile is not None:
    # PI Controller
    chiller_response = pi_controller(load_profile, time, kp, ki)

    # Calculate energy deficit and overperformance
    energy_deficit = np.maximum(load_profile - chiller_response, 0)
    energy_overperformance = np.maximum(chiller_response - load_profile, 0)

    energy_deficit_total = trapezoid(energy_deficit, time) / 60  # Convert to kWh
    energy_overperformance_total = trapezoid(energy_overperformance, time) / 60  # Convert to kWh

    # Display Results
    st.write(f"**Energy Required (Deficit):** {energy_deficit_total:.2f} kWh")
    st.write(f"**Energy Overperformance:** {energy_overperformance_total:.2f} kWh")
    st.write(f"**PI Formula:** Output = {kp:.2f} * Error + {ki:.2f} * ∫Error dt")

    # Create interactive Plotly chart
    fig = go.Figure()

    # Add Heat Load line
    fig.add_trace(go.Scatter(x=time, y=load_profile, mode='lines', name="Heat Load (kW)", line=dict(color='red')))

    # Add Chiller Response line
    fig.add_trace(go.Scatter(x=time, y=chiller_response, mode='lines', name="Chiller Response (kW)", line=dict(color='blue')))

    # Add Energy Deficit area
    fig.add_trace(go.Scatter(
        x=np.concatenate([time, time[::-1]]),
        y=np.concatenate([load_profile, chiller_response[::-1]]),
        fill='toself',
        fillcolor='rgba(0, 255, 0, 0.3)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo='skip',
        name=f"Energy Deficit: {energy_deficit_total:.2f} kWh"
    ))

    # Add Overperformance area
    fig.add_trace(go.Scatter(
        x=np.concatenate([time, time[::-1]]),
        y=np.concatenate([chiller_response, load_profile[::-1]]),
        fill='toself',
        fillcolor='rgba(255, 255, 0, 0.3)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo='skip',
        name=f"Overperformance: {energy_overperformance_total:.2f} kWh"
    ))

    # Update layout
    fig.update_layout(
        title="Chiller Demand Response Simulation",
        xaxis_title="Time (minutes)",
        yaxis_title="Power (kW)",
        legend_title="Legend",
        hovermode="x unified",
        template="plotly_white"
    )

    # Display the chart
    st.plotly_chart(fig)
