#!/usr/bin/env python3
"""
Database reset script - DROP ALL TABLES and recreate them.

⚠️  WARNING: This will delete ALL data in the database!
Only use this in development/testing environments.

Usage:
    python scripts/reset_db.py
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from subtext.db import reset_db, engine


def main():
    """Reset the database"""
    print("⚠️  WARNING: This will DELETE ALL DATA in the database!")
    print(f"📍 Database URL: {engine.url}")

    confirm = input("\nAre you sure you want to continue? Type 'yes' to confirm: ")

    if confirm.lower() != 'yes':
        print("❌ Aborted")
        sys.exit(0)

    try:
        print("\n🔥 Dropping all tables...")
        reset_db()
        print("✅ Database reset successfully!")
        print("\n🎯 Next step: Run 'python scripts/seed_data.py' to add demo data")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
