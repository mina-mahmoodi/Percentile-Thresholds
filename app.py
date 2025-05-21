import streamlit as st
import pandas as pd
import plotly.express as px

# Page config and title
st.set_page_config(page_title="Vibration Threshold Calculator", layout="wide")
st.title("📈 Vibration Warning & Error Threshold Calculator")

# Upload file
uploaded_file = st.file_uploader("Upload your vibration data file (.csv or .xlsx)", type=["csv", "xlsx"])

if uploaded_file:
    try:
        # Determine file type
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Standard column names assumption
        expected_cols = ['t', 'x', 'y', 'z', 'motor_state']
        df.columns = [col.strip().lower() for col in df.columns]

        if not all(col in df.columns for col in ['t', 'x', 'y', 'z', 'motor_state']):
            st.error("Missing required columns. Required columns: t, x, y, z, motor_state.")
        else:
            # Filter only when motor is ON
            df_on = df[df['motor_state'] == 3].copy()

            if df_on.empty:
                st.warning("No valid vibration data while motor state is 3 (ON). Please check your input.")
            else:
                # Calculate thresholds
                thresholds = {}
                for axis in ['x', 'y', 'z']:
                    thresholds[axis] = {
                        'warning': df_on[axis].quantile(0.90),
                        'error': df_on[axis].quantile(0.95)
                    }

                # Display thresholds
                st.subheader("📊 Calculated Thresholds (Motor ON)")
                for axis in ['x', 'y', 'z']:
                    st.metric(label=f"{axis.upper()} Axis - 90% Warning", value=f"{thresholds[axis]['warning']:.4f}")
                    st.metric(label=f"{axis.upper()} Axis - 95% Error", value=f"{thresholds[axis]['error']:.4f}")

                # Plots
                st.subheader("📉 Vibration Data while Motor ON")
                fig = px.line(df_on, x='t', y=['x', 'y', 'z'], labels={'value': 'Vibration', 't': 'Timestamp'})
                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Error loading file: {e}")
else:
    st.info("📂 Please upload a .csv or .xlsx file to begin.")
