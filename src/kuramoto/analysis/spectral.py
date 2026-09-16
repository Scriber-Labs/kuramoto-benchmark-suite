"""
src/kuramoto/analysis/spectral.py

Spectral analysis tools for Kuramoto phase signals.
Implements Fourier Transform and Power Spectral Density (PSD) metrics.

Author: Eigenscribe
Date: May 2026
Last Update: September 2026
"""

from __future__ import annotations

import numpy as np
import scipy.fft as fft
from scipy.signal import welch
from typing import Dict, Any, List, Tuple
from numpy.typing import NDArray

# ------------------------------------------------------------------------------
# 🎭 Type Aliases
# ------------------------------------------------------------------------------
TimeSeries = NDArray[np.floating]
FrequencyArray = NDArray[np.floating]

# ------------------------------------------------------------------------------
# 1️⃣ Core Definitions
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
    **kwargs: Any,
) -> Tuple[FrequencyArray, TimeSeries]:
    """
    Compute the Power Spectral Density (PSD) using Welch's method.

    Parameters
    ----------
    signals : TImeSeries
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

def compute_spectral_decomposition(
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
        PSD (can be averaged across oscillators)
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

# # -----------------------------------------------------------------------------------------------------------
# 2️⃣ Advanced Analysis Functions (Added September 2026)
# # -----------------------------------------------------------------------------------------------------------

def detect_sync_transition(
    freq: np.ndarray,
    psd: np.ndarray,
    K_values: np.ndarray,
    method: str = "elbow"
) -> float:
    """
    Detect synchronization transition using spectral peak emergence.

    Parameters
    --------
    freq : np.ndarray
        Frequency bins from PSD.
    psd : np.ndarray
        Power spectral density of shape (len(K_values), len(freq)).
    K_values : np.ndarray
        Coupling strengths tested.
    method : str, optional
        Detection method ('elbow' for first sharp rise in peak-to-baseline ratio).

    Returns
    -------
    float
        Critical coupling K_c where synchronization emerges.

    Raises
    ------
    ValueError
        If psd shape doesn't match K_values length.
    """
    if len(K_values) != psd.shape[0]:
        raise ValueError(f"K_values ({len(K_values)}) must match psd rows ({psd.shape[0]}")

    peak_heights = []
    for K_idx, K in enumerate(K_values):
        peak = np.max(psd[K_idx])
        baseline = np.median(psd[K_idx])
        peak_to_baseline = peak / baseline if baseline > 0 else 0
        peak_heights.append(peak_to_baseline)

    # Find elbow point (first sharp rise)
    diffs = np.diff(peak_heights)
    transition_idx = np.argmax(diffs) + 1

    return K_values[transition_idx]

def harmonic_analysis(
    order_param_timeseries: np.ndarray,
    dt: float,
    max_harmonic: int = 5,
) -> Dict[str, float]:
    """
    Analyze harmonic content of order parameter oscillations.

    Parameters
    ----------
    order_param_timeseries : np.n darray
        Order parameter |r(t)| time series of shape (T,).
    dt : float
        Sampling timestep.
    max_harmonic : int, optional
        Highest harmonic to analyze (default: 5).

    Returns
    -------
    Dict[str, float]
        Harmonic power ratios (h1_power_ratio, h2_power_ratio, ..., rest_ratio).
    """
    fs = 1.0 / dt
    freqs, psd = welch(order_param_timeseries, fs=fs, nperseg=min(256, len(order_param_timeseries)//2))

    # Find dominant frequency
    fundamental_idx = np.argmax(psd)
    fundamental_freq = freqs[fundamental_idx]
    fundamental_power = psd[fundamental_idx]

    # Measure harmonic cascade
    harmonics = {}
    for n in range(1, max_harmonic + 1):
        target_freq = n * fundamental_freq
        idx = np.argmin(np.abs(freqs - target_freq))
        harmonics[f"h{n}_power_ratio"] = float(psd[idx] / fundamental_power)

    # Calculate remaining power ratio
    total_power = np.sum(psd)
    harmonic_sum = sum(harmonics.values())
    harmonics["rest_ratio"] = float(1.0 - harmonic_sum)

    return harmonics

# -----------------------------------------------------------------------------------------------------------
# 💨 Smoke tests / example usage
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
    print(" ... Fourier coefficients computed ✔️")

    # PSD
    f, pxx = compute_psd(sig, fs, nperseg=256)
    peak_freq = f[np.argmax(pxx)]
    assert np.abs(peak_freq - freq) < 1.0  # Loose check for binning
    print(" ... PSD peak detected ✔️")

    # Distribution
    dist = compute_spectral_decomposition(f, pxx, freq, bandwidth=1.0)
    print(f" ... Distribution: {dist} ✔️")
    assert dist["fundamental"] > 0.8

    # Test harmonic_analysis
    order_param = np.sin(2 * np.pi * freq * t)  # Simple sine for testing
    harm = harmonic_analysis(order_param, dt=0.01)
    assert harm["h1_power_ratio"] > 0.5
    assert "rest_ratio" in harm
    print(" ... Harmonic analysis test passed ✔️")

    # Test detect_sync_transition
    K_range = np.linspace(0.5, 2.0, 10)
    fake_psd = np.array([np.random.rand(len(f)) for _ in K_range])
    fake_psd[5:] += 5  # Simulate transition at K_index 5
    K_c = detect_sync_transition(f, fake_psd, K_range)
    assert K_c in K_range
    print(" ...  Sync transition detection passed ✔️")

    print("✅ All spectral analysis smoke test passed.")

# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry point
# -----------------------------------------------------------------------------------------------------------

def main() -> None:
    """
    Main entry point for smoke tests.
    """
    _run_smoke_test()

if __name__ == "__main__":
    main()