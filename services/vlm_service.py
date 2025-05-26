"""
VLM service for question extraction using SambaNova API.
"""
import openai
import json
import time
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from config import API_CONFIG, PROCESSING_CONFIG, VLM_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

@dataclass
class ExtractedQuestion:
    """Data class for extracted questions."""
    question_id: str
    question_text: str
    question_type: str
    options: Optional[List[str]]
    metadata: Dict[str, Any]

class VLMService:
    """Service for interacting with SambaNova VLM API."""
    
    def __init__(self):
        """Initialize VLM service with API configuration."""
        self.client = openai.OpenAI(
            api_key=API_CONFIG.sambanova_api_key,
            base_url=API_CONFIG.sambanova_base_url,
        )
        self.model = API_CONFIG.sambanova_model
        self.max_retries = PROCESSING_CONFIG.max_retries
        
    def extract_questions_from_image(self, image_base64: str, page_number: int) -> List[ExtractedQuestion]:
        """
        Extract questions from a single image using VLM.
        
        Args:
            image_base64: Base64 encoded image
            page_number: Page number for metadata
            
        Returns:
            List of extracted questions
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Extracting questions from page {page_number}, attempt {attempt + 1}")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": VLM_SYSTEM_PROMPT
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Extract all questions from this image (Page {page_number}). Return a valid JSON array as specified."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {"url": image_base64}
                                }
                            ]
                        }
                    ],
                    temperature=PROCESSING_CONFIG.vlm_temperature,
                    top_p=PROCESSING_CONFIG.vlm_top_p
                )
                
                content = response.choices[0].message.content
                logger.debug(f"VLM response for page {page_number}: {content}")
                
                # Parse JSON response
                questions_data = self._parse_vlm_response(content, page_number)
                
                # Convert to ExtractedQuestion objects
                questions = []
                for q_data in questions_data:
                    question = ExtractedQuestion(
                        question_id=q_data.get("question_id", f"page_{page_number}_q_{len(questions) + 1}"),
                        question_text=q_data.get("question_text", ""),
                        question_type=q_data.get("question_type", "textual_answer"),
                        options=q_data.get("options"),
                        metadata={
                            **q_data.get("metadata", {}),
                            "page_number": page_number,
                            "extraction_attempt": attempt + 1
                        }
                    )
                    questions.append(question)
                
                logger.info(f"Successfully extracted {len(questions)} questions from page {page_number}")
                return questions
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for page {page_number}: {str(e)}")
                if attempt == self.max_retries - 1:
                    logger.error(f"All attempts failed for page {page_number}")
                    return []
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return []
    
    def _parse_vlm_response(self, content: str, page_number: int) -> List[Dict[str, Any]]:
        """
        Parse VLM response and extract JSON data.
        
        Args:
            content: Raw response content
            page_number: Page number for error context
            
        Returns:
            List of question dictionaries
        """
        try:
            # Try to find JSON in the response
            content = content.strip()
            
            # Look for JSON array markers
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = content[start_idx:end_idx]
                questions_data = json.loads(json_str)
                
                if isinstance(questions_data, list):
                    return questions_data
                else:
                    logger.warning(f"Expected list but got {type(questions_data)} for page {page_number}")
                    return []
            else:
                logger.warning(f"No JSON array found in response for page {page_number}")
                return []
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error for page {page_number}: {str(e)}")
            logger.debug(f"Raw content: {content}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error parsing response for page {page_number}: {str(e)}")
            return []

def extract_questions_from_images(images: List[tuple]) -> List[ExtractedQuestion]:
    """
    Extract questions from multiple images.
    
    Args:
        images: List of (page_number, base64_image) tuples
        
    Returns:
        List of all extracted questions
    """
    vlm_service = VLMService()
    all_questions = []
    
    for page_number, image_base64 in images:
        questions = vlm_service.extract_questions_from_image(image_base64, page_number)
        all_questions.extend(questions)
    
    logger.info(f"Total questions extracted: {len(all_questions)}")
    return all_questions

def questions_to_json(questions: List[ExtractedQuestion]) -> Dict[str, Any]:
    """
    Convert extracted questions to a structured JSON format.
    
    Args:
        questions: List of extracted questions
        
    Returns:
        Structured JSON dictionary
    """
    json_data = {
        "total_questions": len(questions),
        "extraction_timestamp": time.time(),
        "questions": []
    }
    
    for question in questions:
        question_dict = {
            "question_id": question.question_id,
            "question_text": question.question_text,
            "question_type": question.question_type,
            "options": question.options,
            "metadata": question.metadata,
            "answer": None  # To be filled by RAG system
        }
        json_data["questions"].append(question_dict)
    
    return json_data
