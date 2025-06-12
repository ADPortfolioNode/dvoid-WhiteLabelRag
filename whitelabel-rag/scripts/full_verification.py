import sys
import subprocess
import os

def run_final_verification():
    print("=== Running final-verification.py ===")
    result = subprocess.run([sys.executable, 'scripts/final-verification.py'])
    if result.returncode != 0:
        print("final-verification.py failed")
        # Attempt to fix errors based on verification results using INSTRUCTIONS.md guidance
        print("Attempting to auto-correct startup and workflow issues...")
        # Example auto-correction implementations:

        # 1. Check and set missing environment variables from .env.example
        env_example_path = '.env.example'
        env_path = '.env'
        if os.path.exists(env_example_path) and not os.path.exists(env_path):
            print("Creating .env file from .env.example")
            with open(env_example_path, 'r') as f:
                env_content = f.read()
            with open(env_path, 'w') as f:
                f.write(env_content)
            print(".env file created. Please update with your actual secrets.")

        # 2. Install missing dependencies using requirements.txt
        print("Installing dependencies from requirements.txt")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

        # 3. Check for missing files or directories (basic example)
        required_dirs = ['app', 'scripts', 'tests']
        for d in required_dirs:
            if not os.path.exists(d):
                print(f"Warning: Required directory '{d}' is missing. Please add it manually.")

        # After auto-correction, re-run verification once
        print("Re-running final-verification.py after auto-correction...")
        retry_result = subprocess.run([sys.executable, 'scripts/final-verification.py'])
        if retry_result.returncode != 0:
            print("Verification still failed after auto-correction. Please fix issues manually.")
            return False
        else:
            print("Verification passed after auto-correction.")
            return True

    return result.returncode == 0

def run_test_internet_search():
    print("\n=== Running test_internet_search.py ===")
    result = subprocess.run([sys.executable, 'scripts/test_internet_search.py'])
    if result.returncode != 0:
        print("test_internet_search.py failed")
    return result.returncode == 0

def run_verify_database():
    print("\n=== Running verify_database.py ===")
    result = subprocess.run([sys.executable, 'scripts/verify_database.py'])
    if result.returncode != 0:
        print("verify_database.py failed")
    return result.returncode == 0

def run_test_google_search_bat():
    print("\n=== Running test_google_search.bat ===")
    # Use cmd to run the batch file
    result = subprocess.run(['cmd', '/c', 'scripts\\test_google_search.bat'])
    if result.returncode != 0:
        print("test_google_search.bat failed")
    return result.returncode == 0

def main():
    print("🔍 Starting Full Verification Process")
    print("="*60)
    all_passed = True

    # Run final verification
    if not run_final_verification():
        all_passed = False

    # Run test_internet_search.py (already covered by test_google_search.bat, but run separately for completeness)
    if not run_test_internet_search():
        all_passed = False

    # Run verify_database.py
    if not run_verify_database():
        all_passed = False

    # Run test_google_search.bat (which runs test_internet_search.py)
    if not run_test_google_search_bat():
        all_passed = False

    print("\n" + "="*60)
    if all_passed:
        print("🎉 FULL VERIFICATION PASSED! Ready for go-live.")
        sys.exit(0)
    else:
        print("❌ FULL VERIFICATION FAILED! Please check errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
