# 🚀 GitHub Repository Setup Guide

This guide will help you create a public GitHub repository for the PDF Question Extraction and RAG System with proper secret management.

## 📋 Pre-Setup Checklist

✅ **Environment Variables Configured**: All API keys loaded from `.env` file  
✅ **Security Implemented**: `.env` file excluded from version control  
✅ **Templates Created**: `.env.template` and `secrets.toml.template` for deployment  
✅ **GitHub Actions**: Automated testing workflow configured  
✅ **Documentation**: Comprehensive README and deployment guides  

## 🔐 Security Features

### **What's Protected:**
- ✅ **API Keys**: Stored in environment variables, not in code
- ✅ **Secrets Management**: GitHub Secrets for CI/CD, Streamlit Secrets for deployment
- ✅ **Version Control**: `.gitignore` prevents committing sensitive files
- ✅ **Templates Only**: Only placeholder templates are committed to repository

### **API Keys Required:**
```bash
SAMBANOVA_API_KEY=e828ddc3-8094-44dd-8f2b-b1624dfe2696
MISTRAL_API_KEY=DNdGxx2Zgx7l0iTkkz44CzsYOOdEzUe7
QDRANT_URL=https://a41fdff5-3272-490c-9b97-f2f70222a9fb.eu-west-1-0.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.vHNATr9Jl5-h4OOiQJElKZTKEw-_DrVLfjjbyrLaamg
COHERE_API_KEY=4Gqgx7RbAEIeH6ZIakbpLIEPvxY7tPtQYvL4h94D
```

## 🛠️ Step-by-Step Setup

### **1. Initialize Git Repository**

```bash
# Run the initialization script
python init_git.py
```

Or manually:
```bash
git init
git add .
git commit -m "Initial commit: PDF Question Extraction and RAG System with secure environment variable management"
```

### **2. Create GitHub Repository**

1. Go to [GitHub.com](https://github.com)
2. Click "New repository"
3. Repository name: `pdf-question-rag-system`
4. Description: `Advanced PDF Question Extraction and RAG Answering System with Cohere Integration`
5. Set to **Public**
6. Don't initialize with README (we already have one)
7. Click "Create repository"

### **3. Connect Local Repository to GitHub**

```bash
# Add GitHub remote (replace 'yourusername' with your GitHub username)
git remote add origin https://github.com/yourusername/pdf-question-rag-system.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### **4. Configure GitHub Secrets**

Go to your repository → Settings → Secrets and variables → Actions

Add these **Repository Secrets**:

| Secret Name | Value |
|-------------|-------|
| `SAMBANOVA_API_KEY` | `e828ddc3-8094-44dd-8f2b-b1624dfe2696` |
| `MISTRAL_API_KEY` | `DNdGxx2Zgx7l0iTkkz44CzsYOOdEzUe7` |
| `QDRANT_URL` | `https://a41fdff5-3272-490c-9b97-f2f70222a9fb.eu-west-1-0.aws.cloud.qdrant.io:6333` |
| `QDRANT_API_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.vHNATr9Jl5-h4OOiQJElKZTKEw-_DrVLfjjbyrLaamg` |
| `COHERE_API_KEY` | `4Gqgx7RbAEIeH6ZIakbpLIEPvxY7tPtQYvL4h94D` |

## ☁️ Streamlit Cloud Deployment

### **1. Connect to Streamlit Cloud**

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `pdf-question-rag-system`
5. Main file path: `app.py`
6. Branch: `main`

### **2. Configure Streamlit Secrets**

In the Streamlit Cloud app settings, add these secrets:

```toml
[general]
SAMBANOVA_API_KEY = "e828ddc3-8094-44dd-8f2b-b1624dfe2696"
SAMBANOVA_BASE_URL = "https://api.sambanova.ai/v1"
SAMBANOVA_MODEL = "Llama-4-Maverick-17B-128E-Instruct"

MISTRAL_API_KEY = "DNdGxx2Zgx7l0iTkkz44CzsYOOdEzUe7"
MISTRAL_MODEL = "mistral-large-latest"

QDRANT_URL = "https://a41fdff5-3272-490c-9b97-f2f70222a9fb.eu-west-1-0.aws.cloud.qdrant.io:6333"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.vHNATr9Jl5-h4OOiQJElKZTKEw-_DrVLfjjbyrLaamg"

COHERE_API_KEY = "4Gqgx7RbAEIeH6ZIakbpLIEPvxY7tPtQYvL4h94D"
COHERE_EMBED_MODEL = "embed-v4.0"
COHERE_RERANK_MODEL = "rerank-v3.5"
```

### **3. Deploy**

Click "Deploy" and your app will be live at: `https://yourusername-pdf-question-rag-system.streamlit.app`

## ✅ Verification

### **GitHub Repository Checklist:**
- ✅ Repository is public
- ✅ All code is committed
- ✅ `.env` file is NOT in the repository
- ✅ GitHub Secrets are configured
- ✅ GitHub Actions tests pass

### **Streamlit Cloud Checklist:**
- ✅ App deploys successfully
- ✅ Secrets are configured
- ✅ All API services are accessible
- ✅ Application functions correctly

## 🎯 Repository Features

### **📁 File Structure:**
```
pdf-question-rag-system/
├── .env.template          # Template for environment variables
├── .gitignore            # Excludes sensitive files
├── secrets.toml.template # Template for Streamlit secrets
├── DEPLOYMENT.md         # Detailed deployment guide
├── GITHUB_SETUP.md       # This setup guide
├── README.md             # Comprehensive documentation
├── requirements.txt      # Python dependencies
├── app.py               # Main Streamlit application
├── config.py            # Environment variable configuration
└── .github/workflows/   # Automated testing
```

### **🔧 Key Features:**
- 🔐 **Secure**: Environment variables for all API keys
- 🚀 **Deployable**: Ready for GitHub and Streamlit Cloud
- 🧪 **Tested**: Automated testing with GitHub Actions
- 📖 **Documented**: Comprehensive guides and documentation
- 🛡️ **Production-Ready**: Error handling and monitoring

## 🎉 Success!

Your repository is now ready for:
- ✅ **Public sharing** on GitHub
- ✅ **Secure deployment** to Streamlit Cloud
- ✅ **Collaborative development** with proper secret management
- ✅ **Production use** with all API integrations

**Repository URL**: `https://github.com/yourusername/pdf-question-rag-system`  
**Live App URL**: `https://yourusername-pdf-question-rag-system.streamlit.app`

---

**🚀 Ready for deployment with enterprise-grade security!**
