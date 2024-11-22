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

# Add Energy Deficit area (Green) - Ensure it's plotted first
fig.add_trace(go.Scatter(
    x=np.concatenate([time, time[::-1]]),
    y=np.concatenate([load_profile, np.minimum(chiller_response, load_profile)[::-1]]),
    fill='toself',
    fillcolor='rgba(34, 139, 34, 0.6)',  # Green color
    line=dict(color='rgba(255,255,255,0)'),  # No border
    name=f"Energy Deficit: {energy_deficit_total:.2f} kWh",
    hoverinfo="skip"  # Remove tooltips for this area
))

# Add Overperformance area (Orange) - Plotted on top
fig.add_trace(go.Scatter(
    x=np.concatenate([time, time[::-1]]),
    y=np.concatenate([chiller_response, np.maximum(load_profile, chiller_response)[::-1]]),
    fill='toself',
    fillcolor='rgba(255, 165, 0, 0.6)',  # Orange color
    line=dict(color='rgba(255,255,255,0)'),  # No border
    name=f"Overperformance: {energy_overperformance_total:.2f} kWh",
    hoverinfo="skip"  # Remove tooltips for this area
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
    hovermode="x unified",  # Unified hover tooltip for lines only
    template="plotly_white",
    width=1400,  # Make the chart wider
    height=600   # Maintain height
)

# Display the chart
st.plotly_chart(fig, use_container_width=True)
