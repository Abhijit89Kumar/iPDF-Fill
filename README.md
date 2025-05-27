# PDF Question Extraction and RAG Answering System

Internal tool for extracting questions from PDF documents using Vision Language Models and answering them via Retrieval-Augmented Generation.

## Overview

This system processes PDF questionnaires by:
1. Converting PDF pages to images
2. Extracting questions using SambaNova VLM
3. Building vector database from knowledge base
4. Answering questions using MistralAI with Cohere embeddings/reranking
5. Generating formatted answer PDFs

## Technology Stack

- **VLM**: SambaNova Llama-4-Maverick-17B
- **LLM**: MistralAI mistral-large-latest  
- **Embeddings**: Cohere embed-v4.0 (1536-dim)
- **Reranking**: Cohere rerank-v3.5
- **Vector DB**: Qdrant
- **Framework**: Streamlit
- **PDF Processing**: PyMuPDF, ReportLab

## Supported Question Types

Multiple choice, fill-in-blank, true/false, matching, tables, checkboxes, numerical, date/time, ordering, categorization, comparison, cause/effect, definition, explanation, analysis, evaluation, textual answers.

## Setup

### Prerequisites
- Python 3.10+
- API keys for SambaNova, MistralAI, Qdrant, Cohere

### Installation
```bash
git clone https://github.com/Abhijit89Kumar/iPDF-Fill.git
cd Sprinto_QnA
pip install -r requirements.txt
```

### Environment Variables
Create `.env` file or set Streamlit secrets:
```
SAMBANOVA_API_KEY=your_key
MISTRAL_API_KEY=your_key
QDRANT_URL=your_url
QDRANT_API_KEY=your_key
COHERE_API_KEY=your_key
```

### Sample Questionnaires and Knowledge Bases
Sample questionnaires and knowledge bases can be found at https://drive.google.com/drive/folders/1TNtYQHlwaGWWJI3KSQMG1vpbxeVVMzwJ?usp=sharing

Note: The Knowledge Base for the Indian Movies is the default one and is pre-loaded in the qdrant vector store.

### Local Development
```bash
streamlit run app.py
```

### Deployment
Deploy to Streamlit Cloud with secrets configured in dashboard.

## Usage

1. Upload knowledge base (Markdown file)
2. Upload PDF questionnaire
3. Click "Process PDF and Generate Answers"
4. Download generated answer PDF and JSON results

## Architecture

### Processing Pipeline
```
PDF → Images → VLM Extraction → Questions JSON
Knowledge Base → Chunking → Embeddings → Vector Store
Questions + Vector Store → Retrieval + Reranking → LLM → Answers → PDF
```

### Key Components

- **PDF Processor** (`utils/pdf_processor.py`): PDF to image conversion
- **VLM Service** (`services/vlm_service.py`): Question extraction
- **Knowledge Processor** (`services/knowledge_processor.py`): Text chunking
- **Vector Store** (`services/vector_store.py`): Qdrant integration
- **RAG Agent** (`services/rag_agent.py`): Answer generation
- **PDF Generator** (`utils/pdf_generator.py`): Answer PDF creation

## Configuration

Key settings in `config.py`:
- Embedding dimensions: 1536 (Cohere embed-v4.0)
- Chunk size: 1000 tokens, overlap: 200
- Top-k retrieval: 10, rerank to top-5
- Rate limiting: 1 req/sec for MistralAI

## Testing

```bash
python test_setup.py
python demo.py
```

## File Structure

```
├── app.py                 # Main Streamlit application
├── demo.py               # Demo script
├── config.py             # Configuration settings
├── requirements.txt      # Dependencies
├── services/
│   ├── vlm_service.py    # VLM question extraction
│   ├── knowledge_processor.py  # Text chunking
│   ├── vector_store.py   # Qdrant vector database
│   └── rag_agent.py      # RAG answer generation
└── utils/
    ├── pdf_processor.py  # PDF processing
    └── pdf_generator.py  # Answer PDF generation
```


