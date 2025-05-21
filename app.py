import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Vibration Threshold Calculator", layout="wide")
st.title("📈 Vibration Warning & Error Threshold Calculator")

uploaded_file = st.file_uploader("Upload the Excel file with vibration and motor state data", type=["xlsx"])

if uploaded_file:
    workbook = pd.ExcelFile(uploaded_file)
    sheet_names = workbook.sheet_names
    results = []

    for sheet in sheet_names:
        df = pd.read_excel(workbook, sheet_name=sheet)

        # Check column count
        if df.shape[1] < 8:
            st.warning(f"Sheet '{sheet}' skipped — not enough columns.")
            continue

        try:
            # Extract correct columns
            x = df.iloc[:, 0]
            y = df.iloc[:, 2]
            z = df.iloc[:, 4]
            motor_time = pd.to_datetime(df.iloc[:, 6], errors='coerce')
            motor_state = df.iloc[:, 7]

            # Get bad dates (motor state 0 or 1)
            bad_dates = motor_time[motor_state.isin([0, 1])].dt.date.unique()

            # For vibration time, just take X's time (col B)
            vib_time = pd.to_datetime(df.iloc[:, 1], errors='coerce')
            vib_date = vib_time.dt.date

            # Filter valid rows
            valid_mask = ~vib_date.isin(bad_dates)
            x_valid = x[valid_mask].dropna()
            y_valid = y[valid_mask].dropna()
            z_valid = z[valid_mask].dropna()

            # Compute percentiles
            result = {
                "Sheet": sheet,
                "X Warning (85%)": np.percentile(x_valid, 85),
                "X Error (95%)": np.percentile(x_valid, 95),
                "Y Warning (85%)": np.percentile(y_valid, 85),
                "Y Error (95%)": np.percentile(y_valid, 95),
                "Z Warning (85%)": np.percentile(z_valid, 85),
                "Z Error (95%)": np.percentile(z_valid, 95),
            }

            results.append(result)

        except Exception as e:
            st.error(f"Error processing sheet '{sheet}': {e}")

    if results:
        st.success("✅ Thresholds calculated successfully!")
        result_df = pd.DataFrame(results)
        st.dataframe(result_df.style.format(precision=2), use_container_width=True)
    else:
        st.warning("⚠️ No valid data found in any sheet.")
