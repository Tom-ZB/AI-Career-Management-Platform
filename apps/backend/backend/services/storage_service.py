"""
Storage Service - Abstraction layer for file storage.
Supports local file system and Azure Blob Storage.
"""
import os
import shutil
from abc import ABC, abstractmethod
from typing import BinaryIO, Optional
from pathlib import Path
from datetime import datetime

from backend.config import settings


class StorageService(ABC):
    """Abstract base class for storage services."""

    @abstractmethod
    async def upload_file(
        self,
        file_data: bytes,
        file_name: str,
        content_type: str,
        folder: Optional[str] = None,
    ) -> dict:
        """
        Upload a file to storage.

        Args:
            file_data: File content as bytes
            file_name: Original file name
            content_type: MIME type
            folder: Optional subfolder path

        Returns:
            dict with file_id, file_path, storage_path, file_name, file_type, file_size
        """
        pass

    @abstractmethod
    async def download_file(self, storage_path: str) -> bytes:
        """
        Download a file from storage.

        Args:
            storage_path: The storage path of the file

        Returns:
            File content as bytes
        """
        pass

    @abstractmethod
    async def delete_file(self, storage_path: str) -> bool:
        """
        Delete a file from storage.

        Args:
            storage_path: The storage path of the file

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    async def get_file_url(self, storage_path: str, expiry_seconds: int = 3600) -> str:
        """
        Get a URL for accessing the file.

        Args:
            storage_path: The storage path of the file
            expiry_seconds: URL expiry time in seconds

        Returns:
            URL string
        """
        pass


class LocalStorageService(StorageService):
    """
    Local file system storage implementation.
    Used for development and testing.
    """

    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path or settings.LOCAL_STORAGE_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def upload_file(
        self,
        file_data: bytes,
        file_name: str,
        content_type: str,
        folder: Optional[str] = None,
    ) -> dict:
        """Upload file to local storage."""
        # Create timestamped folder structure
        now = datetime.utcnow()
        date_path = now.strftime("%Y/%m/%d")
        target_dir = self.base_path / (folder or "") / date_path
        target_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique file name
        timestamp = now.strftime("%H%M%S%f")
        safe_name = f"{timestamp}_{file_name}"
        file_path = target_dir / safe_name

        # Write file
        with open(file_path, "wb") as f:
            f.write(file_data)

        relative_path = str(file_path.relative_to(self.base_path))

        return {
            "file_id": safe_name,
            "file_path": str(file_path),
            "storage_path": relative_path,
            "file_name": file_name,
            "file_type": content_type,
            "file_size": len(file_data),
        }

    async def download_file(self, storage_path: str) -> bytes:
        """Download file from local storage."""
        file_path = self.base_path / storage_path
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {storage_path}")

        with open(file_path, "rb") as f:
            return f.read()

    async def delete_file(self, storage_path: str) -> bool:
        """Delete file from local storage."""
        file_path = self.base_path / storage_path
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    async def get_file_url(self, storage_path: str, expiry_seconds: int = 3600) -> str:
        """Get local file URL (returns the relative path for local)."""
        return f"/api/v1/files/{storage_path}"


class AzureBlobStorageService(StorageService):
    """
    Azure Blob Storage implementation.
    Used for production deployments.
    """

    def __init__(self):
        if not settings.AZURE_STORAGE_CONNECTION_STRING:
            raise ValueError("Azure Storage connection string not configured")

        from azure.storage.blob import BlobServiceClient
        self.blob_service_client = BlobServiceClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING
        )
        self.container_name = settings.AZURE_STORAGE_CONTAINER or "career-documents"

        # Ensure container exists
        container_client = self.blob_service_client.get_container_client(self.container_name)
        if not container_client.exists():
            container_client.create_container()

    async def upload_file(
        self,
        file_data: bytes,
        file_name: str,
        content_type: str,
        folder: Optional[str] = None,
    ) -> dict:
        """Upload file to Azure Blob Storage."""
        from azure.storage.blob import ContentSettings

        # Generate blob path
        now = datetime.utcnow()
        date_path = now.strftime("%Y/%m/%d")
        timestamp = now.strftime("%H%M%S%f")
        safe_name = f"{timestamp}_{file_name}"
        blob_path = f"{folder}/{date_path}/{safe_name}" if folder else f"{date_path}/{safe_name}"

        # Upload blob
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, blob=blob_path
        )
        blob_client.upload_blob(
            file_data,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
        )

        return {
            "file_id": safe_name,
            "file_path": blob_client.url,
            "storage_path": blob_path,
            "file_name": file_name,
            "file_type": content_type,
            "file_size": len(file_data),
        }

    async def download_file(self, storage_path: str) -> bytes:
        """Download file from Azure Blob Storage."""
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, blob=storage_path
        )
        return blob_client.download_blob().readall()

    async def delete_file(self, storage_path: str) -> bool:
        """Delete file from Azure Blob Storage."""
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, blob=storage_path
        )
        blob_client.delete_blob()
        return True

    async def get_file_url(self, storage_path: str, expiry_seconds: int = 3600) -> str:
        """Get a SAS URL for the blob."""
        from azure.storage.blob import generate_blob_sas, BlobSasPermissions
        from datetime import datetime, timedelta

        sas_token = generate_blob_sas(
            account_name=settings.AZURE_STORAGE_ACCOUNT_NAME,
            container_name=self.container_name,
            blob_name=storage_path,
            account_key=settings.AZURE_STORAGE_ACCOUNT_KEY,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(seconds=expiry_seconds),
        )

        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, blob=storage_path
        )
        return f"{blob_client.url}?{sas_token}"


def get_storage_service() -> StorageService:
    """
    Factory function to get the configured storage service.

    Returns:
        StorageService instance based on STORAGE_TYPE setting
    """
    storage_type = settings.STORAGE_TYPE.lower()

    if storage_type == "azure":
        return AzureBlobStorageService()
    else:
        return LocalStorageService()


# Singleton instance
_storage_service: Optional[StorageService] = None


def get_storage() -> StorageService:
    """Get or create the storage service singleton."""
    global _storage_service
    if _storage_service is None:
        _storage_service = get_storage_service()
    return _storage_service