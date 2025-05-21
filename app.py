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
        # Detect file type and load data
        if uploaded_file.name.endswith(".csv"):
            sheets = {"Sheet1": pd.read_csv(uploaded_file)}
        else:
            xls = pd.ExcelFile(uploaded_file)
            sheets = {sheet_name: xls.parse(sheet_name) for sheet_name in xls.sheet_names}

        for sheet_name, df in sheets.items():
            st.header(f"📄 Sheet: {sheet_name}")

            expected_columns = ['X', 'Y', 'Z', 'T(X)', 'T(Y)', 'T(Z)', 'T(motor state)', 'Motor State']
            missing_cols = [col for col in expected_columns if col not in df.columns]

            if missing_cols:
                st.warning(f"Skipping sheet '{sheet_name}' due to missing columns: {missing_cols}")
                continue

            # Rename and select necessary columns
            df_processed = pd.DataFrame({
                't': df['T(motor state)'],
                'x': df['X'],
                'y': df['Y'],
                'z': df['Z'],
                'motor_state': df['Motor State']
            })

            df_processed.dropna(subset=['t', 'x', 'y', 'z', 'motor_state'], inplace=True)

            # Filter motor_state == 3 (motor ON)
            df_on = df_processed[df_processed['motor_state'] == 3].copy()

            if df_on.empty:
                st.warning("⚠️ No motor ON data in this sheet.")
                continue

            # Thresholds: 85th for warning, 95th for error
            thresholds = {
                axis: {
                    'warning': df_on[axis].quantile(0.85),
                    'error': df_on[axis].quantile(0.95)
                } for axis in ['x', 'y', 'z']
            }

            # Display metrics
            st.subheader("🎯 Thresholds (Motor ON)")
            for axis in ['x', 'y', 'z']:
                col1, col2 = st.columns(2)
                col1.metric(f"{axis.upper()} - 85% Warning", f"{thresholds[axis]['warning']:.4f}")
                col2.metric(f"{axis.upper()} - 95% Error", f"{thresholds[axis]['error']:.4f}")

            # Plot
            st.subheader("📉 Vibration Plot (Motor ON only)")
            fig = px.line(df_on, x='t', y=['x', 'y', 'z'], labels={'value': 'Vibration', 't': 'Timestamp'})
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.info("📂 Upload a CSV or Excel file to begin.")
