import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from numpy import trapezoid

# Function to generate a typical heating load profile with increased max amplitude
def typical_heating_load(time_scale):
    time = np.linspace(0, time_scale, 100)
    load_profile = np.piecewise(
        time,
        [time <= 15, (time > 15) & (time <= 40), time > 40],
        [lambda t: 7 * t,  # Morning ramp-up (increased slope)
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

# Function to find the first peak of the response
def find_first_peak(response):
    peaks = (np.diff(np.sign(np.diff(response))) < 0).nonzero()[0] + 1
    return peaks[0] if len(peaks) > 0 else len(response) - 1

# Streamlit app
st.title("Chiller Demand Response Simulation with PI Controller")
st.markdown(
    """
    **What is Demand Response?**
    This simulation models how a chiller responds to varying building cooling demands. 
    Use the sliders to adjust proportional and integral gains, and minimize energy waste.
    """
)

# User inputs
time_scale = st.slider("Timebase (minutes)", 1, 120, 30)
# Gain sliders
kp = st.slider("Proportional Gain (Kp)", 0.0, 2.0, 1.0, step=0.01)
ki = st.slider("Integral Gain (Ki)", 0.0, 2.0, 0.5, step=0.01)

custom_load = st.text_input("Custom Load Profile (comma-separated kW values)")

# Load profile
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

    # Calculate energy deficit
    energy_deficit = np.maximum(load_profile - chiller_response, 0)
    supplemental_energy = trapezoid(energy_deficit, time) / 60

    # Find first peak of the response
    first_peak_idx = find_first_peak(chiller_response)
    instantaneous_power = chiller_response[first_peak_idx]

    # Display results
    st.write(f"**Energy Wasted (Deficit):** {supplemental_energy:.2f} kWh")
    st.write(f"**Power at First Peak:** {instantaneous_power:.2f} kW")
    st.write(f"**PI Formula:** Output = {kp:.2f} * Error + {ki:.2f} * ∫Error dt")

    # Plot the graph
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(time, load_profile, label="Heat Load (kW)", color="red")
    ax.plot(time, chiller_response, label="Chiller Response (kW)", color="blue")
    ax.fill_between(time, load_profile, chiller_response, where=(load_profile > chiller_response),
                    color="green", alpha=0.3, label="Energy Deficit")
    ax.fill_between(time, chiller_response, load_profile, where=(chiller_response > load_profile),
                    color="yellow", alpha=0.3, label="Overperformance (Optimization Opportunity)")
    ax.set_title("Chiller Demand Response Simulation")
    ax.set_xlabel("Time (minutes)")
    ax.set_ylabel("Power (kW)")
    ax.legend()
    ax.grid(True)

    # Display plot
    st.pyplot(fig)
