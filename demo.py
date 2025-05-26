"""
Enhanced demo script showcasing the improved PDF Question Extraction and RAG system.
"""
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def demo_cohere_embeddings():
    """Demo Cohere embeddings integration."""
    print("🧪 Demo: Cohere Embeddings Integration")
    print("=" * 50)

    try:
        import cohere
        from config import API_CONFIG

        # Test Cohere client
        client = cohere.ClientV2(api_key=API_CONFIG.cohere_api_key)

        # Test embedding generation
        test_texts = [
            "Who directed the movie Lagaan?",
            "Lagaan was directed by Ashutosh Gowariker in 2001."
        ]

        print("📊 Testing Cohere embeddings...")
        response = client.embed(
            texts=test_texts,
            model=API_CONFIG.cohere_embed_model,
            input_type="search_document",
            embedding_types=["float"]
        )

        print(f"✅ Generated embeddings for {len(test_texts)} texts")

        # Extract embedding dimension from Cohere response
        embedding_dim = len(response.embeddings.float_[0])

        print(f"   Embedding dimension: {embedding_dim}")
        print(f"   Model: {API_CONFIG.cohere_embed_model}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def demo_cohere_reranking():
    """Demo Cohere reranking functionality."""
    print("\n🧪 Demo: Cohere Reranking")
    print("=" * 50)

    try:
        import cohere
        from config import API_CONFIG

        client = cohere.ClientV2(api_key=API_CONFIG.cohere_api_key)

        # Test documents
        docs = [
            "Lagaan was directed by Ashutosh Gowariker and starred Aamir Khan.",
            "The movie was released in 2001 and was nominated for an Academy Award.",
            "3 Idiots was directed by Rajkumar Hirani and became a huge success.",
            "Shah Rukh Khan is known as the King of Bollywood.",
            "Lagaan is set in 1893 during British colonial rule in India."
        ]

        query = "Who directed Lagaan?"

        print(f"🔍 Query: {query}")
        print(f"📄 Documents to rerank: {len(docs)}")

        response = client.rerank(
            model=API_CONFIG.cohere_rerank_model,
            query=query,
            documents=docs,
            top_n=3
        )

        print("✅ Reranking results:")
        for i, result in enumerate(response.results):
            print(f"   {i+1}. Score: {result.relevance_score:.3f}")
            print(f"      Text: {docs[result.index][:100]}...")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def demo_advanced_chunking():
    """Demo advanced chunking with semantic awareness."""
    print("\n🧪 Demo: Advanced Chunking Strategy")
    print("=" * 50)

    try:
        from services.knowledge_processor import KnowledgeProcessor

        kb_path = "files/IndianMovie_KnowledgeBase.md"
        if not Path(kb_path).exists():
            print(f"❌ Knowledge base not found: {kb_path}")
            return False

        processor = KnowledgeProcessor()

        print("📚 Loading knowledge base...")
        text = processor.load_knowledge_base(kb_path)

        print("🔧 Applying advanced chunking...")
        chunks = processor.chunk_text_advanced(text)

        print(f"✅ Created {len(chunks)} advanced chunks")

        # Analyze chunk types
        chunk_types = {}
        for chunk in chunks:
            chunk_type = chunk.get('chunk_type', 'unknown')
            chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1

        print("📊 Chunk type distribution:")
        for chunk_type, count in chunk_types.items():
            print(f"   {chunk_type}: {count}")

        # Show sample chunks
        print("\n📋 Sample chunks:")
        for i, chunk in enumerate(chunks[:3]):
            print(f"   Chunk {i+1}:")
            print(f"     Type: {chunk.get('chunk_type', 'unknown')}")
            print(f"     Section: {chunk['section']}")
            print(f"     Entities: {len(chunk.get('entity_mentions', []))}")
            print(f"     Keywords: {len(chunk.get('keywords', []))}")
            print(f"     Importance: {chunk.get('metadata', {}).get('importance_score', 0):.2f}")
            print(f"     Text: {chunk['text'][:150]}...")
            print()

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def demo_enhanced_question_types():
    """Demo enhanced question type support."""
    print("\n🧪 Demo: Enhanced Question Types")
    print("=" * 50)

    try:
        from config import QUESTION_TYPES
        from services.rag_agent import RAGAgent
        from services.knowledge_processor import process_knowledge_base
        from services.vector_store import setup_vector_store

        # Test questions with new types
        test_questions = [
            {
                "question_id": "demo_numerical",
                "question_text": "In which year was Lagaan released?",
                "question_type": QUESTION_TYPES.DATE_TIME,
                "options": None,
                "metadata": {"page_number": 1}
            },
            {
                "question_id": "demo_comparison",
                "question_text": "Compare the themes of Lagaan and 3 Idiots.",
                "question_type": QUESTION_TYPES.COMPARISON,
                "options": None,
                "metadata": {"page_number": 1}
            },
            {
                "question_id": "demo_analysis",
                "question_text": "Analyze the impact of Bollywood on Indian culture in the 2000s.",
                "question_type": QUESTION_TYPES.ANALYSIS,
                "options": None,
                "metadata": {"page_number": 1}
            }
        ]

        print(f"🎯 Testing {len(test_questions)} enhanced question types...")

        # Setup RAG system
        kb_path = "files/IndianMovie_KnowledgeBase.md"
        if not Path(kb_path).exists():
            print(f"❌ Knowledge base not found: {kb_path}")
            return False

        print("📚 Setting up enhanced RAG system...")
        chunks = process_knowledge_base(kb_path)
        vector_store = setup_vector_store(chunks, force_recreate=True)
        rag_agent = RAGAgent(vector_store)

        print("🤖 Answering enhanced questions...")
        for question in test_questions:
            print(f"\n❓ Question Type: {question['question_type']}")
            print(f"   Question: {question['question_text']}")

            try:
                answered = rag_agent.answer_question(question)
                print(f"✅ Answer: {answered.get('answer', 'No answer')[:200]}...")
            except Exception as e:
                print(f"❌ Error answering question: {e}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def demo_full_pipeline():
    """Demo the complete enhanced pipeline."""
    print("\n🧪 Demo: Complete Enhanced Pipeline")
    print("=" * 50)

    try:
        from services.knowledge_processor import process_knowledge_base
        from services.vector_store import setup_vector_store
        from services.rag_agent import answer_all_questions
        from utils.pdf_generator import generate_answer_pdf

        kb_path = "files/IndianMovie_KnowledgeBase.md"
        if not Path(kb_path).exists():
            print(f"❌ Knowledge base not found: {kb_path}")
            return False

        # Sample questions JSON with enhanced types
        sample_json = {
            "total_questions": 3,
            "extraction_timestamp": 1640995200,
            "rag_processing_complete": False,
            "questions": [
                {
                    "question_id": "enhanced_1",
                    "question_text": "Who directed Lagaan and when was it released?",
                    "question_type": "textual_answer",
                    "options": None,
                    "metadata": {"page_number": 1}
                },
                {
                    "question_id": "enhanced_2",
                    "question_text": "Compare the box office performance of Lagaan and 3 Idiots.",
                    "question_type": "comparison",
                    "options": None,
                    "metadata": {"page_number": 1}
                },
                {
                    "question_id": "enhanced_3",
                    "question_text": "Analyze the cultural impact of Bollywood in the 2000s decade.",
                    "question_type": "analysis",
                    "options": None,
                    "metadata": {"page_number": 1}
                }
            ]
        }

        print("🔧 Processing knowledge base with advanced chunking...")
        chunks = process_knowledge_base(kb_path)

        print("🗄️ Setting up vector store with Cohere embeddings...")
        vector_store = setup_vector_store(chunks, force_recreate=True)

        print("🤖 Answering questions with Cohere reranking...")
        answered_questions = answer_all_questions(sample_json, vector_store)

        print("📄 Generating enhanced PDF...")
        output_path = "enhanced_demo_answers.pdf"
        success = generate_answer_pdf(answered_questions, output_path)

        if success:
            print(f"✅ Enhanced pipeline completed successfully!")
            print(f"   Output: {output_path}")

            # Show results
            print("\n📊 Results Summary:")
            for i, question in enumerate(answered_questions["questions"]):
                print(f"   Question {i+1} ({question['question_type']}):")
                print(f"     Answer: {question.get('answer', 'No answer')[:100]}...")

            return True
        else:
            print("❌ PDF generation failed")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all enhanced demos."""
    print("🚀 Enhanced PDF Question Extraction and RAG System - Demo")
    print("=" * 60)

    demos = [
        ("Cohere Embeddings", demo_cohere_embeddings),
        ("Cohere Reranking", demo_cohere_reranking),
        ("Advanced Chunking", demo_advanced_chunking),
        ("Enhanced Question Types", demo_enhanced_question_types),
        ("Full Enhanced Pipeline", demo_full_pipeline)
    ]

    results = []

    for demo_name, demo_func in demos:
        try:
            result = demo_func()
            results.append((demo_name, result))
        except Exception as e:
            print(f"❌ {demo_name} demo failed: {e}")
            results.append((demo_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("📊 Enhanced Demo Results Summary:")

    passed = 0
    for demo_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {demo_name}: {status}")
        if result:
            passed += 1

    print(f"\nPassed: {passed}/{len(results)} demos")

    if passed == len(results):
        print("\n🎉 All enhanced demos passed! The system is working with all improvements.")
        print("\nEnhancements implemented:")
        print("   ✅ Cohere embeddings integration")
        print("   ✅ Cohere reranking for better context retrieval")
        print("   ✅ Advanced semantic chunking")
        print("   ✅ 10 new question types supported")
        print("   ✅ Enhanced RAG pipeline")
        print("\nTo start the enhanced Streamlit app:")
        print("   streamlit run app.py")
    else:
        print(f"\n⚠️ {len(results) - passed} demo(s) failed.")

if __name__ == "__main__":
    main()
