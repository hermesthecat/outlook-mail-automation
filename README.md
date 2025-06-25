# Outlook Mail Automation

A Python-based automation tool for Microsoft Outlook email operations using Microsoft Graph API.

## Features

- OAuth2 authentication with Microsoft account
- Send emails programmatically
- Read messages from inbox and junk folders
- Automatic token refresh handling
- Proxy support for network connections

## Prerequisites

- Python 3.6 or higher
- Microsoft account
- Registered application in Azure Portal with appropriate permissions
- Required Python packages:
  - requests
  - DrissionPage

## Installation

### Option 1: Automatic Installation (Recommended)

1. Clone the repository:

```bash
git clone https://github.com/yourusername/outlook-mail-automation.git
cd outlook-mail-automation
```

2. Run the automatic installation script:

```bash
python install.py
```

This will automatically:

- Check Python version compatibility
- Install all required packages
- Set up the package in development mode
- Create configuration template
- Show next steps

### Option 2: Manual Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/outlook-mail-automation.git
cd outlook-mail-automation
```

2. Install required packages:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install requests DrissionPage
```

3. Install the package:

```bash
pip install -e .
```

### Option 3: Install from PyPI (Future)

```bash
pip install outlook-mail-automation
```

## Configuration

1. Configure your Microsoft application:

   - Register a new application in Azure Portal
   - Add required permissions (Mail.ReadWrite, Mail.Send, User.Read)
   - Set redirect URI to `http://localhost:8000/`

2. Create `config.txt` file with your application credentials:

```ini
[microsoft]
client_id = your_client_id_here
redirect_uri = http://localhost:8000/
```

## Usage

### Console Commands (After Installation)

If you installed the package using `pip install -e .` or `python install.py`, you can use these console commands:

1. Obtain authentication token:

```bash
outlook-auth
```

2. Test email operations:

```bash
outlook-mail
```

### Direct Python Scripts

1. First, obtain the authentication token:

```bash
python get_refresh_token.py
```

2. After authentication, use the mail API:

```python
from mail_api import EmailClient

# Initialize client
client = EmailClient()

# Send email
recipients = ['recipient@example.com']
subject = 'Test Email'
content = 'Hello from Python!'
client.send_email(recipients, subject, content)

# Read latest messages
messages = client.get_messages(top=5)
for msg in messages:
    print(f"Subject: {msg['subject']}")
    print(f"From: {msg['from']['emailAddress']['address']}")
```
