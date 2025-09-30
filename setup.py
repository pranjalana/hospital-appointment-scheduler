#!/usr/bin/env python3
"""
Setup script for Hospital Appointment Scheduler
"""

import os
import sys
from datetime import datetime

def setup_environment():
    """Setup the application environment"""
    print("🚀 Setting up Hospital Appointment Scheduler...")
    
    # Create necessary directories
    directories = ['database', 'logs', 'reports']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}/")
    
    # Initialize database
    try:
        from config.database_config import DatabaseConfig
        db_config = DatabaseConfig()
        db_config.initialize_database()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    
    # Load sample data option
    load_sample = input("\nLoad sample data? (y/n): ").strip().lower()
    if load_sample == 'y':
        try:
            from database.sample_data import load_sample_data
            load_sample_data()
            print("✅ Sample data loaded successfully!")
        except Exception as e:
            print(f"❌ Failed to load sample data: {e}")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📖 Quick Start Guide:")
    print("  1. Run: python main.py")
    print("  2. Use menu option 11 to load sample data (if not done during setup)")
    print("  3. Start booking appointments!")
    
    return True

if __name__ == '__main__':
    try:
        success = setup_environment()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)
