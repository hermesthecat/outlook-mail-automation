#!/usr/bin/env python3
"""
Microsoft Mail Processing Script
Used for sending and receiving emails with Microsoft account
"""

import requests
import logging
from datetime import datetime
from typing import Dict, List
import configparser
import winreg
import time

def get_proxy():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Internet Settings") as key:
            proxy_enable, _ = winreg.QueryValueEx(key, "ProxyEnable")
            proxy_server, _ = winreg.QueryValueEx(key, "ProxyServer")
            
            if proxy_enable and proxy_server:
                proxy_parts = proxy_server.split(":")
                if len(proxy_parts) == 2:
                    return {"http": f"http://{proxy_server}", "https": f"http://{proxy_server}"}
    except WindowsError:
        pass
    return {"http": None, "https": None}

def load_config():
    """Load configuration from config.txt"""
    config = configparser.ConfigParser()
    config.read('config.txt', encoding='utf-8')
    return config

def save_config(config):
    """Save configuration to config.txt"""
    with open('config.txt', 'w', encoding='utf-8') as f:
        config.write(f)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = load_config()
microsoft_config = config['microsoft']

CLIENT_ID = microsoft_config['client_id']
GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'
TOKEN_URL = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'

class EmailClient:
    def __init__(self):
        config = load_config()
        if not config.has_section('tokens'):
            config.add_section('tokens')
        self.config = config
        self.refresh_token = config['tokens'].get('refresh_token', '')
        self.access_token = config['tokens'].get('access_token', '')
        expires_at_str = config['tokens'].get('expires_at', '1970-01-01 00:00:00')
        self.expires_at = datetime.strptime(expires_at_str, '%Y-%m-%d %H:%M:%S').timestamp()
    
    def is_token_expired(self) -> bool:
        """Check if access token is expired or about to expire"""
        buffer_time = 300
        return datetime.now().timestamp() + buffer_time >= self.expires_at
    
    def refresh_access_token(self) -> None:
        """Refresh access token"""
        refresh_params = {
            'client_id': CLIENT_ID,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token',
        }
        
        try:
            response = requests.post(TOKEN_URL, data=refresh_params, proxies=get_proxy())
            response.raise_for_status()
            tokens = response.json()
            
            self.access_token = tokens['access_token']
            self.expires_at = time.time() + tokens['expires_in']
            expires_at_str = datetime.fromtimestamp(self.expires_at).strftime('%Y-%m-%d %H:%M:%S')
            
            self.config['tokens']['access_token'] = self.access_token
            self.config['tokens']['expires_at'] = expires_at_str
            
            if 'refresh_token' in tokens:
                self.refresh_token = tokens['refresh_token']
                self.config['tokens']['refresh_token'] = self.refresh_token
            save_config(self.config)
        except requests.RequestException as e:
            logger.error(f"Failed to refresh access token: {e}")
            raise

    def ensure_token_valid(self):
        """Ensure token is valid"""
        if not self.access_token or self.is_token_expired():
            self.refresh_access_token()

    def get_messages(self, folder_id: str = 'inbox', top: int = 10) -> List[Dict]:
        """Get messages from specified folder
        
        Args:
            folder_id: Folder ID, defaults to 'inbox'
            top: Number of messages to retrieve
        """
        self.ensure_token_valid()
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json',
            'Prefer': 'outlook.body-content-type="text"'
        }
        
        query_params = {
            '$top': top,
            '$select': 'subject,receivedDateTime,from,body',
            '$orderby': 'receivedDateTime DESC'
        }
        
        try:
            response = requests.get(
                f'{GRAPH_API_ENDPOINT}/me/mailFolders/{folder_id}/messages',
                headers=headers,
                params=query_params,
                proxies=get_proxy()
            )
            response.raise_for_status()
            return response.json()['value']
        except requests.RequestException as e:
            logger.error(f"Failed to get messages: {e}")
            if response.status_code == 401:
                self.refresh_access_token()
                return self.get_messages(folder_id, top)
            raise

    def get_junk_messages(self, top: int = 10) -> List[Dict]:
        """Get messages from junk email folder"""
        return self.get_messages(folder_id='junkemail', top=top)

    def send_email(self, to_recipients: List[str], subject: str, content: str, is_html: bool = False) -> bool:
        """Send email
        
        Args:
            to_recipients: List of recipient email addresses
            subject: Email subject
            content: Email content
            is_html: Whether content is HTML format, defaults to False
            
        Returns:
            bool: Whether sending was successful
        """
        self.ensure_token_valid()
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        email_msg = {
            'message': {
                'subject': subject,
                'body': {
                    'contentType': 'HTML' if is_html else 'Text',
                    'content': content
                },
                'toRecipients': [
                    {
                        'emailAddress': {
                            'address': recipient
                        }
                    } for recipient in to_recipients
                ]
            }
        }
        
        try:
            response = requests.post(
                f'{GRAPH_API_ENDPOINT}/me/sendMail',
                headers=headers,
                json=email_msg,
                proxies=get_proxy()
            )
            response.raise_for_status()
            logger.info(f"Email successfully sent to {', '.join(to_recipients)}")
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to send email: {e}")
            if response.status_code == 401:
                self.refresh_access_token()
                return self.send_email(to_recipients, subject, content, is_html)
            raise

def main():
    try:
        client = EmailClient()
        
        recipients = ['recipient@example.com']  # Replace with actual recipient email
        print("\nSending email:")
        subject = 'Test Email'                  # Replace with actual email subject
        content = 'This is a test email.\n\nGreetings from Python script!'  # Replace with actual email content
        
        if client.send_email(recipients, subject, content):
            print("Email sent successfully!")
        
        # Get inbox messages, top=n means get latest n messages
        messages = client.get_messages(top=1)
        print("\nLatest inbox message:")
        for msg in messages:
            print("\n" + "="*50)
            print(f"Subject: {msg['subject']}")
            print(f"From: {msg['from']['emailAddress']['address']}")
            print(f"Time: {msg['receivedDateTime']}")
            print(f"\nContent:{msg['body']['content']}")
            
        # Get junk messages, top=n means get latest n messages
        junk_messages = client.get_junk_messages(top=1)
        print("\nLatest junk folder message:")
        for msg in junk_messages:
            print("\n" + "="*50)
            print(f"Subject: {msg['subject']}")
            print(f"From: {msg['from']['emailAddress']['address']}")
            print(f"Time: {msg['receivedDateTime']}")
            print(f"\nContent:{msg['body']['content']}")
            
    except Exception as e:
        logger.error(f"Program execution error: {e}")
        raise

if __name__ == '__main__':
    main()
