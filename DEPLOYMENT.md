# Deployment Guide

This guide covers how to deploy the PDF Question Extraction and RAG System to GitHub and Streamlit Cloud with proper secret management.

## 🔐 Environment Variables & Secrets

The application requires the following API keys and configuration:

- **SAMBANOVA_API_KEY**: SambaNova API key for VLM processing
- **MISTRAL_API_KEY**: MistralAI API key for answer generation
- **QDRANT_URL**: Qdrant cloud database URL
- **QDRANT_API_KEY**: Qdrant API key for vector storage
- **COHERE_API_KEY**: Cohere API key for embeddings and reranking

## 📚 GitHub Repository Setup

### 1. Create GitHub Repository

```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit: PDF Question Extraction and RAG System"

# Add GitHub remote (replace with your repository URL)
git remote add origin https://github.com/yourusername/pdf-question-rag-system.git
git branch -M main
git push -u origin main
```

### 2. Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add the following repository secrets:

```
SAMBANOVA_API_KEY = your_actual_sambanova_api_key
MISTRAL_API_KEY = your_actual_mistral_api_key
QDRANT_URL = your_actual_qdrant_url
QDRANT_API_KEY = your_actual_qdrant_api_key
COHERE_API_KEY = your_actual_cohere_api_key
```

### 3. GitHub Actions

The repository includes automated testing via GitHub Actions:
- Tests run on Python 3.8, 3.9, and 3.10
- Validates configuration loading
- Runs setup verification (when secrets are configured)

## ☁️ Streamlit Cloud Deployment

### 1. Connect Repository

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub repository
4. Select the repository: `pdf-question-rag-system`
5. Set main file path: `app.py`
6. Set branch: `main`

### 2. Configure Secrets

In Streamlit Cloud app settings, go to "Secrets" and add:

```toml
[general]
SAMBANOVA_API_KEY = "your_actual_sambanova_api_key"
SAMBANOVA_BASE_URL = "https://api.sambanova.ai/v1"
SAMBANOVA_MODEL = "Llama-4-Maverick-17B-128E-Instruct"

MISTRAL_API_KEY = "your_actual_mistral_api_key"
MISTRAL_MODEL = "mistral-large-latest"

QDRANT_URL = "your_actual_qdrant_url"
QDRANT_API_KEY = "your_actual_qdrant_api_key"

COHERE_API_KEY = "your_actual_cohere_api_key"
COHERE_EMBED_MODEL = "embed-v4.0"
COHERE_RERANK_MODEL = "rerank-v3.5"
```

### 3. Deploy

Click "Deploy" and Streamlit Cloud will:
- Install dependencies from `requirements.txt`
- Load secrets from the configuration
- Start the application at your custom URL

## 🔧 Local Development

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/pdf-question-rag-system.git
cd pdf-question-rag-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy template and fill in your API keys
cp .env.template .env
# Edit .env with your actual API keys
```

### 3. Run Application

```bash
# Run setup verification
python test_setup.py

# Start Streamlit app
streamlit run app.py
```

## 🛡️ Security Best Practices

### ✅ What's Protected
- ✅ API keys are stored as environment variables/secrets
- ✅ `.env` file is in `.gitignore`
- ✅ Secrets are not committed to version control
- ✅ Template files contain placeholder values only

### ⚠️ Important Notes
- Never commit actual API keys to the repository
- Use different API keys for development and production
- Regularly rotate API keys for security
- Monitor API usage and set up billing alerts

## 🔍 Troubleshooting

### Common Issues

1. **Missing Environment Variables**
   - Ensure all required secrets are configured
   - Check spelling of environment variable names
   - Verify secrets are accessible in the deployment environment

2. **API Key Issues**
   - Verify API keys are valid and active
   - Check API rate limits and quotas
   - Ensure proper permissions for each service

3. **Streamlit Cloud Deployment**
   - Check logs in Streamlit Cloud dashboard
   - Verify `requirements.txt` includes all dependencies
   - Ensure secrets are properly formatted in TOML

### Debug Commands

```bash
# Test configuration loading
python -c "from config import API_CONFIG; print('Config loaded:', bool(API_CONFIG.sambanova_api_key))"

# Verify environment variables
python -c "import os; print('SAMBANOVA_API_KEY:', bool(os.getenv('SAMBANOVA_API_KEY')))"

# Run setup verification
python test_setup.py
```

## 📞 Support

For deployment issues:
1. Check the GitHub Actions logs for automated tests
2. Review Streamlit Cloud logs for deployment errors
3. Verify all secrets are properly configured
4. Ensure API services are accessible and functional

---

**Ready for secure deployment with proper secret management!** 🚀
