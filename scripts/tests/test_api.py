#script to test the FIRE rest-api
import requests
from dotenv import load_dotenv
import os


load_dotenv()

github_token = os.getenv('GITHUB_TOKEN')
file_url = os.getenv('GITHUB_FILE_URL')
api_base_url = os.getenv('FIRE_API_BASE_URL')
pr_url = os.getenv('PR_URL')

def test_fix_endpoint():
    payload = {
        "file_url":file_url,
        "github_token":github_token
    }

    response = requests.post(f"{api_base_url}/fix", json=payload)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")


def test_review_endpoint():
    payload = {
        "pr_url":pr_url,
        "github_token":github_token
    }

    response = requests.post(f'{api_base_url}/review', json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__=="__main__":
    #test_fix_endpoint()
    test_review_endpoint()