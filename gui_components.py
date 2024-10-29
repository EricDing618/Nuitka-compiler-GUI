import tkinter as tk
from tkinter import ttk, filedialog

class AdvancedOptionsFrame:
    def __init__(self, parent, translator, options):
        self.frame = ttk.LabelFrame(parent, text=translator("advanced_options"))
        self.translator = translator
        self.options = options
        self.widgets = {}
        self.create_widgets()
        
    def update_translations(self, current_language):
        """Update translations for all widgets in the frame"""
        self.frame.config(text=self.translator("advanced_options"))
        
        # Update all labels
        for widget_name, widget in self.widgets.items():
            if isinstance(widget, ttk.Label):
                widget.config(text=self.translator(widget_name))
            elif isinstance(widget, ttk.Checkbutton):
                widget.config(text=self.translator(widget_name))
                
    def create_widgets(self):
        left_frame = ttk.Frame(self.frame)
        left_frame.pack(side='left', fill='x', expand=True, padx=5)
        
        right_frame = ttk.Frame(self.frame)
        right_frame.pack(side='left', fill='x', expand=True, padx=5)
        
        self.create_left_options(left_frame)
        self.create_right_options(right_frame)
        
    def create_left_options(self, parent):
        fields = ['company_name', 'product_name', 'file_version', 'include_package']
        for field in fields:
            label = ttk.Label(parent, text=self.translator(field))
            label.pack(anchor='w', pady=2)
            self.widgets[field] = label
            entry = ttk.Entry(parent, textvariable=self.options[field])
            entry.pack(fill='x', pady=2)
            
    def create_right_options(self, parent):
        # Text fields
        fields = ['include_module', 'python_flag']
        for field in fields:
            label = ttk.Label(parent, text=self.translator(field))
            label.pack(anchor='w', pady=2)
            self.widgets[field] = label
            entry = ttk.Entry(parent, textvariable=self.options[field])
            entry.pack(fill='x', pady=2)
        
        # Checkboxes
        checkboxes = ['enable_console', 'windows_uac_admin', 'windows_uac_uiaccess']
        for cb in checkboxes:
            checkbox = ttk.Checkbutton(
                parent, 
                text=self.translator(cb),
                variable=self.options[cb]
            )
            checkbox.pack(anchor='w', pady=2)
            self.widgets[cb] = checkbox
        
        # Special buttons
        self.create_file_selector(parent, "windows_icon", "*.ico")
        self.create_dir_selector(parent, "output_dir")
        
    def create_file_selector(self, parent, option_name, file_type):
        frame = ttk.Frame(parent)
        frame.pack(fill='x', pady=2)
        label = ttk.Label(frame, text=self.translator(option_name))
        label.pack(side='left', pady=2)
        self.widgets[option_name] = label
        ttk.Entry(frame, textvariable=self.options[f'{option_name}_path']).pack(
            side='left', expand=True, fill='x', padx=2)
        ttk.Button(frame, text="...", width=3,
                  command=lambda: self.browse_file(option_name, file_type)).pack(side='right')
                  
    def create_dir_selector(self, parent, option_name):
        frame = ttk.Frame(parent)
        frame.pack(fill='x', pady=2)
        label = ttk.Label(frame, text=self.translator(option_name))
        label.pack(side='left', pady=2)
        self.widgets[option_name] = label
        ttk.Entry(frame, textvariable=self.options[option_name]).pack(
            side='left', expand=True, fill='x', padx=2)
        ttk.Button(frame, text="...", width=3,
                  command=lambda: self.browse_dir(option_name)).pack(side='right')
                  
    def browse_file(self, option_name, file_type):
        filename = filedialog.askopenfilename(
            filetypes=[(f"{option_name} files", file_type), ("All files", "*.*")])
        if filename:
            self.options[f'{option_name}_path'].set(filename)
            
    def browse_dir(self, option_name):
        dirname = filedialog.askdirectory()
        if dirname:
            self.options[option_name].set(dirname) 