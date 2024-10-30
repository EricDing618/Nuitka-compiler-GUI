import customtkinter as ctk
from tkinter import filedialog

class AdvancedOptionsFrame:
    def __init__(self, parent, translator, options):
        self.frame = ctk.CTkFrame(parent)
        self.translator = translator
        self.options = options
        self.widgets = {}
        self.create_widgets()
        
    def create_widgets(self):
        title = ctk.CTkLabel(self.frame, text=self.translator("advanced_options"))
        title.pack(pady=5)
        
        # Create container for two columns
        options_container = ctk.CTkFrame(self.frame)
        options_container.pack(fill='x', expand=True, padx=5)
        
        left_frame = ctk.CTkFrame(options_container)
        left_frame.pack(side='left', fill='x', expand=True, padx=5)
        
        right_frame = ctk.CTkFrame(options_container)
        right_frame.pack(side='left', fill='x', expand=True, padx=5)
        
        self.create_left_options(left_frame)
        self.create_right_options(right_frame)
        
    def create_left_options(self, parent):
        fields = ['company_name', 'product_name', 'file_version', 'include_package']
        for field in fields:
            label = ctk.CTkLabel(parent, text=self.translator(field))
            label.pack(anchor='w', pady=2)
            self.widgets[field] = label
            entry = ctk.CTkEntry(parent, textvariable=self.options[field])
            entry.pack(fill='x', pady=2)
            
    def create_right_options(self, parent):
        # Text fields
        fields = ['include_module', 'python_flag']
        for field in fields:
            label = ctk.CTkLabel(parent, text=self.translator(field))
            label.pack(anchor='w', pady=2)
            self.widgets[field] = label
            entry = ctk.CTkEntry(parent, textvariable=self.options[field])
            entry.pack(fill='x', pady=2)
        
        # Checkboxes
        checkboxes = ['enable_console', 'windows_uac_admin', 'windows_uac_uiaccess']
        for cb in checkboxes:
            checkbox = ctk.CTkCheckBox(
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
        frame = ctk.CTkFrame(parent)
        frame.pack(fill='x', pady=2)
        
        label = ctk.CTkLabel(frame, text=self.translator(option_name))
        label.pack(side='left', pady=2)
        self.widgets[option_name] = label
        
        entry = ctk.CTkEntry(frame, textvariable=self.options[f'{option_name}_path'])
        entry.pack(side='left', expand=True, fill='x', padx=2)
        
        browse_btn = ctk.CTkButton(frame, text="...", width=30,
                                 command=lambda: self.browse_file(option_name, file_type))
        browse_btn.pack(side='right')
                  
    def create_dir_selector(self, parent, option_name):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill='x', pady=2)
        
        label = ctk.CTkLabel(frame, text=self.translator(option_name))
        label.pack(side='left', pady=2)
        self.widgets[option_name] = label
        
        entry = ctk.CTkEntry(frame, textvariable=self.options[option_name])
        entry.pack(side='left', expand=True, fill='x', padx=2)
        
        browse_btn = ctk.CTkButton(frame, text="...", width=30,
                                 command=lambda: self.browse_dir(option_name))
        browse_btn.pack(side='right')

    def browse_file(self, option_name, file_type):
        filename = filedialog.askopenfilename(
            filetypes=[(f"{option_name} files", file_type), ("All files", "*.*")])
        if filename:
            self.options[f'{option_name}_path'].set(filename)
            
    def browse_dir(self, option_name):
        dirname = filedialog.askdirectory()
        if dirname:
            self.options[option_name].set(dirname) 

    def update_translations(self, current_language):
        """Update translations for all widgets in the frame"""
        # Update the frame title
        for widget_name, widget in self.widgets.items():
            if isinstance(widget, (ctk.CTkLabel, ctk.CTkCheckBox)):
                widget.configure(text=self.translator(widget_name))