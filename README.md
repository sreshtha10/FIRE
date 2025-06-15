# 🔥 FIRE - FIx and REview (AI Dev Agent)

**FIRE** is an AI-powered FastAPI service designed to **automatically fix and review code** on GitHub repositories using large language models via Ollama and Langchain.

It consists of:
- `/fix` – Fix code automatically using `deepseek-coder-v2`
- `/review` – Review GitHub PRs using intelligent AI prompts
- `/fire` – End-to-end automation: Fix → PR → Review

---

## ⚙️ Tech Stack

- **Python** 🐍
- **FastAPI** 🚀
- **Langchain**
- **Ollama** (LLM runtime)
- **GitHub REST APIs**
- **deepseek-coder-v2:latest** (LLM model)

---

## 🛠️ Setup Instructions

### 1. Clone and Install

```bash
git clone https://github.com/sremehro/FIRE.git
cd FIRE
pip install -r requirements.txt
```

### 2. Run Ollama with DeepSeek

Make sure [Ollama](https://ollama.com/) is installed and start the model:

```bash
ollama run deepseek-coder-v2:latest
```

### 3. Start the FastAPI Server

```bash
uvicorn api:app --host 0.0.0.0 --port 8080
```

---

## 🔌 API Reference

### ✅ `/fix`

**Purpose:** Analyzes a file and applies improvements (bugs, performance, code quality), then creates a Pull Request on GitHub.

**POST** `/fix`

#### Request
```json
{
  "file_url": "https://github.com/user/repo/blob/main/file.py",
  "github_token": "ghp_YourGithubToken"
}
```

#### Response
```json
{
  "has_solution": true,
  "solution": "Modified code here...",
  "pr_url": "https://github.com/user/repo/pull/123"
}
```

---

### 🔍 `/review`

**Purpose:** Fetches details of a GitHub Pull Request and runs an automated code review, including inline comments.

**POST** `/review`

#### Request
```json
{
  "pr_url": "https://github.com/user/repo/pull/123",
  "github_token": "ghp_YourGithubToken"
}
```

#### Response
```json
{
  "has_comments": true,
  "review_comments": [...],
  "approve": false
}
```

---

### 🔁 `/fire`

**Purpose:** End-to-end automation. Fix a file → Create PR → Review the PR.

**POST** `/fire`

#### Request
Same as `/fix`
```json
{
  "file_url": "https://github.com/user/repo/blob/main/file.py",
  "github_token": "ghp_YourGithubToken"
}
```

#### Response
```json
{
  "fix": {
    "has_solution": true,
    "solution": "...",
    "pr_url": "https://github.com/user/repo/pull/123"
  },
  "review": {
    "has_comments": true,
    "review_comments": [...],
    "approve": false
  }
}
```

---

## 🧠 Model & Agent Details

- Uses `deepseek-coder-v2:latest` through **Ollama**
- Powered by **Langchain agents** to orchestrate prompt execution
- GitHub interactions via REST API:
  - Read file content from a repo
  - Create pull requests
  - Post inline PR reviews

---

## 🔐 GitHub Token

Use a **Personal Access Token (PAT)** with:
- `repo` (all)
- `pull_request` and `contents` scope

Generate it from: [GitHub Developer Settings](https://github.com/settings/tokens)

---

## 🤝 Contribution

Feel free to submit PRs or raise issues to improve the tool. Future enhancements could include:
- CLI wrapper
- Support for batch file processing
- Web dashboard for results
- Implement MCP to get full repo context.

---

## 📄 License

This project is licensed under the MIT License.

---

## ❤️ Acknowledgements

- [Ollama](https://ollama.com/)
- [DeepSeek](https://huggingface.co/deepseek-ai)
- [Langchain](https://www.langchain.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
