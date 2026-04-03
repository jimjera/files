"""
Deployer service for uploading generated apps to DigitalOcean Spaces.

This module provides functionality to upload PWA files to S3-compatible
storage and return public URLs for deployment.
"""

import structlog
from typing import Dict, Optional
from io import BytesIO

import boto3
from botocore.config import Config

from app.config import settings

logger = structlog.get_logger()


class Deployer:
    """
    Deployer for uploading apps to DigitalOcean Spaces.
    
    This class handles uploading generated PWA files to DigitalOcean
    Spaces (S3-compatible storage) and returns public CDN URLs.
    
    Attributes:
        s3_client: Boto3 S3 client configured for DigitalOcean Spaces.
    """
    
    def __init__(self):
        """Initialize Deployer with DigitalOcean Spaces client."""
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.SPACES_ENDPOINT,
            aws_access_key_id=settings.SPACES_KEY,
            aws_secret_access_key=settings.SPACES_SECRET,
            config=Config(signature_version="s3v4"),
            region_name=settings.SPACES_REGION,
        )
        logger.debug("Deployer initialized")
    
    async def upload_to_spaces(
        self,
        user_id: str,
        files: Dict[str, str],
        app_id: Optional[str] = None,
    ) -> str:
        """
        Upload generated PWA files to DigitalOcean Spaces.
        
        Args:
            user_id: User's UUID for organizing files.
            files: Dictionary of filename to file content.
            app_id: Optional app UUID for more specific organization.
            
        Returns:
            str: Public URL to the deployed app's index.html.
            
        Raises:
            Exception: If upload fails.
        """
        import uuid
        
        # Generate app_id if not provided
        if not app_id:
            app_id = str(uuid.uuid4())
        
        # Create S3 prefix for organization
        prefix = f"{user_id}/{app_id}"
        
        try:
            # Upload each file
            for filename, content in files.items():
                key = f"{prefix}/{filename}"
                
                # Determine content type
                content_type = self._get_content_type(filename)
                
                # Upload file
                self.s3_client.put_object(
                    Bucket=settings.SPACES_BUCKET_NAME,
                    Key=key,
                    Body=content.encode("utf-8"),
                    ContentType=content_type,
                    ACL="public-read",
                    CacheControl="public, max-age=31536000, immutable",
                )
                
                logger.debug(
                    "File uploaded",
                    filename=filename,
                    key=key,
                )
            
            # Construct public URL
            public_url = f"https://{settings.SPACES_BUCKET_NAME}.{settings.SPACES_REGION}.cdn.digitaloceanspaces.com/{prefix}/index.html"
            
            logger.info(
                "App deployed successfully",
                user_id=user_id,
                app_id=app_id,
                url=public_url,
            )
            
            return public_url
        
        except Exception as e:
            logger.error(
                "Failed to upload to Spaces",
                user_id=user_id,
                app_id=app_id,
                error=str(e),
            )
            raise
    
    def _get_content_type(self, filename: str) -> str:
        """
        Get MIME content type based on file extension.
        
        Args:
            filename: Name of the file.
            
        Returns:
            str: MIME type string.
        """
        extension_map = {
            ".html": "text/html",
            ".htm": "text/html",
            ".css": "text/css",
            ".js": "application/javascript",
            ".ts": "application/typescript",
            ".tsx": "application/typescript",
            ".json": "application/json",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".svg": "image/svg+xml",
            ".ico": "image/x-icon",
            ".woff": "font/woff",
            ".woff2": "font/woff2",
            ".ttf": "font/ttf",
            ".eot": "application/vnd.ms-fontobject",
            ".txt": "text/plain",
            ".xml": "application/xml",
            ".map": "application/json",
        }
        
        # Get file extension
        ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
        
        return extension_map.get(ext, "application/octet-stream")
    
    async def invalidate_cdn(self, url: str) -> bool:
        """
        Invalidate CDN cache for a specific URL (optional).
        
        This is a placeholder for Cloudflare cache invalidation
        if you're using Cloudflare in front of DigitalOcean Spaces.
        
        Args:
            url: URL to invalidate.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        logger.info("CDN invalidation requested", url=url)
        
        # TODO: Implement Cloudflare API call if needed
        # For now, just log the request
        
        return True
    
    async def delete_app(self, user_id: str, app_id: str) -> bool:
        """
        Delete an app's files from Spaces.
        
        Args:
            user_id: User's UUID.
            app_id: App's UUID.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        prefix = f"{user_id}/{app_id}"
        
        try:
            # List all objects with this prefix
            response = self.s3_client.list_objects_v2(
                Bucket=settings.SPACES_BUCKET_NAME,
                Prefix=prefix,
            )
            
            if "Contents" not in response:
                logger.warning("No files found to delete", prefix=prefix)
                return True
            
            # Delete each object
            objects_to_delete = [
                {"Key": obj["Key"]} for obj in response["Contents"]
            ]
            
            self.s3_client.delete_objects(
                Bucket=settings.SPACES_BUCKET_NAME,
                Delete={"Objects": objects_to_delete},
            )
            
            logger.info(
                "App deleted successfully",
                user_id=user_id,
                app_id=app_id,
            )
            
            return True
        
        except Exception as e:
            logger.error(
                "Failed to delete app",
                user_id=user_id,
                app_id=app_id,
                error=str(e),
            )
            return False
