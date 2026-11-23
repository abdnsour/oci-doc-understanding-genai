#!/usr/bin/env python3
"""
Example usage of the Unified CV Processing System

This script demonstrates how to use the UnifiedCVProcessor class
for different scenarios.
"""

import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from unified_cv_processor import UnifiedCVProcessor

def example_single_cv_processing():
    """Example: Process a single CV file"""
    print("🔍 Example: Single CV Processing")
    print("=" * 50)
    
    # Initialize processor
    processor = UnifiedCVProcessor()
    
    # Process a single CV
    pdf_file = "./sample_documents/sample_cv.pdf"
    
    if os.path.exists(pdf_file):
        result = processor.process_single_cv(
            pdf_file=pdf_file,
            analysis_types=["cv_analysis", "skills_extraction"]
        )
        
        print(f"✅ Processed CV: {result['cv_name']}")
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"📄 Text length: {len(result['extracted_text'])} characters")
            print(f"🤖 Analysis types completed: {list(result['ai_analysis'].keys())}")
    else:
        print(f"❌ File not found: {pdf_file}")

def example_batch_processing():
    """Example: Process multiple CVs with different analysis types"""
    print("\n🔍 Example: Batch Processing")
    print("=" * 50)
    
    # Initialize processor
    processor = UnifiedCVProcessor()
    
    # Process multiple CVs
    cv_directory = "./sample_documents"
    analysis_types = ["cv_analysis", "skills_extraction", "experience_summary"]
    
    if os.path.exists(cv_directory):
        results = processor.process_multiple_cvs(
            cv_directory=cv_directory,
            analysis_types=analysis_types,
            test_mode=True  # Process only first 3 CVs
        )
        
        print(f"📊 Batch processing completed:")
        print(f"   Total CVs processed: {len(results)}")
        print(f"   Analysis types: {', '.join(analysis_types)}")
        
        # Show summary of results
        successful = len([r for r in results if "error" not in r])
        failed = len(results) - successful
        print(f"   Successful: {successful}")
        print(f"   Failed: {failed}")
    else:
        print(f"❌ Directory not found: {cv_directory}")

def example_custom_analysis():
    """Example: Custom analysis with specific prompt"""
    print("\n🔍 Example: Custom Analysis")
    print("=" * 50)
    
    # Initialize processor
    processor = UnifiedCVProcessor()
    
    # Add a custom prompt template
    processor.prompt_templates["custom_analysis"] = """
    Analyze this CV and provide a brief summary focusing on:
    1. Years of experience
    2. Key technical skills
    3. Education level
    4. Career progression
    
    CV Text:
    {input}
    
    Summary:
    """
    
    # Process with custom analysis
    pdf_file = "./sample_documents/sample_cv.pdf"
    
    if os.path.exists(pdf_file):
        result = processor.process_single_cv(
            pdf_file=pdf_file,
            analysis_types=["custom_analysis"]
        )
        
        print(f"✅ Custom analysis completed for: {result['cv_name']}")
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print("📋 Custom analysis result saved to output directory")
    else:
        print(f"❌ File not found: {pdf_file}")

def main():
    """Run all examples"""
    print("🚀 Unified CV Processing System - Examples")
    print("=" * 60)
    
    try:
        # Example 1: Single CV processing
        example_single_cv_processing()
        
        # Example 2: Batch processing
        example_batch_processing()
        
        # Example 3: Custom analysis
        example_custom_analysis()
        
        print("\n🎉 All examples completed!")
        print("📁 Check the 'extracted_cv_data' directory for output files")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")

if __name__ == "__main__":
    main()
