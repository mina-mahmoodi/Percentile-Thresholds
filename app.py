import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ✅ Page settings and title
st.set_page_config(page_title="Vibration Threshold Calculator", layout="wide")
st.title("📈 Vibration Warning & Error Threshold Calculator")

# Upload CSV
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Ensure necessary columns are present
    required_columns = ['t', 'motor_state', 'vibration_x', 'vibration_y', 'vibration_z']
    if not all(col in df.columns for col in required_columns):
        st.error("The CSV file must contain columns: t, motor_state, vibration_x, vibration_y, vibration_z")
    else:
        # Convert timestamp
        try:
            df['t'] = pd.to_datetime(df['t'])
        except Exception as e:
            st.warning(f"Timestamp conversion failed: {e}")

        # ✅ Filter only motor_state == 3 (motor ON)
        motor_on_df = df[df['motor_state'] == 3].copy()

        if motor_on_df.empty:
            st.error("❌ No valid data: motor_state == 3 not found in the uploaded file.")
        else:
            st.success(f"✅ Loaded {len(motor_on_df)} rows with motor ON (state 3).")

            # Summary statistics
            st.subheader("📊 Summary Statistics (Motor ON)")
            stats = motor_on_df[['vibration_x', 'vibration_y', 'vibration_z']].describe()
            st.dataframe(stats)

            # Line plots
            st.subheader("📉 Vibration Over Time (Motor ON)")

            fig_x = px.line(motor_on_df, x='t', y='vibration_x', title='Vibration X over Time')
            fig_y = px.line(motor_on_df, x='t', y='vibration_y', title='Vibration Y over Time')
            fig_z = px.line(motor_on_df, x='t', y='vibration_z', title='Vibration Z over Time')

            col1, col2, col3 = st.columns(3)
            col1.plotly_chart(fig_x, use_container_width=True)
            col2.plotly_chart(fig_y, use_container_width=True)
            col3.plotly_chart(fig_z, use_container_width=True)

            # Download filtered data
            st.subheader("⬇️ Download Filtered Data (Motor ON)")
            csv = motor_on_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name='motor_on_filtered_data.csv',
                mime='text/csv',
            )
