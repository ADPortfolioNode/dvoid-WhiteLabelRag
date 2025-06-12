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

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

class WhiteLabelRAGVerification:
    def __init__(self, project_root_path):
        self.project_root = Path(project_root_path)
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
            if not (self.project_root / dir_path).exists():
                missing_dirs.append(dir_path)
        
        if missing_dirs:
            self.log_result("Directory Structure", False, f"Missing directories: {', '.join(missing_dirs)}")
        else:
            self.log_result("Directory Structure", True, f"All {len(required_dirs)} directories present")
        
        # Check files
        missing_files = []
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.log_result("File Structure", False, f"Missing files: {', '.join(missing_files[:5])}{'...' if len(missing_files) > 5 else ''}")
        else:
            self.log_result("File Structure", True, f"All {len(required_files)} required files present")
    
    def check_python_imports(self):
        """Check if all Python modules can be imported."""
        print("\n🐍 Checking Python Imports...")
        
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
        env_example_path = self.project_root / '.env.example'
        if env_example_path.exists():
            with open(env_example_path, 'r') as f:
                env_content = f.read()
                if 'GEMINI_API_KEY' in env_content:
                    self.log_result("Environment Template", True, ".env.example contains required variables")
                else:
                    self.log_result("Environment Template", False, "GEMINI_API_KEY not found in .env.example")
        else:
            self.log_result("Environment Template", False, ".env.example file missing")
        
        # Check requirements.txt
        requirements_path = self.project_root / 'requirements.txt'
        if requirements_path.exists():
            with open(requirements_path, 'r') as f:
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
            if (self.project_root / file_name).exists():
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
            doc_file_path = self.project_root / doc_file
            if doc_file_path.exists():
                try:
                    with open(doc_file_path, 'r', encoding='utf-8') as f:
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
        
        for script_rel_path in scripts:
            script_abs_path = self.project_root / script_rel_path
            if script_abs_path.exists():
                # Check if script is executable (Unix-like systems)
                if script_rel_path.endswith('.sh') and os.name != 'nt':
                    if os.access(str(script_abs_path), os.X_OK):
                        self.log_result(f"Script {script_rel_path}", True, "Present and executable")
                    else:
                        self.log_result(f"Script {script_rel_path}", True, "Present but not executable", warning=True)
                else:
                    self.log_result(f"Script {script_rel_path}", True, "Present")
            else:
                self.log_result(f"Script {script_rel_path}", False, "Missing")
    
    def check_sample_content(self):
        """Check sample content and test files."""
        print("\n📄 Checking Sample Content...")
        
        # Check sample documents
        sample_dir = self.project_root / 'sample_documents'
        if sample_dir.exists():
            sample_files = list(sample_dir.glob('*'))
            if sample_files:
                self.log_result("Sample Documents", True, f"Found {len(sample_files)} sample files")
            else:
                self.log_result("Sample Documents", True, "Directory exists but empty", warning=True)
        else:
            self.log_result("Sample Documents", False, "sample_documents directory missing")
        
        # Check test files
        test_dir = self.project_root / 'tests'
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
        
        env_path = self.project_root / '.env'
        # Check for .env file
        if env_path.exists():
            self.log_result("Environment File", True, ".env file exists")
            
            # Check if GEMINI_API_KEY is set
            from dotenv import load_dotenv
            load_dotenv(dotenv_path=env_path)
            
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
        
        # Generate final report
        return self.generate_report()

import subprocess

def main():
    """Main verification function."""
    # project_root is defined globally at the top of the script
    # Ensure project_root is a Path object for the / operator
    current_project_root = Path(project_root)
    verifier = WhiteLabelRAGVerification(project_root_path=current_project_root)
    success = verifier.run_verification()
    if success:
        print("\\n✅ No errors found. Proceeding with Docker deployment...")
        try:
            # Proceed to build and run Docker container
            print("\\n🐳 Starting Docker build and run process...")
            # Assuming docker-compose.yml is at the project root (current_project_root)
            # and that docker-compose is in the system PATH.
            docker_compose_command = ["docker-compose", "up", "--build", "-d"]
            # Run docker-compose from the project root directory
            docker_process = subprocess.run(docker_compose_command, cwd=str(current_project_root), check=True, capture_output=True, text=True, shell=True)
            print("🐳 Docker containers built and started successfully.")
            if docker_process.stdout:
                print(f"Docker output:\\n{docker_process.stdout}")

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed during post-verification steps: {e}")
            if hasattr(e, 'stdout') and e.stdout:
                print(f"Stdout:\\n{e.stdout}")
            if hasattr(e, 'stderr') and e.stderr:
                print(f"Stderr:\\n{e.stderr}")
    else:
        print("\n❌ Errors found. App will not be started.")
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
