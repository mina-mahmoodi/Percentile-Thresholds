import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

st.set_page_config(page_title="Vibration Threshold Calculator", layout="wide")
st.title("📈 Vibration Warning & Error Threshold Calculator")

uploaded_file = st.file_uploader("Upload the Excel file with vibration and motor state data", type=["xlsx"])

if uploaded_file:
    workbook = pd.ExcelFile(uploaded_file)
    sheet_names = workbook.sheet_names

    results = []

    for sheet in sheet_names:
        df = pd.read_excel(workbook, sheet_name=sheet)

        # Check if necessary columns exist
        required_cols = ['X T', 'Y T', 'Z T', 'T', 'Motor State']
        if not all(col in df.columns for col in required_cols):
            st.warning(f"Sheet '{sheet}' skipped — missing required columns.")
            continue

        # Rename to avoid confusion
        df = df.rename(columns={'T': 'vib_time'})
        # Motor state timestamps assumed to be in the last column named also 'T' - handle if needed
        motor_time_col = [col for col in df.columns if col == 'T']
        if len(motor_time_col) > 1:
            df['motor_time'] = df[motor_time_col[-1]]
        else:
            df['motor_time'] = df['vib_time']

        df['vib_date'] = pd.to_datetime(df['vib_time']).dt.date
        df['motor_date'] = pd.to_datetime(df['motor_time']).dt.date

        # Get dates when motor was 0 or 1
        excluded_dates = df[df['Motor State'].isin([0, 1])]['motor_date'].unique()

        # Filter vibration data
        valid_data = df[~df['vib_date'].isin(excluded_dates)]
        valid_data = valid_data[['X T', 'Y T', 'Z T']].dropna()

        # Calculate percentiles
        thresholds = {
            'Sheet': sheet,
            'X Warning (85%)': np.percentile(valid_data['X T'], 85),
            'X Error (95%)': np.percentile(valid_data['X T'], 95),
            'Y Warning (85%)': np.percentile(valid_data['Y T'], 85),
            'Y Error (95%)': np.percentile(valid_data['Y T'], 95),
            'Z Warning (85%)': np.percentile(valid_data['Z T'], 85),
            'Z Error (95%)': np.percentile(valid_data['Z T'], 95),
        }

        results.append(thresholds)

    # Display results
    if results:
        result_df = pd.DataFrame(results)
        st.success("✅ Thresholds calculated successfully!")
        st.dataframe(result_df.style.format(precision=2), use_container_width=True)
    else:
        st.warning("No valid sheets processed.")
