"""
File Operations Service - Pure file system operations without UI dependencies.

This module provides a testable, UI-independent interface for file operations.
All methods are static and raise exceptions on failure (caller handles UI feedback).
"""

import os
import shutil
from typing import List, Tuple, Optional


class FileOperations:
    """Static methods for file system operations."""

    @staticmethod
    def copy_file(src: str, dest_dir: str) -> str:
        """Copy a file to destination directory.
        
        Args:
            src: Source file path
            dest_dir: Destination directory
            
        Returns:
            Path to the copied file
            
        Raises:
            OSError: If source doesn't exist or copy fails
            shutil.Error: If copy operation fails
        """
        if not os.path.exists(src):
            raise OSError(f"Source file does not exist: {src}")
        
        dest = os.path.join(dest_dir, os.path.basename(src))
        shutil.copy2(src, dest)
        return dest

    @staticmethod
    def move_file(src: str, dest_dir: str) -> str:
        """Move a file to destination directory.
        
        Args:
            src: Source file path
            dest_dir: Destination directory
            
        Returns:
            Path to the moved file
            
        Raises:
            OSError: If source doesn't exist
            shutil.Error: If move operation fails
        """
        if not os.path.exists(src):
            raise OSError(f"Source file does not exist: {src}")
        
        dest = os.path.join(dest_dir, os.path.basename(src))
        shutil.move(src, dest)
        return dest

    @staticmethod
    def delete_file(path: str) -> bool:
        """Delete a file.
        
        Args:
            path: File path to delete
            
        Returns:
            True if deleted successfully
            
        Raises:
            OSError: If deletion fails
        """
        os.remove(path)
        return True

    @staticmethod
    def rename_file(path: str, new_name: str) -> str:
        """Rename a file.
        
        Args:
            path: Current file path
            new_name: New filename (not full path)
            
        Returns:
            New file path
            
        Raises:
            OSError: If rename fails
        """
        directory = os.path.dirname(path)
        new_path = os.path.join(directory, new_name)
        os.rename(path, new_path)
        return new_path

    @staticmethod
    def bulk_copy(paths: List[str], dest_dir: str) -> Tuple[List[str], List[Tuple[str, str]]]:
        """Copy multiple files to destination directory.
        
        Args:
            paths: List of source file paths
            dest_dir: Destination directory
            
        Returns:
            Tuple of (succeeded paths, failed items as (path, error))
        """
        succeeded = []
        failed = []
        
        for path in paths:
            try:
                dest = FileOperations.copy_file(path, dest_dir)
                succeeded.append(dest)
            except (OSError, shutil.Error) as e:
                failed.append((path, str(e)))
        
        return succeeded, failed

    @staticmethod
    def bulk_delete(paths: List[str]) -> Tuple[List[str], List[Tuple[str, str]]]:
        """Delete multiple files.
        
        Args:
            paths: List of file paths to delete
            
        Returns:
            Tuple of (deleted paths, failed items as (path, error))
        """
        succeeded = []
        failed = []
        
        for path in paths:
            try:
                FileOperations.delete_file(path)
                succeeded.append(path)
            except OSError as e:
                failed.append((path, str(e)))
        
        return succeeded, failed

    @staticmethod
    def bulk_move(paths: List[str], dest_dir: str) -> Tuple[List[str], List[Tuple[str, str]]]:
        """Move multiple files to destination directory.
        
        Args:
            paths: List of source file paths
            dest_dir: Destination directory
            
        Returns:
            Tuple of (succeeded paths, failed items as (path, error))
        """
        succeeded = []
        failed = []
        
        for path in paths:
            try:
                dest = FileOperations.move_file(path, dest_dir)
                succeeded.append(dest)
            except (OSError, shutil.Error) as e:
                failed.append((path, str(e)))
        
        return succeeded, failed
