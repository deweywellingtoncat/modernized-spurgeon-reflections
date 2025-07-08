import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import os
import re
from datetime import datetime, timedelta
import sys

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller bundled app."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

class SpurgeonReflectionReader:
    def __init__(self):
        self.text_files = ["Spurgeon_Complete.txt"]
        
    def parse_date_input(self, date_str):
        """Parse various date input formats."""
        if not date_str:
            return None
        date_str = date_str.strip().lower()
        
        try:
            if date_str in ['today', 'now']:
                return datetime.now()
            elif date_str == 'yesterday':
                return datetime.now() - timedelta(days=1)
            elif date_str == 'tomorrow':
                return datetime.now() + timedelta(days=1)
            
            # Try various date formats
            for fmt in ['%B %d, %Y', '%B %d', '%m/%d/%Y', '%m/%d', '%Y-%m-%d']:
                try:
                    parsed = datetime.strptime(date_str, fmt)
                    if parsed.year == 1900:  # No year specified
                        parsed = parsed.replace(year=datetime.now().year)
                    return parsed
                except ValueError:
                    continue
            return None
        except Exception:
            return None

    def find_reflection(self, date, period):
        """Find reflection for specific date and period."""
        target_pattern = f"*🌄 {date.strftime('%B %#d')}, {period}*" if period == "AM" else f"*🌃 {date.strftime('%B %#d')}, {period}*"
        
        for filename in self.text_files:
            try:
                filepath = get_resource_path(filename)
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                pattern = re.escape(target_pattern).replace(r'\*', r'\*').replace(r'\#', r'#?')
                match = re.search(pattern, content, re.IGNORECASE)
                
                if match:
                    start_pos = match.end()
                    next_marker_pos = content.find('*🌄', start_pos)
                    if next_marker_pos == -1:
                        next_marker_pos = content.find('*🌃', start_pos)
                    
                    if next_marker_pos != -1:
                        reflection_text = content[start_pos:next_marker_pos].strip()
                    else:
                        reflection_text = content[start_pos:].strip()
                    
                    return reflection_text
            except Exception:
                continue
        return None

class SpurgeonGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Daily Spurgeon Reflections")
        self.root.geometry("1000x700")
        
        self.reader = SpurgeonReflectionReader()
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="Daily Spurgeon Reflections", 
                        font=("Arial", 16, "bold"), pady=10)
        title.pack()
        
        # Controls
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        
        tk.Label(control_frame, text="Date:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.date_entry = tk.Entry(control_frame, width=20, font=("Arial", 10))
        self.date_entry.pack(side=tk.LEFT, padx=5)
        self.date_entry.insert(0, "today")
        
        tk.Button(control_frame, text="Load", command=self.load_reflections,
                 bg="#3498db", fg="white", padx=15).pack(side=tk.LEFT, padx=5)
        
        # Copy buttons
        copy_frame = tk.Frame(self.root)
        copy_frame.pack(pady=5)
        
        tk.Button(copy_frame, text="Copy All", command=self.copy_all,
                 bg="#e74c3c", fg="white", padx=15).pack(side=tk.LEFT, padx=5)
        tk.Button(copy_frame, text="Copy AM", command=self.copy_am,
                 bg="#e67e22", fg="white", padx=15).pack(side=tk.LEFT, padx=5)
        tk.Button(copy_frame, text="Copy PM", command=self.copy_pm,
                 bg="#9b59b6", fg="white", padx=15).pack(side=tk.LEFT, padx=5)
        
        # Text area
        self.text_area = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, font=("Consolas", 10), 
            padx=10, pady=10
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Status
        self.status = tk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.date_entry.bind('<Return>', lambda e: self.load_reflections())
        
    def load_reflections(self):
        """Load reflections for the specified date."""
        date_str = self.date_entry.get().strip()
        if not date_str:
            return
            
        date = self.reader.parse_date_input(date_str)
        if not date:
            self.status.config(text="Could not parse date")
            return
            
        self.status.config(text="Loading...")
        self.root.update()
        
        am_reflection = self.reader.find_reflection(date, "AM")
        pm_reflection = self.reader.find_reflection(date, "PM")
        
        output = [f"📅 {date.strftime('%A, %B %d, %Y')}\n" + "="*50]
        found_count = 0
        
        if am_reflection:
            output.append(f"\n🌄 AM REFLECTION\n{'-'*30}")
            output.append(am_reflection)
            self.am_content = am_reflection
            found_count += 1
        else:
            output.append(f"\n⚠️ No AM reflection found for {date.strftime('%B %d, %Y')}")
            self.am_content = ""
            
        if pm_reflection:
            output.append(f"\n🌃 PM REFLECTION\n{'-'*30}")
            output.append(pm_reflection)
            self.pm_content = pm_reflection
            found_count += 1
        else:
            output.append(f"\n⚠️ No PM reflection found for {date.strftime('%B %d, %Y')}")
            self.pm_content = ""
        
        combined_text = "\n\n".join(output)
        self.current_content = combined_text
        
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, combined_text)
        
        self.status.config(text=f"Loaded {found_count} reflection(s)")
    
    def copy_all(self):
        """Copy all text to clipboard."""
        if hasattr(self, 'current_content'):
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_content)
            self.status.config(text="✅ All text copied!")
    
    def copy_am(self):
        """Copy AM reflection to clipboard."""
        if hasattr(self, 'am_content') and self.am_content:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.am_content)
            self.status.config(text="✅ AM reflection copied!")
        else:
            self.status.config(text="No AM content to copy")
    
    def copy_pm(self):
        """Copy PM reflection to clipboard."""
        if hasattr(self, 'pm_content') and self.pm_content:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.pm_content)
            self.status.config(text="✅ PM reflection copied!")
        else:
            self.status.config(text="No PM content to copy")
    
    def run(self):
        """Start the GUI."""
        self.root.mainloop()

if __name__ == "__main__":
    app = SpurgeonGUI()
    app.run()