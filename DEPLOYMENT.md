# Google Cloud Platform (GCP) Deployment Plan

This document outlines the step-by-step procedure to deploy the **BenefitBuddy** welfare navigator to Google Cloud Platform. To provide a public URL that anyone can open in their browser to chat with the agent, we will deploy the **ADK Web UI** to **Google Cloud Run** with unauthenticated access enabled.

---

## 🛠️ Prerequisites

Before executing the deployment, ensure you have set up the following on your local machine and GCP Console:

1.  **Google Cloud SDK (`gcloud` CLI)**: Installed and authenticated.
    ```bash
    gcloud auth login
    gcloud auth application-default login
    ```
2.  **GCP Project**: Create a new project or select an existing one (e.g., `ambient-expense-agent-500708`) and ensure **Billing is enabled**.
3.  **Required APIs**: Enable the following service APIs in your GCP project:
    *   Cloud Run API (`run.googleapis.com`)
    *   Cloud Build API (`cloudbuild.googleapis.com`)
    *   Artifact Registry API (`artifactregistry.googleapis.com`)
    
    You can enable them in one command:
    ```bash
    gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com --project=[YOUR_PROJECT_ID]
    ```

---

## 📦 Preparing the Deployment Package

The ADK deployment CLI bundles your project directory and deploys it. Ensure the following files are set up in the root of the directory:

### 1. Requirements (`requirements.txt`)
All required dependencies are listed in `requirements.txt`:
```text
google-genai==0.1.1
google-adk==2.0.0
ddgs==9.14.4
pydantic
numpy
```

### 2. Project Entrypoint (`__init__.py`)
Ensure your root `__init__.py` exposes `root_agent`:
```python
from .agent import root_agent
```

### 3. Environment Variables & Secrets
> **IMPORTANT**
> Never hardcode secrets (like `GEMINI_API_KEY`) into container files or deploy them inside `.env` files. We will pass them securely as environment variables during the deployment command.

---

## 🚀 Deploying the Public Chatbot

To deploy a fully interactive web chatbot that anyone can access, we will use ADK's native `cloud_run` deployer with the `--deploy_web_ui` flag.

### Step 1: Run the Deployment Command
Execute the deployment from your project directory:
```bash
adk deploy cloud_run \
  --project=[YOUR_PROJECT_ID] \
  --region=[YOUR_REGION] \
  --deploy_web_ui \
  --env-vars GEMINI_API_KEY=[YOUR_GEMINI_API_KEY] \
  .
```
*   `--deploy_web_ui`: Tells the ADK builder to bundle the default web UI template, making it instantly browsable.
*   `--env-vars`: Securely sets environment variables in the Cloud Run container runtime.

### Step 2: Allow Public (Unauthenticated) Access
During the command execution, the CLI will ask:
`Allow unauthenticated invocations to [service-name] (y/N)?` 
👉 Enter **`y`** (Yes) to grant public access.

If the prompt is skipped or you want to enforce it manually via the `gcloud` tool, run the following IAM binding:
```bash
gcloud run services add-iam-policy-binding benefit-buddy \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --project=[YOUR_PROJECT_ID] \
  --region=[YOUR_REGION]
```

---

## 🔗 Accessing the Chatbot
Once the deployment finishes, the terminal will output the service details, including a public URL:
```text
Service [benefit-buddy] has been deployed and is running at:
https://benefit-buddy-xxxx-uc.a.run.app
```
You can share this URL with anyone. When they open it, they will see a beautiful, responsive chat interface where they can interact with **BenefitBuddy** directly in their web browser!
