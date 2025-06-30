#!/usr/bin/env python3
"""
Demo User Creation Script for LinguaLearn
This script creates demo accounts for visitors to try the app.
"""

import os
from dotenv import load_dotenv
from database import db

# Load environment variables
load_dotenv()

def create_demo_users():
    """Create demo users with sample data"""
    print("🎭 Creating demo users for LinguaLearn...")
    
    # Initialize database
    db.init_database()
    
    # Demo user credentials
    demo_users = [
        {
            'username': 'demo',
            'email': 'demo@lingualearn.com',
            'password': 'demo123'
        },
        {
            'username': 'visitor',
            'email': 'visitor@lingualearn.com', 
            'password': 'visitor123'
        }
    ]
    
    created_users = []
    
    for user_data in demo_users:
        try:
            user_id = db.create_user(
                user_data['username'], 
                user_data['email'], 
                user_data['password']
            )
            
            if user_id:
                created_users.append(user_data)
                print(f"✅ Created demo user: {user_data['username']} / {user_data['password']}")
                
                # Add some sample languages and vocabulary
                add_sample_data(user_id)
            else:
                print(f"⚠️ User {user_data['username']} already exists")
                
        except Exception as e:
            print(f"❌ Error creating user {user_data['username']}: {e}")
    
    print(f"\n🎉 Demo setup complete! Created {len(created_users)} demo users.")
    print("\n📝 Demo Credentials:")
    for user in created_users:
        print(f"  - Username: {user['username']} | Password: {user['password']}")
    
    print("\n🚀 Start the app with: python app.py")
    print("🌐 Visit: http://localhost:5000")

def add_sample_data(user_id):
    """Add sample languages and vocabulary for demo users"""
    try:
        # Add Spanish and French to the user's languages
        spanish_id = 1  # Spanish is typically ID 1
        french_id = 2   # French is typically ID 2
        
        db.add_user_language(user_id, spanish_id)
        db.add_user_language(user_id, french_id)
        
        # Add some sample vocabulary
        sample_vocab = [
            # Spanish vocabulary
            (spanish_id, 'hola', 'hello'),
            (spanish_id, 'gracias', 'thank you'),
            (spanish_id, 'por favor', 'please'),
            (spanish_id, 'adiós', 'goodbye'),
            (spanish_id, 'sí', 'yes'),
            (spanish_id, 'no', 'no'),
            (spanish_id, 'agua', 'water'),
            (spanish_id, 'pan', 'bread'),
            (spanish_id, 'casa', 'house'),
            (spanish_id, 'perro', 'dog'),
            
            # French vocabulary
            (french_id, 'bonjour', 'hello'),
            (french_id, 'merci', 'thank you'),
            (french_id, 's\'il vous plaît', 'please'),
            (french_id, 'au revoir', 'goodbye'),
            (french_id, 'oui', 'yes'),
            (french_id, 'non', 'no'),
            (french_id, 'eau', 'water'),
            (french_id, 'pain', 'bread'),
            (french_id, 'maison', 'house'),
            (french_id, 'chien', 'dog'),
        ]
        
        for lang_id, word, translation in sample_vocab:
            db.add_vocabulary(user_id, lang_id, word, translation)
        
        print(f"  📚 Added sample vocabulary for user {user_id}")
        
    except Exception as e:
        print(f"  ⚠️ Could not add sample data: {e}")

if __name__ == '__main__':
    create_demo_users() 