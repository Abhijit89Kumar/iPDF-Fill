"""
Streamlit app for PDF Question Extraction and RAG-based Answering.
"""
import streamlit as st
import logging
import json
import os
from pathlib import Path
import time

# Load environment variables from .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, skip loading (production environment)
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our modules
from utils.pdf_processor import process_uploaded_pdf
from services.vlm_service import extract_questions_from_images, questions_to_json
from services.knowledge_processor import process_knowledge_base
from services.vector_store import setup_vector_store
from services.rag_agent import answer_all_questions
from utils.pdf_generator import generate_answer_pdf, save_json_backup

# Page configuration
st.set_page_config(
    page_title="PDF Question Extraction & RAG Answering System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main Streamlit application."""
    st.title("📚 PDF Question Extraction & RAG Answering System")
    st.markdown("---")

    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Knowledge base selection
        st.subheader("Knowledge Base")
        kb_file = st.file_uploader(
            "Upload Knowledge Base (Markdown)",
            type=['md', 'txt'],
            help="Upload the knowledge base file for RAG"
        )

        # Processing options
        st.subheader("Processing Options")
        force_recreate_db = st.checkbox(
            "Force Recreate Vector DB",
            help="Recreate vector database even if it exists"
        )

        save_intermediate = st.checkbox(
            "Save Intermediate Results",
            value=True,
            help="Save JSON files at each processing step"
        )

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("📄 Upload PDF Questionnaire")
        uploaded_pdf = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload the PDF containing questions to extract and answer"
        )

        if uploaded_pdf is not None:
            st.success(f"✅ PDF uploaded: {uploaded_pdf.name}")

            # Display PDF info
            with st.expander("📊 PDF Information"):
                try:
                    images, pdf_info = process_uploaded_pdf(uploaded_pdf)
                    st.json(pdf_info)
                    st.info(f"📄 Pages: {pdf_info['page_count']}")
                except Exception as e:
                    st.error(f"Error processing PDF: {str(e)}")
                    return

    with col2:
        st.header("🎯 Processing Status")
        status_container = st.container()

    # Processing section
    if uploaded_pdf is not None:
        st.markdown("---")
        st.header("🚀 Start Processing")

        if st.button("🔄 Process PDF and Generate Answers", type="primary"):
            process_pipeline(uploaded_pdf, kb_file, status_container, force_recreate_db, save_intermediate)

def process_pipeline(uploaded_pdf, kb_file, status_container, force_recreate_db, save_intermediate):
    """Execute the complete processing pipeline."""

    with status_container:
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Step 1: Process PDF to images
            status_text.text("📄 Converting PDF to images...")
            progress_bar.progress(10)

            images, pdf_info = process_uploaded_pdf(uploaded_pdf)
            st.success(f"✅ Converted {len(images)} pages to images")

            # Step 2: Extract questions using VLM
            status_text.text("🔍 Extracting questions using VLM...")
            progress_bar.progress(25)

            extracted_questions = extract_questions_from_images(images)
            questions_json = questions_to_json(extracted_questions)

            st.success(f"✅ Extracted {len(extracted_questions)} questions")

            if save_intermediate:
                save_json_backup(questions_json, "extracted_questions.json")

            # Step 3: Process knowledge base
            if kb_file is None:
                # Use default knowledge base
                kb_path = "files/IndianMovie_KnowledgeBase.md"
                if not Path(kb_path).exists():
                    st.error("❌ Default knowledge base not found. Please upload a knowledge base file.")
                    return
            else:
                # Save uploaded knowledge base
                kb_path = f"temp_kb_{kb_file.name}"
                with open(kb_path, "wb") as f:
                    f.write(kb_file.getbuffer())

            status_text.text("📚 Processing knowledge base...")
            progress_bar.progress(40)

            chunks = process_knowledge_base(kb_path)
            st.success(f"✅ Created {len(chunks)} knowledge chunks")

            # Step 4: Setup vector store
            status_text.text("🗄️ Setting up vector database...")
            progress_bar.progress(55)

            vector_store = setup_vector_store(chunks, force_recreate=force_recreate_db)
            st.success("✅ Vector database ready")

            # Step 5: Answer questions using RAG
            status_text.text("🤖 Generating answers using RAG...")
            progress_bar.progress(70)

            answered_questions = answer_all_questions(questions_json, vector_store)
            st.success(f"✅ Generated answers for {len(answered_questions['questions'])} questions")

            if save_intermediate:
                save_json_backup(answered_questions, "answered_questions.json")

            # Step 6: Generate PDF
            status_text.text("📄 Generating answer PDF...")
            progress_bar.progress(85)

            output_pdf_path = f"{Path(uploaded_pdf.name).stem}_Answers.pdf"
            if generate_answer_pdf(answered_questions, output_pdf_path):
                st.success(f"✅ Generated answer PDF: {output_pdf_path}")
            else:
                st.error("❌ Failed to generate PDF")
                return

            # Step 7: Complete
            status_text.text("✅ Processing complete!")
            progress_bar.progress(100)

            # Display results
            display_results(answered_questions, output_pdf_path)

            # Cleanup
            if kb_file is not None and Path(kb_path).exists():
                Path(kb_path).unlink()

        except Exception as e:
            st.error(f"❌ Error during processing: {str(e)}")
            logger.error(f"Pipeline error: {str(e)}", exc_info=True)

def display_results(answered_questions, output_pdf_path):
    """Display processing results."""
    st.markdown("---")
    st.header("📊 Results")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Questions", answered_questions["total_questions"])

    with col2:
        st.metric("Answered Questions", answered_questions.get("answered_questions", 0))

    with col3:
        processing_time = time.time() - answered_questions.get("extraction_timestamp", time.time())
        st.metric("Processing Time", f"{processing_time:.1f}s")

    # Download buttons
    st.subheader("📥 Download Results")

    col1, col2 = st.columns(2)

    with col1:
        if Path(output_pdf_path).exists():
            with open(output_pdf_path, "rb") as pdf_file:
                pdf_data = pdf_file.read()
                st.download_button(
                    label="📄 Download Answer PDF",
                    data=pdf_data,
                    file_name=output_pdf_path,
                    mime="application/pdf",
                    key=f"download_pdf_{output_pdf_path}",
                    use_container_width=True
                )

    with col2:
        json_str = json.dumps(answered_questions, indent=2)
        st.download_button(
            label="📋 Download JSON Results",
            data=json_str,
            file_name=f"{Path(output_pdf_path).stem}.json",
            mime="application/json",
            key=f"download_json_{output_pdf_path}",
            use_container_width=True
        )

    # Preview questions and answers
    st.subheader("👀 Preview Questions & Answers")

    for i, question in enumerate(answered_questions["questions"][:5]):  # Show first 5
        with st.expander(f"Question {i+1}: {question['question_text'][:100]}..."):
            st.write(f"**Type:** {question['question_type']}")

            if question.get('options'):
                st.write("**Options:**")
                for j, option in enumerate(question['options']):
                    st.write(f"  {chr(65+j)}. {option}")

            st.write(f"**Answer:** {question.get('answer', 'No answer')}")

            if question.get('metadata'):
                st.write(f"**Source Page:** {question['metadata'].get('page_number', 'Unknown')}")

    if len(answered_questions["questions"]) > 5:
        st.info(f"Showing first 5 questions. Total: {len(answered_questions['questions'])}")

if __name__ == "__main__":
    main()
