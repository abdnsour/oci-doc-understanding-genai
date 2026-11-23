# coding: utf-8
"""
JSON CV Analyzer
A specialized script for extracting structured JSON data from CVs using OCI Generative AI

This script demonstrates how to:
1. Extract text from PDF using OCI Document Understanding
2. Analyze CV with AI to get structured JSON data
3. Save and display the results in a frontend-friendly format
"""

import os
import json
import sys
from genAI import analyze_cv_to_json, analyze_cv_with_ai
from unified_cv_processor import UnifiedCVProcessor

def test_json_extraction():
    """
    Test the JSON extraction functionality with the existing extracted text
    """
    print("🚀 Testing JSON CV Analysis")
    print("=" * 60)
    
    # Read the extracted text
    try:
        with open("extracted_text.txt", "r", encoding="utf-8") as f:
            cv_text = f.read()
        
        print(f"📄 Loaded CV text ({len(cv_text)} characters)")
        
        # Extract JSON data
        print("\n🤖 Analyzing CV with AI for JSON extraction...")
        json_data = analyze_cv_to_json(cv_text)
        
        if "error" in json_data:
            print(f"❌ Error: {json_data['error']}")
            if "raw_response" in json_data:
                print("\nRaw AI Response:")
                print("-" * 40)
                print(json_data["raw_response"])
            return None
        
        print("✅ JSON data extracted successfully!")
        
        # Display the structured data
        print("\n📋 Extracted CV Data:")
        print("=" * 60)
        print(json.dumps(json_data, indent=2, ensure_ascii=False))
        
        # Save to file
        output_file = "cv_structured_output.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 JSON data saved to: {output_file}")
        
        # Display summary
        print("\n📊 Data Summary:")
        print("-" * 30)
        if "personal_info" in json_data:
            personal = json_data["personal_info"]
            print(f"Name: {personal.get('full_name', 'N/A')}")
            print(f"Email: {personal.get('email', 'N/A')}")
            print(f"Phone: {personal.get('phone', 'N/A')}")
            print(f"Location: {personal.get('location', 'N/A')}")
        
        if "work_experience" in json_data:
            print(f"Work Experience: {len(json_data['work_experience'])} positions")
        
        if "education" in json_data:
            print(f"Education: {len(json_data['education'])} entries")
        
        if "skills" in json_data:
            skills = json_data["skills"]
            total_skills = sum(len(skill_list) for skill_list in skills.values() if isinstance(skill_list, list))
            print(f"Skills: {total_skills} total skills")
        
        return json_data
        
    except FileNotFoundError:
        print("❌ Error: extracted_text.txt not found.")
        print("Please run DocUnderStanding.py first to extract text from PDF.")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def process_pdf_to_json(pdf_path):
    """
    Process a PDF file and extract structured JSON data
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        dict: Structured JSON data or None if error
    """
    print(f"🔄 Processing PDF: {os.path.basename(pdf_path)}")
    print("=" * 60)
    
    try:
        # Initialize the unified processor
        processor = UnifiedCVProcessor()
        
        # Extract text from PDF
        print("📄 Extracting text from PDF...")
        extracted_text = processor.extract_text_from_pdf(pdf_path)
        
        # Analyze with AI for JSON
        print("🤖 Analyzing with AI for JSON extraction...")
        json_data = analyze_cv_to_json(extracted_text)
        
        if "error" in json_data:
            print(f"❌ Error: {json_data['error']}")
            return None
        
        print("✅ JSON data extracted successfully!")
        
        # Save results
        cv_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_file = f"cv_json_{cv_name}.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 JSON data saved to: {output_file}")
        
        return json_data
        
    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        return None

