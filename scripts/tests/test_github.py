#script to test github apis.
from dotenv import load_dotenv
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from scripts.github import copy_file_contents

load_dotenv()

github_token =  os.getenv('GITHUB_TOKEN')
file_url = os.getenv('GITHUB_FILE_URL')

if github_token is None or file_url is None:
    print('Env variables not set!')

#testing copy file contents
result = copy_file_contents(file_url=file_url, github_token=github_token)
print(result)
