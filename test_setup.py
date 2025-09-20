#!/usr/bin/env python3
"""
Quick setup test for Pfadi AI Assistent
"""

import sys
import os
from pathlib import Path

def test_backend_structure():
    """Test if backend structure is correct"""
    backend_path = Path("backend")
    
    required_files = [
        "backend/app/__init__.py",
        "backend/app/main.py", 
        "backend/app/core/config.py",
        "backend/app/api/v1/api.py",
        "backend/requirements.txt",
        "backend/Dockerfile"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing backend files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ Backend structure is correct")
    return True

def test_frontend_structure():
    """Test if frontend structure is correct"""
    required_files = [
        "frontend/package.json",
        "frontend/src/App.tsx", 
        "frontend/vite.config.ts",
        "frontend/Dockerfile"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing frontend files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ Frontend structure is correct") 
    return True

def test_docker_setup():
    """Test if Docker setup is correct"""
    required_files = [
        "docker-compose.yml",
        ".env.example"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing Docker files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ Docker setup is correct")
    return True

def test_project_structure():
    """Test overall project structure"""
    required_dirs = [
        "backend",
        "frontend", 
        "data",
        "docs"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print("❌ Missing directories:")
        for dir in missing_dirs:
            print(f"   - {dir}")
        return False
    
    print("✅ Project structure is correct")
    return True

def main():
    """Run all tests"""
    print("🏕️ Testing Pfadi AI Assistent Setup\n")
    
    tests = [
        test_project_structure,
        test_backend_structure,
        test_frontend_structure,
        test_docker_setup
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    if all(results):
        print("🎉 All tests passed! Setup is ready.")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and configure your Azure credentials")
        print("2. Run: docker-compose up --build")
        print("3. Open http://localhost:3000 for frontend")
        print("4. Open http://localhost:8000/docs for API documentation")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())