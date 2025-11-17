#!/usr/bin/env python3
"""
Test script to verify PostgreSQL database connection and table creation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.db import engine, Base
from sqlalchemy import text

def test_connection():
    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("Database connection successful!")

        # Create tables
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully!")

        # List tables
        with engine.connect() as conn:
            if 'postgresql' in str(engine.url):
                result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            else:
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = result.fetchall()
            print(f"Tables in database: {[table[0] for table in tables]}")

    except Exception as e:
        print(f"Error: {e}")
        return False

    return True

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)