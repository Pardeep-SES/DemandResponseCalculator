import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

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
        response[i] = max(0, response[i])  # Prevent negative response
    return response

# Streamlit title and description
st.title("Chiller Demand Response Simulation with PI Controller")
st.markdown(
    """
    This simulation models how a chiller responds to varying building cooling demands. 
    Adjust the sliders to fine-tune proportional and integral gains for efficient energy use.
    """
)

# User Inputs
time_scale = st.slider("Timebase (minutes)", 1, 120, 30)
kp = st.slider("Proportional Gain (Kp)", 0.0, 2.0, 1.0, step=0.01)
ki = st.slider("Integral Gain (Ki)", 0.0, 2.0, 0.5, step=0.01)
custom_load = st.text_input("Custom Load Profile (comma-separated kW values)")

# Generate or load the heating profile
if custom_load.strip():
    try:
        load_profile = np.array([float(x) for x in custom_load.split(",")])
        time = np.linspace(0, time_scale, len(load_profile))
    except ValueError:
        st.error("Invalid custom load profile. Please provide comma-separated numeric values.")
        load_profile, time = None, None
else:
    time, load_profile = typical_heating_load(time_scale)

# Plotting
if load_profile is not None:
    # Simulate chiller response using the PI controller
    chiller_response = pi_controller(load_profile, time, kp, ki)

    # Plot the graph
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot Heat Load and Chiller Response lines
    ax.plot(time, load_profile, label="Heat Load (kW)", color="red")
    ax.plot(time, chiller_response, label="Chiller Response (kW)", color="blue")

    # Fill areas for deficit and overperformance
    ax.fill_between(time, load_profile, chiller_response, where=(load_profile > chiller_response),
                    color="green", alpha=0.3, label="Energy Deficit")
    ax.fill_between(time, chiller_response, load_profile, where=(chiller_response > load_profile),
                    color="yellow", alpha=0.3, label="Overperformance (Optimization Opportunity)")

    # Plot aesthetics
    ax.set_title("Chiller Demand Response Simulation")
    ax.set_xlabel("Time (minutes)")
    ax.set_ylabel("Power (kW)")
    ax.legend()
    ax.grid(True)

    # Display plot
    st.pyplot(fig)

    # Optional: Display summary stats (Energy Deficit and Overperformance)
    energy_deficit_total = np.trapz(
        np.maximum(load_profile - chiller_response, 0), time) / 60  # Convert to kWh
    energy_overperformance_total = np.trapz(
        np.maximum(chiller_response - load_profile, 0), time) / 60  # Convert to kWh

    st.write(f"**Total Energy Deficit:** {energy_deficit_total:.2f} kWh")
    st.write(f"**Total Overperformance:** {energy_overperformance_total:.2f} kWh")
