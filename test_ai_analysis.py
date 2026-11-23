#!/usr/bin/env python3
"""
Test script to debug AI analysis functionality
"""

import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from unified_cv_processor import UnifiedCVProcessor

def test_ai_analysis():
    """Test AI analysis with extracted text"""
    print("🧪 Testing AI Analysis")
    print("=" * 50)
    
    # Read the extracted text
    extracted_text_file = "./extracted_cv_data/extracted_text_sample_cv.txt"
    
    if not os.path.exists(extracted_text_file):
        print(f"❌ Extracted text file not found: {extracted_text_file}")
        return
    
    # Read the text content (skip the header lines)
    with open(extracted_text_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Find the actual text content (skip header and separator lines)
    text_content = ""
    start_reading = False
    for line in lines:
        if line.strip() == "--- Page 1 ---":
            start_reading = True
            continue
        if line.strip() == "==================================================":
            break
        if start_reading:
            text_content += line
    
    print(f"📄 Text content length: {len(text_content)} characters")
    print(f"📄 First 200 characters: {text_content[:200]}...")
    
    # Initialize processor
    try:
        processor = UnifiedCVProcessor()
        print("✅ Processor initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing processor: {e}")
        return
    
    # Test AI analysis
    try:
        print("\n🤖 Testing AI analysis...")
        analysis_result = processor.analyze_cv_with_ai(text_content, "cv_analysis")
        print("✅ AI analysis completed successfully!")
        print(f"📄 Analysis result length: {len(analysis_result)} characters")
        print(f"📄 Analysis preview: {analysis_result[:300]}...")
        
        # Save the result
        output_file = "./extracted_cv_data/test_ai_analysis.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("AI ANALYSIS TEST RESULT\n")
            f.write("=" * 50 + "\n\n")
            f.write(analysis_result)
        
        print(f"💾 Analysis saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error in AI analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_analysis()

