#!/usr/bin/env python3
"""
Development Setup Script for LinguaLearn
This script helps set up the development environment quickly.
"""

import os
import sys

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_content = """# Development Environment Variables
DEV_MODE=true
FLASK_ENV=development

# OpenAI API Key (replace with your actual key)
APIKEY=your_openai_api_key_here
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
    else:
        print("ℹ️  .env file already exists")

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask',
        'flask-login',
        'openai',
        'python-dotenv',
        'werkzeug'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages are installed")
        return True

def main():
    print("🚀 LinguaLearn Development Setup")
    print("=" * 40)
    
    # Create .env file
    create_env_file()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("\n📝 Next steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Run: python app.py")
    print("3. Open http://localhost:5000")
    print("4. Login with: dev / password123")
    
    print("\n🎉 Development environment is ready!")

if __name__ == '__main__':
    main() 