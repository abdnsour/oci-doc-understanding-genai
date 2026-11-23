#!/usr/bin/env python3
"""
Simple test to demonstrate why AI analysis isn't working
"""

import os

def test_without_oci():
    """Test the workflow without OCI dependencies"""
    print("🧪 Testing CV Analysis Workflow")
    print("=" * 50)
    
    # Check if extracted text exists
    extracted_text_file = "./extracted_cv_data/extracted_text_sample_cv.txt"
    
    if not os.path.exists(extracted_text_file):
        print(f"❌ Extracted text file not found: {extracted_text_file}")
        print("💡 This means the document understanding step didn't complete successfully")
        return
    
    print("✅ Extracted text file found")
    
    # Check for AI analysis files
    ai_analysis_files = []
    for file in os.listdir("./extracted_cv_data"):
        if file.startswith("ai_analysis_"):
            ai_analysis_files.append(file)
    
    if ai_analysis_files:
        print(f"✅ Found AI analysis files: {ai_analysis_files}")
    else:
        print("❌ No AI analysis files found")
        print("💡 This means the AI analysis step didn't run or failed")
    
    # Read the extracted text
    with open(extracted_text_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    print(f"\n📄 Extracted text length: {len(content)} characters")
    print(f"📄 Preview: {content[:200]}...")
    
    # Check if the text looks good
    if len(content.strip()) > 50:
        print("✅ CV text extraction appears successful")
    else:
        print("❌ CV text extraction may have issues")
    
    print("\n🔍 Analysis:")
    print("1. Document Understanding: ✅ Working (text extracted)")
    print("2. AI Analysis: ❌ Not working (no analysis files created)")
    print("\n💡 The issue is likely:")
    print("   - OCI SDK not properly installed")
    print("   - OCI configuration issues")
    print("   - Network/authentication problems")
    print("   - Generative AI service not accessible")

if __name__ == "__main__":
    test_without_oci()

