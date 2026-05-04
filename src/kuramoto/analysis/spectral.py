"""
spectral.py

Spectral analysis tools for Kuramoto phase signals.
Implements Fourier Transform and Power Spectral Density (PSD) metrics.

Author: Eigenscribe
Date: May 2026
"""

from __future__ import annotations

import numpy as np
import scipy.fft as fft
from scipy.signal import welch
from typing import Dict, Any, List, Tuple
from numpy.typing import NDArray

# -----------------------------------------------------------------------------------------------------------
# 0️⃣ Type aliases
# -----------------------------------------------------------------------------------------------------------
TimeSeries = NDArray[np.floating]
FrequencyArray = NDArray[np.floating]

# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Core definitions
# -----------------------------------------------------------------------------------------------------------

def compute_fourier_coefficients(
    time: TimeSeries,
    signals: TimeSeries,
    target_freq: float
) -> NDArray[np.complexfloating]:
    """
    Compute the Fourier coefficient at a specific frequency for multiple signals.

    Parameters
    ----------
    time : TimeSeries
        Time vector of shape (T,).
    signals : TimeSeries
        Phase or order parameter signals of shape (T, N).
    target_freq : float
        The frequency at which to evaluate the Fourier coefficient.

    Returns
    -------
    NDArray[np.complexfloating]
        Fourier coefficients of shape (N,).
    """
    # Exponentials: exp(-2j * pi * f * t)
    dt = time[1] - time[0]
    kernel = np.exp(-2j * np.pi * target_freq * time)
    
    # Integration using trapezoidal rule (simplified to sum for uniform grid)
    coeffs = np.sum(signals * kernel[:, np.newaxis], axis=0) * dt / (time[-1] - time[0])
    return coeffs

def compute_psd(
    signals: TimeSeries,
    fs: float,
    **kwargs: Any
) -> Tuple[FrequencyArray, TimeSeries]:
    """
    Compute the Power Spectral Density (PSD) using Welch's method.

    Parameters
    ----------
    signals : TimeSeries
        Signals of shape (T, N).
    fs : float
        Sampling frequency.
    **kwargs : Any
        Additional arguments for scipy.signal.welch.

    Returns
    -------
    Tuple[FrequencyArray, TimeSeries]
        - Frequencies (F,)
        - Power spectral density (F, N)
    """
    # Remove mean (fluctuations only)
    fluctuations = signals - np.mean(signals, axis=0)
    
    f, pxx = welch(fluctuations, fs=fs, axis=0, **kwargs)
    return f, pxx

def compute_spectral_distribution(
    f: FrequencyArray,
    pxx: TimeSeries,
    target_freq: float,
    bandwidth: float = 0.1
) -> Dict[str, float]:
    """
    Calculate the energy distribution around a target frequency and its harmonics.

    Parameters
    ----------
    f : FrequencyArray
        Frequencies.
    pxx : TimeSeries
        PSD (can be averaged across oscillators).
    target_freq : float
        The base frequency of interest.
    bandwidth : float
        Bandwidth around frequencies to consider as "belonging" to that peak.

    Returns
    -------
    Dict[str, float]
        Proportions of energy in 'fundamental', 'harmonics', and 'rest'.
    """
    if pxx.ndim > 1:
        pxx = np.mean(pxx, axis=1)
        
    total_power = np.sum(pxx)
    
    def get_band_power(freq: float) -> float:
        mask = (f >= freq - bandwidth) & (f <= freq + bandwidth)
        return np.sum(pxx[mask])

    p1 = get_band_power(target_freq)
    p2 = get_band_power(2 * target_freq)
    p3 = get_band_power(3 * target_freq)
    
    harmonics_power = p2 + p3
    rest_power = total_power - p1 - harmonics_power
    
    return {
        "fundamental": p1 / total_power,
        "harmonics": harmonics_power / total_power,
        "rest": rest_power / total_power
    }

# -----------------------------------------------------------------------------------------------------------
# 4️⃣ Smoke tests / example usage
# -----------------------------------------------------------------------------------------------------------

def _run_smoke_test() -> None:
    """
    Sanity check for spectral tools.
    """
    print("💨 Running spectral analysis smoke tests...")
    
    t = np.linspace(0, 10, 1000)
    fs = 100.0
    freq = 5.0
    # Signal with 5Hz component
    sig = np.sin(2 * np.pi * freq * t)[:, np.newaxis]
    
    # Fourier
    coeffs = compute_fourier_coefficients(t, sig, freq)
    assert np.abs(coeffs[0]) > 0.4  # Ideal is 0.5 for real sine
    
    # PSD
    f, pxx = compute_psd(sig, fs, nperseg=256)
    peak_freq = f[np.argmax(pxx)]
    assert np.abs(peak_freq - freq) < 1.0  # Loose check for binning
    
    # Distribution
    dist = compute_spectral_distribution(f, pxx, freq, bandwidth=1.0)
    print(f"Distribution: {dist}")
    assert dist["fundamental"] > 0.8
    
    print("✅ Spectral analysis smoke tests passed.")

# -----------------------------------------------------------------------------------------------------------
# 5️⃣ Entry point
# -----------------------------------------------------------------------------------------------------------

def main() -> None:
    """
    Main entry point for smoke tests.
    """
    _run_smoke_test()

if __name__ == "__main__":
    main()
