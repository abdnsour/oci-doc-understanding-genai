# coding: utf-8
"""
Unified CV Processing System
Combines OCI Document Understanding and Generative AI for comprehensive CV analysis

This script provides:
1. PDF text extraction using OCI Document Understanding
2. AI-powered CV analysis using OCI Generative AI
3. Automated workflow for processing multiple CVs
"""

import oci
import uuid
import base64
import os
import glob
import json
import time
import urllib3
import ssl
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class UnifiedCVProcessor:
    """
    Unified CV processing system that combines document understanding and AI analysis
    """
    
    def __init__(self, config_profile: str = None, config_file: str = None):
        """
        Initialize the CV processor with OCI configuration
        
        Args:
            config_profile: OCI config profile name
            config_file: Path to OCI config file
        """
        profile = config_profile or os.getenv("OCI_CONFIG_PROFILE", "DEFAULT")
        cfg_file = config_file or os.getenv("OCI_CONFIG_FILE", "config")
        self.config = oci.config.from_file(cfg_file, profile)
        self.compartment_id = os.getenv("OCI_COMPARTMENT_ID")
        self.namespace = os.getenv("OCI_NAMESPACE")
        self.bucket_name = os.getenv("OCI_BUCKET_NAME")
        self.output_prefix = os.getenv("OCI_OUTPUT_PREFIX", "doc_understanding_output")
        self.model_id = os.getenv("OCI_GENAI_MODEL_ID")
        
        # Initialize OCI clients
        self._setup_document_understanding_client()
        self._setup_generative_ai_client()
        
        # Setup SSL configuration for development
        self._setup_ssl_config()
        
        # Prompt templates for AI analysis
        self.prompt_templates = {
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
      "duration": "string",
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
    
    def _setup_ssl_config(self):
        """Setup SSL configuration for development environment"""
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Monkey patch SSL verification to disable it
        original_ssl_context = ssl.create_default_context
        def create_unverified_context():
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            return context
        ssl.create_default_context = create_unverified_context
    
    def _setup_document_understanding_client(self):
        """Initialize OCI Document Understanding client"""
        self.aiservicedocument_client = oci.ai_document.AIServiceDocumentClientCompositeOperations(
            oci.ai_document.AIServiceDocumentClient(config=self.config)
        )
        self.object_storage_client = oci.object_storage.ObjectStorageClient(config=self.config)
    
    def _setup_generative_ai_client(self):
        """Initialize OCI Generative AI client"""
        endpoint = "https://inference.generativeai.us-phoenix-1.oci.oraclecloud.com"
        self.generative_ai_client = oci.generative_ai_inference.GenerativeAiInferenceClient(
            config=self.config,
            service_endpoint=endpoint,
            retry_strategy=oci.retry.NoneRetryStrategy(),
            timeout=(10, 240),
            disable_ssl_verification=True
        )
    
    def extract_text_from_pdf(self, pdf_file: str) -> str:
        """
        Extract text from a PDF file using OCI Document Understanding
        
        Args:
            pdf_file: Path to the PDF file
            
        Returns:
            Extracted text from the PDF
        """
        print(f"📄 Processing PDF: {os.path.basename(pdf_file)}")
        
        # Read and encode the PDF file
        try:
            with open(pdf_file, "rb") as document_file:
                text_extraction_sample_string = base64.b64encode(document_file.read()).decode('utf-8')
        except Exception as e:
            raise Exception(f"Error reading file {pdf_file}: {e}")
        
        # Setup text extraction feature
        text_extraction_feature = oci.ai_document.models.DocumentTextExtractionFeature()
        
        # Setup output location
        output_location = oci.ai_document.models.OutputLocation()
        output_location.namespace_name = self.namespace
        output_location.bucket_name = self.bucket_name
        output_location.prefix = self.output_prefix
        
        # Create processor job
        create_processor_job_details = oci.ai_document.models.CreateProcessorJobDetails(
            display_name=str(uuid.uuid4()),
            compartment_id=self.compartment_id,
            input_location=oci.ai_document.models.InlineDocumentContent(data=text_extraction_sample_string),
            output_location=output_location,
            processor_config=oci.ai_document.models.GeneralProcessorConfig(features=[text_extraction_feature])
        )
        
        try:
            print("⏳ Starting OCI Document Understanding job...")
            
            # Create the processor job
            create_processor_response = self.aiservicedocument_client.create_processor_job_and_wait_for_state(
                create_processor_job_details=create_processor_job_details
            )
            
            processor_job_id = create_processor_response.data.id
            print(f"📋 Processor job created with ID: {processor_job_id}")
            print("✅ Job completed successfully!")
            
            # Get the results
            print("📄 Extracting text from document...")
            get_object_response = self.object_storage_client.get_object(
                namespace_name=output_location.namespace_name,
                bucket_name=output_location.bucket_name,
                object_name=f"{output_location.prefix}/{processor_job_id}/_/results/defaultObject.json"
            )
            
            # Parse the JSON response
            result_data = json.loads(get_object_response.data.content.decode())
            
            # Extract text
            extracted_text = ""
            if 'pages' in result_data:
                for i, page in enumerate(result_data['pages'], 1):
                    extracted_text += f"\n--- Page {i} ---\n"
                    if 'lines' in page:
                        for line in page['lines']:
                            if 'text' in line:
                                extracted_text += line['text'] + "\n"
            
            return extracted_text
            
        except Exception as e:
            raise Exception(f"Error processing document {os.path.basename(pdf_file)}: {e}")
    
    def analyze_cv_with_ai(self, cv_text: str, prompt_type: str = "cv_analysis") -> str:
        """
        Analyze CV text using OCI Generative AI
        
        Args:
            cv_text: The CV text to analyze
            prompt_type: Type of analysis to perform
            
        Returns:
            AI analysis result
        """
        if prompt_type not in self.prompt_templates:
            raise ValueError(f"Invalid prompt type. Available types: {list(self.prompt_templates.keys())}")
        
        # Create content with the selected prompt template
        content = oci.generative_ai_inference.models.TextContent()
        content.text = self.prompt_templates[prompt_type].format(input=cv_text)
        
        # Create message
        message = oci.generative_ai_inference.models.Message()
        message.role = "USER"
        message.content = [content]
        
        # Create chat request
        chat_request = oci.generative_ai_inference.models.GenericChatRequest()
        chat_request.api_format = oci.generative_ai_inference.models.BaseChatRequest.API_FORMAT_GENERIC
        chat_request.messages = [message]
        chat_request.max_tokens = 600
        chat_request.temperature = 0
        chat_request.frequency_penalty = 0
        chat_request.presence_penalty = 0
        chat_request.top_p = 1
        chat_request.top_k = 0
        
        # Create chat details
        chat_detail = oci.generative_ai_inference.models.ChatDetails()
        chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(
            model_id=self.model_id
        )
        chat_detail.chat_request = chat_request
        chat_detail.compartment_id = self.compartment_id
        
        try:
            # Get response
            chat_response = self.generative_ai_client.chat(chat_detail)
            return chat_response.data.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error analyzing CV with AI: {e}")
    
    def process_single_cv(self, pdf_file: str, output_dir: str = "extracted_cv_data", 
                         analysis_types: List[str] = None) -> Dict[str, str]:
        """
        Process a single CV file: extract text and analyze with AI
        
        Args:
            pdf_file: Path to the PDF file
            output_dir: Directory to save outputs
            analysis_types: List of analysis types to perform
            
        Returns:
            Dictionary with extracted text and analysis results
        """
        if analysis_types is None:
            analysis_types = ["cv_analysis"]
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"📁 Created output directory: {output_dir}")
        
        cv_name = os.path.splitext(os.path.basename(pdf_file))[0]
        results = {"cv_name": cv_name, "pdf_file": pdf_file}
        
        try:
            # Step 1: Extract text from PDF
            print(f"\n{'='*60}")
            print(f"Processing CV: {cv_name}")
            print(f"{'='*60}")
            
            extracted_text = self.extract_text_from_pdf(pdf_file)
            results["extracted_text"] = extracted_text
            
            # Save extracted text
            text_filename = os.path.join(output_dir, f"extracted_text_{cv_name}.txt")
            with open(text_filename, "w", encoding="utf-8") as f:
                f.write(f"EXTRACTED TEXT FROM DOCUMENT: {cv_name}\n")
                f.write("=" * 50 + "\n")
                f.write(extracted_text)
                f.write("\n" + "=" * 50 + "\n")
                f.write("End of extracted text")
            
            print(f"✅ Text extracted and saved to: {text_filename}")
            print(f"📄 Total characters extracted: {len(extracted_text)}")
            
            # Step 2: Analyze with AI
            print(f"\n🤖 Analyzing CV with AI...")
            results["ai_analysis"] = {}
            
            for analysis_type in analysis_types:
                print(f"📊 Performing {analysis_type} analysis...")
                try:
                    analysis_result = self.analyze_cv_with_ai(extracted_text, analysis_type)
                    results["ai_analysis"][analysis_type] = analysis_result
                    
                    # Save analysis result
                    analysis_filename = os.path.join(output_dir, f"ai_analysis_{analysis_type}_{cv_name}.txt")
                    with open(analysis_filename, "w", encoding="utf-8") as f:
                        f.write(f"AI ANALYSIS: {analysis_type.upper()}\n")
                        f.write(f"CV: {cv_name}\n")
                        f.write("=" * 50 + "\n\n")
                        f.write(analysis_result)
                    
                    print(f"✅ {analysis_type} analysis saved to: {analysis_filename}")
                    
                except Exception as e:
                    print(f"❌ Error in {analysis_type} analysis: {e}")
                    results["ai_analysis"][analysis_type] = f"Error: {e}"
            
            print(f"✅ Completed processing: {cv_name}")
            return results
            
        except Exception as e:
            print(f"❌ Error processing {cv_name}: {e}")
            results["error"] = str(e)
            return results
    
    def process_multiple_cvs(self, cv_directory: str, output_dir: str = "extracted_cv_data",
                            analysis_types: List[str] = None, test_mode: bool = True) -> List[Dict[str, str]]:
        """
        Process multiple CV files from a directory
        
        Args:
            cv_directory: Directory containing PDF files
            output_dir: Directory to save outputs
            analysis_types: List of analysis types to perform
            test_mode: If True, process only first 3 files for testing
            
        Returns:
            List of results for each processed CV
        """
        if analysis_types is None:
            analysis_types = ["cv_analysis"]
        
        # Get all PDF files
        pdf_files = glob.glob(os.path.join(cv_directory, "*.pdf"))
        
        if not pdf_files:
            print(f"❌ No PDF files found in {cv_directory}")
            return []
        
        print(f"Found {len(pdf_files)} PDF files to process:")
        for pdf_file in pdf_files:
            print(f"  - {os.path.basename(pdf_file)}")
        
        # Test mode: Process only first 3 documents
        if test_mode:
            pdf_files = pdf_files[:3]
            print(f"🧪 TEST MODE: Processing only first {len(pdf_files)} documents")
        
        # Create output directory
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"📁 Created output directory: {output_dir}")
        
        all_results = []
        
        # Process each CV
        for index, pdf_file in enumerate(pdf_files, 1):
            print(f"\n{'='*80}")
            print(f"Processing document {index}/{len(pdf_files)}: {os.path.basename(pdf_file)}")
            print(f"{'='*80}")
            
            try:
                result = self.process_single_cv(pdf_file, output_dir, analysis_types)
                all_results.append(result)
            except Exception as e:
                print(f"❌ Failed to process {os.path.basename(pdf_file)}: {e}")
                all_results.append({
                    "cv_name": os.path.splitext(os.path.basename(pdf_file))[0],
                    "pdf_file": pdf_file,
                    "error": str(e)
                })
        
        # Summary
        successful = len([r for r in all_results if "error" not in r])
        failed = len(all_results) - successful
        
        print(f"\n🎉 Processing completed!")
        print(f"📊 Results: {successful} successful, {failed} failed")
        print(f"📁 All files saved in: {os.path.abspath(output_dir)}")
        
        return all_results


def main():
    """
    Main function to run the unified CV processing system
    """
    print("🚀 Starting Unified CV Processing System")
    print("=" * 60)
    
    # Initialize the processor
    try:
        processor = UnifiedCVProcessor()
        print("✅ OCI clients initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing OCI clients: {e}")
        return
    
    # Configuration
    cv_directory = os.getenv("INPUT_PDF_DIR", "./sample_documents")
    output_dir = "extracted_cv_data"
    analysis_types = ["cv_analysis", "skills_extraction", "experience_summary"]
    test_mode = True  # Set to False for production
    
    # Process CVs
    try:
        results = processor.process_multiple_cvs(
            cv_directory=cv_directory,
            output_dir=output_dir,
            analysis_types=analysis_types,
            test_mode=test_mode
        )
        
        print(f"\n📋 Processing Summary:")
        print(f"   Total CVs processed: {len(results)}")
        print(f"   Analysis types: {', '.join(analysis_types)}")
        print(f"   Output directory: {os.path.abspath(output_dir)}")
        
    except Exception as e:
        print(f"❌ Error in main processing: {e}")


if __name__ == "__main__":
    main()
