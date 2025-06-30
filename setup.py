#!/usr/bin/env python3
"""
Quick Setup Script for LinguaLearn Visitors
This script helps visitors get the app running quickly.
"""

import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_content = """# Development Environment Variables
DEV_MODE=true
FLASK_ENV=development

# OpenAI API Key (replace with your actual key)
# Get your key from: https://platform.openai.com/api-keys
APIKEY=your_openai_api_key_here
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
        print("⚠️  IMPORTANT: Edit .env file and add your OpenAI API key")
        print("   Get your key from: https://platform.openai.com/api-keys")
    else:
        print("ℹ️  .env file already exists")

def main():
    print("🚀 LinguaLearn Quick Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("\n💡 Try running: pip install --upgrade pip")
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Create demo users
    if not run_command("python create_demo_user.py", "Creating demo users"):
        print("⚠️  Demo user creation failed, but you can still create your own account")
    
    print("\n🎉 Setup complete!")
    print("\n📝 Next steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Run: python app.py")
    print("3. Open: http://localhost:5000")
    print("4. Login with demo credentials or create your own account")
    print("\n📚 Demo Credentials:")
    print("   - Username: demo | Password: demo123")
    print("   - Username: visitor | Password: visitor123")
    
    print("\n🌟 Features to try:")
    print("   - Add languages to your profile")
    print("   - Add vocabulary words")
    print("   - Try sentence practice (requires OpenAI API key)")
    print("   - View your learning progress")
    
    print("\n🔧 If you encounter issues:")
    print("   - Check that your OpenAI API key is correct")
    print("   - Ensure all dependencies are installed")
    print("   - Try running: python reset_db.py to reset the database")

if __name__ == '__main__':
    main() 