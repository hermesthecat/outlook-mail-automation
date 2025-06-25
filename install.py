#!/usr/bin/env python3
"""
Automatic installation script for Outlook Mail Automation
"""

import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 6):
        print("❌ Python 3.6 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def install_package():
    """Install the package in development mode"""
    print("\n🔧 Installing package in development mode...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
        print("✅ Package installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install package: {e}")
        return False

def create_config_template():
    """Create config template if it doesn't exist"""
    config_file = Path("config.txt")
    if not config_file.exists():
        print("\n📝 Creating config template...")
        config_content = """[microsoft]
client_id = your_client_id_here
redirect_uri = http://localhost:8000/

[tokens]
refresh_token = 
access_token = 
expires_at = 
"""
        with open("config.txt", "w", encoding="utf-8") as f:
            f.write(config_content)
        print("✅ Config template created!")
    else:
        print("✅ Config file already exists!")

def show_next_steps():
    """Show next steps after installation"""
    print("\n" + "="*50)
    print("🎉 Installation completed successfully!")
    print("="*50)
    print("\n📋 Next steps:")
    print("1. Register your application in Azure Portal:")
    print("   - Go to https://portal.azure.com")
    print("   - Navigate to Azure Active Directory > App registrations")
    print("   - Create new application with redirect URI: http://localhost:8000/")
    print("   - Add permissions: Mail.ReadWrite, Mail.Send, User.Read")
    print("\n2. Update config.txt with your client_id")
    print("\n3. Run authentication:")
    print("   python get_refresh_token.py")
    print("   # or")
    print("   outlook-auth")
    print("\n4. Test email operations:")
    print("   python mail_api.py")
    print("   # or")
    print("   outlook-mail")
    print("\n📚 For more information, see README.md")

def main():
    """Main installation function"""
    print("🚀 Outlook Mail Automation - Installation Script")
    print("="*50)
    
    if not check_python_version():
        sys.exit(1)
    
    if not install_requirements():
        sys.exit(1)
    
    if not install_package():
        sys.exit(1)
    
    create_config_template()
    show_next_steps()

if __name__ == "__main__":
    main() 