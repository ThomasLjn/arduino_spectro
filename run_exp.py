"""
Python script connected to the Arduino code in order to do do time-resolved 
Code by Thomas Lejeune 
"""

import os
import serial
import time
import numpy as np
import pandas as pd

# Serial port configuration
PORT = "COM6"  # Serial port for Arduino connection (update with correct port)

# Measurement parameters
NUM_BASELINE = 20  # Number of baseline measurements (I0)
NUM_MEASUREMENTS = 5  # Number of measurements for averaging
IRRADIATION_TIME = 30  # Irradiation time (s))
STABILIZATION_TIME = 0.1  # Stabilization time between operations (s)
MEASUREMENT_INTERVAL = 0.1  # Sleep time between measurements (s)


def r_on(arduino):
    """Turn on Red LED."""
    arduino.write(str.encode("0"))


def r_off(arduino):
    """Turn off Red LED."""
    arduino.write(str.encode("1"))


def g_on(arduino):
    """Turn on Green LED."""
    arduino.write(str.encode("2"))


def g_off(arduino):
    """Turn off Green LED."""
    arduino.write(str.encode("3"))


def b_on(arduino):
    """Turn on Blue LED."""
    arduino.write(str.encode("4"))


def b_off(arduino):
    """Turn off Blue LED."""
    arduino.write(str.encode("5"))


def uv_on(arduino):
    """Turn on UV LED."""
    arduino.write(str.encode("6"))


def uv_off(arduino):
    """Turn off UV LED."""
    arduino.write(str.encode("7"))


def read_intensity(arduino):
    """
    Read intensity from the sensor.
    Returns:
        float: Intensity value.
    """
    arduino.write(str.encode("8"))
    intensity_str = str(arduino.readline())
    return float(intensity_str[2:-5])


def read_temperature(arduino):
    """
    Read temperature from the sensor.
    Returns:
        str: Temperature reading.
    """
    arduino.reset_output_buffer()
    arduino.write(str.encode("9"))
    return str(arduino.readline())


def measure_average_intensity(arduino):
    """
    Measure average intensity over multiple readings.
    Returns:
        float: Mean intensity.
    """
    intensities = []
    for _ in range(NUM_MEASUREMENTS):
        intensities.append(read_intensity(arduino))
        time.sleep(MEASUREMENT_INTERVAL)
    return np.mean(intensities)


def perform_spectroscopy_measurement(path, measurement_time, arduino):
    """
    Perform spectroscopy measurement.

    Args:
        path (str): Output file path.
        measurement_time (float): Total measurement time.
        arduino (serial.Serial): Serial connection object.

    Returns:
        pandas.DataFrame: Measurement results.
    """
    # Baseline measurement (I0) before irradiation
    g_off(arduino)
    uv_off(arduino)

    # Measure baseline intensities
    baseline_measurements = np.zeros((NUM_BASELINE, 2))
    g_on(arduino)
    time.sleep(STABILIZATION_TIME)

    for i in range(NUM_BASELINE):
        baseline_measurements[i] = read_intensity(arduino)

    # Calculate baseline intensity and initial temperature
    baseline_intensity = np.mean(baseline_measurements)
    initial_temperature = read_temperature(arduino)

    g_off(arduino)
    time.sleep(STABILIZATION_TIME)

    # UV Irradiation sequence
    uv_on(arduino)
    time.sleep(IRRADIATION_TIME)
    uv_off(arduino)
    time.sleep(STABILIZATION_TIME)

    # Measurement with green LED
    g_on(arduino)
    time.sleep(STABILIZATION_TIME)

    current_intensity = measure_average_intensity(arduino)
    time.sleep(STABILIZATION_TIME)

    # Initialize results tracking
    start_time = time.time()
    results = {
        'I': [current_intensity],      # Current intensity
        'I0': [baseline_intensity],    # Baseline intensity
        't': [0],                      # Time point
        'T': [initial_temperature],    # Temperature
        'A': [np.log(baseline_intensity / current_intensity)]  # Absorbance
    }
    df = pd.DataFrame(results)

    arduino.reset_output_buffer()

    # Continuous measurement loop
    while time.time() - start_time < measurement_time:
        current_intensity = measure_average_intensity(arduino)
        new_row = {
            'I': current_intensity,
            'I0': baseline_intensity,
            't': time.time() - start_time,
            'T': initial_temperature,
            'A': np.log(baseline_intensity / current_intensity)
        }
        df.loc[len(df)] = new_row

    # Save results to Excel
    df.to_excel(path)
    g_off(arduino)
    return df


def main():
    """
    Main execution function for running multiple spectroscopy measurements.
    """
    # Ensure output directory exists
    os.makedirs('data', exist_ok=True)

    # Connect to Arduino
    arduino = serial.Serial(port=PORT, baudrate=9600)
    # Perform multiple consecutive measurements
    for i in range(10):
        output_file = f"data/experiment{i}.xlsx"
        perform_spectroscopy_measurement(
            path=output_file,
            measurement_time=1000,
            arduino=arduino
        )
    # Ensure Arduino connection is closed
    arduino.close()


if __name__ == "__main__":
    main()