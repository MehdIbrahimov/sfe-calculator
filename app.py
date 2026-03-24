import streamlit as st
import pandas as pd
import math

# --- App Configuration ---
st.set_page_config(page_title="SFE Calculator", layout="centered", page_icon="🧪")

# --- SFE Calculation Function ---
def calculate_sfe(theta_d_deg, theta_g_deg):
    GAMMA_D_TOTAL, GAMMA_D_D = 50.8, 50.8
    GAMMA_G_TOTAL, GAMMA_G_D, GAMMA_G_P = 64.0, 34.0, 30.0

    theta_d = math.radians(theta_d_deg)
    theta_g = math.radians(theta_g_deg)

    W_d = GAMMA_D_TOTAL * (1 + math.cos(theta_d))
    gamma_s_d = (W_d ** 2) / (4 * GAMMA_D_D)

    W_g = GAMMA_G_TOTAL * (1 + math.cos(theta_g))
    numerator = W_g - 2 * math.sqrt(gamma_s_d * GAMMA_G_D)
    
    gamma_s_p = 0.0 if numerator < 0 else (numerator / (2 * math.sqrt(GAMMA_G_P))) ** 2
    gamma_s_total = gamma_s_d + gamma_s_p

    return gamma_s_total, gamma_s_d, gamma_s_p

# --- Main App Interface ---
st.title("SFE Calculator 🧪")
st.markdown("Enter your contact angles below to calculate the Surface Free Energy.")

# Initialize a session state list to store our trial data
if "data" not in st.session_state:
    st.session_state.data = []

# --- Input Section ---
st.subheader("Add a Measurement")
col1, col2 = st.columns(2)

with col1:
    d_val = st.number_input("Diiodomethane Angle (°)", min_value=0.0, max_value=180.0, value=45.0, step=0.1)
with col2:
    g_val = st.number_input("Glycerol Angle (°)", min_value=0.0, max_value=180.0, value=60.0, step=0.1)

# Buttons
btn_col1, btn_col2 = st.columns([1, 3])
with btn_col1:
    if st.button("Add Trial", type="primary", use_container_width=True):
        total, disp, polar = calculate_sfe(d_val, g_val)
        trial_num = len(st.session_state.data) + 1
        
        # Append the new data to our session state
        st.session_state.data.append({
            "Trial": trial_num,
            "Diio (°)": d_val,
            "Gly (°)": g_val,
            "Total SFE": round(total, 2),
            "Dispersive": round(disp, 2),
            "Polar": round(polar, 2)
        })

with btn_col2:
    if st.button("Clear Data", use_container_width=False):
        st.session_state.data = []
        st.rerun() # Refresh the page to clear everything

# --- Results Section ---
if st.session_state.data:
    st.divider()
    
    # Convert list of dictionaries to a Pandas DataFrame
    df = pd.DataFrame(st.session_state.data)
    
    # 1. Show Data Table
    st.subheader("Data Table")
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # 2. Show Statistics
    col_mean, col_std = st.columns(2)
    mean_total = df["Total SFE"].mean()
    std_total = df["Total SFE"].std() if len(df) > 1 else 0.0
    
    col_mean.metric("Mean Total SFE", f"{mean_total:.2f} mN/m")
    col_std.metric("Standard Deviation", f"{std_total:.2f} mN/m" if len(df) > 1 else "--")
    
    # 3. Show Graph
    st.subheader("Total SFE vs Dispersive Part")
    # Streamlit's native scatter chart makes this a one-liner!
    st.scatter_chart(df, x="Total SFE", y="Dispersive", color="#FF4B4B")