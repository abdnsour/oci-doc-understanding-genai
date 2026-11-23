# coding: utf-8
# Copyright (c) 2023, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.

##########################################################################
# chat_demo.py
# Supports Python 3
##########################################################################
# Info:
# Get texts from LLM model for given prompts using OCI Generative AI Service.
##########################################################################
# Application Command line(no parameter needed)
# python chat_demo.py
##########################################################################
import oci
import urllib3
import os
from dotenv import load_dotenv

load_dotenv()

# Setup basic variables
# Auth Config
compartment_id = os.getenv("OCI_COMPARTMENT_ID")
MODEL_ID = os.getenv("OCI_GENAI_MODEL_ID")
CONFIG_PROFILE = os.getenv("OCI_CONFIG_PROFILE", "DEFAULT")
CONFIG_FILE = os.getenv("OCI_CONFIG_FILE", "config")
config = oci.config.from_file(CONFIG_FILE, CONFIG_PROFILE)

# Custom prompt templates
PROMPT_TEMPLATES = {
    "cv_analysis": """You are an expert CV analyzer. Please analyze the following CV text and extract:

1. **Personal Information**: Name, contact details, location
2. **Professional Summary**: Key skills and experience
3. **Work Experience**: Job titles, companies, dates, responsibilities
4. **Education**: Degrees, institutions, graduation years
5. **Skills**: Technical and soft skills
6. **Certifications**: Any professional certifications
7. **Languages**: Languages spoken and proficiency levels

Format the output in a clean, structured way:

CV Text:
{input}

Analysis:""",

    "cv_json_analysis": """You are an expert CV analyzer. Analyze the following CV text and extract all relevant information in a structured JSON format.

IMPORTANT: Return ONLY valid JSON. No additional text, explanations, or markdown formatting.

Extract the following information and structure it as JSON:

{{
  "personal_info": {{
    "full_name": "string",
    "email": "string",
    "phone": "string",
    "location": "string",
    "linkedin": "string",
    "title": "string"
  }},
  "professional_summary": "string",
  "work_experience": [
    {{
      "job_title": "string",
      "company": "string",
      "start_date": "string",
      "end_date": "string",
      "duration": "string (extract if mentioned, otherwise calculate from start_date and end_date in format like '2 years 3 months' or 'Present')",
      "description": "string",
      "achievements": ["string"]
    }}
  ],
  "education": [
    {{
      "degree": "string",
      "institution": "string",
      "start_date": "string",
      "end_date": "string",
      "gpa": "string",
      "field_of_study": "string"
    }}
  ],
  "skills": {{
    "technical_skills": ["string"],
    "programming_languages": ["string"],
    "frameworks": ["string"],
    "tools": ["string"],
    "soft_skills": ["string"]
  }},
  "certifications": [
    {{
      "name": "string",
      "issuer": "string",
      "date": "string",
      "credential_id": "string"
    }}
  ],
  "projects": [
    {{
      "name": "string",
      "description": "string",
      "technologies": ["string"],
      "url": "string"
    }}
  ],
  "languages": [
    {{
      "language": "string",
      "proficiency": "string"
    }}
  ],
  "additional_info": {{
    "interests": ["string"],
    "volunteer_work": ["string"],
    "publications": ["string"],
    "awards": ["string"]
  }}
}}

CV Text:
{input}

JSON Response:""",

    "skills_extraction": """Extract only the technical and soft skills from this CV text. List them in two categories:

Technical Skills:
- [list technical skills]

Soft Skills:
- [list soft skills]

CV Text:
{input}""",

    "experience_summary": """Summarize the work experience from this CV in a concise format:

**Work Experience Summary:**
- [Job Title] at [Company] ([Duration])
  - Key responsibilities and achievements

CV Text:
{input}""",

    "general_analysis": """Analyze this CV and provide insights about the candidate's qualifications, strengths, and areas for improvement:

CV Text:
{input}

Analysis:"""
}

# Choose your prompt template
SELECTED_PROMPT = "cv_analysis"  # Change this to any key from PROMPT_TEMPLATES

# Service endpoint
endpoint = "https://inference.generativeai.us-phoenix-1.oci.oraclecloud.com"

# Disable SSL warnings (for development only)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Monkey patch SSL verification to disable it
import ssl
original_ssl_context = ssl.create_default_context
def create_unverified_context():
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context
ssl.create_default_context = create_unverified_context

# Also monkey patch urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create client with custom SSL configuration
generative_ai_inference_client = oci.generative_ai_inference.GenerativeAiInferenceClient(
    config=config, 
    service_endpoint=endpoint, 
    retry_strategy=oci.retry.NoneRetryStrategy(), 
    timeout=(10,240),
    disable_ssl_verification=True  # This fixes the Acronis certificate issue
)
chat_detail = oci.generative_ai_inference.models.ChatDetails()

