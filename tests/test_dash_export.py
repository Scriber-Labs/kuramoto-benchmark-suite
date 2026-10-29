# tests/test_dash_export.py
"""
Tests for the dash_export module.

Validates:
- Mean field phase ψ(t) range and edge cases.
- Frequency locking fraction range and edge cases.
- Export JSON structure and backward compatibility.
- Metadata completeness.
"""

from __future__ import annotations

import json
import os
import tempfile

import numpy as np
import pandas as pd
import pytest

from kuramoto.api import generate_kuramoto_dataset
from kuramoto.dash_export import (
    compute_locking_fraction,
    compute_mean_field_phase,
    export_for_dash,
)


class TestMeanFieldPhase:
    """Tests for compute_mean_field_phase()."""

    def test_output_shape(self) -> None:
        """ψ(t) should have shape (T,) for input (T, N)."""
        theta = np.random.rand(50, 10)
        psi = compute_mean_field_phase(theta)
        assert psi.shape == (50,)

    def test_range(self) -> None:
        """ψ(t) values should be in [-π, π]."""
        theta = np.random.rand(100, 20) * 2 * np.pi
        psi = compute_mean_field_phase(theta)
        assert np.all((psi >= -np.pi) & (psi <= np.pi))

    def test_perfectly_synchronized(self) -> None:
        """All phases equal → ψ(t) = 0 (or the common phase)."""
        theta = np.ones((50, 10)) * 0.5
        psi = compute_mean_field_phase(theta)
        assert np.allclose(psi, 0.5)

    def test_zero_phases(self) -> None:
        """All phases at 0 → ψ(t) = 0."""
        theta = np.zeros((30, 5))
        psi = compute_mean_field_phase(theta)
        assert np.allclose(psi, 0.0)

    def test_invalid_input(self) -> None:
        """1D input should raise ValueError."""
        theta = np.array([0.0, 0.1, 0.2])
        with pytest.raises(ValueError, match="2D"):
            compute_mean_field_phase(theta)


class TestLockingFraction:
    """Tests for compute_locking_fraction()."""

    def test_output_shape(self) -> None:
        """Locking fraction should have shape (T,)."""
        time = np.linspace(0, 10, 100)
        theta = np.random.rand(100, 20)
        locking = compute_locking_fraction(theta, time)
        assert locking.shape == (100,)

    def test_range(self) -> None:
        """Locking fraction values should be in [0, 1]."""
        time = np.linspace(0, 10, 100)
        theta = np.random.rand(100, 20)
        locking = compute_locking_fraction(theta, time)
        assert np.all((locking >= 0.0) & (locking <= 1.0))

    def test_perfectly_synchronized(self) -> None:
        """Identical frequencies → locking fraction = 1.0 after warmup."""
        # All oscillators have the same phase trajectory → identical frequencies
        time = np.linspace(0, 10, 100)
        theta = np.tile(time, (20, 1)).T  # shape (100, 20), all identical
        locking = compute_locking_fraction(theta, time, threshold=0.1, window=10)
        # After the warmup window, all should be locked
        assert locking[-1] == 1.0

    def test_single_oscillator(self) -> None:
        """Single oscillator (N=1) → locking fraction = 1.0 everywhere."""
        time = np.linspace(0, 10, 50)
        theta = np.column_stack([time])  # shape (50, 1)
        locking = compute_locking_fraction(theta, time)
        assert np.allclose(locking, 1.0)

    def test_no_coupling_random_phases(self) -> None:
        """Random phases with no coupling → low locking fraction."""
        time = np.linspace(0, 10, 100)
        rng = np.random.default_rng(42)
        theta = rng.uniform(0, 2 * np.pi, (100, 20))
        locking = compute_locking_fraction(theta, time, threshold=0.1, window=10)
        # Random phases should have very low locking fraction
        assert np.mean(locking) < 0.5

    def test_invalid_input(self) -> None:
        """1D theta should raise ValueError."""
        time = np.linspace(0, 10, 50)
        theta = np.array([0.0, 0.1, 0.2])
        with pytest.raises(ValueError, match="2D"):
            compute_locking_fraction(theta, time)


class TestExportForDash:
    """Tests for export_for_dash()."""

    def _make_dataset(self) -> dict:
        """Create a small test dataset."""
        return generate_kuramoto_dataset(
            n_oscillators=10,
            natural_frequencies=np.ones(10),
            coupling=1.5,
            timesteps=50,
            dt=0.02,
            seed=42,
        )

    def test_json_structure(self) -> None:
        """Export should produce valid JSON with metadata and data keys."""
        dataset = self._make_dataset()
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            tmp_path = f.name

        try:
            export_for_dash(dataset, tmp_path)
            with open(tmp_path, "r") as f:
                exported = json.load(f)

            assert "metadata" in exported
            assert "data" in exported
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_metadata_completeness(self) -> None:
        """Metadata should contain all expected fields."""
        dataset = self._make_dataset()
        dataset["solver"] = "rk45"
        dataset["dt"] = 0.02
        dataset["topology_type"] = "complete"

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            tmp_path = f.name

        try:
            export_for_dash(dataset, tmp_path)
            with open(tmp_path, "r") as f:
                exported = json.load(f)

            metadata = exported["metadata"]
            expected_keys = [
                "n_oscillators",
                "timesteps",
                "coupling",
                "noise_std",
                "solver",
                "dt",
                "topology_type",
                "topology_stats",
                "solver_params",
            ]
            for key in expected_keys:
                assert key in metadata, f"Missing metadata key: {key}"
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_backward_compatibility(self) -> None:
        """Data should be loadable by pd.read_json(orient='split')."""
        dataset = self._make_dataset()
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            tmp_path = f.name

        try:
            export_for_dash(dataset, tmp_path)
            with open(tmp_path, "r") as f:
                exported = json.load(f)

            # Reconstruct DataFrame from split format
            df = pd.DataFrame(
                exported["data"]["data"], columns=exported["data"]["columns"]
            )

            assert "time" in df.columns
            assert "order_parameter" in df.columns
            assert "mean_field_phase" in df.columns
            assert "locking_fraction" in df.columns
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_data_columns(self) -> None:
        """Data should include node columns plus metrics."""
        dataset = self._make_dataset()
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            tmp_path = f.name

        try:
            export_for_dash(dataset, tmp_path)
            with open(tmp_path, "r") as f:
                exported = json.load(f)

            columns = exported["data"]["columns"]
            assert "time" in columns
            assert "node_0" in columns
            assert "node_9" in columns
            assert "order_parameter" in columns
            assert "mean_field_phase" in columns
            assert "locking_fraction" in columns
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_topology_stats(self) -> None:
        """Topology stats should be computed from adjacency matrix."""
        dataset = self._make_dataset()
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            tmp_path = f.name

        try:
            export_for_dash(dataset, tmp_path)
            with open(tmp_path, "r") as f:
                exported = json.load(f)

            stats = exported["metadata"]["topology_stats"]
            assert "num_nodes" in stats
            assert "num_edges" in stats
            assert stats["num_nodes"] == 10
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_include_locking_false(self) -> None:
        """When include_locking=False, locking_fraction should be all zeros."""
        dataset = self._make_dataset()
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            tmp_path = f.name

        try:
            export_for_dash(dataset, tmp_path, include_locking=False)
            with open(tmp_path, "r") as f:
                exported = json.load(f)

            df = pd.DataFrame(
                exported["data"]["data"], columns=exported["data"]["columns"]
            )
            assert np.allclose(df["locking_fraction"], 0.0)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
