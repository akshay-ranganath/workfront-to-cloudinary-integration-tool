"""
Cloudinary Service Module

Handles all interactions with Cloudinary including:
- Configuration
- File uploads
- Metadata management
"""

import logging
from typing import Dict, Optional
import cloudinary
import cloudinary.uploader
from config import Config

logger = logging.getLogger(__name__)


class CloudinaryServiceError(Exception):
    """Custom exception for Cloudinary service errors."""
    pass


class CloudinaryService:
    """Service for interacting with Cloudinary."""
    
    def __init__(
        self,
        cloud_name: Optional[str] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None
    ):
        """
        Initialize Cloudinary service.
        
        Args:
            cloud_name: Cloudinary cloud name (uses Config if not provided)
            api_key: Cloudinary API key (uses Config if not provided)
            api_secret: Cloudinary API secret (uses Config if not provided)
        """
        self.cloud_name = cloud_name or Config.CLOUDINARY_CLOUD_NAME
        self.api_key = api_key or Config.CLOUDINARY_API_KEY
        self.api_secret = api_secret or Config.CLOUDINARY_API_SECRET
        self.asset_folder = Config.CLOUDINARY_ASSET_FOLDER
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret
        )
        
        logger.debug(f"Cloudinary configured for cloud: {self.cloud_name}")
    
    def upload_file(
        self,
        file_path: str,
        public_id: str,
        display_name: str,
        resource_type: str = 'auto',
        asset_folder: Optional[str] = None
    ) -> Dict:
        """
        Upload a file to Cloudinary.
        
        Args:
            file_path: Local path to the file to upload
            public_id: Public ID for the asset in Cloudinary
            display_name: Display name for the asset
            resource_type: Type of resource (auto, image, video, raw)
            asset_folder: Folder to organize assets (uses default if not provided)
            
        Returns:
            Dict containing upload response with 'secure_url' and other metadata
            
        Raises:
            CloudinaryServiceError: If upload fails
        """
        folder = asset_folder or self.asset_folder
        
        logger.debug(f"Uploading {file_path} to Cloudinary as {public_id}")
        
        try:
            response = cloudinary.uploader.upload(
                file_path,
                resource_type=resource_type,
                asset_folder=folder,
                display_name=display_name,
                public_id=public_id
            )
            
            secure_url = response.get('secure_url')
            logger.info(f"✅ File uploaded successfully: {secure_url}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Failed to upload file {file_path}: {e}")
            raise CloudinaryServiceError(f"Upload failed: {e}")
    
    def get_asset_url(self, public_id: str, resource_type: str = 'image') -> str:
        """
        Get the URL for an asset in Cloudinary.
        
        Args:
            public_id: Public ID of the asset
            resource_type: Type of resource
            
        Returns:
            Secure URL to the asset
        """
        return cloudinary.CloudinaryImage(public_id).build_url(secure=True)

