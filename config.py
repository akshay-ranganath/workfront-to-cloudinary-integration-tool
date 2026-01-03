"""
Configuration Management Module

Centralizes all configuration loading and validation from environment variables.
Provides a clean interface for accessing application settings.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for managing application settings."""
    
    # Workfront API Configuration
    WORKFRONT_BASE_URL: str = os.getenv('WORKFRONT_BASE_URL', '')
    WORKFRONT_API_KEY: str = os.getenv('WORKFRONT_API_KEY', '')
    WORKFRONT_API_VERSION: str = 'v19.0'
    
    # Workfront OAuth Configuration
    WORKFRONT_BASE: str = os.getenv('WORKFRONT_BASE', '')
    WORKFRONT_CLIENT_ID: str = os.getenv('WORKFRONT_CLIENT_ID', '')
    WORKFRONT_CLIENT_SECRET: str = os.getenv('WORKFRONT_CLIENT_SECRET', '')
    WORKFRONT_CUSTOMER_ID: str = os.getenv('WORKFRONT_CUSTOMER_ID', '')
    WORKFRONT_USER_ID: str = os.getenv('WORKFRONT_USER_ID', '')
    WORKFRONT_PRIVATE_KEY: str = os.getenv('WORKFRONT_PRIVATE_KEY', '')
    
    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME: str = os.getenv('CLOUDINARY_CLOUD_NAME', '')
    CLOUDINARY_API_KEY: str = os.getenv('CLOUDINARY_API_KEY', '')
    CLOUDINARY_API_SECRET: str = os.getenv('CLOUDINARY_API_SECRET', '')
    CLOUDINARY_ASSET_FOLDER: str = os.getenv('CLOUDINARY_ASSET_FOLDER', 'workfront')
    
    # Task Status Codes
    TASK_STATUS_UPLOAD: str = os.getenv('TASK_STATUS_UPLOAD', 'UPL')
    TASK_COMPLETE: str = os.getenv('TASK_COMPLETE', 'CPL')
    TASK_ERROR: str = os.getenv('TASK_ERROR', 'ERR')
    
    # Processing Configuration
    MAX_TASKS_PER_RUN: int = int(os.getenv('MAX_TASKS_PER_RUN', '100'))
    
    @classmethod
    def get_workfront_api_base_url(cls) -> str:
        """Get the full Workfront API base URL."""
        return f"{cls.WORKFRONT_BASE_URL}/attask/api/{cls.WORKFRONT_API_VERSION}"
    
    @classmethod
    def validate_workfront_config(cls) -> None:
        """Validate that all required Workfront configuration is present."""
        required = {
            'WORKFRONT_BASE_URL': cls.WORKFRONT_BASE_URL,
            'WORKFRONT_API_KEY': cls.WORKFRONT_API_KEY,
            'WORKFRONT_BASE': cls.WORKFRONT_BASE,
            'WORKFRONT_CLIENT_ID': cls.WORKFRONT_CLIENT_ID,
            'WORKFRONT_CLIENT_SECRET': cls.WORKFRONT_CLIENT_SECRET,
            'WORKFRONT_CUSTOMER_ID': cls.WORKFRONT_CUSTOMER_ID,
            'WORKFRONT_USER_ID': cls.WORKFRONT_USER_ID,
            'WORKFRONT_PRIVATE_KEY': cls.WORKFRONT_PRIVATE_KEY,
        }
        missing = [key for key, value in required.items() if not value]
        if missing:
            raise ValueError(f"Missing required Workfront configuration: {', '.join(missing)}")
    
    @classmethod
    def validate_cloudinary_config(cls) -> None:
        """Validate that all required Cloudinary configuration is present."""
        required = {
            'CLOUDINARY_CLOUD_NAME': cls.CLOUDINARY_CLOUD_NAME,
            'CLOUDINARY_API_KEY': cls.CLOUDINARY_API_KEY,
            'CLOUDINARY_API_SECRET': cls.CLOUDINARY_API_SECRET,
        }
        missing = [key for key, value in required.items() if not value]
        if missing:
            raise ValueError(f"Missing required Cloudinary configuration: {', '.join(missing)}")
    
    @classmethod
    def validate_all(cls) -> None:
        """Validate all required configuration."""
        cls.validate_workfront_config()
        cls.validate_cloudinary_config()

