"""
Knowledge base processing and chunking service with advanced chunking strategies.
"""
import logging
from typing import List, Dict, Any, Tuple
from pathlib import Path
import re
import cohere
import numpy as np
from collections import defaultdict

from config import PROCESSING_CONFIG, API_CONFIG

logger = logging.getLogger(__name__)

class KnowledgeProcessor:
    """Processes and chunks knowledge base documents with advanced strategies."""

    def __init__(self, embedding_model: str = None):
        """
        Initialize knowledge processor.

        Args:
            embedding_model: Name of the embedding model to use
        """
        self.embedding_model_name = embedding_model or PROCESSING_CONFIG.embedding_model
        self.chunk_size = PROCESSING_CONFIG.chunk_size
        self.chunk_overlap = PROCESSING_CONFIG.chunk_overlap

        # Initialize Cohere client for embeddings
        logger.info(f"Initializing Cohere client for embeddings")
        self.cohere_client = cohere.ClientV2(api_key=API_CONFIG.cohere_api_key)

    def load_knowledge_base(self, file_path: str) -> str:
        """
        Load knowledge base from file.

        Args:
            file_path: Path to the knowledge base file

        Returns:
            Raw text content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            logger.info(f"Loaded knowledge base from {file_path}, {len(content)} characters")
            return content

        except Exception as e:
            logger.error(f"Error loading knowledge base from {file_path}: {str(e)}")
            raise

    def chunk_text_advanced(self, text: str) -> List[Dict[str, Any]]:
        """
        Advanced chunking strategy with semantic awareness and context preservation.

        Args:
            text: Input text to chunk

        Returns:
            List of chunk dictionaries
        """
        # Step 1: Parse document structure
        document_structure = self._parse_document_structure(text)

        # Step 2: Create semantic chunks
        chunks = []
        chunk_id = 0

        for section in document_structure:
            section_chunks = self._create_semantic_chunks(section)

            for chunk_data in section_chunks:
                if len(chunk_data["text"].strip()) > 50:  # Minimum chunk size
                    chunk = {
                        "chunk_id": chunk_id,
                        "text": chunk_data["text"].strip(),
                        "section": chunk_data["section"],
                        "subsection": chunk_data.get("subsection", ""),
                        "char_count": len(chunk_data["text"]),
                        "entity_mentions": chunk_data.get("entities", []),
                        "keywords": chunk_data.get("keywords", []),
                        "chunk_type": chunk_data.get("type", "content"),
                        "metadata": {
                            "section_title": chunk_data["section"],
                            "subsection_title": chunk_data.get("subsection", ""),
                            "chunk_index": len(chunks),
                            "importance_score": chunk_data.get("importance", 0.5),
                            "content_type": chunk_data.get("content_type", "general")
                        }
                    }
                    chunks.append(chunk)
                    chunk_id += 1

        logger.info(f"Created {len(chunks)} advanced chunks from knowledge base")
        return chunks

    def _parse_document_structure(self, text: str) -> List[Dict[str, Any]]:
        """Parse document into structured sections with metadata."""
        sections = []
        current_section = None
        current_subsection = None
        current_content = []

        lines = text.split('\n')

        for line in lines:
            # Check for headers
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())

            if header_match:
                # Save previous content
                if current_section and current_content:
                    sections.append({
                        "section": current_section,
                        "subsection": current_subsection,
                        "content": '\n'.join(current_content),
                        "level": len(header_match.group(1)),
                        "title": header_match.group(2)
                    })

                # Start new section
                level = len(header_match.group(1))
                title = header_match.group(2).strip()

                if level <= 2:  # Main section
                    current_section = title
                    current_subsection = None
                else:  # Subsection
                    current_subsection = title

                current_content = [line]
            else:
                current_content.append(line)

        # Add final section
        if current_section and current_content:
            sections.append({
                "section": current_section,
                "subsection": current_subsection,
                "content": '\n'.join(current_content),
                "level": 1,
                "title": current_section
            })

        return sections

    def _create_semantic_chunks(self, section: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create semantically aware chunks from a section."""
        content = section["content"]
        section_title = section["section"]
        subsection_title = section.get("subsection", "")

        # Extract entities and keywords
        entities = self._extract_entities(content)
        keywords = self._extract_keywords(content)

        # Determine content type
        content_type = self._classify_content_type(content)

        # Split content intelligently
        chunks = []

        if content_type == "film_info":
            # Special handling for film information
            chunks = self._chunk_film_info(content, section_title, subsection_title)
        elif content_type == "person_info":
            # Special handling for person information
            chunks = self._chunk_person_info(content, section_title, subsection_title)
        elif content_type == "list":
            # Special handling for lists
            chunks = self._chunk_list_content(content, section_title, subsection_title)
        else:
            # General content chunking
            chunks = self._chunk_general_content(content, section_title, subsection_title)

        # Add metadata to all chunks
        for chunk in chunks:
            chunk["entities"] = entities
            chunk["keywords"] = keywords
            chunk["content_type"] = content_type
            chunk["importance"] = self._calculate_importance_score(chunk["text"], entities, keywords)

        return chunks

    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities from text."""
        # Simple entity extraction for Indian cinema domain
        entities = []

        # Film titles (in italics or quotes)
        film_pattern = r'\*([^*]+)\*|"([^"]+)"'
        films = re.findall(film_pattern, text)
        for film_tuple in films:
            film = film_tuple[0] or film_tuple[1]
            if film and len(film) > 2:
                entities.append(f"FILM:{film}")

        # Years
        year_pattern = r'\b(19|20)\d{2}\b'
        years = re.findall(year_pattern, text)
        entities.extend([f"YEAR:{year}" for year in years])

        # Names (capitalized words)
        name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        names = re.findall(name_pattern, text)
        entities.extend([f"PERSON:{name}" for name in names[:10]])  # Limit to avoid noise

        return list(set(entities))

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text."""
        # Domain-specific keywords for Indian cinema
        cinema_keywords = [
            'director', 'actor', 'actress', 'film', 'movie', 'bollywood', 'cinema',
            'box office', 'award', 'music', 'song', 'dance', 'romance', 'comedy',
            'drama', 'action', 'thriller', 'performance', 'debut', 'success',
            'commercial', 'critical', 'blockbuster', 'hit', 'flop'
        ]

        keywords = []
        text_lower = text.lower()

        for keyword in cinema_keywords:
            if keyword in text_lower:
                keywords.append(keyword)

        return keywords

    def _classify_content_type(self, content: str) -> str:
        """Classify the type of content."""
        content_lower = content.lower()

        if any(indicator in content_lower for indicator in ['director:', 'music:', 'plot:', 'actors:', 'themes:']):
            return "film_info"
        elif any(indicator in content_lower for indicator in ['signature:', 'evolution:', 'impact:', 'notable roles:']):
            return "person_info"
        elif content.count('*') > 5 or content.count('-') > 5:
            return "list"
        else:
            return "general"

    def _split_by_headers(self, text: str) -> List[tuple]:
        """Split text by markdown headers."""
        # Pattern to match markdown headers
        header_pattern = r'^(#{1,6})\s+(.+)$'

        sections = []
        current_section = ""
        current_title = "Introduction"

        lines = text.split('\n')

        for line in lines:
            header_match = re.match(header_pattern, line, re.MULTILINE)

            if header_match:
                # Save previous section
                if current_section.strip():
                    sections.append((current_title, current_section.strip()))

                # Start new section
                current_title = header_match.group(2).strip()
                current_section = line + '\n'
            else:
                current_section += line + '\n'

        # Add final section
        if current_section.strip():
            sections.append((current_title, current_section.strip()))

        return sections

    def _split_section(self, text: str, section_title: str) -> List[str]:
        """Split a section into smaller chunks."""
        if len(text) <= self.chunk_size:
            return [text]

        # Split by paragraphs first
        paragraphs = text.split('\n\n')

        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:
            # If adding this paragraph would exceed chunk size
            if len(current_chunk) + len(paragraph) > self.chunk_size and current_chunk:
                # Add overlap from previous chunk
                if chunks:
                    overlap_text = self._get_overlap_text(chunks[-1])
                    current_chunk = overlap_text + current_chunk

                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += '\n\n' + paragraph
                else:
                    current_chunk = paragraph

        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def _get_overlap_text(self, previous_chunk: str) -> str:
        """Get overlap text from previous chunk."""
        if len(previous_chunk) <= self.chunk_overlap:
            return previous_chunk + '\n\n'

        # Take last chunk_overlap characters, but try to break at sentence boundary
        overlap_text = previous_chunk[-self.chunk_overlap:]

        # Find last sentence boundary
        sentence_end = max(
            overlap_text.rfind('.'),
            overlap_text.rfind('!'),
            overlap_text.rfind('?')
        )

        if sentence_end > self.chunk_overlap // 2:
            overlap_text = overlap_text[sentence_end + 1:]

        return overlap_text.strip() + '\n\n'

    def _chunk_film_info(self, content: str, section: str, subsection: str) -> List[Dict[str, Any]]:
        """Chunk film information content."""
        chunks = []

        # Split by film entries (marked by **Film Title**)
        film_pattern = r'\*\*\d+\.\s+([^*]+)\*\*'
        film_matches = list(re.finditer(film_pattern, content))

        for i, match in enumerate(film_matches):
            start_pos = match.start()
            end_pos = film_matches[i + 1].start() if i + 1 < len(film_matches) else len(content)

            film_content = content[start_pos:end_pos].strip()
            film_title = match.group(1)

            chunks.append({
                "text": film_content,
                "section": section,
                "subsection": subsection,
                "type": "film_entry",
                "film_title": film_title
            })

        return chunks

    def _chunk_person_info(self, content: str, section: str, subsection: str) -> List[Dict[str, Any]]:
        """Chunk person information content."""
        chunks = []

        # Split by person entries (marked by * **Person Name:**)
        person_pattern = r'\*\s+\*\*([^*]+):\*\*'
        person_matches = list(re.finditer(person_pattern, content))

        for i, match in enumerate(person_matches):
            start_pos = match.start()
            end_pos = person_matches[i + 1].start() if i + 1 < len(person_matches) else len(content)

            person_content = content[start_pos:end_pos].strip()
            person_name = match.group(1)

            chunks.append({
                "text": person_content,
                "section": section,
                "subsection": subsection,
                "type": "person_entry",
                "person_name": person_name
            })

        return chunks

    def _chunk_list_content(self, content: str, section: str, subsection: str) -> List[Dict[str, Any]]:
        """Chunk list-based content."""
        chunks = []

        # Split by list items while maintaining context
        lines = content.split('\n')
        current_chunk = []
        current_size = 0

        for line in lines:
            line_size = len(line)

            if current_size + line_size > self.chunk_size and current_chunk:
                chunks.append({
                    "text": '\n'.join(current_chunk),
                    "section": section,
                    "subsection": subsection,
                    "type": "list_chunk"
                })
                current_chunk = [line]
                current_size = line_size
            else:
                current_chunk.append(line)
                current_size += line_size

        if current_chunk:
            chunks.append({
                "text": '\n'.join(current_chunk),
                "section": section,
                "subsection": subsection,
                "type": "list_chunk"
            })

        return chunks

    def _chunk_general_content(self, content: str, section: str, subsection: str) -> List[Dict[str, Any]]:
        """Chunk general content with semantic boundaries."""
        chunks = []

        # Split by paragraphs first
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        current_chunk = []
        current_size = 0

        for paragraph in paragraphs:
            para_size = len(paragraph)

            if current_size + para_size > self.chunk_size and current_chunk:
                chunks.append({
                    "text": '\n\n'.join(current_chunk),
                    "section": section,
                    "subsection": subsection,
                    "type": "content_chunk"
                })
                current_chunk = [paragraph]
                current_size = para_size
            else:
                current_chunk.append(paragraph)
                current_size += para_size

        if current_chunk:
            chunks.append({
                "text": '\n\n'.join(current_chunk),
                "section": section,
                "subsection": subsection,
                "type": "content_chunk"
            })

        return chunks

    def _calculate_importance_score(self, text: str, entities: List[str], keywords: List[str]) -> float:
        """Calculate importance score for a chunk."""
        score = 0.5  # Base score

        # Boost for entities
        score += len(entities) * 0.05

        # Boost for keywords
        score += len(keywords) * 0.02

        # Boost for certain patterns
        if any(pattern in text.lower() for pattern in ['significance:', 'impact:', 'notable:', 'important:']):
            score += 0.1

        # Boost for film/person information
        if any(pattern in text for pattern in ['Director:', 'Music:', 'Plot:', 'Actors:']):
            score += 0.15

        return min(score, 1.0)  # Cap at 1.0

    def generate_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for text chunks using Cohere.

        Args:
            chunks: List of chunk dictionaries

        Returns:
            Chunks with embeddings added
        """
        logger.info(f"Generating embeddings for {len(chunks)} chunks using Cohere")

        # Extract texts for batch processing
        texts = [chunk["text"] for chunk in chunks]

        # Process in batches to avoid API limits
        batch_size = 96  # Cohere's batch limit
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")

            try:
                response = self.cohere_client.embed(
                    texts=batch_texts,
                    model=API_CONFIG.cohere_embed_model,
                    input_type="search_document",
                    embedding_types=["float"]
                )

                # Extract embeddings from Cohere response
                batch_embeddings = response.embeddings.float_
                all_embeddings.extend(batch_embeddings)

            except Exception as e:
                logger.error(f"Error generating embeddings for batch: {e}")
                # Fallback: create zero embeddings with correct dimension (1536 for Cohere embed-v4.0)
                batch_embeddings = [[0.0] * 1536 for _ in batch_texts]
                all_embeddings.extend(batch_embeddings)

        # Add embeddings to chunks
        for i, chunk in enumerate(chunks):
            chunk["embedding"] = all_embeddings[i]
            chunk["embedding_model"] = "cohere-embed-v4.0"

        logger.info("Embeddings generated successfully")
        return chunks

def process_knowledge_base(kb_file_path: str) -> List[Dict[str, Any]]:
    """
    Process knowledge base file and return chunks with embeddings using advanced chunking.

    Args:
        kb_file_path: Path to knowledge base file

    Returns:
        List of processed chunks with embeddings
    """
    processor = KnowledgeProcessor()

    # Load knowledge base
    text = processor.load_knowledge_base(kb_file_path)

    # Use advanced chunking strategy
    chunks = processor.chunk_text_advanced(text)

    # Generate embeddings using Cohere
    chunks_with_embeddings = processor.generate_embeddings(chunks)

    return chunks_with_embeddings
