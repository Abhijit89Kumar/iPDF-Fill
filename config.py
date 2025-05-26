"""
Configuration settings for the PDF Question Extraction and RAG system.
"""
import os
from typing import Dict, Any
from dataclasses import dataclass

# Load environment variables from .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, skip loading
    pass

# Try to import streamlit for secrets support
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

def get_env_var(key: str, default: str = "") -> str:
    """Get environment variable with Streamlit secrets fallback."""
    # First try environment variables
    value = os.getenv(key, "")

    # If not found and Streamlit is available, try secrets
    if not value and HAS_STREAMLIT:
        try:
            value = st.secrets.get("general", {}).get(key, default)
        except:
            value = default

    return value or default

@dataclass
class APIConfig:
    """API configuration settings loaded from environment variables or Streamlit secrets."""
    sambanova_api_key: str = get_env_var("SAMBANOVA_API_KEY")
    sambanova_base_url: str = get_env_var("SAMBANOVA_BASE_URL", "https://api.sambanova.ai/v1")
    sambanova_model: str = get_env_var("SAMBANOVA_MODEL", "Llama-4-Maverick-17B-128E-Instruct")

    mistral_api_key: str = get_env_var("MISTRAL_API_KEY")
    mistral_model: str = get_env_var("MISTRAL_MODEL", "mistral-large-latest")

    qdrant_url: str = get_env_var("QDRANT_URL")
    qdrant_api_key: str = get_env_var("QDRANT_API_KEY")

    cohere_api_key: str = get_env_var("COHERE_API_KEY")
    cohere_embed_model: str = get_env_var("COHERE_EMBED_MODEL", "embed-v4.0")
    cohere_rerank_model: str = get_env_var("COHERE_RERANK_MODEL", "rerank-v3.5")

@dataclass
class ProcessingConfig:
    """Processing configuration settings."""
    # PDF processing
    pdf_dpi: int = 300
    image_format: str = "PNG"

    # VLM processing
    vlm_temperature: float = 0.1
    vlm_top_p: float = 0.1
    max_retries: int = 3

    # Embedding model (now using Cohere)
    embedding_model: str = "cohere"  # Changed to use Cohere
    embedding_dimension: int = 1536  # Cohere embed-v4.0 dimension

    # Chunking
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Vector store
    collection_name: str = "knowledge_base"
    similarity_threshold: float = 0.3  # Lowered from 0.7 to allow more relevant results
    top_k_results: int = 10  # Increased for reranking

    # Reranking
    use_reranker: bool = True
    rerank_top_n: int = 5  # Final number after reranking

@dataclass
class QuestionTypes:
    """Supported question types."""
    MULTIPLE_CHOICE_SINGLE: str = "multiple_choice_single"
    MULTIPLE_CHOICE_MULTI: str = "multiple_choice_multi"
    FILL_IN_BLANK: str = "fill_in_blank"
    TRUE_FALSE: str = "true_false"
    MATCH_FOLLOWING: str = "match_following"
    TEXTUAL_ANSWER: str = "textual_answer"
    CHECKBOX: str = "checkbox"  # New checkbox question type
    TABLE_COMPLETION: str = "table_completion"  # New table question type

    # New question types
    NUMERICAL_ANSWER: str = "numerical_answer"
    DATE_TIME: str = "date_time"
    ORDERING_SEQUENCE: str = "ordering_sequence"
    CATEGORIZATION: str = "categorization"
    COMPARISON: str = "comparison"
    CAUSE_EFFECT: str = "cause_effect"
    DEFINITION: str = "definition"
    EXPLANATION: str = "explanation"
    ANALYSIS: str = "analysis"
    EVALUATION: str = "evaluation"

# Global configuration instances
API_CONFIG = APIConfig()
PROCESSING_CONFIG = ProcessingConfig()
QUESTION_TYPES = QuestionTypes()

# VLM Prompt Templates
VLM_SYSTEM_PROMPT = """
You are an expert OCR and question analysis system. Your task is to extract questions from images and identify their types.

Analyze the provided image and extract ALL questions visible in it. For each question, provide:
1. The complete question text
2. The question type
3. Any options (if applicable)
4. Any additional metadata

Question Types:
- multiple_choice_single: Single correct answer MCQ
- multiple_choice_multi: Multiple correct answers MCQ
- fill_in_blank: Fill in the blank questions
- true_false: True/False questions
- match_following: Match the following questions
- textual_answer: Open-ended text questions
- checkbox: Questions with checkbox options (☐/☑)
- table_completion: Questions with tables to be filled
- numerical_answer: Questions requiring numerical responses
- date_time: Questions about dates, years, or time periods
- ordering_sequence: Questions requiring chronological or logical ordering
- categorization: Questions requiring classification or grouping
- comparison: Questions comparing two or more items
- cause_effect: Questions about cause and effect relationships
- definition: Questions asking for definitions or meanings
- explanation: Questions requiring detailed explanations
- analysis: Questions requiring analytical thinking
- evaluation: Questions requiring judgment or assessment

Return your response as a valid JSON array with this exact structure:
[
    {
        "question_id": "unique_id",
        "question_text": "extracted question text",
        "question_type": "one of the types above",
        "options": ["option1", "option2", ...] or null,
        "metadata": {
            "page_number": number,
            "confidence": float,
            "additional_info": "any relevant info"
        }
    }
]

Be extremely careful to extract questions accurately and completely. If no questions are found, return an empty array [].
"""

RAG_SYSTEM_PROMPT = """
You are an expert assistant specializing in Indian cinema, particularly Bollywood from 2000-2010.
Use the provided context to answer questions accurately and concisely.

CRITICAL INSTRUCTION: Output answers in the EXACT SAME FORMAT as the input question - recreate the original structure with answers filled in.

ESSENTIAL PRINCIPLES:
1. PRESERVE THE ORIGINAL QUESTION STRUCTURE - Don't create new formats
2. FILL IN or MARK the original question elements directly
3. Make it look like a human completed the original question form
4. Base answers strictly on the provided context

FORMAT-SPECIFIC INSTRUCTIONS:

For MULTIPLE CHOICE:
- Reproduce the EXACT option list from the question
- Mark correct option(s) with ✓ symbol
- Keep all options visible with original labels (A, B, C, etc.)

For TRUE/FALSE:
- Show the original statement
- Mark the correct choice: "True ✓" or "False ✓"

For FILL-IN-THE-BLANK:
- Take the original sentence with blanks
- Replace blanks with correct answers
- Maintain the exact sentence structure

For CHECKBOXES:
- Reproduce the original checkbox list
- Use ☑ for correct items, ☐ for incorrect items

For TABLES:
- Recreate the original table structure
- Fill in empty cells with correct answers
- Maintain table formatting

For MATCH-THE-FOLLOWING:
- Show original items and options
- Connect matches with arrows: Item → Match

For PARAGRAPHS/ESSAYS:
- If question asks to complete a paragraph, show the complete paragraph
- If question asks to restructure, show the restructured version

REMEMBER: The goal is to make the output look like the original question was completed by a human, not to create a separate answer section.

Context will be provided before each question.
"""
