#!/usr/bin/env python3
"""
Test script to verify Streamlit download functionality improvements.
"""

import streamlit as st
import json
from pathlib import Path
from utils.pdf_generator import generate_answer_pdf

def test_download_functionality():
    """Test the download button functionality."""
    
    st.title("Download Functionality Test")
    
    # Create test data
    test_questions = [
        {
            "question_text": "Test question?",
            "question_type": "multiple_choice_single",
            "options": ["Option A", "Option B", "Option C"],
            "answer": "A. Option A B. Option B ✓ C. Option C",
            "metadata": {"page_number": 1},
            "context_used": 3
        }
    ]
    
    test_json = {
        "total_questions": 1,
        "extraction_timestamp": 1234567890,
        "rag_processing_complete": True,
        "questions": test_questions
    }
    
    # Generate test PDF
    output_pdf_path = "test_download.pdf"
    
    if st.button("Generate Test PDF"):
        with st.spinner("Generating test PDF..."):
            success = generate_answer_pdf(test_json, output_pdf_path)
            
            if success:
                st.success("✅ Test PDF generated successfully!")
                
                # Test download buttons
                st.subheader("📥 Download Test")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if Path(output_pdf_path).exists():
                        with open(output_pdf_path, "rb") as pdf_file:
                            pdf_data = pdf_file.read()
                            st.download_button(
                                label="📄 Download Test PDF",
                                data=pdf_data,
                                file_name=output_pdf_path,
                                mime="application/pdf",
                                key=f"download_pdf_{output_pdf_path}",
                                use_container_width=True
                            )
                
                with col2:
                    json_str = json.dumps(test_json, indent=2)
                    st.download_button(
                        label="📋 Download Test JSON",
                        data=json_str,
                        file_name="test_download.json",
                        mime="application/json",
                        key=f"download_json_{output_pdf_path}",
                        use_container_width=True
                    )
                
                st.info("✅ If the page doesn't refresh when you click download, the fix is working!")
                
            else:
                st.error("❌ Failed to generate test PDF")

if __name__ == "__main__":
    test_download_functionality()
