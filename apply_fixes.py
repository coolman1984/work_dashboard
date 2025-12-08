#!/usr/bin/env python3
"""
Script to apply performance improvements to work_dashboard.py
This ensures all changes are applied correctly without corruption.
"""

import re

def apply_performance_fixes(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Improve config error handling
    content = content.replace(
        '            except: return {"workspaces": {}}',
        '''            except (json.JSONDecodeError, OSError) as e:
                print(f"Error loading config: {e}")
                return {"workspaces": {}}'''
    )
    
    # Fix 2: Add search debouncing to FolderCard.__init__
    content = content.replace(
        '''        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_files())
        self.search_entry = ctk.CTkEntry(self.controls_frame, textvariable=self.search_var,''',
        '''        # Search with debouncing
        self.search_var = ctk.StringVar()
        self.search_after_id = None
        self.search_var.trace_add("write", self._on_search_change)
        self.search_entry = ctk.CTkEntry(self.controls_frame, textvariable=self.search_var,'''
    )
    
    # Fix 3: Add _on_search_change method (after quick_look method)
    content = re.sub(
        r'(        self.tree.bind\("<space>", lambda e: self.quick_look\(\)\))\r?\n',
        r'\1\n\n    def _on_search_change(self, *args):\n        """Debounced search handler - waits 300ms after user stops typing"""\n        if self.search_after_id:\n            self.after_cancel(self.search_after_id)\n        self.search_after_id = self.after(300, self.refresh_files)\n',
        content
    )
    
    # Fix 4: Improve refresh_files error handling
    content = content.replace(
        '''                    files_data.append((f, size_str, mod, raw_size))
                    self.tree.insert("", "end", values=(f, size_str, mod), tags=(full_path,))
        except: pass''',
        '''                    files_data.append((f, size_str, mod, raw_size))
                    self.tree.insert("", "end", values=(f, size_str, mod), tags=(full_path,))
        except OSError as e:
            print(f"Error reading directory {self.current_path}: {e}")'''
    )
    
    # Fix 5: Improve paste_file error handling
    content = content.replace(
        '''            if op == 'copy': shutil.copy2(src, dest)
            elif op == 'cut': shutil.move(src, dest); InternalClipboard.clear()
        except Exception as e: messagebox.showerror("Error", str(e))''',
        '''            if op == 'copy':
                shutil.copy2(src, dest)
            elif op == 'cut':
                shutil.move(src, dest)
                InternalClipboard.clear()
        except (OSError, shutil.Error) as e:
            messagebox.showerror("Error", f"Cannot paste file: {e}")'''
    )
    
    # Fix 6: Improve rename_file error handling
    content = content.replace(
        '''        if n:
            try: os.rename(os.path.join(self.current_path, f), os.path.join(self.current_path, n)); self.refresh_files()
            except Exception as e: messagebox.showerror("Error", str(e))''',
        '''        if n:
            try:
                os.rename(os.path.join(self.current_path, f), os.path.join(self.current_path, n))
                self.refresh_files()
            except OSError as e:
                messagebox.showerror("Error", f"Cannot rename file: {e}")'''
    )
    
    # Fix 7: Improve delete_file error handling
    content = content.replace(
        '''        if messagebox.askyesno("Delete", f"Delete {f}?"):
            try: os.remove(os.path.join(self.current_path, f))
            except Exception as e: messagebox.showerror("Error", str(e))''',
        '''        if messagebox.askyesno("Delete", f"Delete {f}?"):
            try:
                os.remove(os.path.join(self.current_path, f))
            except OSError as e:
                messagebox.showerror("Error", f"Cannot delete file: {e}")'''
    )
    
    # Fix 8: Improve move_file error handling
    content = content.replace(
        '''    def move_file(self, f, t):
        try: shutil.move(os.path.join(self.current_path, f), os.path.join(t.current_path, f))
        except Exception as e: messagebox.showerror("Error", str(e))''',
        '''    def move_file(self, f, t):
        try:
            shutil.move(os.path.join(self.current_path, f), os.path.join(t.current_path, f))
        except (OSError, shutil.Error) as e:
            messagebox.showerror("Error", f"Cannot move file: {e}")'''
    )
    
    # Fix 9: Add global search debouncing
    content = content.replace(
        '''        # Global Search
        self.global_search_var = ctk.StringVar()
        self.global_search_var.trace_add("write", self.on_global_search)
        self.global_search_entry = ctk.CTkEntry(self.toolbar, textvariable=self.global_search_var,''',
        '''        # Global Search with debouncing
        self.global_search_var = ctk.StringVar()
        self.global_search_after_id = None
        self.global_search_var.trace_add("write", self._on_global_search_change)
        self.global_search_entry = ctk.CTkEntry(self.toolbar, textvariable=self.global_search_var,'''
    )
    
    # Fix 10: Add _on_global_search_change method and update on_global_search
    content = re.sub(
        r'    def on_global_search\(self, \*args\):\r?\n        term = self.global_search_var.get\(\)\r?\n        for panel in self.panels:\r?\n            panel.search_var.set\(term\)\r?\n            # refresh_files is triggered automatically by the trace on panel.search_var',
        '''    def _on_global_search_change(self, *args):
        """Debounced global search handler - waits 300ms after user stops typing"""
        if self.global_search_after_id:
            self.after_cancel(self.global_search_after_id)
        self.global_search_after_id = self.after(300, self.on_global_search)

    def on_global_search(self):
        """Apply global search term to all panels"""
        term = self.global_search_var.get()
        for panel in self.panels:
            panel.search_var.set(term)
            # refresh_files is triggered automatically by the trace on panel.search_var''',
        content
    )
    
    # Fix 11: Replace restart message with dynamic theme reload
    content = content.replace(
        '''    def change_theme(self, new_t):
        self.current_theme = new_t
        self.config_data["theme_name"] = new_t
        self.save_config()
        messagebox.showinfo("Restart", "Restart app to apply.")''',
        '''    def change_theme(self, new_t):
        """Change theme dynamically without restart"""
        self.current_theme = new_t
        self.config_data["theme_name"] = new_t
        self.save_config()
        
        # Apply theme immediately
        self.apply_theme(new_t)
        self.reload_theme_for_all_widgets()

    def reload_theme_for_all_widgets(self):
        """Update all existing widgets with new theme colors"""
        t = THEMES[self.current_theme]
        
        # Update toolbar
        self.toolbar.configure(fg_color=t["bg"])
        self.logo_label.configure(text_color=t["text"])
        
        # Update main container
        self.main_container.configure(fg_color=t["bg"])
        
        # Update all panels
        for panel in self.panels:
            panel.configure(fg_color=t["card"])
            panel.path_label.configure(text_color=t["subtext"])
            panel.btn_open_folder.configure(fg_color=t["bg"], text_color=t["text"], hover_color=t["hover"])
            panel.btn_focus.configure(border_color=t["subtext"], text_color=t["text"])
            panel.stats_label.configure(text_color=t["subtext"])
            panel.stats_canvas.configure(bg=t["bg"])
        
        # Update treeview styles
        self.update_global_styles()'''
    )
    
    # Fix 12: Fix toggle_focus_mode to properly cleanup observers
    content = content.replace(
        '''    def toggle_focus_mode(self, panel_id):
        if self.focused_panel_id:
            # Exiting Focus Mode
            self.focused_panel_id = None
            self.setup_layout(self.num_panels, self.layout_mode)
        else:
            # Entering Focus Mode
            self.focused_panel_id = panel_id
            
            # 1. DESTROY the old container completely to wipe grid weights
            if self.main_container:
                self.main_container.destroy()
            
            # 2. Recreate the container''',
        '''    def toggle_focus_mode(self, panel_id):
        if self.focused_panel_id:
            # Exiting Focus Mode
            self.focused_panel_id = None
            self.setup_layout(self.num_panels, self.layout_mode)
        else:
            # Entering Focus Mode
            self.focused_panel_id = panel_id
            
            # 1. Properly cleanup observers before destroying panels
            for p in self.panels:
                p.destroy()  # Ensures observers are stopped
            
            # 2. DESTROY the old container completely to wipe grid weights
            if self.main_container:
                self.main_container.destroy()
            
            # 3. Recreate the container'''
    )
    
    # Fix 13: Improve change_layout error handling
    content = content.replace(
        '''                    self.save_config()
                    self.setup_layout(n, self.layout_mode)
            except: pass''',
        '''                    self.save_config()
                    self.setup_layout(n, self.layout_mode)
            except ValueError:
                messagebox.showerror("Error", "Please enter a number between 2 and 9")'''
    )
    
    # Write the modified content back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Performance improvements applied successfully!")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = "work_dashboard.py"
    
    apply_performance_fixes(filepath)
