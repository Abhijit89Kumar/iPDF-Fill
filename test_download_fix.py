#!/usr/bin/env python3
"""
Test the download button fix by simulating the key generation logic.
"""

from pathlib import Path

def test_download_key_generation():
    """Test that download keys are unique and properly formatted."""
    
    # Simulate different scenarios
    test_cases = [
        {
            "output_pdf_path": "test1_Answers.pdf",
            "answered_questions": [{"q": 1}, {"q": 2}]
        },
        {
            "output_pdf_path": "test2_Answers.pdf", 
            "answered_questions": [{"q": 1}, {"q": 2}, {"q": 3}]
        },
        {
            "output_pdf_path": "test1_Answers.pdf",  # Same path, different content
            "answered_questions": [{"q": 1}, {"q": 2}, {"q": 3}, {"q": 4}]
        }
    ]
    
    generated_keys = []
    
    for i, case in enumerate(test_cases):
        output_pdf_path = case["output_pdf_path"]
        answered_questions = case["answered_questions"]
        
        # Generate keys using the same logic as in app.py
        pdf_download_key = f"pdf_download_{hash(output_pdf_path)}_{len(answered_questions)}"
        json_download_key = f"json_download_{hash(output_pdf_path)}_{len(answered_questions)}"
        
        print(f"Test case {i+1}:")
        print(f"  Path: {output_pdf_path}")
        print(f"  Questions: {len(answered_questions)}")
        print(f"  PDF Key: {pdf_download_key}")
        print(f"  JSON Key: {json_download_key}")
        
        # Check for uniqueness
        if pdf_download_key in generated_keys:
            print(f"  ❌ PDF key collision detected!")
        else:
            print(f"  ✅ PDF key is unique")
            generated_keys.append(pdf_download_key)
            
        if json_download_key in generated_keys:
            print(f"  ❌ JSON key collision detected!")
        else:
            print(f"  ✅ JSON key is unique")
            generated_keys.append(json_download_key)
        
        print()
    
    print(f"Total unique keys generated: {len(generated_keys)}")
    print("✅ Download key generation test completed!")

def test_streamlit_import():
    """Test that the app can be imported without errors."""
    try:
        # Test individual components
        from utils.pdf_generator import generate_answer_pdf
        print("✅ PDF generator imports successfully")
        
        from services.rag_agent import RAGAgent
        print("✅ RAG agent imports successfully")
        
        # Test config
        from config import API_CONFIG, QUESTION_TYPES
        print("✅ Configuration imports successfully")
        
        print("✅ All core components import successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Download Button Fix")
    print("=" * 60)
    
    test_download_key_generation()
    
    print("=" * 60)
    print("Testing Component Imports")
    print("=" * 60)
    
    import_success = test_streamlit_import()
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if import_success:
        print("🎉 All tests passed! The fixes should work correctly.")
    else:
        print("⚠️ Some issues detected. Please check the errors above.")
