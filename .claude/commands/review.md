Perform a comprehensive code review of recent changes or specified files: $ARGUMENTS

Steps:

1. **Identify Files to Review**
   - If $ARGUMENTS is empty, review recent git changes: `git diff --name-only HEAD~1`
   - Otherwise, review the specified file(s)

2. **Check Code Quality**
   - Follows PEP 8 style guidelines
   - Uses type hints for function signatures
   - Has docstrings for public classes/methods
   - No hardcoded values (use styles.py for colors)

3. **Review Patterns**
   - Check against CLAUDE.md conventions:
     - UI uses CTkFrame/CTkToplevel inheritance
     - Services use @classmethod singleton pattern
     - No mixed grid()/pack() in same container
     - Theme colors from styles.py, not hardcoded

4. **Test Coverage**
   - New features have corresponding tests
   - Existing tests still pass

5. **Security Check**
   - No personal file paths committed
   - No credentials or API keys
   - Safe error handling (no bare except:)

6. **Performance**
   - No unnecessary file operations
   - Proper debouncing for search/refresh
   - Thread safety for UI updates

Provide specific, actionable feedback with file/line references.
Use ✅ for good patterns and ❌ for issues to fix.
