#!/usr/bin/env python3
"""
Database initialization script for Subtext app.

Creates all database tables based on SQLAlchemy models.
Run this once when setting up the application.

Usage:
    python scripts/init_db.py
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from subtext.db import init_db, engine
from sqlalchemy import text


def main():
    """Initialize the database"""
    print("🚀 Initializing Subtext database...")
    print(f"📍 Database URL: {engine.url}")

    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        print("✅ Database connection successful")

        # Create tables
        init_db()
        print("✅ Database initialized successfully!")
        print("\n📋 Tables created:")
        print("   - users")
        print("   - players")
        print("   - interactions")
        print("   - power_relationships")
        print("   - decoded_messages")
        print("\n🎯 Next step: Run 'python scripts/seed_data.py' to add demo data")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
