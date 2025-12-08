"""
Unit tests for FileOperations service.
"""

import unittest
import os
import shutil
import tempfile
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.file_operations import FileOperations


class TestFileOperations(unittest.TestCase):
    """Tests for FileOperations service."""

    def setUp(self):
        """Create temp directory with test files."""
        self.test_dir = tempfile.mkdtemp()
        self.dest_dir = tempfile.mkdtemp()
        
        # Create test files
        self.test_file = os.path.join(self.test_dir, "test.txt")
        with open(self.test_file, 'w') as f:
            f.write("test content")
        
        self.test_file2 = os.path.join(self.test_dir, "test2.txt")
        with open(self.test_file2, 'w') as f:
            f.write("test content 2")

    def tearDown(self):
        """Clean up temp directories."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        shutil.rmtree(self.dest_dir, ignore_errors=True)

    def test_copy_file(self):
        """Test copying a single file."""
        dest = FileOperations.copy_file(self.test_file, self.dest_dir)
        
        self.assertTrue(os.path.exists(dest))
        self.assertTrue(os.path.exists(self.test_file))  # Original still exists
        self.assertEqual(os.path.basename(dest), "test.txt")

    def test_copy_file_nonexistent(self):
        """Test copying a nonexistent file raises OSError."""
        with self.assertRaises(OSError):
            FileOperations.copy_file("/nonexistent/file.txt", self.dest_dir)

    def test_move_file(self):
        """Test moving a single file."""
        original_path = self.test_file
        dest = FileOperations.move_file(original_path, self.dest_dir)
        
        self.assertTrue(os.path.exists(dest))
        self.assertFalse(os.path.exists(original_path))  # Original is gone

    def test_delete_file(self):
        """Test deleting a file."""
        result = FileOperations.delete_file(self.test_file)
        
        self.assertTrue(result)
        self.assertFalse(os.path.exists(self.test_file))

    def test_rename_file(self):
        """Test renaming a file."""
        new_path = FileOperations.rename_file(self.test_file, "renamed.txt")
        
        self.assertTrue(os.path.exists(new_path))
        self.assertFalse(os.path.exists(self.test_file))
        self.assertEqual(os.path.basename(new_path), "renamed.txt")

    def test_bulk_delete(self):
        """Test deleting multiple files."""
        paths = [self.test_file, self.test_file2]
        succeeded, failed = FileOperations.bulk_delete(paths)
        
        self.assertEqual(len(succeeded), 2)
        self.assertEqual(len(failed), 0)
        self.assertFalse(os.path.exists(self.test_file))
        self.assertFalse(os.path.exists(self.test_file2))

    def test_bulk_delete_partial_failure(self):
        """Test bulk delete with one nonexistent file."""
        paths = [self.test_file, "/nonexistent/file.txt"]
        succeeded, failed = FileOperations.bulk_delete(paths)
        
        self.assertEqual(len(succeeded), 1)
        self.assertEqual(len(failed), 1)

    def test_bulk_copy(self):
        """Test copying multiple files."""
        paths = [self.test_file, self.test_file2]
        succeeded, failed = FileOperations.bulk_copy(paths, self.dest_dir)
        
        self.assertEqual(len(succeeded), 2)
        self.assertEqual(len(failed), 0)
        # Originals still exist
        self.assertTrue(os.path.exists(self.test_file))
        self.assertTrue(os.path.exists(self.test_file2))

    def test_bulk_move(self):
        """Test moving multiple files."""
        paths = [self.test_file, self.test_file2]
        succeeded, failed = FileOperations.bulk_move(paths, self.dest_dir)
        
        self.assertEqual(len(succeeded), 2)
        self.assertEqual(len(failed), 0)
        # Originals are gone
        self.assertFalse(os.path.exists(self.test_file))
        self.assertFalse(os.path.exists(self.test_file2))


if __name__ == '__main__':
    unittest.main()
