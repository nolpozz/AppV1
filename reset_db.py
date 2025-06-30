#!/usr/bin/env python3
"""
Database reset script for LinguaLearn
Use this if you encounter database issues and want to start fresh
"""

import os
from database import DatabaseManager

def reset_database():
    """Reset the database by removing the file and reinitializing"""
    db_file = 'language_learning.db'
    
    if os.path.exists(db_file):
        print(f"Removing existing database: {db_file}")
        os.remove(db_file)
    
    print("Creating new database...")
    db = DatabaseManager()
    db.init_database()
    print("Database reset completed successfully!")

if __name__ == '__main__':
    confirm = input("This will delete all existing data. Are you sure? (y/N): ")
    if confirm.lower() == 'y':
        reset_database()
    else:
        print("Database reset cancelled.") 