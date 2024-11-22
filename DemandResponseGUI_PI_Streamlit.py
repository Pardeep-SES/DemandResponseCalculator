# Calculate energy deficit and overperformance
energy_deficit = np.where(load_profile > chiller_response, load_profile - chiller_response, 0)
energy_overperformance = np.where(chiller_response > load_profile, chiller_response - load_profile, 0)

energy_deficit_total = np.trapz(energy_deficit, time) / 60  # Convert to kWh
energy_overperformance_total = np.trapz(energy_overperformance, time) / 60  # Convert to kWh

# Display Results
st.write(f"**Energy Deficit (Underperformance):** {energy_deficit_total:.2f} kWh")
st.write(f"**Energy Overperformance:** {energy_overperformance_total:.2f} kWh")
st.write(f"**PI Formula:** Output = {kp:.2f} * Error + {ki:.2f} * ∫Error dt")

# Create interactive Plotly chart
fig = go.Figure()

# Add Heat Load line
fig.add_trace(go.Scatter(
    x=time, 
    y=load_profile, 
    mode='lines', 
    name="Heat Load (kW)", 
    line=dict(color='red')
))

# Add Chiller Response line
fig.add_trace(go.Scatter(
    x=time, 
    y=chiller_response, 
    mode='lines', 
    name="Chiller Response (kW)", 
    line=dict(color='blue')
))

# Add Energy Deficit area (Green)
fig.add_trace(go.Scatter(
    x=np.concatenate([time, time[::-1]]),
    y=np.concatenate([load_profile, chiller_response[::-1]]),
    fill='toself',
    fillcolor='rgba(34, 139, 34, 0.6)',  # Green for deficit
    line=dict(color='rgba(255,255,255,0)'),  # No border
    name=f"Energy Deficit: {energy_deficit_total:.2f} kWh"
))

# Add Overperformance area (Orange)
fig.add_trace(go.Scatter(
    x=np.concatenate([time, time[::-1]]),
    y=np.concatenate([chiller_response, load_profile[::-1]]),
    fill='toself',
    fillcolor='rgba(255, 165, 0, 0.6)',  # Orange for overperformance
    line=dict(color='rgba(255,255,255,0)'),  # No border
    name=f"Overperformance: {energy_overperformance_total:.2f} kWh"
))

# Update layout
fig.update_layout(
    title="Chiller Demand Response Simulation",
    xaxis_title="Time (minutes)",
    yaxis_title="Power (kW)",
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.25,  # Position the legend below the chart
        xanchor="center",
        x=0.5
    ),
    hovermode="x unified",  # Unified hover tooltip
    template="plotly_white",
    width=1300,  # Wider chart
    height=600   # Maintain height
)

# Display the chart
st.plotly_chart(fig, use_container_width=True)
