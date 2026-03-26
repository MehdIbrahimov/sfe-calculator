import streamlit as st
import pandas as pd
import math

# --- App Configuration ---
st.set_page_config(page_title="SFE Calculator", layout="centered", page_icon="🧪")

# --- SFE Calculation Function ---
def calculate_sfe(theta_d_deg, theta_g_deg, gamma_d_tot, gamma_d_d, gamma_d_p, gamma_g_tot, gamma_g_d, gamma_g_p):
    theta_d = math.radians(theta_d_deg)
    theta_g = math.radians(theta_g_deg)

    # Calculate the Work of Adhesion divided by 2 for each liquid
    W_d = (gamma_d_tot * (1 + math.cos(theta_d))) / 2.0
    W_g = (gamma_g_tot * (1 + math.cos(theta_g))) / 2.0

    # Get the square roots of all liquid constants
    sq_d_d = math.sqrt(gamma_d_d)
    sq_d_p = math.sqrt(gamma_d_p)
    sq_g_d = math.sqrt(gamma_g_d)
    sq_g_p = math.sqrt(gamma_g_p)

    # Solve the system of linear equations using Cramer's rule
    determinant = (sq_d_d * sq_g_p) - (sq_d_p * sq_g_d)
    
    if determinant == 0:
        return 0.0, 0.0, 0.0 # Failsafe to prevent division by zero

    sq_s_d = ((W_d * sq_g_p) - (W_g * sq_d_p)) / determinant
    sq_s_p = ((W_g * sq_d_d) - (W_d * sq_g_d)) / determinant

    # Calculate final energies (force to 0 if the root is mathematically negative)
    gamma_s_d = sq_s_d**2 if sq_s_d > 0 else 0.0
    gamma_s_p = sq_s_p**2 if sq_s_p > 0 else 0.0

    gamma_s_total = gamma_s_d + gamma_s_p

    return gamma_s_total, gamma_s_d, gamma_s_p

# --- Main App Interface ---
st.title("SFE Calculator 🧪")
st.markdown("Enter your contact angles below to calculate the Surface Free Energy.")

# Initialize a session state list to store our trial data
if "data" not in st.session_state:
    st.session_state.data = []

# --- Input Section ---
# --- Import Section ---
with st.expander("📂 Import Previous Data"):
    uploaded_file = st.file_uploader("Upload a previously saved CSV file", type=["csv"])
    
    if uploaded_file is not None:
        if st.button("Load Data (Overrides current table)", type="secondary"):
            try:
                # Read the CSV with Pandas
                df_imported = pd.read_csv(uploaded_file)
                
                # Convert it back to a dictionary and save it to the app's memory
                st.session_state.data = df_imported.to_dict('records')
                
                # Refresh the app to show the new data
                st.rerun()
            except Exception as e:
                st.error(f"Error loading file: {e}. Make sure it's a valid SFE CSV!")

st.subheader("Add a Measurement")
col1, col2 = st.columns(2)

with col1:
    d_val = st.number_input("Diiodomethane Angle (°)", min_value=0.0, max_value=180.0, value=45.0, step=0.1)
    d_tot = st.number_input("Diiodomethane Total Surface Tension (mN/m)", min_value=0.0, max_value=100.0, value=50.0, step=0.1)
    d_d = st.number_input("Diiodomethane Dispersive Surface Tension (mN/m)", min_value=0.0, max_value=100.0, value=47.4, step=0.1)
    d_p = st.number_input("Diiodomethane Polar Surface Tension (mN/m)", min_value=0.0, max_value=100.0, value=2.6, step=0.1)
with col2:
    g_val = st.number_input("Glycerol Angle (°)", min_value=0.0, max_value=180.0, value=60.0, step=0.1)
    g_tot = st.number_input("Glycerol Total Surface Tension (mN/m)", min_value=0.0, max_value=100.0, value=64.0, step=0.1)
    g_d = st.number_input("Glycerol Dispersive Surface Tension (mN/m)", min_value=0.0, max_value=100.0, value=34.0, step=0.1)
    g_p = st.number_input("Glycerol Polar Surface Tension (mN/m)", min_value=0.0, max_value=100.0, value=30.0, step=0.1)

# Buttons
btn_col1, btn_col2 = st.columns([1, 3])
with btn_col1:
    if st.button("Add Trial", type="primary", width='stretch'):
        total, disp, polar = calculate_sfe(d_val, g_val, d_tot, d_d, d_p, g_tot, g_d, g_p)
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
    if st.button("Clear Data", width='content'):
        st.session_state.data = []
        st.rerun() # Refresh the page to clear everything

# --- Results Section ---
if st.session_state.data:
    st.divider()
    
    # Convert list of dictionaries to a Pandas DataFrame
    df = pd.DataFrame(st.session_state.data)
    
# 1. Show Data Table (Now Editable!)
    st.subheader("Data Table")
    st.markdown("💡 *Tip: Click the checkbox on the far left of any row and press the **Delete** key (or use the trash icon at the top right of the table) to remove a bad trial.*")
    
    # We swap st.dataframe for st.data_editor and add num_rows="dynamic"
    edited_df = st.data_editor(
        df, 
        width='stretch', 
        num_rows="dynamic" # This is the magic command that enables row deletion
    )
    
    # Instantly sync the edited table back to the app's memory so the graph updates!
    st.session_state.data = edited_df.to_dict('records')
    
    # --- NEW EXPORT FEATURE ---
    # Convert the dataframe to a CSV format
    csv = df.to_csv(index=False).encode('utf-8')
    
    # Create the download button
    st.download_button(
        label="💾 Download Data as CSV",
        data=csv,
        file_name="sfe_data.csv",
        mime="text/csv",
    )
    # --------------------------
    
    # 2. Show Statistics
    col_mean, col_std = st.columns(2)
    mean_total = df["Total SFE"].mean()
    std_total = df["Total SFE"].std() if len(df) > 1 else 0.0
    
    col_mean.metric("Mean Total SFE", f"{mean_total:.2f} mN/m")
    col_std.metric("Standard Deviation", f"{std_total:.2f} mN/m" if len(df) > 1 else "--")
    
    # 3. Show Graph
    st.subheader("Dispersive vs Polar Part")
    # Streamlit's native scatter chart makes this a one-liner!
    st.scatter_chart(df, x="Dispersive", y="Polar", color="#FF4B4B")