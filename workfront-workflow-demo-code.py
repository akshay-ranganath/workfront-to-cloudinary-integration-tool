"""
Workfront to Cloudinary Document Upload Workflow

This script automates the process of uploading documents from Workfront tasks to Cloudinary.
It searches for tasks with a specific status, downloads their associated documents,
uploads them to Cloudinary, and updates both the document and task status in Workfront.

Dependencies:
- cloudinary: For uploading files to Cloudinary
- requests: For HTTP API calls
- python-dotenv: For loading environment variables
- tempfile: For temporary file handling
- authenticate: Local module for Workfront authentication

Environment Variables Required:
- WORKFRONT_BASE_URL: Base URL for Workfront API
- WORKFRONT_API_KEY: API key for Workfront authentication
- WORKFRONT_BASE: Base domain for Workfront (e.g., 'example')
- WORKFRONT_CLIENT_ID: OAuth client ID
- WORKFRONT_CLIENT_SECRET: OAuth client secret
- WORKFRONT_CUSTOMER_ID: Customer ID (issuer)
- WORKFRONT_USER_ID: User ID (subject)
- WORKFRONT_PRIVATE_KEY: Private key for JWT signing
- CLOUDINARY_CLOUD_NAME: Cloudinary cloud name
- CLOUDINARY_API_KEY: Cloudinary API key
- CLOUDINARY_API_SECRET: Cloudinary API secret
- TASK_COMPLETE: Status code for completed tasks
- TASK_ERROR: Status code for failed tasks
"""

import cloudinary
import cloudinary.uploader
import requests
import json
import os
from dotenv import load_dotenv
import logging
import tempfile
from authenticate import get_workfront_session_id

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# API UTILITY FUNCTIONS
# ============================================================================

def api_request(
    uri_base: str,
    headers: dict,
    object_name: str = None,
    action: str = None,
    params: str = None,
    method: str = "GET",
    data: dict = None,
    object_id: str = None
):
    """
    Make API requests to Workfront with support for GET and PUT methods.
    
    Args:
        uri_base: Base URI for the API
        headers: Request headers
        object_name: Name of the object (e.g., 'TASK', 'document')
        action: Action to perform (e.g., 'search') - used for GET requests
        params: Query parameters string - used for GET requests
        method: HTTP method ('GET' or 'PUT')
        data: Data payload for PUT requests
        object_id: ID of the object for PUT requests
        
    Returns:
        Response data or status code depending on request type
    """
    result = None
    
    if method.upper() == "GET":
        url = f"{uri_base}/{object_name}/{action}"
        if params:
            url += f"?{params}"
        logging.debug(f"GET: {url}")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            logging.info("✅ GET Successful")
            result = response.json()
        else:
            logging.error("❌ Failed to GET")
            print(response.text)
            
    elif method.upper() == "PUT":
        url = f"{uri_base}/{object_name}/{object_id}"
        logging.debug(f"PUT: {url}")
        response = requests.put(url, headers=headers, json=data)
        
        if response.status_code == 200:
            logging.info("✅ PUT Successful")
            logging.debug(response.text)
            result = response.status_code
        else:
            print("❌ Failed to PUT")
            logging.error(f"Status: {response.status_code}")
            logging.error(response.text)
            result = response.status_code
    
    return result

# ============================================================================
# AUTHENTICATION FUNCTIONS
# ============================================================================

def login_to_workfront():
    """
    Authenticate with Workfront using OAuth JWT flow.
    
    Returns:
        str: Session ID for authenticated Workfront API calls
    """
    return get_workfront_session_id()

# ============================================================================
# DOCUMENT HANDLING FUNCTIONS
# ============================================================================

