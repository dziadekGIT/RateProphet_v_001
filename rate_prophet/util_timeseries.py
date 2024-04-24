import pandas as pd
import numpy as np


def create_timeseries(
    start_datetime: str,
    end_datetime: str,
    cycle_frequency: float = 2.0,
    freq: str = "h",
    amplitude: float = 1.0,
    mean: float = 3.0,
    std: float = 0.1,
    name: str = "XYZ/FKE",
) -> pd.Series:
    """
    Creates a cyclic time series with a specified frequency, distorted by normal noise.

    Parameters:
    - start_datetime: The start datetime for the time series (inclusive).
    - end_datetime: The end datetime for the time series (inclusive).
    - cycle_frequency: The frequency of the cycle in the sine wave (number of cycles per day).
    - freq: The frequency of the time series data points (default is daily 'D').
    - amplitude: The amplitude of the sine wave (default is 1.0).
    - mean: The mean value for the normal distribution noise (default is 0.0).
    - std: The standard deviation for the normal distribution noise (default is 0.1).
    - name: The name for the resulting Pandas Series (default is 'cyclic_ts').

    Returns:
    - A Pandas Series representing the cyclic time series.
    """
    # Generate the date range
    date_range = pd.date_range(start=start_datetime, end=end_datetime, freq=freq)

    # Calculate the sine wave with the specified cycle frequency
    sine_wave = amplitude * np.sin(
        2 * np.pi * cycle_frequency * np.arange(len(date_range)) / len(date_range)
    )

    # Add normal noise to the sine wave
    noisy_sine_wave = sine_wave + np.random.normal(
        loc=mean, scale=std, size=len(date_range)
    )

    # Create and return the Pandas Series
    timeseries = pd.Series(data=noisy_sine_wave, index=date_range, name=name).abs()

    return timeseries
