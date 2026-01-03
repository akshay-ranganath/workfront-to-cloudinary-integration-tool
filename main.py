"""
Main Workflow Script

Orchestrates the complete Workfront to Cloudinary document upload workflow.
This is the entry point for running the automation.
"""

import logging
import sys
from typing import List, Dict

from config import Config
from authenticate import get_workfront_session_id
from workfront_api import WorkfrontAPI, WorkfrontAPIError
from cloudinary_service import CloudinaryService, CloudinaryServiceError
from document_processor import DocumentProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_configuration() -> bool:
    """
    Validate all required configuration before starting.
    
    Returns:
        bool: True if configuration is valid, False otherwise
    """
    try:
        Config.validate_all()
        logger.info("✅ Configuration validated successfully")
        return True
    except ValueError as e:
        logger.error(f"❌ Configuration validation failed: {e}")
        return False


def find_tasks_for_upload(workfront_api: WorkfrontAPI) -> List[Dict]:
    """
    Search for tasks that need Cloudinary upload.
    
    Args:
        workfront_api: Workfront API client
        
    Returns:
        List of tasks with documents to process
    """
    logger.info(f"Searching for tasks with status '{Config.TASK_STATUS_UPLOAD}'...")
    
    try:
        tasks = workfront_api.search_tasks(
            status=Config.TASK_STATUS_UPLOAD,
            limit=Config.MAX_TASKS_PER_RUN,
            include_documents=True
        )
        
        if not tasks:
            logger.info("No tasks found for processing")
            return []
        
        logger.info(f"Found {len(tasks)} tasks for processing")
        
        # Filter tasks that have documents
        tasks_with_docs = [task for task in tasks if task.get('hasDocuments')]
        tasks_without_docs = len(tasks) - len(tasks_with_docs)
        
        if tasks_without_docs > 0:
            logger.warning(f"⚠️  {tasks_without_docs} tasks have no documents and will be skipped")
        
        return tasks_with_docs
        
    except WorkfrontAPIError as e:
        logger.error(f"Failed to search for tasks: {e}")
        return []


def process_tasks(
    tasks: List[Dict],
    workfront_api: WorkfrontAPI,
    cloudinary_service: CloudinaryService,
    session_id: str
) -> Dict[str, int]:
    """
    Process all tasks and their documents.
    
    Args:
        tasks: List of tasks to process
        workfront_api: Workfront API client
        cloudinary_service: Cloudinary service
        session_id: Workfront session ID for downloads
        
    Returns:
        Dict with processing statistics
    """
    processor = DocumentProcessor(workfront_api, cloudinary_service)
    
    stats = {
        'total_tasks': len(tasks),
        'successful_tasks': 0,
        'failed_tasks': 0,
        'total_documents': 0
    }
    
    for i, task in enumerate(tasks, 1):
        task_id = task['ID']
        document_count = len(task.get('documents', []))
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing Task {i}/{len(tasks)}: {task_id}")
        logger.info(f"Documents: {document_count}")
        logger.info(f"{'='*60}")
        
        stats['total_documents'] += document_count
        
        try:
            # Process all documents in the task
            final_status = processor.process_task_documents(task, session_id)
            
            # Update task status in Workfront
            workfront_api.update_task_status(task_id, final_status)
            
            if final_status == Config.TASK_COMPLETE:
                stats['successful_tasks'] += 1
            else:
                stats['failed_tasks'] += 1
                
        except Exception as e:
            logger.error(f"Unexpected error processing task {task_id}: {e}")
            stats['failed_tasks'] += 1
            
            # Try to mark task as failed
            try:
                workfront_api.update_task_status(task_id, Config.TASK_ERROR)
            except Exception as update_error:
                logger.error(f"Failed to update task status: {update_error}")
    
    return stats


def print_summary(stats: Dict[str, int]) -> None:
    """
    Print workflow execution summary.
    
    Args:
        stats: Processing statistics dictionary
    """
    logger.info(f"\n{'='*60}")
    logger.info("WORKFLOW SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Total Tasks Processed: {stats['total_tasks']}")
    logger.info(f"Successful Tasks: {stats['successful_tasks']}")
    logger.info(f"Failed Tasks: {stats['failed_tasks']}")
    logger.info(f"Total Documents: {stats['total_documents']}")
    logger.info(f"{'='*60}\n")


def main() -> int:
    """
    Main entry point for the workflow.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    logger.info("🚀 Starting Workfront to Cloudinary document upload workflow\n")
    
    # Step 1: Validate configuration
    if not validate_configuration():
        logger.error("Exiting due to configuration errors")
        return 1
    
    try:
        # Step 2: Initialize services
        logger.info("Initializing services...")
        workfront_api = WorkfrontAPI()
        cloudinary_service = CloudinaryService()
        logger.info("✅ Services initialized\n")
        
        # Step 3: Authenticate with Workfront
        logger.info("Authenticating with Workfront...")
        session_id = get_workfront_session_id()
        logger.info("✅ Authentication successful\n")
        
        # Step 4: Find tasks to process
        tasks = find_tasks_for_upload(workfront_api)
        
        if not tasks:
            logger.info("No tasks to process. Workflow complete.")
            return 0
        
        # Step 5: Process tasks
        logger.info(f"\nProcessing {len(tasks)} tasks...")
        stats = process_tasks(tasks, workfront_api, cloudinary_service, session_id)
        
        # Step 6: Print summary
        print_summary(stats)
        
        # Determine exit code based on results
        if stats['failed_tasks'] > 0:
            logger.warning("⚠️  Workflow completed with some failures")
            return 1
        else:
            logger.info("✅ Workflow completed successfully")
            return 0
            
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Workflow interrupted by user")
        return 130
        
    except Exception as e:
        logger.error(f"❌ Unexpected error in workflow: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

