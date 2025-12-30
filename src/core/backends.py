import os
import shutil
import gzip
from abc import ABC, abstractmethod
from typing import BinaryIO, Union
import logging

class StorageBackend(ABC):
    """Abstract base class for storage backends (Local, S3, GCS, Azure)."""
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        pass

    @abstractmethod
    def put(self, key: str, data: bytes):
        pass
    
    @abstractmethod
    def put_file(self, key: str, file_path: str):
        """Put file content to storage."""
        pass
    
    @abstractmethod
    def get(self, key: str) -> bytes:
        pass
        
    @abstractmethod
    def get_file(self, key: str, dest_path: str):
        """Get object content to file."""
        pass

class LocalBackend(StorageBackend):
    """Local file system backend."""
    
    def __init__(self, objects_dir: str):
        self.objects_dir = objects_dir
        
    def _get_path(self, key: str) -> str:
        return os.path.join(self.objects_dir, key)

    def exists(self, key: str) -> bool:
        return os.path.exists(self._get_path(key))

    def put(self, key: str, data: bytes):
        path = self._get_path(key)
        with open(path, 'wb') as f:
            f.write(data)
            
    def put_file(self, key: str, file_path: str):
        shutil.copy2(file_path, self._get_path(key))

    def get(self, key: str) -> bytes:
        if not self.exists(key):
            raise FileNotFoundError(f"Key {key} not found")
        with open(self._get_path(key), 'rb') as f:
            return f.read()
            
    def get_file(self, key: str, dest_path: str):
        if not self.exists(key):
            raise FileNotFoundError(f"Key {key} not found")
        shutil.copy2(self._get_path(key), dest_path)

class S3Backend(StorageBackend):
    def __init__(self, bucket_name: str, prefix: str = ""):
        try:
            import boto3
            self.s3 = boto3.client('s3')
            self.bucket = bucket_name
            self.prefix = prefix
        except ImportError:
            raise ImportError("boto3 is required for S3 support")

    def _key(self, key: str) -> str:
        return f"{self.prefix}/{key}" if self.prefix else key

    def exists(self, key: str) -> bool:
        from botocore.exceptions import ClientError
        try:
            self.s3.head_object(Bucket=self.bucket, Key=self._key(key))
            return True
        except ClientError:
            return False

    def put(self, key: str, data: bytes):
        self.s3.put_object(Bucket=self.bucket, Key=self._key(key), Body=data)

    def put_file(self, key: str, file_path: str):
        self.s3.upload_file(file_path, self.bucket, self._key(key))

    def get(self, key: str) -> bytes:
        response = self.s3.get_object(Bucket=self.bucket, Key=self._key(key))
        return response['Body'].read()

    def get_file(self, key: str, dest_path: str):
        self.s3.download_file(self.bucket, self._key(key), dest_path)


class GCSBackend(StorageBackend):
    def __init__(self, bucket_name: str, prefix: str = ""):
        try:
            from google.cloud import storage
            self.client = storage.Client()
            self.bucket = self.client.bucket(bucket_name)
            self.prefix = prefix
        except ImportError:
            raise ImportError("google-cloud-storage is required for GCS support")

    def _blob_name(self, key: str) -> str:
        return f"{self.prefix}/{key}" if self.prefix else key

    def exists(self, key: str) -> bool:
        blob = self.bucket.blob(self._blob_name(key))
        return blob.exists()

    def put(self, key: str, data: bytes):
        blob = self.bucket.blob(self._blob_name(key))
        blob.upload_from_string(data)

    def put_file(self, key: str, file_path: str):
        blob = self.bucket.blob(self._blob_name(key))
        blob.upload_from_filename(file_path)

    def get(self, key: str) -> bytes:
        blob = self.bucket.blob(self._blob_name(key))
        return blob.download_as_bytes()

    def get_file(self, key: str, dest_path: str):
        blob = self.bucket.blob(self._blob_name(key))
        blob.download_to_filename(dest_path)


class AzureBackend(StorageBackend):
    def __init__(self, container_name: str, connection_string: str = None, prefix: str = ""):
        try:
            from azure.storage.blob import BlobServiceClient
            conn_str = connection_string or os.getenv("AZURE_STORAGE_CONNECTION_STRING")
            if not conn_str:
                raise ValueError("Azure connection string required")
            self.client = BlobServiceClient.from_connection_string(conn_str)
            self.container = self.client.get_container_client(container_name)
            self.prefix = prefix
        except ImportError:
            raise ImportError("azure-storage-blob is required for Azure support")

    def _blob_name(self, key: str) -> str:
        return f"{self.prefix}/{key}" if self.prefix else key

    def exists(self, key: str) -> bool:
        blob = self.container.get_blob_client(self._blob_name(key))
        return blob.exists()

    def put(self, key: str, data: bytes):
        blob = self.container.get_blob_client(self._blob_name(key))
        blob.upload_blob(data, overwrite=True)

    def put_file(self, key: str, file_path: str):
        blob = self.container.get_blob_client(self._blob_name(key))
        with open(file_path, "rb") as data:
            blob.upload_blob(data, overwrite=True)

    def get(self, key: str) -> bytes:
        blob = self.container.get_blob_client(self._blob_name(key))
        return blob.download_blob().readall()

    def get_file(self, key: str, dest_path: str):
        blob = self.container.get_blob_client(self._blob_name(key))
        with open(dest_path, "wb") as f:
            f.write(blob.download_blob().readall())
