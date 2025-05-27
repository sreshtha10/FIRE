#script for github functions.
import requests
import os
from dotenv import load_dotenv
from git import Repo
import shutil
from datetime import datetime
import uuid


def copy_file_contents(file_url, github_token):
    if 'github.com' in file_url and 'raw.githubusercontent.com' not in file_url:
        file_url = file_url.replace('github.com', 'raw.githubusercontent.com')
        file_url = file_url.replace('/blob/', '/')

    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3.raw',
        'User-Agent': 'Python-Script'
    }

    try:
        response = requests.get(file_url, headers=headers)
        response.raise_for_status()
        if 'text/plain' in response.headers.get('content-type', ''):
            return response.text
        else:
            if 'api.github.com' in file_url:
                return response.json()['content']
            return response.text
    
    except Exception as e:
        print(f"Error fetching file contents: {e}")
        return None

def create_pr(modified_code, github_token):
    pass