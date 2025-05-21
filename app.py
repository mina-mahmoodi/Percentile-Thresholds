import streamlit as st
import pandas as pd
import plotly.express as px

# Page setup
st.set_page_config(page_title="Vibration Threshold Calculator", layout="wide")
st.title("📈 Vibration Warning & Error Threshold Calculator")

# Upload
uploaded_file = st.file_uploader("Upload your vibration data (.csv or .xlsx)", type=["csv", "xlsx"])

if uploaded_file:
    try:
        # Load file
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Expected column names (case-sensitive)
        expected_columns = ['X', 'Y', 'Z', 'T(X)', 'T(Y)', 'T(Z)', 'T(Motor State)', 'Motor State']
        missing_cols = [col for col in expected_columns if col not in df.columns]

        if missing_cols:
            st.error(f"Missing required columns: {missing_cols}")
        else:
            # Rename columns for processing
            df_processed = pd.DataFrame({
                't': df['T(Motor State)'],
                'x': df['X'],
                'y': df['Y'],
                'z': df['Z'],
                'motor_state': df['Motor State']
            })

            # Drop rows with missing values
            df_processed.dropna(subset=['t', 'x', 'y', 'z', 'motor_state'], inplace=True)

            # Filter for motor ON
            df_on = df_processed[df_processed['motor_state'] == 3].copy()

            if df_on.empty:
                st.warning("No vibration data where motor state is 3 (ON).")
            else:
                # Calculate thresholds
                thresholds = {
                    axis: {
                        'warning': df_on[axis].quantile(0.90),
                        'error': df_on[axis].quantile(0.95)
                    } for axis in ['x', 'y', 'z']
                }

                st.subheader("📊 Calculated Thresholds (Motor ON)")
                for axis in ['x', 'y', 'z']:
                    st.metric(f"{axis.upper()} Axis - 90% Warning", f"{thresholds[axis]['warning']:.4f}")
                    st.metric(f"{axis.upper()} Axis - 95% Error", f"{thresholds[axis]['error']:.4f}")

                # Plot
                st.subheader("📉 Vibration While Motor ON")
                fig = px.line(df_on, x='t', y=['x', 'y', 'z'], labels={'value': 'Vibration', 't': 'Timestamp'})
                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
else:
    st.info("📂 Upload a CSV or Excel file to start.")
