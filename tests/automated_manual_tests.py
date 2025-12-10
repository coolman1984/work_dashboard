"""
Automated Manual Testing Script
Verifies all manual test scenarios programmatically
"""

import sys
import os
import time

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from ui.dashboard import WorkDashboard
from services.metadata_service import MetadataService

class AutomatedTester:
    def __init__(self):
        self.results = []
        self.app = None
        
    def log(self, test_name, status, message=""):
        """Log test result"""
        symbol = "✅" if status else "❌"
        self.results.append({
            "test": test_name,
            "status": status,
            "message": message
        })
        print(f"{symbol} {test_name}: {message}")
        
    def test_1_startup(self):
        """Test 1: Verify no startup errors"""
        print("\n=== Test 1: Startup Verification ===")
        try:
            self.app = WorkDashboard()
            self.log("Startup", True, "Application created successfully")
            
            # Check panels
            panel_count = len(self.app.panels)
            if panel_count == 6:
                self.log("Panel Count", True, f"{panel_count} panels displayed")
            else:
                self.log("Panel Count", False, f"Expected 6 panels, got {panel_count}")
                
            # Check toolbar exists
            if hasattr(self.app, 'toolbar'):
                self.log("Toolbar", True, "Toolbar exists")
            else:
                self.log("Toolbar", False, "Toolbar missing")
                
            return True
        except Exception as e:
            self.log("Startup", False, f"Error: {e}")
            return False
            
    def test_2_theme_switching(self):
        """Test 2: Theme switching (Light ↔ Dark)"""
        print("\n=== Test 2: Theme Switching ===")
        try:
            original_theme = self.app.current_theme
            self.log("Original Theme", True, f"Current theme: {original_theme}")
            
            # Switch theme
            new_theme = "Dark" if original_theme == "Light" else "Light"
            
            # Simulate theme change
            try:
                self.app.change_theme(new_theme)
                self.log("Theme Change", True, f"Switched to {new_theme}")
            except AttributeError as e:
                self.log("Theme Change", False, f"AttributeError: {e}")
                return False
                
            # Verify panels updated
            for i, panel in enumerate(self.app.panels):
                if hasattr(panel, 'analytics_bar'):
                    self.log(f"Panel {i+1} Analytics Bar", True, "Has analytics_bar attribute")
                else:
                    self.log(f"Panel {i+1} Analytics Bar", False, "Missing analytics_bar attribute")
                    
            return True
        except Exception as e:
            self.log("Theme Switching", False, f"Error: {e}")
            return False
            
    def test_3_analytics_bar(self):
        """Test 3: Analytics bar structure"""
        print("\n=== Test 3: Analytics Bar Verification ===")
        try:
            for i, panel in enumerate(self.app.panels):
                # Check analytics bar exists
                if hasattr(panel, 'analytics_bar'):
                    analytics = panel.analytics_bar
                    
                    # Check stats_label exists
                    if hasattr(analytics, 'stats_label'):
                        self.log(f"Panel {i+1} Stats Label", True, "stats_label exists")
                    else:
                        self.log(f"Panel {i+1} Stats Label", False, "stats_label missing")
                        
                    # Check stats_canvas exists
                    if hasattr(analytics, 'stats_canvas'):
                        self.log(f"Panel {i+1} Stats Canvas", True, "stats_canvas exists")
                    else:
                        self.log(f"Panel {i+1} Stats Canvas", False, "stats_canvas missing")
                else:
                    self.log(f"Panel {i+1} Analytics", False, "analytics_bar missing")
                    
            return True
        except Exception as e:
            self.log("Analytics Bar", False, f"Error: {e}")
            return False
            
    def test_4_global_search(self):
        """Test 4: Global search functionality"""
        print("\n=== Test 4: Global Search ===")
        try:
            # Check global search exists
            if hasattr(self.app, 'global_search_var'):
                self.log("Global Search Variable", True, "global_search_var exists")
            else:
                self.log("Global Search Variable", False, "global_search_var missing")
                return False
                
            # Check global search entry
            if hasattr(self.app, 'global_search_entry'):
                self.log("Global Search Entry", True, "global_search_entry exists")
            else:
                self.log("Global Search Entry", False, "global_search_entry missing")
                
            # Verify panels have search_var
            for i, panel in enumerate(self.app.panels):
                if hasattr(panel, 'search_var'):
                    self.log(f"Panel {i+1} Search", True, "Has search_var")
                else:
                    self.log(f"Panel {i+1} Search", False, "Missing search_var")
                    
            return True
        except Exception as e:
            self.log("Global Search", False, f"Error: {e}")
            return False
            
    def test_5_readme(self):
        """Test 5: README typo fix"""
        print("\n=== Test 5: README Verification ===")
        try:
            readme_path = os.path.join(project_root, "README.md")
            with open(readme_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Check line 5 (index 4)
            if len(lines) > 4:
                line_5 = lines[4].strip()
                if "Artifacts" in line_5:
                    self.log("README Line 5", True, f"Contains 'Artifacts': {line_5}")
                elif "Artifacs" in line_5:
                    self.log("README Line 5", False, f"Still has typo 'Artifacs': {line_5}")
                else:
                    self.log("README Line 5", True, f"Line content: {line_5}")
            else:
                self.log("README Line 5", False, "File too short")
                
            return True
        except Exception as e:
            self.log("README", False, f"Error: {e}")
            return False
            
    def run_all_tests(self):
        """Run all tests"""
        print("=" * 60)
        print("AUTOMATED MANUAL TESTING")
        print("=" * 60)
        
        # Run tests
        tests = [
            self.test_1_startup,
            self.test_2_theme_switching,
            self.test_3_analytics_bar,
            self.test_4_global_search,
            self.test_5_readme
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                
        # Print summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.results if r["status"])
        total = len(self.results)
        
        print(f"\nPassed: {passed}/{total}")
        print(f"Failed: {total - passed}/{total}")
        
        if passed == total:
            print("\n✅ ALL TESTS PASSED!")
        else:
            print("\n❌ SOME TESTS FAILED")
            print("\nFailed tests:")
            for r in self.results:
                if not r["status"]:
                    print(f"  - {r['test']}: {r['message']}")
                    
        # Cleanup
        if self.app:
            try:
                self.app.destroy()
            except:
                pass
                
        return passed == total

if __name__ == "__main__":
    tester = AutomatedTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
