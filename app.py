import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Vibration Threshold Calculator", layout="wide")
st.title("📈 Vibration Warning & Error Threshold Calculator")

# Upload CSV file
uploaded_file = st.file_uploader("Upload vibration data CSV", type=['csv'])

if uploaded_file is not None:
    # Load data
    df = pd.read_csv(uploaded_file, parse_dates=['timestamp'])

    st.write("Raw data sample:")
    st.dataframe(df.head())

    # Check necessary columns
    required_cols = ['timestamp', 'motor_state', 'vibration_x', 'vibration_y', 'vibration_z']
    if not all(col in df.columns for col in required_cols):
        st.error(f"CSV must contain columns: {required_cols}")
    else:
        # Step 1: Calculate baseline vibration ranges (motor state 0 or 1)
        baseline_df = df[df['motor_state'].isin([0, 1])]
        if baseline_df.empty:
            st.warning("No motor state 0 or 1 data found for baseline calculation.")
        else:
            baseline_ranges = {
                'x_min': baseline_df['vibration_x'].min(),
                'x_max': baseline_df['vibration_x'].max(),
                'y_min': baseline_df['vibration_y'].min(),
                'y_max': baseline_df['vibration_y'].max(),
                'z_min': baseline_df['vibration_z'].min(),
                'z_max': baseline_df['vibration_z'].max(),
            }
            st.write("Baseline vibration ranges (motor state 0 or 1):")
            st.json(baseline_ranges)

            # Step 2: Filter motor state 3 data only
            motor_on_df = df[df['motor_state'] == 3]
            if motor_on_df.empty:
                st.warning("No motor state 3 data found.")
            else:
                # Step 3: Exclude data within baseline range
                filtered_df = motor_on_df[
                    (motor_on_df['vibration_x'] < baseline_ranges['x_min']) | (motor_on_df['vibration_x'] > baseline_ranges['x_max']) |
                    (motor_on_df['vibration_y'] < baseline_ranges['y_min']) | (motor_on_df['vibration_y'] > baseline_ranges['y_max']) |
                    (motor_on_df['vibration_z'] < baseline_ranges['z_min']) | (motor_on_df['vibration_z'] > baseline_ranges['z_max'])
                ]

                st.write(f"Filtered motor ON data count: {len(filtered_df)}")
                st.dataframe(filtered_df.head())

                # Step 4: Show some statistics
                stats = {
                    'mean_x': filtered_df['vibration_x'].mean(),
                    'mean_y': filtered_df['vibration_y'].mean(),
                    'mean_z': filtered_df['vibration_z'].mean(),
                    'count': len(filtered_df),
                }
                st.write("Statistics for filtered vibration data (motor ON outside baseline):")
                st.json(stats)

                # Plot vibration_x over time (filtered)
                st.subheader("Vibration X over Time (Filtered)")
                fig, ax = plt.subplots()
                ax.plot(filtered_df['timestamp'], filtered_df['vibration_x'], label='Vibration X')
                ax.set_xlabel("Timestamp")
                ax.set_ylabel("Vibration X")
                ax.legend()
                plt.xticks(rotation=45)
                st.pyplot(fig)

                # You can similarly add plots for vibration_y, vibration_z or combined plots
