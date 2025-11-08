#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modern Cursor-style GUI for PDF Batch Processor
Clean, minimal interface inspired by Cursor
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox, simpledialog
import threading
import sys
import os
from pathlib import Path

# Import the batch processor functions
from pdf_batch_processor import (
    is_valid_folder_name,
    find_matching_pdf,
    clean_and_structure_pdf,
    reverse_hebrew_in_text
)


class CursorStyleGUI:
    """Cursor-inspired PDF Processor GUI"""
    
    # Cursor-style colors (dark theme)
    COLORS = {
        'bg': '#1E1E1E',              # Dark background
        'card': '#252526',            # Card background
        'card_hover': '#2D2D30',      # Card hover
        'input_bg': '#3C3C3C',        # Input background
        'border': '#3E3E42',          # Border color
        'text': '#CCCCCC',            # Primary text
        'text_secondary': '#858585',  # Secondary text
        'text_muted': '#6A6A6A',      # Muted text
        'accent': '#007ACC',          # Accent blue
        'accent_hover': '#1C97EA',    # Accent hover
        'success': '#4EC9B0',         # Success/teal
        'warning': '#CE9178',         # Warning/orange
        'error': '#F48771',           # Error/red
        'white': '#FFFFFF',           # Pure white
        'selected': '#094771'         # Selected item bg
    }
    
    def __init__(self, root):
        self.root = root
        self.root.title("מעבד PDF")
        self.root.geometry("1400x750")
        self.root.minsize(1200, 700)
        
        # Data
        self.selected_folder = tk.StringVar()
        self.is_processing = False
        self.folders_data = []
        
        # Configure style
        self.root.configure(bg=self.COLORS['bg'])
        self.setup_style()
        self.create_widgets()
        
    def setup_style(self):
        """Configure dark theme style"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure Treeview
        style.configure(
            "Dark.Treeview",
            background=self.COLORS['card'],
            foreground=self.COLORS['text'],
            fieldbackground=self.COLORS['card'],
            borderwidth=0,
            rowheight=32,
            font=('Arial', 11)
        )
        
        style.configure(
            "Dark.Treeview.Heading",
            background=self.COLORS['bg'],
            foreground=self.COLORS['text'],
            borderwidth=0,
            font=('Arial', 11, 'bold')
        )
        
        style.map('Dark.Treeview',
                 background=[('selected', self.COLORS['selected'])],
                 foreground=[('selected', self.COLORS['white'])])
        
        # Scrollbar
        style.configure("Dark.Vertical.TScrollbar",
                       background=self.COLORS['card'],
                       troughcolor=self.COLORS['bg'],
                       borderwidth=0,
                       arrowsize=12)
        
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Main container
        main = tk.Frame(self.root, bg=self.COLORS['bg'])
        main.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Header
        self.create_header(main)
        
        # Folder selection
        self.create_folder_section(main)
        
        # Middle section - folders list and log side by side
        middle = tk.Frame(main, bg=self.COLORS['bg'])
        middle.pack(fill='both', expand=True, pady=(0, 12))
        
        # Folders list on the right
        self.create_list_section(middle)
        
        # Log section on the left
        self.create_log_section(middle)
        
        # Action bar at bottom
        self.create_action_bar(main)
        
    def create_rounded_button(self, parent, text, command, bg, fg=None, state='normal'):
        """Create modern rounded button with rounded corners"""
        fg = fg or self.COLORS['white']
        
        # Container canvas for rounded corners
        canvas = tk.Canvas(
            parent,
            bg=parent['bg'],
            highlightthickness=0,
            borderwidth=0
        )
        
        # Calculate size based on text
        temp_label = tk.Label(parent, text=text, font=('Arial', 11, 'bold'))
        temp_label.update_idletasks()
        text_width = temp_label.winfo_reqwidth()
        text_height = temp_label.winfo_reqheight()
        temp_label.destroy()
        
        width = text_width + 32  # padding
        height = text_height + 16
        canvas.config(width=width, height=height)
        
        # Draw rounded rectangle
        radius = 8
        rect = self._create_rounded_rectangle(canvas, 2, 2, width-2, height-2, radius, fill=bg, outline='')
        
        # Add text
        text_id = canvas.create_text(
            width//2, height//2,
            text=text,
            font=('Arial', 11, 'bold'),
            fill=fg
        )
        
        # Store original color
        canvas.original_bg = bg
        canvas.hover_bg = self.lighten_color(bg)
        canvas.rect_id = rect
        canvas.text_id = text_id
        canvas.is_enabled = state == 'normal'
        canvas.command = command
        
        # Hover effects
        def on_enter(e):
            if canvas.is_enabled:
                canvas.itemconfig(rect, fill=canvas.hover_bg)
                canvas.config(cursor='hand2')
        
        def on_leave(e):
            if canvas.is_enabled:
                canvas.itemconfig(rect, fill=canvas.original_bg)
                canvas.config(cursor='')
        
        def on_click(e):
            if canvas.is_enabled and canvas.command:
                canvas.command()
        
        if state == 'normal':
            canvas.bind('<Enter>', on_enter)
            canvas.bind('<Leave>', on_leave)
            canvas.bind('<Button-1>', on_click)
        else:
            canvas.itemconfig(rect, fill='#404040')
            canvas.itemconfig(text_id, fill='#707070')
        
        return canvas, canvas
    
    def _create_rounded_rectangle(self, canvas, x1, y1, x2, y2, radius=25, **kwargs):
        """Create a rounded rectangle on canvas"""
        points = [
            x1+radius, y1,
            x1+radius, y1,
            x2-radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1+radius,
            x1, y1
        ]
        return canvas.create_polygon(points, smooth=True, **kwargs)
    
    def lighten_color(self, hex_color):
        """Lighten a hex color by 10%"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r * 1.15))
        g = min(255, int(g * 1.15))
        b = min(255, int(b * 1.15))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def enable_button(self, btn, color):
        """Enable a button"""
        btn.is_enabled = True
        btn.original_bg = color
        btn.hover_bg = self.lighten_color(color)
        btn.itemconfig(btn.rect_id, fill=color)
        btn.itemconfig(btn.text_id, fill=self.COLORS['white'])
        
        # Re-bind events
        def on_enter(e):
            if btn.is_enabled:
                btn.itemconfig(btn.rect_id, fill=btn.hover_bg)
                btn.config(cursor='hand2')
        
        def on_leave(e):
            if btn.is_enabled:
                btn.itemconfig(btn.rect_id, fill=btn.original_bg)
                btn.config(cursor='')
        
        def on_click(e):
            if btn.is_enabled and btn.command:
                btn.command()
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        btn.bind('<Button-1>', on_click)
    
    def disable_button(self, btn):
        """Disable a button"""
        btn.is_enabled = False
        btn.itemconfig(btn.rect_id, fill='#404040')
        btn.itemconfig(btn.text_id, fill='#707070')
    
    def create_header(self, parent):
        """Create header section"""
        header = tk.Frame(parent, bg=self.COLORS['bg'])
        header.pack(fill='x', pady=(0, 15))
        
        # Title
        title = tk.Label(
            header,
            text="מעבד PDF לדוחות רפואיים",
            font=('Arial', 20, 'bold'),
            bg=self.COLORS['bg'],
            fg=self.COLORS['text']
        )
        title.pack(anchor='e')
        
        # Subtitle
        subtitle = tk.Label(
            header,
            text="עיבוד אצווה מתקדם",
            font=('Arial', 11),
            bg=self.COLORS['bg'],
            fg=self.COLORS['text_secondary']
        )
        subtitle.pack(anchor='e', pady=(3, 0))
        
    def create_folder_section(self, parent):
        """Create folder selection section"""
        section = tk.Frame(parent, bg=self.COLORS['card'])
        section.pack(fill='x', pady=(0, 12))
        
        content = tk.Frame(section, bg=self.COLORS['card'])
        content.pack(fill='x', padx=20, pady=15)
        
        # Row with button and path
        row = tk.Frame(content, bg=self.COLORS['card'])
        row.pack(fill='x')
        
        # Browse button
        self.browse_btn, _ = self.create_rounded_button(
            row, "📁 בחר תיקייה", self.browse_folder,
            self.COLORS['accent']
        )
        self.browse_btn.pack(side='right')
        
        # Path display
        path_bg = tk.Frame(row, bg=self.COLORS['input_bg'])
        path_bg.pack(side='right', fill='x', expand=True, padx=(0, 10))
        
        self.path_entry = tk.Entry(
            path_bg,
            textvariable=self.selected_folder,
            font=('Arial', 11),
            bg=self.COLORS['input_bg'],
            fg=self.COLORS['text'],
            relief='flat',
            state='readonly',
            readonlybackground=self.COLORS['input_bg'],
            insertbackground=self.COLORS['text']
        )
        self.path_entry.pack(fill='x', padx=12, pady=8)
        
        # Info
        info = tk.Label(
            content,
            text="תיקיות בפורמט: 2 אותיות עבריות + 3 ספרות (דוגמה: אה456)",
            font=('Arial', 10),
            bg=self.COLORS['card'],
            fg=self.COLORS['text_muted'],
            justify='right'
        )
        info.pack(anchor='e', pady=(8, 0))
        
    def create_list_section(self, parent):
        """Create folders list section"""
        section = tk.Frame(parent, bg=self.COLORS['card'])
        section.pack(side='right', fill='both', expand=True, padx=(0, 6))
        
        content = tk.Frame(section, bg=self.COLORS['card'])
        content.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Header with title and buttons
        header = tk.Frame(content, bg=self.COLORS['card'])
        header.pack(fill='x', pady=(0, 12))
        
        # Title
        tk.Label(
            header,
            text="תיקיות",
            font=('Arial', 13, 'bold'),
            bg=self.COLORS['card'],
            fg=self.COLORS['text']
        ).pack(side='right')
        
        # Buttons
        btns = tk.Frame(header, bg=self.COLORS['card'])
        btns.pack(side='left')
        
        # Select all
        self.select_all_btn, _ = self.create_rounded_button(
            btns, "✓ בחר הכל", self.toggle_select_all,
            self.COLORS['success']
        )
        self.select_all_btn.pack(side='left', padx=(0, 6))
        
        # Refresh
        self.refresh_btn, _ = self.create_rounded_button(
            btns, "🔄 רענן", self.refresh_folders,
            self.COLORS['border'], state='disabled'
        )
        self.refresh_btn.pack(side='left')
        
        # Tree container
        tree_bg = tk.Frame(content, bg=self.COLORS['border'])
        tree_bg.pack(fill='both', expand=True)
        
        tree_inner = tk.Frame(tree_bg, bg=self.COLORS['card'])
        tree_inner.pack(fill='both', expand=True, padx=1, pady=1)
        
        # Scrollbar
        vsb = ttk.Scrollbar(tree_inner, orient="vertical", style="Dark.Vertical.TScrollbar")
        vsb.pack(side='left', fill='y')
        
        # Treeview
        self.tree = ttk.Treeview(
            tree_inner,
            columns=('status', 'folder', 'pdf'),
            show='headings',
            style='Dark.Treeview',
            yscrollcommand=vsb.set,
            selectmode='browse'
        )
        
        vsb.config(command=self.tree.yview)
        
        self.tree.heading('status', text='')
        self.tree.heading('folder', text='תיקייה')
        self.tree.heading('pdf', text='קובץ PDF')
        
        self.tree.column('status', width=50, anchor='center')
        self.tree.column('folder', width=180, anchor='e')
        self.tree.column('pdf', width=250, anchor='e')
        
        self.tree.pack(side='right', fill='both', expand=True)
        
        # Bindings
        self.tree.bind('<Double-1>', self.toggle_folder_selection)
        self.tree.bind('<Return>', self.toggle_folder_selection)
        self.tree.bind('<space>', self.toggle_folder_selection)
        
    def create_action_bar(self, parent):
        """Create action bar with start button and status"""
        bar = tk.Frame(parent, bg=self.COLORS['bg'])
        bar.pack(fill='x', pady=(0, 12))
        
        # Status
        self.status_label = tk.Label(
            bar,
            text="ממתין לבחירת תיקייה",
            font=('Arial', 11),
            bg=self.COLORS['bg'],
            fg=self.COLORS['text_secondary']
        )
        self.status_label.pack(side='right', padx=15)
        
        # Start button
        self.start_btn, _ = self.create_rounded_button(
            bar, "▶ התחל עיבוד", self.start_processing,
            self.COLORS['accent'], state='disabled'
        )
        self.start_btn.pack(side='left')
        
    def create_log_section(self, parent):
        """Create log section"""
        section = tk.Frame(parent, bg=self.COLORS['card'])
        section.pack(side='left', fill='both', expand=True, padx=(6, 0))
        
        content = tk.Frame(section, bg=self.COLORS['card'])
        content.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Title
        tk.Label(
            content,
            text="יומן",
            font=('Arial', 13, 'bold'),
            bg=self.COLORS['card'],
            fg=self.COLORS['text']
        ).pack(anchor='e', pady=(0, 8))
        
        # Log area
        log_bg = tk.Frame(content, bg=self.COLORS['border'])
        log_bg.pack(fill='both', expand=True)
        
        log_inner = tk.Frame(log_bg, bg=self.COLORS['input_bg'])
        log_inner.pack(fill='both', expand=True, padx=1, pady=1)
        
        self.log_text = scrolledtext.ScrolledText(
            log_inner,
            font=('Consolas', 10),
            wrap=tk.WORD,
            bg=self.COLORS['input_bg'],
            fg=self.COLORS['text'],
            insertbackground=self.COLORS['text'],
            state='disabled',
            relief='flat',
            padx=12,
            pady=10,
            borderwidth=0
        )
        self.log_text.pack(fill='both', expand=True)
        
        # Tags for colors
        self.log_text.tag_config('success', foreground=self.COLORS['success'])
        self.log_text.tag_config('error', foreground=self.COLORS['error'])
        self.log_text.tag_config('warning', foreground=self.COLORS['warning'])
        self.log_text.tag_config('info', foreground=self.COLORS['accent'])
        
    def browse_folder(self):
        """Browse for folder"""
        folder = filedialog.askdirectory(
            title="בחר תיקיית אם",
            initialdir=os.path.expanduser("~")
        )
        
        if folder:
            self.selected_folder.set(folder)
            self.scan_folders(folder)
    
    def scan_folders(self, mother_folder):
        """Scan and display folders"""
        try:
            self.log_message(f"סורק: {mother_folder}\n", 'info')
            
            all_items = os.listdir(mother_folder)
            self.folders_data = []
            
            for item in all_items:
                item_path = os.path.join(mother_folder, item)
                if os.path.isdir(item_path) and is_valid_folder_name(item):
                    pdf_path = find_matching_pdf(item_path, item)
                    pdf_name = f"{item}.pdf" if pdf_path else "❌ לא נמצא"
                    
                    self.folders_data.append({
                        'path': item_path,
                        'name': item,
                        'selected': True,
                        'pdf_name': pdf_name,
                        'pdf_exists': pdf_path is not None
                    })
            
            if self.folders_data:
                self.update_tree()
                self.enable_button(self.start_btn, self.COLORS['accent'])
                self.enable_button(self.refresh_btn, self.COLORS['border'])
                self.status_label.config(
                    text=f"נמצאו {len(self.folders_data)} תיקיות",
                    fg=self.COLORS['success']
                )
                self.log_message(f"✓ {len(self.folders_data)} תיקיות\n\n", 'success')
            else:
                self.tree.delete(*self.tree.get_children())
                self.status_label.config(
                    text="לא נמצאו תיקיות",
                    fg=self.COLORS['error']
                )
                self.log_message("לא נמצאו תיקיות תקינות\n", 'error')
                
        except Exception as e:
            self.log_message(f"שגיאה: {str(e)}\n", 'error')
            messagebox.showerror("שגיאה", f"שגיאה בסריקה:\n{str(e)}")
    
    def update_tree(self):
        """Update tree with folders"""
        self.tree.delete(*self.tree.get_children())
        
        for folder in self.folders_data:
            status = '✓' if folder['selected'] else '○'
            values = (status, folder['name'], folder['pdf_name'])
            item_id = self.tree.insert('', 'end', values=values)
            
            if not folder['pdf_exists']:
                self.tree.item(item_id, tags=('missing',))
            elif folder['selected']:
                self.tree.item(item_id, tags=('selected',))
            else:
                self.tree.item(item_id, tags=('unselected',))
        
        self.tree.tag_configure('missing', foreground=self.COLORS['error'])
        self.tree.tag_configure('selected', foreground=self.COLORS['success'])
        self.tree.tag_configure('unselected', foreground=self.COLORS['text_muted'])
    
    def toggle_folder_selection(self, event=None):
        """Toggle folder selection"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        index = self.tree.index(item)
        
        if 0 <= index < len(self.folders_data):
            self.folders_data[index]['selected'] = not self.folders_data[index]['selected']
            self.update_tree()
    
    def toggle_select_all(self):
        """Toggle select all"""
        if not self.folders_data:
            return
        
        all_selected = all(f['selected'] for f in self.folders_data if f['pdf_exists'])
        new_state = not all_selected
        
        for folder in self.folders_data:
            if folder['pdf_exists']:
                folder['selected'] = new_state
        
        self.update_tree()
    
    def edit_pdf_name(self):
        """Edit PDF name"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("מידע", "בחר תיקייה")
            return
        
        item = selection[0]
        index = self.tree.index(item)
        
        if 0 <= index < len(self.folders_data):
            folder = self.folders_data[index]
            
            new_name = simpledialog.askstring(
                "ערוך שם",
                f"שם PDF עבור {folder['name']}:",
                initialvalue=folder['pdf_name'].replace('.pdf', '').replace('❌ לא נמצא', '')
            )
            
            if new_name:
                if not new_name.endswith('.pdf'):
                    new_name += '.pdf'
                
                folder['pdf_name'] = new_name
                pdf_path = os.path.join(folder['path'], new_name)
                folder['pdf_exists'] = os.path.exists(pdf_path)
                
                self.update_tree()
                
                if folder['pdf_exists']:
                    self.log_message(f"✓ עודכן: {new_name}\n", 'success')
                else:
                    self.log_message(f"⚠ הקובץ לא נמצא: {new_name}\n", 'warning')
    
    def refresh_folders(self):
        """Refresh folder list"""
        folder = self.selected_folder.get()
        if folder:
            self.scan_folders(folder)
    
    def start_processing(self):
        """Start processing"""
        if self.is_processing:
            return
        
        selected = [f for f in self.folders_data if f['selected'] and f['pdf_exists']]
        
        if not selected:
            messagebox.showwarning("אזהרה", "בחר לפחות תיקייה אחת")
            return
        
        if not messagebox.askyesno("אישור", f"לעבד {len(selected)} תיקיות?"):
            return
        
        self.is_processing = True
        self.disable_button(self.start_btn)
        self.disable_button(self.refresh_btn)
        self.disable_button(self.browse_btn)
        self.status_label.config(text="מעבד...", fg=self.COLORS['warning'])
        
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        
        thread = threading.Thread(target=self.run_process, args=(selected,))
        thread.daemon = True
        thread.start()
    
    def run_process(self, selected):
        """Run processing"""
        try:
            self.log_message("═" * 60 + "\n")
            self.log_message("מתחיל עיבוד\n", 'info')
            self.log_message("═" * 60 + "\n\n")
            
            success = 0
            failed = 0
            total = len(selected)
            
            for i, folder_data in enumerate(selected, 1):
                folder_path = folder_data['path']
                folder_name = folder_data['name']
                pdf_name = folder_data['pdf_name']
                
                self.log_message(f"[{i}/{total}] {folder_name}\n")
                self.root.after(0, lambda t=f"מעבד {i}/{total}": 
                              self.status_label.config(text=t))
                
                try:
                    pdf_path = os.path.join(folder_path, pdf_name)
                    
                    if not os.path.exists(pdf_path):
                        self.log_message(f"  ❌ לא נמצא\n", 'error')
                        failed += 1
                        continue
                    
                    self.log_message(f"  📖 קורא...\n")
                    cleaned = clean_and_structure_pdf(pdf_path)
                    
                    self.log_message(f"  🔄 מתקן עברית...\n")
                    fixed = reverse_hebrew_in_text(cleaned)
                    
                    output = f"{folder_name}_CLEANED.txt"
                    output_path = os.path.join(folder_path, output)
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(fixed)
                    
                    self.log_message(f"  ✅ הושלם\n", 'success')
                    success += 1
                    
                except Exception as e:
                    self.log_message(f"  ❌ {str(e)}\n", 'error')
                    failed += 1
            
            self.log_message("\n" + "═" * 60 + "\n")
            self.log_message("סיכום\n", 'info')
            self.log_message("═" * 60 + "\n")
            self.log_message(f"✅ הצליחו: {success}\n", 'success')
            self.log_message(f"❌ נכשלו: {failed}\n", 'error' if failed > 0 else 'info')
            self.log_message(f"📁 סה״כ: {total}\n")
            self.log_message("\n🎉 הושלם!\n", 'success')
            
            self.finish_processing(success, failed, total)
            
        except Exception as e:
            self.log_message(f"\nשגיאה: {str(e)}\n", 'error')
            self.finish_processing(0, 0, 0)
    
    def finish_processing(self, success, failed, total):
        """Finish processing"""
        self.is_processing = False
        self.enable_button(self.start_btn, self.COLORS['accent'])
        self.enable_button(self.refresh_btn, self.COLORS['border'])
        self.enable_button(self.browse_btn, self.COLORS['accent'])
        
        if success > 0:
            self.status_label.config(
                text=f"הושלם! {success}/{total}",
                fg=self.COLORS['success']
            )
            messagebox.showinfo(
                "הושלם",
                f"✅ הצליחו: {success}\n"
                f"❌ נכשלו: {failed}\n"
                f"📁 סה״כ: {total}"
            )
        else:
            self.status_label.config(text="נכשל", fg=self.COLORS['error'])
    
    def log_message(self, message, tag=None):
        """Add log message"""
        def append():
            self.log_text.config(state='normal')
            if tag:
                self.log_text.insert(tk.END, message, tag)
            else:
                self.log_text.insert(tk.END, message)
            self.log_text.see(tk.END)
            self.log_text.config(state='disabled')
        
        self.root.after(0, append)


def main():
    """Main entry"""
    root = tk.Tk()
    app = CursorStyleGUI(root)
    
    # Center window
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f'{w}x{h}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()