content = oci.generative_ai_inference.models.TextContent()
content.text = PROMPT_TEMPLATES[SELECTED_PROMPT]
message = oci.generative_ai_inference.models.Message()
message.role = "USER"
message.content = [content]

chat_request = oci.generative_ai_inference.models.GenericChatRequest()
chat_request.api_format = oci.generative_ai_inference.models.BaseChatRequest.API_FORMAT_GENERIC
chat_request.messages = [message]
chat_request.max_tokens = 600
chat_request.temperature = 0
chat_request.frequency_penalty = 0
chat_request.presence_penalty = 0
chat_request.top_p = 1

chat_request.top_k = 0





chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id=MODEL_ID)
chat_detail.chat_request = chat_request
chat_detail.compartment_id = compartment_id

def analyze_cv_with_ai(cv_text, prompt_type="cv_analysis"):
    """
    Analyze CV text using OCI Generative AI
    
    Args:
        cv_text (str): The CV text to analyze
        prompt_type (str): Type of analysis to perform
        
    Returns:
        str: AI analysis result
    """
    # Update the prompt template
    content.text = PROMPT_TEMPLATES[prompt_type].format(input=cv_text)
    
    # Create new chat detail with updated content
    chat_detail = oci.generative_ai_inference.models.ChatDetails()
    message = oci.generative_ai_inference.models.Message()
    message.role = "USER"
    message.content = [content]
    
    chat_request = oci.generative_ai_inference.models.GenericChatRequest()
    chat_request.api_format = oci.generative_ai_inference.models.BaseChatRequest.API_FORMAT_GENERIC
    chat_request.messages = [message]
    chat_request.max_tokens = 600
    chat_request.temperature = 0
    chat_request.frequency_penalty = 0
    chat_request.presence_penalty = 0
    chat_request.top_p = 1
    chat_request.top_k = 0
    
    chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id=MODEL_ID)
    chat_detail.chat_request = chat_request
    chat_detail.compartment_id = compartment_id
    
    # Get response
    chat_response = generative_ai_inference_client.chat(chat_detail)
    
    return chat_response.data.choices[0].message.content

def analyze_cv_to_json(cv_text):
    """
    Analyze CV text and return structured JSON data
    
    Args:
        cv_text (str): The CV text to analyze
        
    Returns:
        dict: Structured JSON data extracted from CV
    """
    import json
    import re
    
    try:
        # Get AI analysis with JSON prompt
        ai_response = analyze_cv_with_ai(cv_text, "cv_json_analysis")
        
        # Clean the response to extract only JSON
        # Remove any text before the first { and after the last }
        json_start = ai_response.find('{')
        json_end = ai_response.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            raise ValueError("No JSON found in AI response")
        
        json_str = ai_response[json_start:json_end]
        
        # Parse JSON
        cv_data = json.loads(json_str)
        
        return cv_data
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print(f"Raw AI response: {ai_response}")
        return {"error": "Failed to parse JSON", "raw_response": ai_response}
    except Exception as e:
        print(f"❌ Error analyzing CV: {e}")
        return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    # Read the extracted text from your PDF
    try:
        with open("extracted_text.txt", "r", encoding="utf-8") as f:
            cv_text = f.read()
        
        print("🤖 Analyzing CV with AI...")
        print("=" * 50)
        
        # Analyze with JSON structure
        print("📊 Extracting structured JSON data...")
        json_data = analyze_cv_to_json(cv_text)
        
        if "error" in json_data:
            print(f"❌ Error: {json_data['error']}")
        else:
            print("✅ JSON data extracted successfully!")
            
            # Pretty print the JSON
            import json
            print("\n📋 Structured CV Data:")
            print("=" * 50)
            print(json.dumps(json_data, indent=2, ensure_ascii=False))
            
            # Save JSON to file
            with open("cv_structured_data.json", "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ JSON data saved to: cv_structured_data.json")
        
        # Also perform regular analysis for comparison
        print(f"\n📝 Regular Analysis:")
        print("=" * 50)
        analysis = analyze_cv_with_ai(cv_text, "cv_analysis")
        print(analysis)
        
        # Save the analysis to a file
        with open("ai_analysis.txt", "w", encoding="utf-8") as f:
            f.write("AI ANALYSIS OF CV\n")
            f.write("=" * 50 + "\n\n")
            f.write(analysis)
        
        print("\n✅ Analysis saved to: ai_analysis.txt")
        
    except FileNotFoundError:
        print("❌ Error: extracted_text.txt not found. Please run DocUnderStanding.py first.")
    except Exception as e:
        print(f"❌ Error: {e}")
