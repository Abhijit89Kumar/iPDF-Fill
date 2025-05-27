#!/usr/bin/env python3
from utils.pdf_generator import PDFGenerator
from config import QUESTION_TYPES

# Test with the exact format from the screenshot
test_question = {
    'question_text': 'Which movie features the song "Jai Ho"?',
    'question_type': QUESTION_TYPES.MULTIPLE_CHOICE_SINGLE,
    'options': ['Om Shanti Om', 'Slumdog Millionaire', 'Rab Ne Bana Di Jodi', '3 Idiots'],
    'answer': 'A. Om Shanti Om\nB. Slumdog Millionaire ✓\nC. Rab Ne Bana Di Jodi\nD. 3 Idiots',
    'metadata': {'page_number': 1},
    'context_used': 5
}

test_json = {
    'total_questions': 1,
    'extraction_timestamp': 1234567890,
    'rag_processing_complete': True,
    'questions': [test_question]
}

pdf_gen = PDFGenerator()
success = pdf_gen.generate_answer_pdf(test_json, 'format_test.pdf')
print(f'PDF generation: {"SUCCESS" if success else "FAILED"}')

# Test the formatting function directly
formatted = pdf_gen._format_answer_by_type(
    QUESTION_TYPES.MULTIPLE_CHOICE_SINGLE,
    'A. Om Shanti Om\nB. Slumdog Millionaire ✓\nC. Rab Ne Bana Di Jodi\nD. 3 Idiots',
    ['Om Shanti Om', 'Slumdog Millionaire', 'Rab Ne Bana Di Jodi', '3 Idiots']
)
print(f'Formatted answer: {formatted}')
