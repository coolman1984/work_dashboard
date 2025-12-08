Analyze and fix an issue in the Work Dashboard: $ARGUMENTS

Steps:

1. **Understand the Issue**
   - Parse the issue description from $ARGUMENTS
   - Search codebase for relevant files using `rg`
   - Read CLAUDE.md in relevant directories for patterns

2. **Find Relevant Code**
   ```bash
   # Search for related files
   rg -n "keyword from issue" work_dashboard.py ui/ services/ utils/
   ```

3. **Analyze Root Cause**
   - Read the relevant source files
   - Identify the bug or missing functionality
   - Check if similar patterns exist elsewhere

4. **Implement Fix**
   - Follow patterns from CLAUDE.md files
   - Use established coding conventions
   - Keep changes minimal and focused

5. **Verify Fix**
   - Run syntax check: `python -m py_compile <modified_files>`
   - Run tests: `python -m unittest tests/verify_features.py`
   - Test manually if UI-related

6. **Document Changes**
   - Create descriptive commit message
   - Update relevant documentation if needed

Remember to follow our testing and code quality standards from CLAUDE.md.
