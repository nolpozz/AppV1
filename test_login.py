#!/usr/bin/env python3
"""
Test script to check login functionality
"""

import os
from dotenv import load_dotenv
from database import db

# Load environment variables
load_dotenv()

def print_all_users():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, email, created_at FROM users')
    users = cursor.fetchall()
    print("\n👥 All users in the database:")
    for user in users:
        print(f"  - ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Created: {user[3]}")
    conn.close()

def test_database():
    """Test database connection and user creation"""
    print("🔍 Testing database functionality...")
    
    # Initialize database
    db.init_database()
    
    # Check if users exist
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    print(f"📊 Total users in database: {user_count}")
    
    if user_count > 0:
        cursor.execute('SELECT id, username, email FROM users')
        users = cursor.fetchall()
        print("👥 Existing users:")
        for user in users:
            print(f"  - ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
    
    conn.close()
    
    # Try to create dev user
    print("\n🔧 Creating dev user...")
    try:
        user_id = db.create_user('dev', 'dev@example.com', 'password123')
        if user_id:
            print(f"✅ Dev user created with ID: {user_id}")
        else:
            print("❌ Failed to create dev user")
    except Exception as e:
        print(f"❌ Error creating dev user: {e}")
    
    # Test authentication
    print("\n🔐 Testing authentication...")
    user_data = db.authenticate_user('dev', 'password123')
    if user_data:
        print(f"✅ Authentication successful for dev user: {user_data}")
    else:
        print("❌ Authentication failed for dev user")
    
    # Test with wrong password
    user_data = db.authenticate_user('dev', 'wrongpassword')
    if user_data:
        print("❌ Authentication should have failed with wrong password")
    else:
        print("✅ Authentication correctly failed with wrong password")

if __name__ == '__main__':
    test_database()
    print_all_users() 