"""
Test script to verify the setup and basic functionality.
"""
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test if all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        # Test core dependencies
        import streamlit
        import fitz  # PyMuPDF
        import openai
        from mistralai import Mistral
        from qdrant_client import QdrantClient
        from sentence_transformers import SentenceTransformer
        from reportlab.platypus import SimpleDocTemplate
        
        print("✅ Core dependencies imported successfully")
        
        # Test our modules
        from config import API_CONFIG, PROCESSING_CONFIG
        from utils.pdf_processor import PDFProcessor
        from services.vlm_service import VLMService
        from services.knowledge_processor import KnowledgeProcessor
        from services.vector_store import VectorStore
        from services.rag_agent import RAGAgent
        from utils.pdf_generator import PDFGenerator
        
        print("✅ Custom modules imported successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_api_connections():
    """Test API connections."""
    print("\n🌐 Testing API connections...")
    
    # Test SambaNova (basic client creation)
    try:
        import openai
        from config import API_CONFIG
        
        client = openai.OpenAI(
            api_key=API_CONFIG.sambanova_api_key,
            base_url=API_CONFIG.sambanova_base_url,
        )
        print("✅ SambaNova client created successfully")
    except Exception as e:
        print(f"⚠️ SambaNova client creation failed: {e}")
    
    # Test Mistral (basic client creation)
    try:
        from mistralai import Mistral
        client = Mistral(api_key=API_CONFIG.mistral_api_key)
        print("✅ Mistral client created successfully")
    except Exception as e:
        print(f"⚠️ Mistral client creation failed: {e}")
    
    # Test Qdrant (basic client creation)
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(
            url=API_CONFIG.qdrant_url,
            api_key=API_CONFIG.qdrant_api_key,
        )
        print("✅ Qdrant client created successfully")
    except Exception as e:
        print(f"⚠️ Qdrant client creation failed: {e}")

def test_embedding_model():
    """Test embedding model loading."""
    print("\n🤖 Testing embedding model...")
    
    try:
        from sentence_transformers import SentenceTransformer
        from config import PROCESSING_CONFIG
        
        print(f"Loading model: {PROCESSING_CONFIG.embedding_model}")
        model = SentenceTransformer(PROCESSING_CONFIG.embedding_model)
        
        # Test encoding
        test_text = "This is a test sentence."
        embedding = model.encode(test_text)
        
        print(f"✅ Embedding model loaded successfully")
        print(f"   Model: {PROCESSING_CONFIG.embedding_model}")
        print(f"   Embedding dimension: {len(embedding)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Embedding model test failed: {e}")
        return False

def test_file_structure():
    """Test if required files and directories exist."""
    print("\n📁 Testing file structure...")
    
    required_files = [
        "app.py",
        "config.py",
        "requirements.txt",
        "services/__init__.py",
        "utils/__init__.py"
    ]
    
    optional_files = [
        "files/IndianMovie_KnowledgeBase.md"
    ]
    
    # Check required files
    missing_required = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_required.append(file_path)
    
    if missing_required:
        print("❌ Missing required files:")
        for file_path in missing_required:
            print(f"   - {file_path}")
        return False
    else:
        print("✅ All required files found")
    
    # Check optional files
    missing_optional = []
    for file_path in optional_files:
        if not Path(file_path).exists():
            missing_optional.append(file_path)
    
    if missing_optional:
        print("⚠️ Missing optional files:")
        for file_path in missing_optional:
            print(f"   - {file_path}")
        print("   These can be uploaded through the app interface")
    else:
        print("✅ All optional files found")
    
    return True

def test_basic_functionality():
    """Test basic functionality of core components."""
    print("\n⚙️ Testing basic functionality...")
    
    try:
        # Test PDF processor
        from utils.pdf_processor import PDFProcessor
        processor = PDFProcessor()
        print("✅ PDF processor initialized")
        
        # Test VLM service
        from services.vlm_service import VLMService
        vlm = VLMService()
        print("✅ VLM service initialized")
        
        # Test knowledge processor
        from services.knowledge_processor import KnowledgeProcessor
        kb_processor = KnowledgeProcessor()
        print("✅ Knowledge processor initialized")
        
        # Test vector store
        from services.vector_store import VectorStore
        vector_store = VectorStore()
        print("✅ Vector store initialized")
        
        # Test PDF generator
        from utils.pdf_generator import PDFGenerator
        pdf_gen = PDFGenerator()
        print("✅ PDF generator initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Running setup verification tests...")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("API Connections", test_api_connections),
        ("Embedding Model", test_embedding_model),
        ("File Structure", test_file_structure),
        ("Basic Functionality", test_basic_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("\n🎉 All tests passed! The system is ready to use.")
        print("\nTo start the application:")
        print("   streamlit run app.py")
    else:
        print(f"\n⚠️ {len(results) - passed} test(s) failed. Please check the issues above.")
        print("Run 'python setup.py' to install missing dependencies.")

if __name__ == "__main__":
    main()
