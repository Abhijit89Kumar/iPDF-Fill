"""
PDF generation utilities for creating answer sheets.
"""
import logging
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black, blue, red, green
from datetime import datetime
import json

from config import QUESTION_TYPES

logger = logging.getLogger(__name__)

class PDFGenerator:
    """Generates PDF documents with questions and answers."""

    def __init__(self, page_size=A4):
        """
        Initialize PDF generator.

        Args:
            page_size: Page size for the PDF
        """
        self.page_size = page_size
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Set up custom paragraph styles."""
        # Question style
        self.question_style = ParagraphStyle(
            'QuestionStyle',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=6,
            textColor=black,
            fontName='Helvetica-Bold'
        )

        # Answer style
        self.answer_style = ParagraphStyle(
            'AnswerStyle',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            textColor=blue,
            leftIndent=20
        )

        # Option style
        self.option_style = ParagraphStyle(
            'OptionStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=3,
            leftIndent=30
        )

        # Header style
        self.header_style = ParagraphStyle(
            'HeaderStyle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            textColor=black,
            alignment=1  # Center alignment
        )

        # Metadata style
        self.metadata_style = ParagraphStyle(
            'MetadataStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=red,
            spaceAfter=6
        )

    def generate_answer_pdf(self, questions_json: Dict[str, Any], output_path: str) -> bool:
        """
        Generate PDF with questions and answers.

        Args:
            questions_json: JSON containing questions and answers
            output_path: Path for the output PDF

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Generating answer PDF: {output_path}")

            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=self.page_size,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )

            # Build content
            story = []

            # Add header
            story.extend(self._create_header(questions_json))

            # Add questions and answers
            for i, question_data in enumerate(questions_json["questions"]):
                story.extend(self._create_question_section(question_data, i + 1))

                # Add page break every 3 questions (optional)
                if (i + 1) % 3 == 0 and i < len(questions_json["questions"]) - 1:
                    story.append(PageBreak())

            # Build PDF
            doc.build(story)

            logger.info(f"Successfully generated PDF: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            return False

    def _create_header(self, questions_json: Dict[str, Any]) -> List:
        """Create header section for the PDF."""
        story = []

        # Title
        title = Paragraph("Question and Answer Sheet", self.header_style)
        story.append(title)
        story.append(Spacer(1, 12))

        # Metadata
        total_questions = questions_json.get("total_questions", 0)
        timestamp = datetime.fromtimestamp(
            questions_json.get("extraction_timestamp", 0)
        ).strftime("%Y-%m-%d %H:%M:%S")

        metadata_text = f"""
        <b>Total Questions:</b> {total_questions}<br/>
        <b>Processing Date:</b> {timestamp}<br/>
        <b>RAG Processing:</b> {'Complete' if questions_json.get('rag_processing_complete') else 'Incomplete'}
        """

        metadata = Paragraph(metadata_text, self.metadata_style)
        story.append(metadata)
        story.append(Spacer(1, 20))

        return story

    def _create_question_section(self, question_data: Dict[str, Any], question_num: int) -> List:
        """Create a section for a single question and answer."""
        story = []

        # Question number and text
        question_text = question_data.get("question_text", "No question text")
        question_type = question_data.get("question_type", "unknown")

        question_header = f"<b>Question {question_num}:</b> {self._escape_html(question_text)}"
        story.append(Paragraph(question_header, self.question_style))

        # Question type
        type_text = f"<i>Type: {self._format_question_type(question_type)}</i>"
        story.append(Paragraph(type_text, self.metadata_style))

        # Handle different question types and their answers
        answer = question_data.get("answer", "No answer provided")
        options = question_data.get("options")

        # Format answer based on question type
        formatted_answer = self._format_answer_by_type(question_type, answer, options, question_text)

        story.append(Spacer(1, 6))
        story.append(Paragraph(formatted_answer, self.answer_style))

        # Metadata
        page_num = question_data.get("metadata", {}).get("page_number", "Unknown")
        context_used = question_data.get("context_used", 0)

        meta_text = f"<i>Source Page: {page_num} | Context Chunks Used: {context_used}</i>"
        story.append(Paragraph(meta_text, self.metadata_style))

        story.append(Spacer(1, 15))

        return story

    def _format_answer_by_type(self, question_type: str, answer: str, options: List[str] = None, question_text: str = "") -> str:
        """Format answer based on question type to match input format."""
        if question_type == QUESTION_TYPES.MULTIPLE_CHOICE_SINGLE or question_type == QUESTION_TYPES.MULTIPLE_CHOICE_MULTI:
            # If answer already contains tick marks, use it as is
            if "✓" in answer:
                return f"<b>Answer:</b><br/>{self._escape_html(answer)}"
            else:
                # Fallback to traditional format if tick marks not found
                return f"<b>Answer:</b> {self._escape_html(answer)}"

        elif question_type == QUESTION_TYPES.TRUE_FALSE:
            # If answer already contains tick marks, use it as is
            if "✓" in answer:
                return f"<b>Answer:</b><br/>{self._escape_html(answer)}"
            else:
                # Fallback to traditional format
                return f"<b>Answer:</b> {self._escape_html(answer)}"

        elif question_type == QUESTION_TYPES.FILL_IN_BLANK:
            # For fill-in-blank, show the complete filled sentence
            return f"<b>Completed Text:</b><br/>{self._escape_html(answer)}"

        elif question_type == QUESTION_TYPES.MATCH_FOLLOWING:
            # For match-the-following, show the matched pairs
            return f"<b>Matches:</b><br/>{self._escape_html(answer)}"

        elif question_type == QUESTION_TYPES.CHECKBOX:
            # For checkbox questions, show the checked/unchecked options
            return f"<b>Answer:</b><br/>{self._escape_html(answer)}"

        else:
            # For all other question types, use standard format
            return f"<b>Answer:</b> {self._escape_html(answer)}"

    def _format_question_type(self, question_type: str) -> str:
        """Format question type for display."""
        type_mapping = {
            QUESTION_TYPES.MULTIPLE_CHOICE_SINGLE: "Multiple Choice (Single Answer)",
            QUESTION_TYPES.MULTIPLE_CHOICE_MULTI: "Multiple Choice (Multiple Answers)",
            QUESTION_TYPES.FILL_IN_BLANK: "Fill in the Blank",
            QUESTION_TYPES.TRUE_FALSE: "True/False",
            QUESTION_TYPES.MATCH_FOLLOWING: "Match the Following",
            QUESTION_TYPES.TEXTUAL_ANSWER: "Textual Answer",
            QUESTION_TYPES.CHECKBOX: "Checkbox",
            QUESTION_TYPES.NUMERICAL_ANSWER: "Numerical Answer",
            QUESTION_TYPES.DATE_TIME: "Date/Time",
            QUESTION_TYPES.ORDERING_SEQUENCE: "Ordering/Sequence",
            QUESTION_TYPES.CATEGORIZATION: "Categorization",
            QUESTION_TYPES.COMPARISON: "Comparison",
            QUESTION_TYPES.CAUSE_EFFECT: "Cause & Effect",
            QUESTION_TYPES.DEFINITION: "Definition",
            QUESTION_TYPES.EXPLANATION: "Explanation",
            QUESTION_TYPES.ANALYSIS: "Analysis",
            QUESTION_TYPES.EVALUATION: "Evaluation"
        }
        return type_mapping.get(question_type, question_type.replace("_", " ").title())

    def _escape_html(self, text: str) -> str:
        """Escape HTML characters in text."""
        if not text:
            return ""

        text = str(text)
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        text = text.replace('"', "&quot;")
        text = text.replace("'", "&#x27;")

        return text

def generate_answer_pdf(questions_json: Dict[str, Any], output_path: str) -> bool:
    """
    Generate PDF with questions and answers.

    Args:
        questions_json: JSON containing questions and answers
        output_path: Path for the output PDF

    Returns:
        True if successful, False otherwise
    """
    generator = PDFGenerator()
    return generator.generate_answer_pdf(questions_json, output_path)

def save_json_backup(questions_json: Dict[str, Any], output_path: str) -> bool:
    """
    Save JSON backup of questions and answers.

    Args:
        questions_json: JSON data to save
        output_path: Path for the output JSON file

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(questions_json, f, indent=2, ensure_ascii=False)

        logger.info(f"JSON backup saved: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error saving JSON backup: {str(e)}")
        return False
