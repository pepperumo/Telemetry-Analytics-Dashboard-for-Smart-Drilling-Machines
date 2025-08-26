#!/usr/bin/env python3
"""
Test script to verify data loading
"""

import sys
from pathlib import Path

# Add the current directory to Python path so we can import our modules
sys.path.append(str(Path(__file__).parent))

from app.services.data_processor import DataProcessor

def test_data_loading():
    print("Testing data processor...")
    
    # Initialize processor
    processor = DataProcessor()
    
    print(f"Data directory: {processor.data_dir}")
    print(f"Data directory exists: {processor.data_dir.exists()}")
    
    # List files in data directory
    if processor.data_dir.exists():
        files = list(processor.data_dir.glob("*.csv"))
        print(f"CSV files found: {[f.name for f in files]}")
    
    # Try to load data
    try:
        processor.load_data()
        print("✅ Data loaded successfully!")
        
        # Print some basic info
        if processor.telemetry_df is not None:
            print(f"   Telemetry rows: {len(processor.telemetry_df)}")
        if processor.sessions_df is not None:
            print(f"   Sessions: {len(processor.sessions_df)}")
        if processor.raw_df is not None:
            print(f"   Raw data rows: {len(processor.raw_df)}")
            
    except Exception as e:
        print(f"❌ Error loading data: {e}")

if __name__ == "__main__":
    test_data_loading()