def create_frontend_example(json_data):
    """
    Create a frontend-friendly example showing how to use the JSON data
    
    Args:
        json_data (dict): The structured CV data
    """
    if not json_data or "error" in json_data:
        print("❌ No valid JSON data to create frontend example")
        return
    
    print("\n🌐 Frontend Integration Example:")
    print("=" * 60)
    
    # Create a simple HTML example
    html_example = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CV Data Display</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ color: #333; border-bottom: 2px solid #007bff; }}
        .info-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .card {{ background: #f8f9fa; padding: 15px; border-radius: 8px; }}
        .skill-tag {{ background: #007bff; color: white; padding: 4px 8px; margin: 2px; border-radius: 4px; display: inline-block; }}
    </style>
</head>
<body>
    <h1>CV Information</h1>
    
    <div class="section">
        <h2>Personal Information</h2>
        <div class="info-grid">
            <div class="card">
                <strong>Name:</strong> {json_data.get('personal_info', {}).get('full_name', 'N/A')}<br>
                <strong>Email:</strong> {json_data.get('personal_info', {}).get('email', 'N/A')}<br>
                <strong>Phone:</strong> {json_data.get('personal_info', {}).get('phone', 'N/A')}<br>
                <strong>Location:</strong> {json_data.get('personal_info', {}).get('location', 'N/A')}
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>Professional Summary</h2>
        <p>{json_data.get('professional_summary', 'N/A')}</p>
    </div>
    
    <div class="section">
        <h2>Work Experience</h2>
        {''.join([f'''
        <div class="card">
            <h3>{exp.get('job_title', 'N/A')} at {exp.get('company', 'N/A')}</h3>
            <p><strong>Duration:</strong> {exp.get('start_date', 'N/A')} - {exp.get('end_date', 'N/A')}</p>
            <p>{exp.get('description', 'N/A')}</p>
        </div>
        ''' for exp in json_data.get('work_experience', [])])}
    </div>
    
    <div class="section">
        <h2>Skills</h2>
        <div>
            <h3>Technical Skills</h3>
            {''.join([f'<span class="skill-tag">{skill}</span>' for skill in json_data.get('skills', {}).get('technical_skills', [])])}
        </div>
        <div style="margin-top: 15px;">
            <h3>Programming Languages</h3>
            {''.join([f'<span class="skill-tag">{lang}</span>' for lang in json_data.get('skills', {}).get('programming_languages', [])])}
        </div>
    </div>
    
    <script>
        // Example JavaScript to work with the JSON data
        const cvData = {json.dumps(json_data, indent=8)};
        
        // Function to search for specific skills
        function hasSkill(skillName) {{
            const allSkills = [
                ...cvData.skills.technical_skills || [],
                ...cvData.skills.programming_languages || [],
                ...cvData.skills.frameworks || [],
                ...cvData.skills.tools || []
            ];
            return allSkills.some(skill => 
                skill.toLowerCase().includes(skillName.toLowerCase())
            );
        }}
        
        // Example usage
        console.log('Has Python skill:', hasSkill('Python'));
        console.log('Has Machine Learning skill:', hasSkill('Machine Learning'));
    </script>
</body>
</html>
"""
    
    # Save HTML example
    with open("cv_frontend_example.html", "w", encoding="utf-8") as f:
        f.write(html_example)
    
    print("📄 Frontend example created: cv_frontend_example.html")
    print("🌐 Open this file in a browser to see how the JSON data can be displayed")
    
    # Create JavaScript example
    js_example = f"""
// JavaScript example for working with CV JSON data
const cvData = {json.dumps(json_data, indent=4)};

// Helper functions for frontend integration
class CVDataHandler {{
    constructor(data) {{
        this.data = data;
    }}
    
    // Get personal information
    getPersonalInfo() {{
        return this.data.personal_info || {{}};
    }}
    
    // Get all skills as a flat array
    getAllSkills() {{
        const skills = this.data.skills || {{}};
        return [
            ...(skills.technical_skills || []),
            ...(skills.programming_languages || []),
            ...(skills.frameworks || []),
            ...(skills.tools || []),
            ...(skills.soft_skills || [])
        ];
    }}
    
    // Search for specific skill
    hasSkill(skillName) {{
        const allSkills = this.getAllSkills();
        return allSkills.some(skill => 
            skill.toLowerCase().includes(skillName.toLowerCase())
        );
    }}
    
    // Get work experience by company
    getExperienceByCompany(companyName) {{
        return (this.data.work_experience || []).filter(exp => 
            exp.company && exp.company.toLowerCase().includes(companyName.toLowerCase())
        );
    }}
    
    // Get education by degree type
    getEducationByDegree(degreeType) {{
        return (this.data.education || []).filter(edu => 
            edu.degree && edu.degree.toLowerCase().includes(degreeType.toLowerCase())
        );
    }}
    
    // Calculate years of experience
    getTotalExperience() {{
        const experiences = this.data.work_experience || [];
        // This is a simplified calculation - you might want to improve this
        return experiences.length;
    }}
}}

// Usage example
const cvHandler = new CVDataHandler(cvData);

console.log('Personal Info:', cvHandler.getPersonalInfo());
console.log('All Skills:', cvHandler.getAllSkills());
console.log('Has Python:', cvHandler.hasSkill('Python'));
console.log('Total Experience:', cvHandler.getTotalExperience());
"""
    
    with open("cv_data_handler.js", "w", encoding="utf-8") as f:
        f.write(js_example)
    
    print("📄 JavaScript helper created: cv_data_handler.js")
    print("💡 Use this JavaScript class to easily work with CV data in your frontend")

def main():
    """
    Main function to run the JSON CV analyzer
    """
    print("🚀 JSON CV Analyzer")
    print("=" * 60)
    print("This tool extracts structured JSON data from CVs for frontend integration")
    print()
    
    # Check if extracted text exists
    if os.path.exists("extracted_text.txt"):
        print("📄 Found existing extracted text, analyzing...")
        json_data = test_json_extraction()
        
        if json_data:
            create_frontend_example(json_data)
    else:
        print("❌ No extracted text found.")
        print("Please run DocUnderStanding.py first to extract text from a PDF.")
        
        # Offer to process a PDF directly
        pdf_path = input("\nEnter path to a PDF file to process (or press Enter to skip): ").strip()
        if pdf_path and os.path.exists(pdf_path):
            json_data = process_pdf_to_json(pdf_path)
            if json_data:
                create_frontend_example(json_data)
        else:
            print("No PDF file provided. Exiting.")

if __name__ == "__main__":
    main()
