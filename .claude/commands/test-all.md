Run all tests and quality checks for the Work Dashboard:

1. Syntax check all Python files:
   ```bash
   python -m py_compile work_dashboard.py ui/folder_card.py ui/styles.py services/metadata_service.py
   ```

2. Run unit tests:
   ```bash
   python -m unittest tests/verify_features.py -v
   ```

3. Check imports work correctly:
   ```bash
   python -c "from ui.folder_card import FolderCard; from services.metadata_service import MetadataService; from config.manager import ConfigManager; print('All imports OK')"
   ```

4. Report test results with pass/fail summary

If any tests fail, analyze the failure and suggest fixes.
