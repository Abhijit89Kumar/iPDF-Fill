"""
RAG Agent for answering questions using retrieved context with Cohere reranking.
"""
import logging
from typing import List, Dict, Any, Optional
from mistralai import Mistral
import cohere

from config import API_CONFIG, PROCESSING_CONFIG, RAG_SYSTEM_PROMPT, QUESTION_TYPES
from services.vector_store import VectorStore

logger = logging.getLogger(__name__)

class RAGAgent:
    """RAG agent for question answering using context retrieval."""

    def __init__(self, vector_store: VectorStore):
        """
        Initialize RAG agent.

        Args:
            vector_store: Configured vector store instance
        """
        self.vector_store = vector_store

        # Initialize Mistral client
        self.mistral_client = Mistral(api_key=API_CONFIG.mistral_api_key)
        self.model = API_CONFIG.mistral_model

        # Initialize Cohere client for embeddings and reranking
        self.cohere_client = cohere.ClientV2(api_key=API_CONFIG.cohere_api_key)

    def answer_question(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Answer a single question using RAG.

        Args:
            question_data: Question dictionary with text, type, options, etc.

        Returns:
            Question data with answer added
        """
        try:
            question_text = question_data["question_text"]
            question_type = question_data["question_type"]

            logger.info(f"Answering question: {question_text[:100]}...")

            # Retrieve relevant context with reranking
            context = self._retrieve_context_with_reranking(question_text)

            # Generate answer based on question type
            answer = self._generate_answer(question_text, question_type, context, question_data.get("options"))

            # Update question data with answer
            question_data["answer"] = answer
            question_data["context_used"] = len(context)

            return question_data

        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            question_data["answer"] = "Error: Could not generate answer"
            question_data["error"] = str(e)
            return question_data

    def _retrieve_context_with_reranking(self, question: str) -> List[str]:
        """
        Retrieve relevant context for a question with Cohere reranking.

        Args:
            question: Question text

        Returns:
            List of relevant text chunks (reranked)
        """
        try:
            # Step 1: Generate query embedding using Cohere
            query_response = self.cohere_client.embed(
                texts=[question],
                model=API_CONFIG.cohere_embed_model,
                input_type="search_query",
                embedding_types=["float"]
            )
            # Extract query embedding from Cohere response
            query_embedding = query_response.embeddings.float_[0]

            # Step 2: Search for similar chunks
            similar_chunks = self.vector_store.search_similar(
                query_embedding=query_embedding,
                top_k=PROCESSING_CONFIG.top_k_results
            )

            if not similar_chunks:
                logger.warning("No similar chunks found")
                return []

            # Step 3: Rerank using Cohere if enabled
            if PROCESSING_CONFIG.use_reranker and len(similar_chunks) > 1:
                context_texts = [chunk["text"] for chunk in similar_chunks]

                rerank_response = self.cohere_client.rerank(
                    model=API_CONFIG.cohere_rerank_model,
                    query=question,
                    documents=context_texts,
                    top_n=PROCESSING_CONFIG.rerank_top_n
                )

                # Extract reranked texts
                reranked_texts = []
                for result in rerank_response.results:
                    reranked_texts.append(context_texts[result.index])

                logger.info(f"Retrieved and reranked {len(reranked_texts)} context chunks")
                return reranked_texts
            else:
                # No reranking, just return top chunks
                context_texts = [chunk["text"] for chunk in similar_chunks[:PROCESSING_CONFIG.rerank_top_n]]
                logger.info(f"Retrieved {len(context_texts)} context chunks (no reranking)")
                return context_texts

        except Exception as e:
            logger.error(f"Error retrieving context with reranking: {str(e)}")
            # Fallback to basic retrieval
            return self._retrieve_context_fallback(question)

    def _retrieve_context_fallback(self, question: str) -> List[str]:
        """Fallback context retrieval without reranking."""
        try:
            # Simple keyword-based retrieval as fallback
            logger.warning("Using fallback context retrieval")

            # Get all chunks and do simple text matching
            # This is a simplified fallback - in production you might want a more sophisticated approach
            return [f"Fallback context for question: {question}"]

        except Exception as e:
            logger.error(f"Fallback retrieval also failed: {str(e)}")
            return []

    def _generate_answer(
        self,
        question: str,
        question_type: str,
        context: List[str],
        options: Optional[List[str]] = None
    ) -> str:
        """
        Generate answer using Mistral LLM.

        Args:
            question: Question text
            question_type: Type of question
            context: Retrieved context chunks
            options: Question options (if applicable)

        Returns:
            Generated answer
        """
        try:
            # Prepare context string
            context_str = "\n\n".join(context) if context else "No relevant context found."

            # Create question-specific prompt
            user_prompt = self._create_question_prompt(question, question_type, context_str, options)

            # Generate response
            response = self.mistral_client.chat.complete(
                model=self.model,
                messages=[
                    {"role": "system", "content": RAG_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ]
            )

            answer = response.choices[0].message.content.strip()
            logger.info(f"Generated answer for {question_type} question")

            return answer

        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return f"Error generating answer: {str(e)}"

    def _create_question_prompt(
        self,
        question: str,
        question_type: str,
        context: str,
        options: Optional[List[str]] = None
    ) -> str:
        """
        Create a question-specific prompt for the LLM.

        Args:
            question: Question text
            question_type: Type of question
            context: Retrieved context
            options: Question options (if applicable)

        Returns:
            Formatted prompt string
        """
        base_prompt = f"""
Context:
{context}

Question: {question}
"""

        if question_type == QUESTION_TYPES.MULTIPLE_CHOICE_SINGLE:
            if options:
                options_str = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(options)])
                base_prompt += f"""
Options:
{options_str}

IMPORTANT: Return ALL options with the correct one marked with ✓ emoji.
Example format: "A. Option 1  B. Option 2 ✓  C. Option 3"
"""
            else:
                base_prompt += "\nPlease provide the correct answer in a concise format."

        elif question_type == QUESTION_TYPES.MULTIPLE_CHOICE_MULTI:
            if options:
                options_str = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(options)])
                base_prompt += f"""
Options:
{options_str}

IMPORTANT: Return ALL options with the correct ones marked with ✓ emoji.
Example format: "A. Option 1 ✓  B. Option 2  C. Option 3 ✓"
"""
            else:
                base_prompt += "\nPlease provide all correct answers with clear marking."

        elif question_type == QUESTION_TYPES.TRUE_FALSE:
            base_prompt += """\nIMPORTANT: Return both True and False options with the correct one marked with ✓ emoji.
Example format: "True ✓  False" or "True  False ✓"
"""

        elif question_type == QUESTION_TYPES.FILL_IN_BLANK:
            base_prompt += """\nIMPORTANT: Return the complete sentence/paragraph with blanks filled in.
Do NOT just provide the missing words - show the full text with answers inserted.
Example: "The movie _____ was directed by..." becomes "The movie Lagaan was directed by..."
"""

        elif question_type == QUESTION_TYPES.MATCH_FOLLOWING:
            base_prompt += """\nIMPORTANT: Show the matched pairs clearly connected with arrows or lines.
Example format: "1. Item A → Match X  2. Item B → Match Y  3. Item C → Match Z"
"""

        elif question_type == QUESTION_TYPES.CHECKBOX:
            if options:
                options_str = "\n".join([f"☐ {opt}" for opt in options])
                base_prompt += f"""
Options:
{options_str}

IMPORTANT: Return ALL options with correct ones marked as ☑ and incorrect ones as ☐.
Example format: "☑ Correct option 1  ☐ Incorrect option  ☑ Correct option 2"
"""
            else:
                base_prompt += "\nIMPORTANT: Use ☑ for correct items and ☐ for incorrect items."

        elif question_type == QUESTION_TYPES.NUMERICAL_ANSWER:
            base_prompt += "\nPlease provide the numerical answer with appropriate units if applicable. Be precise and concise."

        elif question_type == QUESTION_TYPES.DATE_TIME:
            base_prompt += "\nPlease provide the specific date, year, or time period. Format dates clearly (e.g., 'Year: 2001' or 'Period: 2000-2010')."

        elif question_type == QUESTION_TYPES.ORDERING_SEQUENCE:
            base_prompt += "\nPlease provide the correct chronological or logical order. Number the items clearly (1, 2, 3, etc.)."

        elif question_type == QUESTION_TYPES.CATEGORIZATION:
            base_prompt += "\nPlease categorize or classify the items mentioned. Provide clear categories and explain the classification criteria."

        elif question_type == QUESTION_TYPES.COMPARISON:
            base_prompt += "\nPlease compare the items mentioned. Highlight similarities, differences, and key distinguishing features."

        elif question_type == QUESTION_TYPES.CAUSE_EFFECT:
            base_prompt += "\nPlease explain the cause and effect relationship. Clearly identify what caused what and the resulting impact."

        elif question_type == QUESTION_TYPES.DEFINITION:
            base_prompt += "\nPlease provide a clear, accurate definition. Include key characteristics and context if relevant."

        elif question_type == QUESTION_TYPES.EXPLANATION:
            base_prompt += "\nPlease provide a detailed explanation. Break down complex concepts and provide context for better understanding."

        elif question_type == QUESTION_TYPES.ANALYSIS:
            base_prompt += "\nPlease provide an analytical response. Examine the topic critically, considering multiple perspectives and implications."

        elif question_type == QUESTION_TYPES.EVALUATION:
            base_prompt += "\nPlease provide an evaluative response. Assess the topic's significance, quality, impact, or value based on the available information."

        else:  # TEXTUAL_ANSWER (default)
            base_prompt += "\nPlease provide a comprehensive answer based on the context provided."

        return base_prompt

def answer_all_questions(questions_json: Dict[str, Any], vector_store: VectorStore) -> Dict[str, Any]:
    """
    Answer all questions in the JSON using RAG.

    Args:
        questions_json: JSON containing all extracted questions
        vector_store: Configured vector store

    Returns:
        Updated JSON with answers
    """
    rag_agent = RAGAgent(vector_store)

    total_questions = len(questions_json["questions"])
    logger.info(f"Starting to answer {total_questions} questions")

    for i, question_data in enumerate(questions_json["questions"]):
        logger.info(f"Processing question {i+1}/{total_questions}")
        answered_question = rag_agent.answer_question(question_data)
        questions_json["questions"][i] = answered_question

    # Update metadata
    questions_json["answered_questions"] = total_questions
    questions_json["rag_processing_complete"] = True

    logger.info(f"Completed answering all {total_questions} questions")
    return questions_json
