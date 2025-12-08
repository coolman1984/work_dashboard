Build the Work Dashboard as a standalone executable:

1. **Check PyInstaller Installation**
   ```bash
   pip show pyinstaller || pip install pyinstaller
   ```

2. **Clean Previous Build**
   ```bash
   # Remove old build artifacts
   rm -rf build/ dist/
   ```

3. **Build Executable**
   ```bash
   pyinstaller work_dashboard.spec
   ```

4. **Verify Build**
   - Check `dist/WorkDashboard.exe` exists
   - Report file size
   - List files in `dist/` directory

5. **Test Executable** (if possible)
   - Run `dist/WorkDashboard.exe`
   - Verify basic functionality

6. **Report Results**
   - Build success/failure
   - Output path
   - Any warnings during build

Note: Build artifacts (build/, dist/) should NOT be committed to git.
