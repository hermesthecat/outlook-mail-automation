#!/usr/bin/env python3
"""
Microsoft OAuth2 Authentication Script
Used to obtain Microsoft access_token and refresh_token
"""

from DrissionPage import Chromium
import requests
from typing import Dict
import logging
import configparser
from urllib.parse import quote, parse_qs
import time
from datetime import datetime
import winreg
import base64
import hashlib
import secrets
import string
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

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
    config = configparser.ConfigParser()
    config.read('config.txt', encoding='utf-8')
    return config

def save_config(config):
    with open('config.txt', 'w', encoding='utf-8') as f:
        config.write(f)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载配置
config = load_config()
microsoft_config = config['microsoft']

CLIENT_ID = microsoft_config['client_id']
REDIRECT_URI = microsoft_config['redirect_uri']

# API端点
AUTH_URL = 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize'
TOKEN_URL = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'

# 权限范围
SCOPES = [
    'offline_access',
    'https://graph.microsoft.com/Mail.ReadWrite',
    'https://graph.microsoft.com/Mail.Send',
    'https://graph.microsoft.com/User.Read'
]

def generate_code_verifier(length=128) -> str:
    """生成PKCE验证码"""
    alphabet = string.ascii_letters + string.digits + '-._~'
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_code_challenge(code_verifier: str) -> str:
    """生成PKCE挑战码"""
    sha256_hash = hashlib.sha256(code_verifier.encode()).digest()
    return base64.urlsafe_b64encode(sha256_hash).decode().rstrip('=')

def request_authorization(tab) -> tuple:
    """Request Microsoft OAuth2 Authorization"""
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)
    
    scope = ' '.join(SCOPES)
    auth_params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': scope,
        'response_mode': 'query',
        'prompt': 'select_account',
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }
    
    params = '&'.join([f'{k}={quote(v)}' for k, v in auth_params.items()])
    auth_url = f'{AUTH_URL}?{params}'
    
    tab.get(auth_url)
    logger.info("Waiting for user login and authorization...")
    
    tab.wait.url_change(text='localhost:8000', timeout=300)
    
    callback_url = tab.url
    logger.info(f"Callback URL: {callback_url}")
    
    query_components = parse_qs(callback_url.split('?')[1]) if '?' in callback_url else {}
    
    if 'code' not in query_components:
        raise ValueError("Failed to get authorization code")
    
    auth_code = query_components['code'][0]
    logger.info("Successfully obtained authorization code")
    
    return auth_code, code_verifier

def get_tokens(auth_code: str, code_verifier: str) -> Dict[str, str]:
    """Get access token and refresh token using authorization code"""
    token_params = {
        'client_id': CLIENT_ID,
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code',
        'scope': ' '.join(SCOPES),
        'code_verifier': code_verifier
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        response = requests.post(TOKEN_URL, data=token_params, headers=headers, proxies=get_proxy())
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to get token: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        raise

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if '/?code=' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            with open('templates/callback.html', 'r', encoding='utf-8') as f:
                content = f.read()
                self.wfile.write(content.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def start_server():
    server = HTTPServer(('localhost', 8000), OAuthHandler)
    server.serve_forever()

def main():
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    try:
        browser = Chromium()
        tab = browser.new_tab() 

        logger.info("Opening browser for authorization...")
        
        try:
            auth_code, code_verifier = request_authorization(tab)
            logger.info("Successfully obtained authorization code!")
            
            tokens = get_tokens(auth_code, code_verifier)
            
            if 'refresh_token' in tokens:
                logger.info("Successfully obtained refresh_token!")
                config['tokens']['refresh_token'] = tokens['refresh_token']
                if 'access_token' in tokens:
                    config['tokens']['access_token'] = tokens['access_token']
                    expires_at = time.time() + tokens['expires_in']
                    expires_at_str = datetime.fromtimestamp(expires_at).strftime('%Y-%m-%d %H:%M:%S')
                    config['tokens']['expires_at'] = expires_at_str
                save_config(config)

                time.sleep(15)
                tab.close()
        finally:
            browser.quit()
        
    except Exception as e:
        logger.error(f"Program execution error: {e}")
        raise

if __name__ == '__main__':
    main()
