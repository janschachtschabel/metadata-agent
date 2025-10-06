"""Test script to verify installation and setup."""
import sys
import os


def test_python_version():
    """Test Python version."""
    print("🔍 Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (requires 3.10+)")
        return False


def test_dependencies():
    """Test if all dependencies are installed."""
    print("\n🔍 Testing dependencies...")
    
    required_packages = [
        ("openai", "OpenAI"),
        ("langchain", "Langchain"),
        ("langchain_openai", "Langchain OpenAI"),
        ("langgraph", "Langgraph"),
        ("gradio", "Gradio"),
        ("pydantic", "Pydantic"),
        ("dotenv", "python-dotenv")
    ]
    
    all_installed = True
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name} - NOT INSTALLED")
            all_installed = False
    
    return all_installed


def test_env_file():
    """Test if .env file exists and has API key."""
    print("\n🔍 Testing .env configuration...")
    
    if not os.path.exists(".env"):
        print("   ❌ .env file not found")
        print("   💡 Create .env file from .env.example and add your OpenAI API key")
        return False
    
    print("   ✅ .env file exists")
    
    # Try to load
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("   ❌ OPENAI_API_KEY not set in .env")
        print("   💡 Add: OPENAI_API_KEY=sk-...")
        return False
    
    if not api_key.startswith("sk-"):
        print("   ⚠️  OPENAI_API_KEY doesn't look valid (should start with 'sk-')")
        return False
    
    # Mask the key
    masked = api_key[:10] + "..." + api_key[-4:]
    print(f"   ✅ OPENAI_API_KEY set: {masked}")
    return True


def test_schema_files():
    """Test if schema files exist."""
    print("\n🔍 Testing schema files...")
    
    required_schemas = [
        "schemata/core.json",
        "schemata/event.json"
    ]
    
    all_exist = True
    for schema_path in required_schemas:
        if os.path.exists(schema_path):
            # Check if it's valid JSON
            try:
                import json
                with open(schema_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                print(f"   ✅ {schema_path}")
            except json.JSONDecodeError:
                print(f"   ⚠️  {schema_path} - Invalid JSON")
                all_exist = False
        else:
            print(f"   ❌ {schema_path} - NOT FOUND")
            all_exist = False
    
    return all_exist


def test_modules():
    """Test if custom modules can be imported."""
    print("\n🔍 Testing custom modules...")
    
    modules = [
        "schema_loader",
        "models",
        "agent",
        "validator"
    ]
    
    all_imported = True
    for module in modules:
        try:
            __import__(module)
            print(f"   ✅ {module}.py")
        except Exception as e:
            print(f"   ❌ {module}.py - {str(e)}")
            all_imported = False
    
    return all_imported


def test_schema_loading():
    """Test if schemas can be loaded."""
    print("\n🔍 Testing schema loading...")
    
    try:
        from schema_loader import SchemaManager
        
        manager = SchemaManager()
        
        # Test core schema
        core_schema = manager.load_schema("core.json")
        print(f"   ✅ Core schema loaded ({len(core_schema.get('fields', []))} fields)")
        
        # Test event schema
        event_schema = manager.load_schema("event.json")
        print(f"   ✅ Event schema loaded ({len(event_schema.get('fields', []))} fields)")
        
        # Test field extraction
        core_fields = manager.get_fields("core.json")
        required = manager.get_required_fields("core.json")
        print(f"   ✅ Field extraction works ({len(required)} required fields)")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False


def test_openai_connection():
    """Test if OpenAI API is accessible."""
    print("\n🔍 Testing OpenAI API connection...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("   ⏭️  Skipped (no API key)")
            return True
        
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        # Simple test with GPT-5
        response = client.responses.create(
            model="gpt-5-mini",
            input="Say 'OK'",
            reasoning={"effort": "minimal"},
            text={"verbosity": "low"}
        )
        
        if response.output_text:
            print(f"   ✅ OpenAI API reachable (model: gpt-5-mini)")
            return True
        else:
            print("   ⚠️  OpenAI responded but empty content")
            return False
            
    except Exception as e:
        print(f"   ❌ API Error: {str(e)}")
        print("   💡 Check your API key and internet connection")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Metadata Agent - Setup Test")
    print("=" * 60)
    
    results = []
    
    results.append(("Python Version", test_python_version()))
    results.append(("Dependencies", test_dependencies()))
    results.append((".env Configuration", test_env_file()))
    results.append(("Schema Files", test_schema_files()))
    results.append(("Custom Modules", test_modules()))
    results.append(("Schema Loading", test_schema_loading()))
    results.append(("OpenAI Connection", test_openai_connection()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} {test_name}")
    
    print("\n" + "-" * 60)
    print(f"Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! You're ready to go!")
        print("\n▶️  Start the app with: python app.py")
        print("▶️  Or try the example: python example.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\n💡 Tips:")
        print("   - Install missing packages: pip install -r requirements.txt")
        print("   - Create .env file with your OpenAI API key")
        print("   - Check that all files are present")
    
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
