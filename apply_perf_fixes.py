#!/usr/bin/env python3
"""Performance fix application script"""
import sys

def main():
    filepath = sys.argv[1] if len(sys.argv) > 1 else "work_dashboard.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Track modifications
    modified_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Fix 1: Config error handling (around line 50)
        if '            except: return {"workspaces": {}}' in line:
            modified_lines.append('            except (json.JSONDecodeError, OSError) as e:\r\n')
            modified_lines.append('                print(f"Error loading config: {e}")\r\n')
            modified_lines.append('                return {"workspaces": {}}\r\n')
            i += 1
            continue
        
        # Fix 2: Search debouncing setup (around line 216-217)
        if 'self.search_var = ctk.StringVar()' in line and i < len(lines) - 1:
            if 'self.search_var.trace_add("write", lambda *args: self.refresh_files())' in lines[i+1]:
                modified_lines.append('        # Search with debouncing\r\n')
                modified_lines.append(line)  # Keep the StringVar line
                modified_lines.append('        self.search_after_id = None\r\n')
                modified_lines.append('        self.search_var.trace_add("write", self._on_search_change)\r\n')
                i += 2  # Skip the next line (old trace_add)
                continue
       
        # Fix 3: Add debounce method after space binding (around line 266)
        if '        self.tree.bind("<space>", lambda e: self.quick_look())' in line:
            modified_lines.append(line)
            modified_lines.append('\r\n')
            modified_lines.append('    def _on_search_change(self, *args):\r\n')
            modified_lines.append('        """Debounced search handler - waits 300ms after user stops typing"""\r\n')
            modified_lines.append('        if self.search_after_id:\r\n')
            modified_lines.append('            self.after_cancel(self.search_after_id)\r\n')
            modified_lines.append('        self.search_after_id = self.after(300, self.refresh_files)\r\n')
            i += 1
            continue
        
        # Fix 4: Improve refresh_files error handling (around line 418)
        if '        except: pass' in line and 'refresh_files' in ''.join(lines[max(0, i-20):i]):
            modified_lines.append('        except OSError as e:\r\n')
            modified_lines.append('            print(f"Error reading directory {self.current_path}: {e}")\r\n')
            i += 1
            continue
        
        # Fix 5: Global search debouncing (around line 533)
        if 'self.global_search_var = ctk.StringVar()' in line and i < len(lines) - 1:
            if 'self.global_search_var.trace_add("write", self.on_global_search)' in lines[i+1]:
                modified_lines.append('        # Global Search with debouncing\r\n')
                modified_lines.append(line)
                modified_lines.append('        self.global_search_after_id = None\r\n')
                modified_lines.append('        self.global_search_var.trace_add("write", self._on_global_search_change)\r\n')
                i += 2
                continue
        
        # Fix 6: Global search methods (around line 567-571)
        if '    def on_global_search(self, *args):' in line:
            modified_lines.append('    def _on_global_search_change(self, *args):\r\n')
            modified_lines.append('        """Debounced global search handler - waits 300ms after user stops typing"""\r\n')
            modified_lines.append('        if self.global_search_after_id:\r\n')
            modified_lines.append('            self.after_cancel(self.global_search_after_id)\r\n')
            modified_lines.append('        self.global_search_after_id = self.after(300, self.on_global_search)\r\n')
            modified_lines.append('\r\n')
            modified_lines.append('    def on_global_search(self):\r\n')
            modified_lines.append('        """Apply global search term to all panels"""\r\n')
            i += 1
            continue
        
        # Fix 7: Dynamic theme reload (around line 578-582)
        if '    def change_theme(self, new_t):' in line:
            # Read forward to find the messagebox line
            j = i + 1
            while j < len(lines) and 'messagebox.showinfo("Restart"' not in lines[j]:
                modified_lines.append('\r\n')
                modified_lines.append('    def reload_theme_for_all_widgets(self):\r\n')
                modified_lines.append('        """Update all existing widgets with new theme colors"""\r\n')
                modified_lines.append('        t = THEMES[self.current_theme]\r\n')
                modified_lines.append('        \r\n')
                modified_lines.append('        # Update toolbar\r\n')
                modified_lines.append('        self.toolbar.configure(fg_color=t["bg"])\r\n')
                modified_lines.append('        self.logo_label.configure(text_color=t["text"])\r\n')
                modified_lines.append('        \r\n')
                modified_lines.append('        # Update main container\r\n')
                modified_lines.append('        self.main_container.configure(fg_color=t["bg"])\r\n')
                modified_lines.append('        \r\n')
                modified_lines.append('        # Update all panels\r\n')
                modified_lines.append('        for panel in self.panels:\r\n')
                modified_lines.append('            panel.configure(fg_color=t["card"])\r\n')
                modified_lines.append('            panel.path_label.configure(text_color=t["subtext"])\r\n')
                modified_lines.append('            panel.btn_open_folder.configure(fg_color=t["bg"], text_color=t["text"], hover_color=t["hover"])\r\n')
                modified_lines.append('            panel.btn_focus.configure(border_color=t["subtext"], text_color=t["text"])\r\n')
                modified_lines.append('            panel.stats_label.configure(text_color=t["subtext"])\r\n')
                modified_lines.append('            panel.stats_canvas.configure(bg=t["bg"])\r\n')
                modified_lines.append('        \r\n')
                modified_lines.append('        # Update treeview styles\r\n')
                modified_lines.append('        self.update_global_styles()\r\n')
                i = j + 1
                continue
        
        # Fix 8: Observer cleanup in toggle_focus_mode (around line 655)
        if '            # 1. DESTROY the old container completely to wipe grid weights' in line:
            modified_lines.append('            # 1. Properly cleanup observers before destroying panels\r\n')
            modified_lines.append('            for p in self.panels:\r\n')
            modified_lines.append('                p.destroy()  # Ensures observers are stopped\r\n')
            modified_lines.append('            \r\n')
            modified_lines.append('            # 2. DESTROY the old container completely to wipe grid weights\r\n')
            i += 1
            continue
        
        # Fix numbering in toggle_focus_mode comments
        if '            # 2. Recreate the container' in line:
            modified_lines.append('            # 3. Recreate the container\r\n')
            i += 1
            continue
        if '            # 3. Setup a clean 1x1 Grid' in line:
            modified_lines.append('            # 4. Setup a clean 1x1 Grid\r\n')
            i += 1
            continue
        if '            # 4. Create the single focused panel' in line:
            modified_lines.append('            # 5. Create the single focused panel\r\n')
            i += 1
            continue
        
        # Default: keep the line as is
        modified_lines.append(line)
        i += 1
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(modified_lines)
    
    print(f"Applied performance fixes to {filepath}")

if __name__ == "__main__":
    main()
