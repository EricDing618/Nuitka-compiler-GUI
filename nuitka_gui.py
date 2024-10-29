import customtkinter as ctk
from tkinter import filedialog, messagebox
from config import (DEFAULT_WINDOW_SIZE, DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES,
                   load_translations)
from compiler import NuitkaCompiler
from gui_components import AdvancedOptionsFrame

class NuitkaGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.setup_window()
        self.widgets = {}
        self.options = {}
        self.translatable_widgets = {}
        self.load_translations()
        self.create_widgets()
        
    def setup_window(self):
        self.root.title("Nuitka GUI Compiler")
        self.root.geometry(DEFAULT_WINDOW_SIZE)
        ctk.set_appearance_mode("dark")  # Always dark theme
        ctk.set_default_color_theme("blue")
        
    def load_translations(self):
        try:
            self.translations = load_translations()
            self.current_language = DEFAULT_LANGUAGE
        except FileNotFoundError as e:
            messagebox.showerror("Error", str(e))
            self.root.quit()
            
    def create_widgets(self):
        # Create main container with padding
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_language_selection()
        self.create_file_selection()
        self.create_basic_options()
        self.create_advanced_options()
        self.create_compile_section()
        self.create_output_section()
        
    def create_language_selection(self):
        lang_frame = ctk.CTkFrame(self.main_container)
        lang_frame.pack(fill='x', pady=5)
        
        lang_label = ctk.CTkLabel(lang_frame, text=self.translate("language"))
        lang_label.pack(side='left', padx=5)
        
        for lang_code, lang_name in SUPPORTED_LANGUAGES.items():
            btn = ctk.CTkButton(
                lang_frame, 
                text=lang_name,
                command=lambda l=lang_code: self.change_language(l),
                width=100
            )
            btn.pack(side='left', padx=5, pady=5)
            self.widgets[f"lang_{lang_code}"] = btn
        
    def create_file_selection(self):
        file_frame = ctk.CTkFrame(self.main_container)
        file_frame.pack(fill='x', pady=5)
        
        self.file_path = ctk.StringVar()
        self.file_entry = ctk.CTkEntry(file_frame, textvariable=self.file_path)
        self.file_entry.pack(side='left', padx=5, pady=5, expand=True, fill='x')
        
        browse_btn = ctk.CTkButton(file_frame, text="...", width=30,
                                 command=self.browse_file)
        browse_btn.pack(side='right', padx=5, pady=5)

    def create_basic_options(self):
        basic_frame = ctk.CTkFrame(self.main_container)
        basic_frame.pack(fill='x', pady=5)
        
        title = ctk.CTkLabel(basic_frame, text=self.translate("basic_options"))
        title.pack(pady=5)
        
        # Create two columns for options
        left_frame = ctk.CTkFrame(basic_frame)
        left_frame.pack(side='left', fill='x', expand=True, padx=5)
        
        right_frame = ctk.CTkFrame(basic_frame)
        right_frame.pack(side='left', fill='x', expand=True, padx=5)
        
        self.options.update({
            'standalone': ctk.BooleanVar(value=True),
            'onefile': ctk.BooleanVar(value=True),
            'remove_output': ctk.BooleanVar(value=True),
            'follow_imports': ctk.BooleanVar(value=True),
            'show_progress': ctk.BooleanVar(value=True),
            'show_memory': ctk.BooleanVar(value=True)
        })
        
        # Left column options
        for option in ['standalone', 'onefile', 'remove_output']:
            cb = ctk.CTkCheckBox(
                left_frame,
                text=self.translate(option),
                variable=self.options[option]
            )
            cb.pack(anchor='w', pady=2)
            self.translatable_widgets[option] = cb
        
        # Right column options
        for option in ['follow_imports', 'show_progress', 'show_memory']:
            cb = ctk.CTkCheckBox(
                right_frame,
                text=self.translate(option),
                variable=self.options[option]
            )
            cb.pack(anchor='w', pady=2)
            self.translatable_widgets[option] = cb

    def create_advanced_options(self):
        """Create the advanced options section"""
        # Initialize advanced options first
        self.options.update({
            'enable_console': ctk.BooleanVar(value=True),
            'windows_uac_admin': ctk.BooleanVar(value=False),
            'windows_uac_uiaccess': ctk.BooleanVar(value=False),
            'windows_icon_path': ctk.StringVar(),
            'company_name': ctk.StringVar(),
            'product_name': ctk.StringVar(),
            'file_version': ctk.StringVar(),
            'output_dir': ctk.StringVar(),
            'python_flag': ctk.StringVar(),
            'include_package': ctk.StringVar(),
            'include_module': ctk.StringVar()
        })
        
        # Then create the frame
        self.advanced_frame = AdvancedOptionsFrame(
            self.main_container,
            self.translate,
            self.options
        )
        self.advanced_frame.frame.pack(fill='x', pady=5)

    def create_compile_section(self):
        compile_frame = ctk.CTkFrame(self.main_container)
        compile_frame.pack(fill='x', pady=10)
        
        self.compile_btn = ctk.CTkButton(
            compile_frame,
            text=self.translate("compile"),
            command=self.compile
        )
        self.compile_btn.pack(pady=5)
        
        self.progress = ctk.CTkProgressBar(compile_frame)
        self.progress.pack(fill='x', pady=5)
        self.progress.set(0)  # Initialize progress
        
    def create_output_section(self):
        output_frame = ctk.CTkFrame(self.main_container)
        output_frame.pack(fill='both', expand=True, pady=5)
        
        output_label = ctk.CTkLabel(output_frame, text=self.translate("output"))
        output_label.pack(pady=5)
        
        self.output_text = ctk.CTkTextbox(output_frame)
        self.output_text.pack(fill='both', expand=True, padx=5, pady=5)

    def translate(self, key):
        return self.translations[self.current_language].get(key, key)
        
    def change_language(self, lang):
        self.current_language = lang
        self.update_translations()
        
    def update_translations(self):
        """Update all translatable widgets"""
        # Update basic widgets and frames
        for widget_name, widget in self.translatable_widgets.items():
            if hasattr(widget, 'configure'):
                widget.configure(text=self.translate(widget_name))
        
        # Update frame labels
        for frame_name in ['basic_options', 'file_selection', 'output']:
            if frame_name in self.widgets:
                self.widgets[frame_name].configure(text=self.translate(frame_name))
        
        # Update advanced options
        if hasattr(self, 'advanced_frame'):
            self.advanced_frame.update_translations(self.current_language)
        
        # Update compile button
        if hasattr(self, 'compile_btn'):
            self.compile_btn.configure(text=self.translate('compile'))
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Python files", "*.py"), ("All files", "*.*")])
        if filename:
            self.file_path.set(filename)
            
    def compile(self):
        if not self.file_path.get():
            messagebox.showerror(
                self.translate("error"),
                self.translate("no_file_selected")
            )
            return
            
        self.compile_btn.configure(state='disabled')
        self.progress.start()
        self.output_text.delete(1.0, ctk.END)
        self.output_text.insert(ctk.END, self.translate("compilation_started") + "\n")
        
        success, error = NuitkaCompiler.compile(
            self.file_path.get(),
            {k: v.get() for k, v in self.options.items()},
            lambda x: self.output_text.insert(ctk.END, x),
            lambda: self.root.update()
        )
        
        self.progress.stop()
        self.compile_btn.configure(state='normal')
        
        if success:
            messagebox.showinfo(
                self.translate("success"),
                self.translate("compilation_successful")
            )
        else:
            messagebox.showerror(
                self.translate("error"),
                error or self.translate("compilation_failed")
            )

def main():
    app = NuitkaGUI()
    app.root.mainloop()

if __name__ == "__main__":
    main()
