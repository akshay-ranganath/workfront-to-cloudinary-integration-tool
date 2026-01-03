"""
Document Processor Module

Orchestrates the workflow of processing documents from Workfront to Cloudinary.
Handles the complete pipeline: download -> upload -> update.
"""

import logging
import tempfile
import os
from typing import Dict, List, Tuple
from workfront_api import WorkfrontAPI, WorkfrontAPIError
from cloudinary_service import CloudinaryService, CloudinaryServiceError
from config import Config

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Processes documents from Workfront to Cloudinary."""
    
    def __init__(self, workfront_api: WorkfrontAPI, cloudinary_service: CloudinaryService):
        """
        Initialize document processor.
        
        Args:
            workfront_api: Workfront API client instance
            cloudinary_service: Cloudinary service instance
        """
        self.workfront_api = workfront_api
        self.cloudinary_service = cloudinary_service
    
    def _download_to_temp_file(self, document: Dict, session_id: str) -> str:
        """
        Download a document from Workfront to a temporary file.
        
        Args:
            document: Document dictionary containing ID
            session_id: Workfront session ID
            
        Returns:
            Path to the temporary file
            
        Raises:
            WorkfrontAPIError: If download fails
        """
        document_id = document['ID']
        content = self.workfront_api.download_document(document_id, session_id)
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(content)
        temp_file.flush()
        temp_file.close()
        
        logger.info(f"Document {document_id} saved to {temp_file.name}")
        return temp_file.name
    
    def _cleanup_temp_file(self, file_path: str) -> None:
        """
        Remove temporary file from filesystem.
        
        Args:
            file_path: Path to the file to delete
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to clean up temporary file {file_path}: {e}")
    
    def process_document(self, document: Dict, session_id: str) -> Tuple[bool, str]:
        """
        Process a single document: download, upload to Cloudinary, and update Workfront.
        
        Args:
            document: Document dictionary from Workfront
            session_id: Workfront session ID for downloads
            
        Returns:
            Tuple of (success: bool, status_message: str)
        """
        document_id = document['ID']
        document_name = document.get('name', document_id)
        temp_file_path = None
        
        try:
            # Step 1: Download document
            logger.info(f"Processing document {document_id} ({document_name})")
            temp_file_path = self._download_to_temp_file(document, session_id)
            
            # Step 2: Upload to Cloudinary
            logger.debug(f"Uploading document {document_id} to Cloudinary")
            upload_response = self.cloudinary_service.upload_file(
                file_path=temp_file_path,
                public_id=document_id,
                display_name=document_name
            )
            
            secure_url = upload_response['secure_url']
            logger.info(f"Document {document_id} uploaded to Cloudinary: {secure_url}")
            
            # Step 3: Update Workfront document with Cloudinary URL
            self.workfront_api.update_document(document_id, secure_url)
            
            return True, Config.TASK_COMPLETE
            
        except (WorkfrontAPIError, CloudinaryServiceError) as e:
            logger.error(f"Failed to process document {document_id}: {e}")
            return False, Config.TASK_ERROR
            
        finally:
            # Always cleanup temporary file
            if temp_file_path:
                self._cleanup_temp_file(temp_file_path)
    
    def process_task_documents(self, task: Dict, session_id: str) -> str:
        """
        Process all documents in a task.
        
        Args:
            task: Task dictionary from Workfront
            session_id: Workfront session ID
            
        Returns:
            Final task status code (TASK_COMPLETE or TASK_ERROR)
        """
        task_id = task['ID']
        documents = task.get('documents', [])
        
        if not documents:
            logger.warning(f"Task {task_id} has no documents to process")
            return Config.TASK_ERROR
        
        logger.info(f"Processing {len(documents)} documents for task {task_id}")
        
        # Track success/failure for all documents
        results = []
        for document in documents:
            success, status = self.process_document(document, session_id)
            results.append(success)
        
        # Determine overall task status
        # Task is successful only if ALL documents were processed successfully
        if all(results):
            final_status = Config.TASK_COMPLETE
            logger.info(f"✅ All documents processed successfully for task {task_id}")
        else:
            final_status = Config.TASK_ERROR
            success_count = sum(results)
            logger.warning(
                f"⚠️  Task {task_id} partially failed: "
                f"{success_count}/{len(results)} documents processed successfully"
            )
        
        return final_status

