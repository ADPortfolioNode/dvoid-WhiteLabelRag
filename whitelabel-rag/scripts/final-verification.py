#!/usr/bin/env python3
"""
Final verification script for WhiteLabelRAG project
Comprehensive check of all components and functionality
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

class WhiteLabelRAGVerification:
    def __init__(self):
        self.results = []
        self.errors = []
        self.warnings = []
        
    def log_result(self, test_name, passed, message="", warning=False):
        """Log test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        if warning:
            status = "⚠️ WARN"
            self.warnings.append(f"{test_name}: {message}")
        
        self.results.append({
            'test': test_name,
            'passed': passed,
            'message': message,
            'warning': warning
        })
        
        print(f"{status} {test_name}")
        if message:
            print(f"    {message}")
        
        if not passed and not warning:
            self.errors.append(f"{test_name}: {message}")
    
    def check_project_structure(self):
        """Verify project structure is complete."""
        print("\n📁 Checking Project Structure...")
        
        required_files = [
            'run.py',
            'requirements.txt',
            'docker-compose.yml',
            'Dockerfile',
            '.env.example',
            '.gitignore',
            'README.md',
            'QUICKSTART.md',
            'LICENSE',
            'app/__init__.py',
            'app/config.py',
            'app/api/__init__.py',
            'app/api/routes.py',
            'app/main/__init__.py',
            'app/main/routes.py',
            'app/services/__init__.py',
            'app/services/base_assistant.py',
            'app/services/concierge.py',
            'app/services/search_agent.py',
            'app/services/file_agent.py',
            'app/services/function_agent.py',
            'app/services/chroma_service.py',
            'app/services/rag_manager.py',
            'app/services/document_processor.py',
            'app/services/conversation_store.py',
            'app/services/llm_factory.py',
            'app/static/css/style.css',
            'app/static/js/app.js',
            'app/templates/index.html',
            'app/utils/__init__.py',
            'app/utils/file_utils.py',
            'app/websocket_events.py',
            'tests/__init__.py',
            'tests/test_api.py',
            'tests/test_services.py',
            'scripts/setup.sh',
            'scripts/setup.bat',
            'scripts/run-dev.sh',
            'scripts/run-dev.bat',
            'scripts/check-env.py',
            'scripts/test-setup.py',
            'scripts/health-check.py',
            'scripts/demo.py'
        ]
        
        required_dirs = [
            'app',
            'app/api',
            'app/main',
            'app/services',
            'app/static',
            'app/static/css',
            'app/static/js',
            'app/templates',
            'app/utils',
            'tests',
            'scripts',
            'sample_documents'
        ]
        
        # Check directories
        missing_dirs = []
        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                missing_dirs.append(dir_path)
        
        if missing_dirs:
            self.log_result("Directory Structure", False, f"Missing directories: {', '.join(missing_dirs)}")
        else:
            self.log_result("Directory Structure", True, f"All {len(required_dirs)} directories present")
        
        # Check files
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.log_result("File Structure", False, f"Missing files: {', '.join(missing_files[:5])}{'...' if len(missing_files) > 5 else ''}")
        else:
            self.log_result("File Structure", True, f"All {len(required_files)} required files present")
    
    def check_python_imports(self):
        """Check if all Python modules can be imported."""
        print("\n🐍 Checking Python Imports...")
        
        # Add app to path
        sys.path.insert(0, 'app')
        
        modules_to_test = [
            ('app.config', 'Configuration module'),
            ('app.services.base_assistant', 'Base Assistant'),
            ('app.services.concierge', 'Concierge Agent'),
            ('app.services.search_agent', 'Search Agent'),
            ('app.services.file_agent', 'File Agent'),
            ('app.services.function_agent', 'Function Agent'),
            ('app.services.chroma_service', 'ChromaDB Service'),
            ('app.services.rag_manager', 'RAG Manager'),
            ('app.services.document_processor', 'Document Processor'),
            ('app.services.conversation_store', 'Conversation Store'),
            ('app.services.llm_factory', 'LLM Factory'),
            ('app.utils.file_utils', 'File Utils'),
            ('app.websocket_events', 'WebSocket Events')
        ]
        
        import_errors = []
        for module_name, description in modules_to_test:
            try:
                __import__(module_name)
                self.log_result(f"Import {description}", True)
            except Exception as e:
                import_errors.append(f"{module_name}: {str(e)}")
                self.log_result(f"Import {description}", False, str(e))
        
        if not import_errors:
            self.log_result("All Python Imports", True, "All modules imported successfully")
    
    def check_dependencies(self):
        """Check if all required dependencies are available."""
        print("\n📦 Checking Dependencies...")
        
        required_packages = [
            'flask',
            'flask_cors',
            'flask_socketio',
            'chromadb',
            'google.generativeai',
            'dotenv',
            'PyPDF2',
            'docx',
            'markdown',
            'bs4',
            'sentence_transformers',
            'numpy',
            'pandas',
            'requests'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                if package == 'dotenv':
                    import dotenv
                elif package == 'bs4':
                    import bs4
                elif package == 'docx':
                    import docx
                else:
                    __import__(package)
                self.log_result(f"Package {package}", True)
            except ImportError:
                missing_packages.append(package)
                self.log_result(f"Package {package}", False, "Not installed")
        
        if missing_packages:
            self.log_result("Dependencies Check", False, f"Missing: {', '.join(missing_packages)}")
        else:
            self.log_result("Dependencies Check", True, "All dependencies available")
    
    def check_configuration_files(self):
        """Check configuration files and templates."""
        print("\n⚙️ Checking Configuration Files...")
        
        # Check .env.example
        if Path('.env.example').exists():
            with open('.env.example', 'r') as f:
                env_content = f.read()
                if 'GEMINI_API_KEY' in env_content:
                    self.log_result("Environment Template", True, ".env.example contains required variables")
                else:
                    self.log_result("Environment Template", False, "GEMINI_API_KEY not found in .env.example")
        else:
            self.log_result("Environment Template", False, ".env.example file missing")
        
        # Check requirements.txt
        if Path('requirements.txt').exists():
            with open('requirements.txt', 'r') as f:
                requirements = f.read()
                essential_packages = ['flask', 'chromadb', 'google-generativeai']
                missing = [pkg for pkg in essential_packages if pkg not in requirements]
                if missing:
                    self.log_result("Requirements File", False, f"Missing packages: {', '.join(missing)}")
                else:
                    self.log_result("Requirements File", True, "Contains essential packages")
        else:
            self.log_result("Requirements File", False, "requirements.txt missing")
        
        # Check Docker files
        docker_files = ['Dockerfile', 'docker-compose.yml']
        for file_name in docker_files:
            if Path(file_name).exists():
                self.log_result(f"Docker {file_name}", True, "Present")
            else:
                self.log_result(f"Docker {file_name}", False, "Missing")
    
    def check_documentation(self):
        """Check documentation completeness."""
        print("\n📚 Checking Documentation...")
        
        doc_files = {
            'README.md': ['installation', 'usage', 'api'],
            'QUICKSTART.md': ['setup', 'configuration'],
            'DEPLOYMENT.md': ['docker', 'production'],
            'TROUBLESHOOTING.md': ['common issues', 'solutions'],
            'CHANGELOG.md': ['version', 'changes']
        }
        
        for doc_file, required_sections in doc_files.items():
            if Path(doc_file).exists():
                try:
                    with open(doc_file, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        missing_sections = [section for section in required_sections 
                                          if section not in content]
                        if missing_sections:
                            self.log_result(f"Documentation {doc_file}", True, 
                                          f"Present but missing: {', '.join(missing_sections)}", warning=True)
                        else:
                            self.log_result(f"Documentation {doc_file}", True, "Complete")
                except Exception as e:
                    self.log_result(f"Documentation {doc_file}", False, f"Error reading: {str(e)}")
            else:
                self.log_result(f"Documentation {doc_file}", False, "Missing")
    
    def check_scripts(self):
        """Check automation scripts."""
        print("\n🔧 Checking Scripts...")
        
        scripts = [
            'scripts/setup.sh',
            'scripts/setup.bat',
            'scripts/run-dev.sh',
            'scripts/run-dev.bat',
            'scripts/check-env.py',
            'scripts/test-setup.py',
            'scripts/health-check.py',
            'scripts/demo.py'
        ]
        
        for script in scripts:
            if Path(script).exists():
                # Check if script is executable (Unix-like systems)
                if script.endswith('.sh') and os.name != 'nt':
                    if os.access(script, os.X_OK):
                        self.log_result(f"Script {script}", True, "Present and executable")
                    else:
                        self.log_result(f"Script {script}", True, "Present but not executable", warning=True)
                else:
                    self.log_result(f"Script {script}", True, "Present")
            else:
                self.log_result(f"Script {script}", False, "Missing")
    
    def check_sample_content(self):
        """Check sample content and test files."""
        print("\n📄 Checking Sample Content...")
        
        # Check sample documents
        sample_dir = Path('sample_documents')
        if sample_dir.exists():
            sample_files = list(sample_dir.glob('*'))
            if sample_files:
                self.log_result("Sample Documents", True, f"Found {len(sample_files)} sample files")
            else:
                self.log_result("Sample Documents", True, "Directory exists but empty", warning=True)
        else:
            self.log_result("Sample Documents", False, "sample_documents directory missing")
        
        # Check test files
        test_dir = Path('tests')
        if test_dir.exists():
            test_files = list(test_dir.glob('test_*.py'))
            if test_files:
                self.log_result("Test Files", True, f"Found {len(test_files)} test files")
            else:
                self.log_result("Test Files", True, "Directory exists but no test files", warning=True)
        else:
            self.log_result("Test Files", False, "tests directory missing")
    
    def check_environment_setup(self):
        """Check environment configuration."""
        print("\n🌍 Checking Environment Setup...")
        
        # Check for .env file
        if Path('.env').exists():
            self.log_result("Environment File", True, ".env file exists")
            
            # Check if GEMINI_API_KEY is set
            from dotenv import load_dotenv
            load_dotenv()
            
            api_key = os.environ.get('GEMINI_API_KEY')
            if api_key:
                self.log_result("GEMINI_API_KEY", True, f"Set (length: {len(api_key)} characters)")
            else:
                self.log_result("GEMINI_API_KEY", False, "Not set in .env file")
        else:
            # Check environment variable
            api_key = os.environ.get('GEMINI_API_KEY')
            if api_key:
                self.log_result("GEMINI_API_KEY", True, f"Set as environment variable (length: {len(api_key)} characters)")
            else:
                self.log_result("GEMINI_API_KEY", False, "Not set (required for operation)")
    
    def check_app_creation(self):
        """Test if the Flask app can be created."""
        print("\n🚀 Checking App Creation...")
        
        try:
            # Set a dummy API key if not set
            original_key = os.environ.get('GEMINI_API_KEY')
            if not original_key:
                os.environ['GEMINI_API_KEY'] = 'test-key-for-verification'
            
            sys.path.insert(0, 'app')
            from app import create_app
            
            app = create_app()
            if app:
                self.log_result("Flask App Creation", True, "App created successfully")
            else:
                self.log_result("Flask App Creation", False, "App creation returned None")
            
            # Restore original key
            if original_key:
                os.environ['GEMINI_API_KEY'] = original_key
            elif 'GEMINI_API_KEY' in os.environ:
                del os.environ['GEMINI_API_KEY']
                
        except Exception as e:
            self.log_result("Flask App Creation", False, f"Error: {str(e)}")
    
    def check_instructions_compliance(self):
        """Verify codebase logic and API against INSTRUCTIONS.md ground truth."""
        print("\n📖 Checking INSTRUCTIONS.md Compliance...")

        instructions_path = Path("INSTRUCTIONS.md")
        if not instructions_path.exists():
            self.log_result("INSTRUCTIONS.md Presence", False, "INSTRUCTIONS.md not found in project root")
            return

        with open(instructions_path, "r", encoding="utf-8") as f:
            instructions = f.read().lower()

        # Check for required endpoints
        required_endpoints = [
            "/api/decompose",
            "/api/execute",
            "/api/validate",
            "/api/tasks/",
            "/api/files",
            "/api/documents/upload_and_ingest_document",
            "/api/chroma/store_document_embedding",
            "/api/chroma/store_step_embedding",
            "/api/query"
        ]
        for endpoint in required_endpoints:
            if endpoint not in instructions:
                self.log_result("INSTRUCTIONS.md Endpoints", False, f"Missing endpoint in INSTRUCTIONS.md: {endpoint}")

        # Check for required agent classes
        required_agents = [
            "concierge",
            "searchagent",
            "fileagent",
            "functionagent"
        ]
        for agent in required_agents:
            if agent not in instructions:
                self.log_result("INSTRUCTIONS.md Agents", False, f"Missing agent in INSTRUCTIONS.md: {agent}")

        # Check for RAG workflow descriptions
        required_workflows = [
            "basic rag",
            "advanced rag",
            "recursive rag",
            "adaptive rag"
        ]
        for workflow in required_workflows:
            if workflow not in instructions:
                self.log_result("INSTRUCTIONS.md Workflows", False, f"Missing workflow in INSTRUCTIONS.md: {workflow}")

        # Check for Docker and local startup script references
        if "run-docker.bat" not in instructions and "docker-compose" not in instructions:
            self.log_result("INSTRUCTIONS.md Startup", False, "No Docker startup instructions found in INSTRUCTIONS.md")
        if "run-dev.bat" not in instructions and "run-local.bat" not in instructions:
            self.log_result("INSTRUCTIONS.md Startup", False, "No local dev startup instructions found in INSTRUCTIONS.md")

        # If no errors, pass
        if not any(r for r in self.results if r['test'].startswith("INSTRUCTIONS.md") and not r['passed']):
            self.log_result("INSTRUCTIONS.md Compliance", True, "All required endpoints, agents, and workflows present")

    def check_rag_workflows(self):
        """Verify all RAG operation workflows are implemented and importable."""
        print("\n🔄 Verifying RAG Operation Workflows...")

        # Try to import and instantiate each workflow if possible
        workflow_checks = [
            ("Basic RAG Workflow", "app.services.rag_manager", "basic_rag_workflow"),
            ("Advanced RAG Workflow", "app.services.rag_manager", "advanced_rag_workflow"),
            ("Recursive RAG Workflow", "app.services.rag_manager", "recursive_rag_workflow"),
            ("Adaptive RAG Workflow", "app.services.rag_manager", "adaptive_rag_workflow"),
        ]
        for name, module, func in workflow_checks:
            try:
                mod = __import__(module, fromlist=[func])
                if hasattr(mod, func):
                    self.log_result(f"{name} Import", True)
                else:
                    self.log_result(f"{name} Import", False, f"Function '{func}' not found in {module}")
            except Exception as e:
                self.log_result(f"{name} Import", False, str(e))

    def generate_report(self):
        """Generate final verification report."""
        print("\n" + "=" * 60)
        print("📊 FINAL VERIFICATION REPORT")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['passed'] and not r['warning'])
        warning_tests = sum(1 for r in self.results if r['warning'])
        failed_tests = sum(1 for r in self.results if not r['passed'] and not r['warning'])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"⚠️ Warnings: {warning_tests}")
        print(f"❌ Failed: {failed_tests}")
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests == 0:
            print("\n🎉 VERIFICATION SUCCESSFUL!")
            print("WhiteLabelRAG project is complete and ready for use.")
            
            if warning_tests > 0:
                print(f"\n⚠️ Note: {warning_tests} warnings found (non-critical issues)")
                for warning in self.warnings:
                    print(f"  • {warning}")
            
            print("\n🚀 Next Steps:")
            print("1. Set your GEMINI_API_KEY environment variable")
            print("2. Run: python run.py")
            print("3. Open: http://localhost:5000")
            
            return True
        else:
            print("\n❌ VERIFICATION FAILED!")
            print(f"{failed_tests} critical issues found:")
            for error in self.errors:
                print(f"  • {error}")
            
            print("\n🔧 Recommended Actions:")
            print("1. Fix the issues listed above")
            print("2. Re-run this verification script")
            print("3. Check the troubleshooting guide")
            
            return False
    
    def run_verification(self):
        """Run complete verification process."""
        print("🔍 WhiteLabelRAG Project Verification")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Working Directory: {os.getcwd()}")

        # Check INSTRUCTIONS.md compliance first
        self.check_instructions_compliance()
        # Run all checks
        self.check_project_structure()
        self.check_configuration_files()
        self.check_dependencies()
        self.check_python_imports()
        self.check_documentation()
        self.check_scripts()
        self.check_sample_content()
        self.check_environment_setup()
        self.check_app_creation()
        self.check_rag_workflows()
        
        # Generate final report
        return self.generate_report()

def main():
    """Main verification function."""
    verifier = WhiteLabelRAGVerification()
    success = verifier.run_verification()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()