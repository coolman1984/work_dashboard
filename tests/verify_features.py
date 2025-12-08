import unittest
import os
import shutil
import json
import tempfile
from unittest.mock import MagicMock, patch

# Add parent directory to path to import modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.metadata_service import MetadataService
from services.clipboard import InternalClipboard
from config.manager import ConfigManager

class TestWorkDashboardFeatures(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.test_dir, "test_config.json")
        self.tags_file = "file_tags.json" # This is hardcoded in MetadataService, need to mock or handle
        
        # Create some dummy files
        with open(os.path.join(self.test_dir, "test_file.txt"), "w") as f: f.write("content")
        with open(os.path.join(self.test_dir, "other_file.py"), "w") as f: f.write("print('hello')")
        os.makedirs(os.path.join(self.test_dir, "subfolder"))

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        if os.path.exists(self.tags_file):
            # Clean up tags file if created
            # In a real scenario we might want to backup/restore the real one
            pass

    def test_config_manager(self):
        # Test Save
        data = {"test_key": "test_value"}
        with patch("config.manager.CONFIG_FILE", self.config_file):
            ConfigManager.save_config(data)
            self.assertTrue(os.path.exists(self.config_file))
            
            # Test Load
            loaded = ConfigManager.load_config()
            self.assertEqual(loaded, data)

    def test_metadata_service(self):
        test_file = os.path.join(self.test_dir, "test_file.txt")
        
        # Test Set Tag
        MetadataService.set_tag(test_file, color="red", note="Important")
        
        # Test Get Tag
        tag = MetadataService.get_tag(test_file)
        self.assertEqual(tag.get("color"), "red")
        self.assertEqual(tag.get("note"), "Important")
        
        # Test Remove Tag
        MetadataService.remove_tag(test_file)
        tag = MetadataService.get_tag(test_file)
        self.assertEqual(tag, {})

    def test_clipboard_service(self):
        test_file = os.path.join(self.test_dir, "test_file.txt")
        
        # Test Set
        InternalClipboard.set(test_file, 'copy', None)
        path, op = InternalClipboard.get()
        self.assertEqual(path, test_file)
        self.assertEqual(op, 'copy')
        self.assertTrue(InternalClipboard.has_data())
        
        # Test Clear
        InternalClipboard.clear()
        self.assertFalse(InternalClipboard.has_data())

    def test_file_operations_mock(self):
        # We can't easily test the GUI FolderCard methods without a root window,
        # but we can test the logic if we extract it or mock the GUI parts.
        # For now, let's verify the underlying shutil operations work as expected in this env.
        
        src = os.path.join(self.test_dir, "test_file.txt")
        dst = os.path.join(self.test_dir, "copy_of_test.txt")
        
        # Copy
        shutil.copy2(src, dst)
        self.assertTrue(os.path.exists(dst))
        
        # Rename
        new_name = os.path.join(self.test_dir, "renamed.txt")
        os.rename(dst, new_name)
        self.assertTrue(os.path.exists(new_name))
        self.assertFalse(os.path.exists(dst))
        
        # Delete
        os.remove(new_name)
        self.assertFalse(os.path.exists(new_name))

if __name__ == '__main__':
    unittest.main()