def download_document(document: dict, session_id: str):
    """
    Download a document from Workfront to a temporary file.
    
    Args:
        document: Dictionary containing document information with 'ID' key
        session_id: Authenticated session ID for Workfront API
        
    Returns:
        str: Path to the temporary file containing the downloaded document
    """
    resp = requests.get(
        f"{os.getenv('WORKFRONT_BASE_URL')}/document/download",
        params = {
            "ID": document['ID']
        },
        headers = {
            "sessionID": session_id
        }
    )
    
    # Create a temporary file to store the downloaded document
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(resp.content)
    temp_file.flush()
    return temp_file.name

def upload_to_cloudinary(local_path: str, document: dict):
    """
    Upload a local file to Cloudinary cloud storage.
    
    Args:
        local_path: Path to the local file to upload
        document: Dictionary containing document metadata
        
    Returns:
        str or None: Secure URL of the uploaded file, or None if upload failed
    """
    # Configure Cloudinary with credentials from environment variables
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET')
    )
    try:
        # Upload file to Cloudinary with metadata
        resp = cloudinary.uploader.upload(
            local_path,
            resource_type = 'auto',  # Auto-detect file type
            asset_folder = 'workfront',  # Organize files in workfront folder
            display_name = document['name'],  # Use document name as display name
            public_id = document['ID']  # Use Workfront document ID as public ID
        )
        return resp['secure_url']
    except Exception as e:
        logging.error(f"Error uploading document {document['ID']} to Cloudinary: {e}")
        return None

def cleanup_temp_file(local_path: str):
    """
    Remove temporary file from local filesystem.
    
    Args:
        local_path: Path to the temporary file to delete
    """
    os.remove(local_path)

# ============================================================================
# WORKFRONT UPDATE FUNCTIONS
# ============================================================================

def update_document_with_cloudinary_url(document: dict, cloudinary_url: str):
    """
    Update a Workfront document's description field with the Cloudinary URL.
    
    Args:
        document: Dictionary containing document information with 'ID' key
        cloudinary_url: The secure URL from Cloudinary upload
        
    Returns:
        int: HTTP status code from the update request
    """
    headers = {
        "Content-Type": "application/json",
        "apiKey": os.getenv('WORKFRONT_API_KEY')
    }
    update_data = {
        "description": cloudinary_url  # Store Cloudinary URL in description field
    }
    uri_base = f"{os.getenv('WORKFRONT_BASE_URL')}/attask/api/v19.0"
    
    try:
        status_code = api_request(
            uri_base=uri_base,
            headers=headers,
            object_name="document",
            object_id=document['ID'],
            method="PUT",
            data=update_data
        )
        
        if status_code == 200:
            logging.info(f"Document {document['ID']} updated with Cloudinary url {cloudinary_url}")
        else:
            logging.error(f"Failed to update document {document['ID']} with Cloudinary url {cloudinary_url}")
            
        return status_code
    except Exception as e:
        logging.error(f"Error updating document {document['ID']} with Cloudinary url {cloudinary_url}: {e}")
        return 500

def upload_document(document: dict, session_id: str):
    """
    Complete workflow to upload a document from Workfront to Cloudinary.
    
    This function:
    1. Downloads the document from Workfront
    2. Uploads it to Cloudinary
    3. Updates the Workfront document with the Cloudinary URL
    4. Cleans up temporary files
    
    Args:
        document: Dictionary containing document information
        session_id: Authenticated session ID for Workfront API
        
    Returns:
        str: Task status code (TASK_COMPLETE or TASK_ERROR from env vars)
    """
    logging.debug(f"Downloading document {document['ID']} from Workfront")
    local_path = download_document(document, session_id)
    logging.info(f"Downloaded document {document['ID']} to {local_path}")
    
    logging.debug(f"Uploading document {document['ID']} to Cloudinary")
    secure_url = upload_to_cloudinary(local_path, document)
    
    if secure_url:
        logging.debug(f"Document {document['ID']} uploaded to Cloudinary with url {secure_url}")
        # Update the document in Workfront with the Cloudinary URL
        update_document_with_cloudinary_url(document, secure_url)
        task_status = os.getenv('TASK_COMPLETE')
    else:
        logging.error(f"Failed to upload document {document['ID']} to Cloudinary")
        
        task_status = os.getenv('TASK_ERROR')
    
    # Clean up temporary file
    cleanup_temp_file(local_path)
    return task_status


