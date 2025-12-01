# 🎓 AI Assistant for Cloud and Scrum Exams

An intelligent study companion powered by **Amazon Bedrock** (Claude 3 Sonnet) to help you prepare for AWS and Scrum certifications.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red)
![AWS](https://img.shields.io/badge/AWS-Bedrock-orange)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

## 📋 Table of Contents

- [Features](#-features)
- [Supported Certifications](#-supported-certifications)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [Docker Deployment](#-docker-deployment)
- [Usage Guide](#-usage-guide)
- [Project Structure](#-project-structure)
- [Troubleshooting](#-troubleshooting)

## ✨ Features

| Feature | Description |
|---------|-------------|
| 💬 **Interactive Chat** | Natural conversation with AI tutor |
| 📄 **Document Analysis** | Upload and analyze PDF, DOCX, TXT files |
| 🖼️ **Image Analysis** | Upload screenshots, diagrams, or exam questions |
| 📚 **Quick Topics** | Pre-built prompts for common exam topics |
| 🛡️ **Guardrails** | Optional content filtering with AWS Bedrock Guardrails |
| 📝 **Markdown Responses** | Well-formatted responses with tables, code blocks, and lists |
| 💾 **Chat History** | Persistent conversation within session |

## 🎯 Supported Certifications

1. **AWS Certified AI Practitioner** (AIF-C01)
   - AI/ML fundamentals
   - AWS AI services (SageMaker, Rekognition, Comprehend, etc.)
   - Responsible AI practices

2. **AWS Certified Cloud Practitioner** (CLF-C02)
   - Cloud concepts
   - AWS core services
   - Security and compliance
   - Pricing and billing

3. **Scrum Certifications** (PSM I, CSM)
   - Scrum framework
   - Roles and responsibilities
   - Events and artifacts
   - Agile principles

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Streamlit     │────▶│  Amazon Bedrock │────▶│  Claude 3       │
│   Frontend      │     │  Runtime API    │     │  Sonnet         │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │
        │                       ▼
        │               ┌─────────────────┐
        │               │   Guardrails    │
        │               │   (Optional)    │
        │               └─────────────────┘
        ▼
┌─────────────────┐
│  File Processing│
│  - PDF (PyPDF2) │
│  - DOCX         │
│  - Images       │
└─────────────────┘
```

## 📋 Prerequisites

- **Python 3.11+**
- **AWS Account** with Bedrock access
- **Model Access** enabled for Claude 3 Sonnet in AWS Bedrock Console
- **AWS Credentials** with permissions for `bedrock:InvokeModel`

### Required IAM Permissions

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-*"
        }
    ]
}
```

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ai-scm/bld-AI-assistant-workshop-FelipeGarzon.git
cd bld-AI-assistant-workshop-FelipeGarzon
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### 1. Create Environment File

Create a `.env` file in the project root:

```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_SESSION_TOKEN=your-session-token  # Required for temporary credentials

# Optional: AWS Profile (alternative to explicit credentials)
SESSION=your-aws-profile-name
```

### 2. Enable Model Access in AWS

1. Go to **AWS Console** → **Amazon Bedrock** → **Model access**
2. Click **Manage model access**
3. Enable **Anthropic Claude 3 Sonnet**
4. Save changes

### 3. Configure Guardrails (Optional)

1. Go to **AWS Console** → **Amazon Bedrock** → **Guardrails**
2. Create a new guardrail with desired content filters
3. Update `GUARDRAIL_ID` in `app.py` with your guardrail ID

## 🏃 Running the Application

### Local Development

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

### With Custom Port

```bash
streamlit run app.py --server.port=8080
```

## 🐳 Docker Deployment

### Build the Image

```bash
docker build -t ai-assistant .
```

### Run the Container

```bash
docker run -p 8501:8501 --env-file .env ai-assistant
```

### Docker Compose (Alternative)

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  ai-assistant:
    build: .
    ports:
      - "8501:8501"
    env_file:
      - .env
    restart: unless-stopped
```

Run with:

```bash
docker-compose up -d
```

## 📖 Usage Guide

### Basic Chat

1. Type your question in the chat input at the bottom
2. Press Enter or click Send
3. Wait for the AI response (formatted in Markdown)

### Quick Topics

1. Open the sidebar (click `>` on mobile)
2. Select a topic from the dropdown under **📚 Quick Topics**
3. Click **"Ask about this topic"**

### Document Analysis

1. Click **"Browse files"** in the sidebar
2. Upload a PDF, DOCX, or TXT file
3. Ask questions about the content
4. The AI will reference your uploaded material

### Image Analysis

1. Upload an image (PNG, JPG, GIF, WebP)
2. Ask questions about diagrams, screenshots, or exam questions
3. The AI will analyze and explain the image content

### Using Guardrails

1. Check **"Enable Guardrails"** in the Settings section
2. The AI will filter responses according to your guardrail configuration
3. Off-topic requests will be politely redirected

## 📁 Project Structure

```
bld-AI-assistant-workshop-FelipeGarzon/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker configuration
├── .env                # Environment variables (create this)
├── .env.example        # Example environment file
├── .dockerignore       # Docker ignore patterns
├── .gitignore          # Git ignore patterns
└── README.md           # This file
```

## 🔧 Key Components

### `app.py`

| Function | Description |
|----------|-------------|
| `encode_image()` | Converts uploaded images to base64 |
| `extract_text_from_pdf()` | Extracts text from PDF files |
| `extract_text_from_docx()` | Extracts text from Word documents |
| `process_uploaded_file()` | Routes files to appropriate processor |
| `invoke_bedrock_simple()` | Calls Bedrock API without guardrails |
| `invoke_bedrock_with_guardrails()` | Calls Bedrock API with guardrails enabled |

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AWS_ACCESS_KEY_ID` | Yes | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | Yes | AWS secret key |
| `AWS_SESSION_TOKEN` | For temp creds | Session token for temporary credentials |
| `SESSION` | Optional | AWS profile name |

## 🐛 Troubleshooting

### "The security token included in the request is invalid"

**Cause:** Expired or invalid AWS credentials

**Solution:**
1. Refresh your AWS credentials
2. If using SSO: `aws sso login --profile your-profile`
3. Update `.env` with new credentials

### "roles must alternate between user and assistant"

**Cause:** Consecutive messages from same role in conversation

**Solution:** This is handled automatically in the code. If it persists, click **"🗑️ Clear Chat"** to reset.

### "Model not found" or "Access denied"

**Cause:** Claude 3 Sonnet not enabled in your region

**Solution:**
1. Go to AWS Bedrock Console → Model access
2. Enable Anthropic Claude 3 Sonnet
3. Ensure you're using `us-east-1` region

### Docker build is slow

**Solution:**
1. Add `.dockerignore` file to exclude unnecessary files
2. Use BuildKit: `DOCKER_BUILDKIT=1 docker build -t ai-assistant .`

### Responses not showing Markdown formatting

**Solution:** Ensure you're using `st.chat_message()` with `st.markdown()` for display (already implemented).

## 📄 License

This project is for educational purposes as part of the AI Workshop.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

**Happy Studying! 🚀**

*Built with ❤️ using Streamlit and Amazon Bedrock*
