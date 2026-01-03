"""
Workfront API Module

Handles all interactions with the Workfront API including:
- Searching for tasks
- Downloading documents
- Updating task and document status
"""

import logging
from typing import Dict, List, Optional, Any
import requests
from config import Config

logger = logging.getLogger(__name__)


class WorkfrontAPIError(Exception):
    """Custom exception for Workfront API errors."""
    pass


class WorkfrontAPI:
    """Client for interacting with Workfront API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Workfront API client.
        
        Args:
            api_key: Workfront API key (uses Config if not provided)
        """
        self.api_key = api_key or Config.WORKFRONT_API_KEY
        self.base_url = Config.get_workfront_api_base_url()
        self.headers = {
            "Content-Type": "application/json",
            "apiKey": self.api_key
        }
    
    def _make_request(
        self,
        method: str,
        object_name: str,
        action: Optional[str] = None,
        object_id: Optional[str] = None,
        params: Optional[str] = None,
        data: Optional[Dict] = None
    ) -> Any:
        """
        Make a request to the Workfront API.
        
        Args:
            method: HTTP method (GET, PUT, POST, etc.)
            object_name: Workfront object type (e.g., 'TASK', 'document')
            action: Action to perform (e.g., 'search') for GET requests
            object_id: Object ID for PUT/POST requests
            params: Query parameters string
            data: Request body data
            
        Returns:
            Response data (dict for GET, status code for PUT/POST)
            
        Raises:
            WorkfrontAPIError: If the request fails
        """
        # Build URL
        if method.upper() == "GET" and action:
            url = f"{self.base_url}/{object_name}/{action}"
            if params:
                url += f"?{params}"
        elif object_id:
            url = f"{self.base_url}/{object_name}/{object_id}"
        else:
            url = f"{self.base_url}/{object_name}"
        
        logger.debug(f"{method.upper()}: {url}")
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            else:
                raise WorkfrontAPIError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            # Return JSON for GET, status code for others
            if method.upper() == "GET":
                logger.info(f"✅ {method.upper()} Successful")
                return response.json()
            else:
                logger.info(f"✅ {method.upper()} Successful")
                return response.status_code
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ {method.upper()} Failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise WorkfrontAPIError(f"API request failed: {e}")
    
    def search_tasks(
        self,
        status: str,
        limit: int = 100,
        include_documents: bool = True
    ) -> List[Dict]:
        """
        Search for tasks with a specific status.
        
        Args:
            status: Task status code to search for
            limit: Maximum number of tasks to return
            include_documents: Whether to include document information
            
        Returns:
            List of task dictionaries
        """
        fields = "fields=*,documents" if include_documents else "fields=*"
        params = f"{fields}&isComplete=false&$$LIMIT={limit}&status_Sort=desc&status={status}"
        
        response = self._make_request(
            method="GET",
            object_name="TASK",
            action="search",
            params=params
        )
        
        return response.get('data', [])
    
    def download_document(self, document_id: str, session_id: str) -> bytes:
        """
        Download a document from Workfront.
        
        Args:
            document_id: ID of the document to download
            session_id: Authenticated session ID
            
        Returns:
            Document content as bytes
            
        Raises:
            WorkfrontAPIError: If download fails
        """
        url = f"{Config.WORKFRONT_BASE_URL}/document/download"
        params = {"ID": document_id}
        headers = {"sessionID": session_id}
        
        logger.debug(f"Downloading document {document_id}")
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            logger.info(f"✅ Downloaded document {document_id}")
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to download document {document_id}: {e}")
            raise WorkfrontAPIError(f"Document download failed: {e}")
    
    def update_document(self, document_id: str, description: str) -> int:
        """
        Update a document's description field.
        
        Args:
            document_id: ID of the document to update
            description: New description (typically Cloudinary URL)
            
        Returns:
            HTTP status code
        """
        logger.debug(f"Updating document {document_id} with description: {description}")
        
        status_code = self._make_request(
            method="PUT",
            object_name="document",
            object_id=document_id,
            data={"description": description}
        )
        
        if status_code == 200:
            logger.info(f"Document {document_id} updated successfully")
        else:
            logger.error(f"Failed to update document {document_id}")
        
        return status_code
    
    def update_task_status(self, task_id: str, status: str) -> int:
        """
        Update a task's status.
        
        Args:
            task_id: ID of the task to update
            status: New status code
            
        Returns:
            HTTP status code
        """
        logger.debug(f"Updating task {task_id} to status: {status}")
        
        status_code = self._make_request(
            method="PUT",
            object_name="task",
            object_id=task_id,
            data={"status": status}
        )
        
        if status_code == 200:
            logger.info(f"Task {task_id} updated to status '{status}'")
        else:
            logger.error(f"Failed to update task {task_id} to status '{status}'")
        
        return status_code

