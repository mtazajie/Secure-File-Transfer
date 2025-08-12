# SFTP Module for Secure File Transfer
import paramiko
import os
from typing import Optional, Dict, Any
import tempfile
import logging

class SFTPManager:
    """
    SFTP Manager for secure file transfers over SSH
    Designed for use in developing countries where cloud storage is expensive
    """
    
    def __init__(self, host: str, port: int = 22, username: str = None, 
                 private_key_path: str = None, password: str = None):
        self.host = host
        self.port = port
        self.username = username
        self.private_key_path = private_key_path
        self.password = password
        self.client = None
        self.sftp = None
        
    def connect(self) -> bool:
        """Establish SFTP connection"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if self.private_key_path and os.path.exists(self.private_key_path):
                # Use private key authentication
                private_key = paramiko.RSAKey.from_private_key_file(self.private_key_path)
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    pkey=private_key
                )
            elif self.password:
                # Use password authentication
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password
                )
            else:
                logging.error("No authentication method provided")
                return False
                
            self.sftp = self.client.open_sftp()
            return True
            
        except Exception as e:
            logging.error(f"SFTP connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close SFTP connection"""
        if self.sftp:
            self.sftp.close()
        if self.client:
            self.client.close()
    
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload file to SFTP server"""
        try:
            if not self.sftp:
                if not self.connect():
                    return False
            
            # Create remote directory if it doesn't exist
            remote_dir = os.path.dirname(remote_path)
            self._create_remote_directory(remote_dir)
            
            # Upload file
            self.sftp.put(local_path, remote_path)
            logging.info(f"File uploaded successfully: {local_path} -> {remote_path}")
            return True
            
        except Exception as e:
            logging.error(f"File upload failed: {e}")
            return False
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Download file from SFTP server"""
        try:
            if not self.sftp:
                if not self.connect():
                    return False
            
            # Create local directory if it doesn't exist
            local_dir = os.path.dirname(local_path)
            os.makedirs(local_dir, exist_ok=True)
            
            # Download file
            self.sftp.get(remote_path, local_path)
            logging.info(f"File downloaded successfully: {remote_path} -> {local_path}")
            return True
            
        except Exception as e:
            logging.error(f"File download failed: {e}")
            return False
    
    def list_files(self, remote_path: str = '.') -> Optional[list]:
        """List files in remote directory"""
        try:
            if not self.sftp:
                if not self.connect():
                    return None
            
            files = self.sftp.listdir(remote_path)
            return files
            
        except Exception as e:
            logging.error(f"Failed to list files: {e}")
            return None
    
    def delete_file(self, remote_path: str) -> bool:
        """Delete file from SFTP server"""
        try:
            if not self.sftp:
                if not self.connect():
                    return False
            
            self.sftp.remove(remote_path)
            logging.info(f"File deleted successfully: {remote_path}")
            return True
            
        except Exception as e:
            logging.error(f"File deletion failed: {e}")
            return False
    
    def file_exists(self, remote_path: str) -> bool:
        """Check if file exists on SFTP server"""
        try:
            if not self.sftp:
                if not self.connect():
                    return False
            
            self.sftp.stat(remote_path)
            return True
            
        except FileNotFoundError:
            return False
        except Exception as e:
            logging.error(f"Error checking file existence: {e}")
            return False
    
    def get_file_info(self, remote_path: str) -> Optional[Dict[str, Any]]:
        """Get file information"""
        try:
            if not self.sftp:
                if not self.connect():
                    return None
            
            stat = self.sftp.stat(remote_path)
            return {
                'size': stat.st_size,
                'modified_time': stat.st_mtime,
                'permissions': oct(stat.st_mode)[-3:]
            }
            
        except Exception as e:
            logging.error(f"Failed to get file info: {e}")
            return None
    
    def _create_remote_directory(self, remote_dir: str):
        """Create remote directory recursively"""
        if not remote_dir or remote_dir == '/':
            return
        
        try:
            self.sftp.stat(remote_dir)
        except FileNotFoundError:
            # Directory doesn't exist, create it
            parent_dir = os.path.dirname(remote_dir)
            if parent_dir != remote_dir:
                self._create_remote_directory(parent_dir)
            
            try:
                self.sftp.mkdir(remote_dir)
            except Exception as e:
                logging.warning(f"Could not create directory {remote_dir}: {e}")

# Utility functions for SFTP integration

def setup_sftp_from_env() -> Optional[SFTPManager]:
    """Setup SFTP manager from environment variables"""
    host = os.environ.get('SFTP_HOST')
    if not host:
        return None
    
    port = int(os.environ.get('SFTP_PORT', 22))
    username = os.environ.get('SFTP_USERNAME')
    private_key_path = os.environ.get('SFTP_PRIVATE_KEY_PATH')
    password = os.environ.get('SFTP_PASSWORD')
    
    return SFTPManager(
        host=host,
        port=port,
        username=username,
        private_key_path=private_key_path,
        password=password
    )

def transfer_encrypted_file_via_sftp(local_encrypted_path: str, 
                                   remote_path: str,
                                   sftp_manager: SFTPManager) -> bool:
    """Transfer encrypted file via SFTP"""
    try:
        return sftp_manager.upload_file(local_encrypted_path, remote_path)
    except Exception as e:
        logging.error(f"SFTP transfer failed: {e}")
        return False

def retrieve_encrypted_file_via_sftp(remote_path: str,
                                   local_path: str,
                                   sftp_manager: SFTPManager) -> bool:
    """Retrieve encrypted file via SFTP"""
    try:
        return sftp_manager.download_file(remote_path, local_path)
    except Exception as e:
        logging.error(f"SFTP retrieval failed: {e}")
        return False