def update_task_status(task_id: str, status: str):
    """
    Update the status of a Workfront task.
    
    Args:
        task_id: The ID of the task to update
        status: The new status code to set for the task
        
    Returns:
        int: HTTP status code from the update request
    """
    headers = {
        "Content-Type": "application/json",
        "apiKey": os.getenv('WORKFRONT_API_KEY')
    }
    
    update_data = {
        "status": status
    }
    uri_base = f"{os.getenv('WORKFRONT_BASE_URL')}/attask/api/v19.0"
    
    try:
        status_code = api_request(
            uri_base=uri_base,
            headers=headers,
            object_name="task",
            object_id=task_id,
            method="PUT",
            data=update_data
        )
        
        if status_code == 200:
            logging.info(f"Task {task_id} updated to status '{status}'")
        else:
            logging.error(f"Failed to update task {task_id} to status '{status}'")
            
        return status_code
    except Exception as e:
        logging.error(f"Error updating task {task_id} to status '{status}': {e}")
        return 500

# ============================================================================
# MAIN WORKFLOW EXECUTION
# ============================================================================

"""
Main Workflow Process:
1. Search for tasks with status "Upload to Cloudinary" (UPL)
2. For each task, check if it has documents
3. If documents exist, download and upload them to Cloudinary
4. Update the document with Cloudinary URL and task status
5. Clean up temporary files

This workflow processes tasks that are marked for Cloudinary upload,
handling the complete document migration process from Workfront to Cloudinary.
"""

proceed = True

# Step 1: Search for tasks that need Cloudinary upload
logger.info("Starting Workfront to Cloudinary document upload workflow...")
uri_base = f"{os.getenv('WORKFRONT_BASE_URL')}/attask/api/v19.0"

# Set up API headers for Workfront authentication
headers = {        
        "Content-Type": "application/json",
        "apiKey": os.getenv('WORKFRONT_API_KEY')
    }

# Search for tasks with status "UPL" (Upload to Cloudinary)
# Include document information in the response
response = api_request(
    uri_base=uri_base,
    headers=headers,
    object_name='TASK',
    action='search',
    params='fields=*,documents&isComplete=false&$$LIMIT=100&status_Sort=desc&status=UPL',
    method='GET'
)

# Check if any tasks were found
if len(response['data']) > 0:
    logger.info(f"Found {len(response['data'])} tasks with status 'Upload to Cloudinary'")
else:
    logger.info("No tasks found with status 'Upload to Cloudinary'")
    proceed = False

# Step 2: Validate that tasks have documents
if proceed:
    logger.info("Validating tasks have documents...")
    for task in response['data']:
        if task['hasDocuments']:            
            logger.info(f"Task {task['ID']} has {len(task['documents'])} documents")
        else:
            logger.error(f"Task {task['ID']} does not have documents")

# Step 3: Process document uploads
if proceed:
    logger.info("Starting document upload process...")
    
    # Authenticate with Workfront to get session ID for document downloads
    session_id = login_to_workfront()
    logger.info("Successfully authenticated with Workfront")

    # Process each task and its documents
    for task in response['data']:
        if task['hasDocuments']:
            logger.info(f"Processing task {task['ID']} with {len(task['documents'])} documents")
            
            # Upload each document in the task to Cloudinary
            for document in task['documents']:                
                task_status = upload_document(document, session_id)                
                # TODO: handle the task status
                # For now, we are assuming the task status is same as last task. Ideally, we want to mark this as a success only if all documents are uploaded successfully.
                
            # Update the task status based on upload success/failure
            update_task_status(task['ID'], task_status)
            logger.info(f"Task {task['ID']} updated to status: {task_status}")

# Workflow completion
logger.info("All tasks have been processed. Workflow complete.")        