import aiohttp
import requests
import uuid
import ssl
import certifi
import datetime
import base64
from urllib.parse import urlparse

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
        return response.text
    except Exception as e:
        print(f"Error fetching file contents: {e}")
        return None


async def create_pr(file_url, modified_code, github_token):
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            headers = {
                'Authorization': f'token {github_token}',
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'Python-Script'
            }

            branch_info = await create_new_branch(file_url, headers, session)
            new_branch_name = branch_info['new_branch_name']
            api_url = branch_info['api_url']
            base_url = branch_info['base_url']
            branch = branch_info['branch']
            path = branch_info['file_path']

            # Get current file content
            async with session.get(api_url, headers=headers) as response:
                response.raise_for_status()
                current_file = await response.json()
                print(f"Fetched current file content: {response.status}")

            # Push modified file to new branch
            await push_code_to_new_branch(modified_code, new_branch_name, current_file, api_url, headers, session)

            # Create PR
            pr_data = {
                "title": "Auto-fix: Code modifications",
                "head": new_branch_name,
                "base": branch,
                "body": f"Automated pull request with code modifications to `{path}`."
            }

            async with session.post(f"{base_url}/pulls", headers=headers, json=pr_data) as response:
                response.raise_for_status()
                print(f"PR created successfully: {response.status}")
                return await response.json()

        except Exception as e:
            print(f"Error creating pull request: {e}")
            try:
                await session.delete(f"{base_url}/git/refs/heads/{new_branch_name}", headers=headers)
            except:
                pass
            return None


async def push_code_to_new_branch(modified_code, new_branch_name, current_file, api_url, headers, session):
    encoded_content = base64.b64encode(modified_code.encode('utf-8')).decode('utf-8')

    update_file_data = {
        "message": "Auto-fix: Code modification",
        "content": encoded_content,
        "branch": new_branch_name,
        "sha": current_file['sha']
    }

    async with session.put(api_url, headers=headers, json=update_file_data) as response:
        response.raise_for_status()
        print(f"Modified code pushed to new branch: {response.status}")
        await response.json()


async def create_new_branch(file_url, headers, session):
    parsed = urlparse(file_url)
    path_parts = parsed.path.strip('/').split('/')

    if len(path_parts) < 5:
        raise ValueError("Invalid GitHub file URL. Must include owner, repo, blob, branch, and file path.")

    owner = path_parts[0]
    repo = path_parts[1]
    branch = path_parts[3]
    file_path = '/'.join(path_parts[4:])

    base_url = f"https://api.github.com/repos/{owner}/{repo}"
    api_url = f"{base_url}/contents/{file_path}"

    # Get SHA of source branch
    async with session.get(f"{base_url}/git/refs/heads/{branch}", headers=headers) as response:
        response.raise_for_status()
        source_sha = (await response.json())['object']['sha']

    # Generate new branch name
    timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    short_uuid = uuid.uuid4().hex[:6]
    new_branch_name = f"auto-fix-{timestamp}-{short_uuid}"

    # Create new branch
    create_branch_data = {
        "ref": f"refs/heads/{new_branch_name}",
        "sha": source_sha
    }

    async with session.post(f"{base_url}/git/refs", headers=headers, json=create_branch_data) as response:
        response.raise_for_status()
        print(f"New branch created: {new_branch_name} ({response.status})")
        await response.json()

    return {
        'new_branch_name': new_branch_name,
        'api_url': api_url,
        'base_url': base_url,
        'branch': branch,
        'file_path': file_path
    }