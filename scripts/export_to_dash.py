# scripts/export_to_dash.py
"""
Export Kuramoto simulation results to a format optimized for the Kuramoto Dash App.

Converts .npz datasets into high-speed JSON or CSV formats, including
pre-computed macroscopic metrics (order parameter).

Author: Eigenscribe & Junie
Date: 10-2026
"""

import json
import os
import argparse
import numpy as np
import pandas as pd
from typing import Any, Dict

def export_to_dash(input_path: str, output_path: str, format: str = "json"):
    """
    Load a Kuramoto dataset and export it for Dash integration.
    """
    if not os.path.exists(input_path):
        print(f"❌ Input file not found: {input_path}")
        return

    print(f"🚀 Loading dataset from {input_path}...")
    data = np.load(input_path)
    
    phases = data['theta']
    times = data['time']
    N = phases.shape[1]
    
    # Compute macroscopic order parameter R(t)
    # R(t) = |1/N * sum(exp(i*theta))|
    v_mean = np.mean(np.exp(1j * phases), axis=1)
    R = np.abs(v_mean)
    
    # Create DataFrame for structured export
    df = pd.DataFrame(phases, columns=[f"node_{i}" for i in range(N)])
    df.insert(0, 'time', times)
    df['order_parameter'] = R
    
    # Handle metadata
    metadata = {
        "n_oscillators": int(N),
        "coupling": float(data.get('coupling', 0.0)),
        "noise_std": float(data.get('noise_std', 0.0)),
        "solver": str(data.get('solver', 'unknown'))
    }

    if format.lower() == "json":
        # We use 'split' orientation to keep time/columns/data separate and efficient
        result = {
            "metadata": metadata,
            "data": df.to_dict(orient='split')
        }
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
    else:
        # CSV is simpler but loses metadata
        df.to_csv(output_path, index=False)
        print(f"⚠️ Metadata not included in CSV export.")

    print(f"✅ Successfully exported to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Export Kuramoto data to Dash App")
    parser.add_argument("-i", "--input", required=True, help="Input .npz file")
    parser.add_argument("-o", "--output", required=True, help="Output file path")
    parser.add_argument("-f", "--format", default="json", choices=["json", "csv"], help="Export format")
    
    args = parser.parse_args()
    export_to_dash(args.input, args.output, args.format)

if __name__ == "__main__":
    main()
