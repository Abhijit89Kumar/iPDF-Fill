"""
Vector store service using Qdrant for similarity search.
"""
import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, Range
import numpy as np

from config import API_CONFIG, PROCESSING_CONFIG

logger = logging.getLogger(__name__)

class VectorStore:
    """Manages vector storage and retrieval using Qdrant."""
    
    def __init__(self, collection_name: str = None):
        """
        Initialize vector store.
        
        Args:
            collection_name: Name of the collection to use
        """
        self.client = QdrantClient(
            url=API_CONFIG.qdrant_url,
            api_key=API_CONFIG.qdrant_api_key,
        )
        self.collection_name = collection_name or PROCESSING_CONFIG.collection_name
        self.embedding_dimension = PROCESSING_CONFIG.embedding_dimension
        
    def create_collection(self, force_recreate: bool = False) -> bool:
        """
        Create a new collection in Qdrant.
        
        Args:
            force_recreate: Whether to recreate if collection exists
            
        Returns:
            True if collection was created/exists, False otherwise
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_exists = any(
                col.name == self.collection_name 
                for col in collections.collections
            )
            
            if collection_exists:
                if force_recreate:
                    logger.info(f"Deleting existing collection: {self.collection_name}")
                    self.client.delete_collection(self.collection_name)
                else:
                    logger.info(f"Collection {self.collection_name} already exists")
                    return True
            
            # Create new collection
            logger.info(f"Creating collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dimension,
                    distance=Distance.COSINE
                ),
            )
            
            logger.info(f"Collection {self.collection_name} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating collection {self.collection_name}: {str(e)}")
            return False
    
    def store_chunks(self, chunks: List[Dict[str, Any]]) -> bool:
        """
        Store text chunks with embeddings in the vector store.
        
        Args:
            chunks: List of chunks with embeddings
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Storing {len(chunks)} chunks in vector store")
            
            # Prepare points for insertion
            points = []
            for chunk in chunks:
                point = PointStruct(
                    id=chunk["chunk_id"],
                    vector=chunk["embedding"],
                    payload={
                        "text": chunk["text"],
                        "section": chunk["section"],
                        "char_count": chunk["char_count"],
                        "metadata": chunk["metadata"],
                        "embedding_model": chunk.get("embedding_model", "unknown")
                    }
                )
                points.append(point)
            
            # Insert points in batches
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
                logger.info(f"Inserted batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")
            
            logger.info(f"Successfully stored {len(chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Error storing chunks: {str(e)}")
            return False
    
    def search_similar(
        self, 
        query_embedding: List[float], 
        top_k: int = None,
        score_threshold: float = None,
        section_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using vector similarity.
        
        Args:
            query_embedding: Query vector embedding
            top_k: Number of results to return
            score_threshold: Minimum similarity score
            section_filter: Filter by section name
            
        Returns:
            List of similar chunks with scores
        """
        try:
            top_k = top_k or PROCESSING_CONFIG.top_k_results
            score_threshold = score_threshold or PROCESSING_CONFIG.similarity_threshold
            
            # Prepare search filter
            search_filter = None
            if section_filter:
                search_filter = Filter(
                    must=[
                        FieldCondition(
                            key="section",
                            match={"value": section_filter}
                        )
                    ]
                )
            
            # Perform search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=top_k,
                score_threshold=score_threshold
            )
            
            # Format results
            results = []
            for result in search_results:
                chunk_data = {
                    "chunk_id": result.id,
                    "score": result.score,
                    "text": result.payload["text"],
                    "section": result.payload["section"],
                    "metadata": result.payload["metadata"]
                }
                results.append(chunk_data)
            
            logger.info(f"Found {len(results)} similar chunks")
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar chunks: {str(e)}")
            return []
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection.
        
        Returns:
            Collection information dictionary
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "name": collection_info.config.params.vectors.size,
                "vectors_count": collection_info.vectors_count,
                "indexed_vectors_count": collection_info.indexed_vectors_count,
                "points_count": collection_info.points_count,
                "status": collection_info.status
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            return {}
    
    def delete_collection(self) -> bool:
        """
        Delete the collection.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Collection {self.collection_name} deleted")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")
            return False

def setup_vector_store(chunks: List[Dict[str, Any]], force_recreate: bool = False) -> VectorStore:
    """
    Set up vector store with knowledge base chunks.
    
    Args:
        chunks: List of chunks with embeddings
        force_recreate: Whether to recreate the collection
        
    Returns:
        Configured VectorStore instance
    """
    vector_store = VectorStore()
    
    # Create collection
    if not vector_store.create_collection(force_recreate=force_recreate):
        raise RuntimeError("Failed to create vector store collection")
    
    # Store chunks
    if not vector_store.store_chunks(chunks):
        raise RuntimeError("Failed to store chunks in vector store")
    
    return vector_store
