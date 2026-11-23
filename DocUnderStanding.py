# coding: utf-8
# Copyright (c) 2016, 2021, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.

##########################################################################
# inline_text_extraction_demo.py
#
# Supports Python 3
##########################################################################
# Info:
# Inline Text Extraction Processor Job creation using OCI AI Document Understanding service.
#
##########################################################################
# Application Command line(no parameter needed)
# python inline_text_extraction_demo.py
##########################################################################

"""
This python script provides an example of how to use OCI Document Understanding text extraction feature

The configuration file used by service clients will be sourced from the default location (~/.oci/config) and the
CONFIG_PROFILE profile will be used.

The sample attempts to extract text from an inline document
Successful run of this sample will create job results under object storage configured under output_location variable
"""
import oci
import uuid
import base64
import os
import glob
from dotenv import load_dotenv

load_dotenv()

# Setup basic variables
# Auth Config
CONFIG_PROFILE = os.getenv("OCI_CONFIG_PROFILE", "DEFAULT")
CONFIG_FILE = os.getenv("OCI_CONFIG_FILE", "config")
config = oci.config.from_file(CONFIG_FILE, CONFIG_PROFILE)

# Compartment where processor job will be created
COMPARTMENT_ID = os.getenv("OCI_COMPARTMENT_ID")

# Get all PDF files from input directory
cv_directory = os.getenv("INPUT_PDF_DIR", "./sample_documents")
pdf_files = glob.glob(os.path.join(cv_directory, "*.pdf"))

# Create output directory for extracted files
output_dir = "extracted_cv_data"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"📁 Created output directory: {output_dir}")
else:
    print(f"📁 Using existing output directory: {output_dir}")

print(f"Found {len(pdf_files)} PDF files to process:")
for pdf_file in pdf_files:
    print(f"  - {os.path.basename(pdf_file)}")

# Initialize OCI clients once outside the loop for better performance
def create_processor_job_callback(times_called, response):
    print("Waiting for processor lifecycle state to go into succeeded state:", response.data)

aiservicedocument_client = oci.ai_document.AIServiceDocumentClientCompositeOperations(oci.ai_document.AIServiceDocumentClient(config=config))
object_storage_client = oci.object_storage.ObjectStorageClient(config=config)

# Test mode: Process only first 3 documents to test
test_mode = True
if test_mode:
    pdf_files = pdf_files[:3]  # Process only first 3 files for testing
    print(f"🧪 TEST MODE: Processing only first {len(pdf_files)} documents")

