#!/usr/bin/env python3
"""
Test script to verify the improvements made to the PDF Question Extraction system.
"""

import json
from pathlib import Path
from utils.pdf_generator import PDFGenerator
from services.rag_agent import RAGAgent
from config import QUESTION_TYPES

def test_answer_formatting():
    """Test the answer formatting improvements."""

    print("Testing answer formatting improvements...")

    # Test data with different answer formats
    test_questions = [
        {
            "question_text": "Which movie features the song 'Jai Ho'?",
            "question_type": QUESTION_TYPES.MULTIPLE_CHOICE_SINGLE,
            "options": ["Om Shanti Om", "Slumdog Millionaire", "Rab Ne Bana Di Jodi", "3 Idiots"],
            "answer": "A. Om Shanti Om\nB. Slumdog Millionaire ✓\nC. Rab Ne Bana Di Jodi\nD. 3 Idiots",
            "metadata": {"page_number": 1},
            "context_used": 5
        },
        {
            "question_text": "Who directed the film 'Rang De Basanti'?",
            "question_type": QUESTION_TYPES.MULTIPLE_CHOICE_SINGLE,
            "options": ["Karan Johar", "Rakeysh Omprakash Mehra", "Aditya Chopra", "Sanjay Leela Bhansali"],
            "answer": "A. Karan Johar\nB. Rakeysh Omprakash Mehra ✓\nC. Aditya Chopra\nD. Sanjay Leela Bhansali",
            "metadata": {"page_number": 1},
            "context_used": 5
        },
        {
            "question_text": "Which actor played the lead role in the movie 'Ghajini'?",
            "question_type": QUESTION_TYPES.MULTIPLE_CHOICE_SINGLE,
            "options": ["Shah Rukh Khan", "Aamir Khan", "Salman Khan", "Hrithik Roshan"],
            "answer": "A. Shah Rukh Khan\nB. Aamir Khan ✓\nC. Salman Khan\nD. Hrithik Roshan",
            "metadata": {"page_number": 1},
            "context_used": 5
        }
    ]

    # Create test JSON structure
    test_json = {
        "total_questions": len(test_questions),
        "extraction_timestamp": 1234567890,
        "rag_processing_complete": True,
        "questions": test_questions
    }

    # Test PDF generation
    pdf_generator = PDFGenerator()
    output_path = "test_formatted_answers.pdf"

    try:
        success = pdf_generator.generate_answer_pdf(test_json, output_path)
        if success:
            print(f"✅ Successfully generated test PDF: {output_path}")
            print("✅ Answer formatting test passed!")

            # Check if file exists and has content
            if Path(output_path).exists() and Path(output_path).stat().st_size > 0:
                print(f"✅ PDF file created with size: {Path(output_path).stat().st_size} bytes")
            else:
                print("❌ PDF file is empty or not created properly")

        else:
            print("❌ Failed to generate test PDF")

    except Exception as e:
        print(f"❌ Error during PDF generation: {str(e)}")

    return success

def test_post_processing():
    """Test the answer post-processing functionality."""

    print("\nTesting answer post-processing...")

    # Mock RAG agent for testing post-processing
    class MockRAGAgent:
        def _post_process_answer(self, answer: str, question_type: str) -> str:
            # Import the actual method logic
            from services.rag_agent import RAGAgent
            from services.vector_store import VectorStore

            # Create a dummy vector store (won't be used for this test)
            class DummyVectorStore:
                pass

            dummy_vs = DummyVectorStore()
            rag_agent = RAGAgent.__new__(RAGAgent)  # Create without calling __init__
            return rag_agent._post_process_answer(answer, question_type)

    mock_agent = MockRAGAgent()

    # Test cases
    test_cases = [
        {
            "input": "Answer: A. Option 1 B. Option 2 ✓ C. Option 3",
            "question_type": QUESTION_TYPES.MULTIPLE_CHOICE_SINGLE,
            "expected_contains": ["A. Option 1", "B. Option 2 ✓", "C. Option 3"]
        },
        {
            "input": "The answer is: A. Wrong B. Correct ✓ C. Also Wrong",
            "question_type": QUESTION_TYPES.MULTIPLE_CHOICE_SINGLE,
            "expected_contains": ["A. Wrong", "B. Correct ✓", "C. Also Wrong"]
        }
    ]

    all_passed = True

    for i, test_case in enumerate(test_cases):
        try:
            result = mock_agent._post_process_answer(test_case["input"], test_case["question_type"])
            print(f"Test {i+1}:")
            print(f"  Input: {test_case['input']}")
            print(f"  Output: {result}")

            # Check if expected content is present
            for expected in test_case["expected_contains"]:
                if expected not in result:
                    print(f"  ❌ Expected '{expected}' not found in result")
                    all_passed = False
                else:
                    print(f"  ✅ Found expected content: '{expected}'")

        except Exception as e:
            print(f"  ❌ Error in test {i+1}: {str(e)}")
            all_passed = False

    if all_passed:
        print("✅ All post-processing tests passed!")
    else:
        print("❌ Some post-processing tests failed!")

    return all_passed

def main():
    """Run all improvement tests."""

    print("=" * 60)
    print("Testing PDF Question Extraction System Improvements")
    print("=" * 60)

    # Test 1: Answer formatting
    formatting_success = test_answer_formatting()

    # Test 2: Post-processing
    processing_success = test_post_processing()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    if formatting_success:
        print("✅ Answer formatting improvements: PASSED")
    else:
        print("❌ Answer formatting improvements: FAILED")

    if processing_success:
        print("✅ Answer post-processing: PASSED")
    else:
        print("❌ Answer post-processing: FAILED")

    if formatting_success and processing_success:
        print("\n🎉 All improvements are working correctly!")
        return True
    else:
        print("\n⚠️  Some improvements need attention.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