# Process each CV file
for index, pdf_file in enumerate(pdf_files, 1):
    print(f"\n{'='*60}")
    print(f"Processing document {index}/{len(pdf_files)}: {os.path.basename(pdf_file)}")
    print(f"{'='*60}")
    
    # Read and encode the PDF file
    text_extraction_sample_string = None
    try:
        with open(pdf_file, "rb") as document_file:
            text_extraction_sample_string = base64.b64encode(document_file.read()).decode('utf-8')
    except Exception as e:
        print(f"❌ Error reading file {pdf_file}: {e}")
        continue

    # Text extraction feature 
    text_extraction_feature = oci.ai_document.models.DocumentTextExtractionFeature()

    # Setup the output location where processor job results will be created
    output_location = oci.ai_document.models.OutputLocation()
    output_location.namespace_name = os.getenv("OCI_NAMESPACE")
    output_location.bucket_name = os.getenv("OCI_BUCKET_NAME")
    output_location.prefix = os.getenv("OCI_OUTPUT_PREFIX", "doc_understanding_output")

    # Create a processor_job for text_extraction feature
    create_processor_job_details_text_extraction = oci.ai_document.models.CreateProcessorJobDetails(
                                                        display_name=str(uuid.uuid4()),
                                                        compartment_id=COMPARTMENT_ID,
                                                        input_location=oci.ai_document.models.InlineDocumentContent(data=text_extraction_sample_string),
                                                        output_location=output_location,
                                                        processor_config=oci.ai_document.models.GeneralProcessorConfig(features=[text_extraction_feature]))

    print("Calling create_processor with create_processor_job_details_text_extraction:", create_processor_job_details_text_extraction)
    
    try:
        print("⏳ Starting OCI Document Understanding job...")
        
        # First, create the processor job without waiting
        create_processor_response = aiservicedocument_client.create_processor_job(
            create_processor_job_details=create_processor_job_details_text_extraction)
        
        processor_job_id = create_processor_response.data.id
        print(f"📋 Processor job created with ID: {processor_job_id}")
        print("⏳ Waiting for job to complete (this may take a few minutes)...")
        
        # Now wait for completion with timeout
        import time
        max_wait_time = 300  # 5 minutes
        check_interval = 10  # Check every 10 seconds
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            try:
                get_job_response = aiservicedocument_client.get_processor_job(processor_job_id=processor_job_id)
                job_state = get_job_response.data.lifecycle_state
                
                print(f"🔄 Job status: {job_state} (elapsed: {elapsed_time}s)")
                
                if job_state == oci.ai_document.models.ProcessorJob.LIFECYCLE_STATE_SUCCEEDED:
                    print("✅ Job completed successfully!")
                    break
                elif job_state in [oci.ai_document.models.ProcessorJob.LIFECYCLE_STATE_FAILED, 
                                 oci.ai_document.models.ProcessorJob.LIFECYCLE_STATE_CANCELED]:
                    raise Exception(f"Job failed with state: {job_state}")
                
                time.sleep(check_interval)
                elapsed_time += check_interval
                
            except Exception as check_error:
                print(f"⚠️  Error checking job status: {check_error}")
                time.sleep(check_interval)
                elapsed_time += check_interval
        
        if elapsed_time >= max_wait_time:
            raise Exception("Job timed out after 5 minutes")
        
        print("📄 Extracting text from document...")
        get_object_response = object_storage_client.get_object(namespace_name=output_location.namespace_name,
                                                                bucket_name=output_location.bucket_name,
                                                                object_name="{}/{}/_/results/defaultObject.json".format(
                                                                    output_location.prefix, processor_job_id))
        
    except Exception as e:
        print(f"❌ Error processing document {os.path.basename(pdf_file)}: {e}")
        print(f"⏭️  Skipping to next document...")
        continue

    # Parse the JSON response
    try:
        import json
        result_data = json.loads(get_object_response.data.content.decode())

        # Extract text and save to file
        extracted_text = ""
        if 'pages' in result_data:
            for i, page in enumerate(result_data['pages'], 1):
                extracted_text += f"\n--- Page {i} ---\n"
                if 'lines' in page:
                    for line in page['lines']:
                        if 'text' in line:
                            extracted_text += line['text'] + "\n"

        # Create output filename based on the CV name
        cv_name = os.path.splitext(os.path.basename(pdf_file))[0]
        output_filename = os.path.join(output_dir, f"extracted_text_{cv_name}.txt")
        
        # Save to text file
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(f"EXTRACTED TEXT FROM DOCUMENT: {cv_name}\n")
            f.write("=" * 50 + "\n")
            f.write(extracted_text)
            f.write("\n" + "=" * 50 + "\n")
            f.write("End of extracted text")

        print(f"✅ Text extracted and saved to: {output_filename}")
        print(f"📄 Total characters extracted: {len(extracted_text)}")

        # Also save the raw JSON for reference
        json_filename = os.path.join(output_dir, f"raw_output_{cv_name}.json")
        with open(json_filename, "w", encoding="utf-8") as f:
            f.write(get_object_response.data.content.decode())

        print(f"📁 Raw JSON data saved to: {json_filename}")
        print(f"✅ Completed processing: {os.path.basename(pdf_file)}")
        
    except Exception as e:
        print(f"❌ Error parsing or saving data for {os.path.basename(pdf_file)}: {e}")
        print(f"⏭️  Skipping to next document...")
        continue

print(f"\n🎉 All CV files processed successfully!")
print(f"📁 All extracted files saved in: {os.path.abspath(output_dir)}")
print(f"📊 Total files created: {len(pdf_files) * 2} (2 files per CV: .txt and .json)")

