import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from config import DEFAULT_WINDOW_SIZE, DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, load_translations
from compiler import NuitkaCompiler
from gui_components import AdvancedOptionsFrame

class NuitkaGUI:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.widgets = {}
        self.options = {}
        self.translatable_widgets = {}
        self.load_translations()
        self.create_widgets()
        
    def setup_window(self):
        self.root.title("Nuitka GUI Compiler")
        self.root.geometry(DEFAULT_WINDOW_SIZE)
        self.root.configure(bg='#f0f0f0')
        ttk.Style().theme_use('clam')
        
    def load_translations(self):
        try:
            self.translations = load_translations()
            self.current_language = DEFAULT_LANGUAGE
        except FileNotFoundError as e:
            messagebox.showerror("Error", str(e))
            self.root.quit()
            
    def create_widgets(self):
        self.create_language_selection()
        self.create_file_selection()
        self.create_basic_options()
        self.create_advanced_options()
        self.create_compile_section()
        self.create_output_section()
        
    def create_language_selection(self):
        lang_frame = ttk.LabelFrame(self.root, text=self.translate("language"))
        lang_frame.pack(fill='x', padx=10, pady=5)
        
        for lang_code, lang_name in SUPPORTED_LANGUAGES.items():
            btn = ttk.Button(
                lang_frame, 
                text=lang_name,
                command=lambda l=lang_code: self.change_language(l)
            )
            btn.pack(side='left', padx=5, pady=5)
            self.widgets[f"lang_{lang_code}"] = btn

    def create_advanced_options(self):
        self.options.update({
            'enable_console': tk.BooleanVar(value=True),
            'windows_uac_admin': tk.BooleanVar(value=False),
            'windows_uac_uiaccess': tk.BooleanVar(value=False),
            'windows_icon_path': tk.StringVar(),
            'company_name': tk.StringVar(),
            'product_name': tk.StringVar(),
            'file_version': tk.StringVar(),
            'output_dir': tk.StringVar(),
            'python_flag': tk.StringVar(),
            'include_package': tk.StringVar(),
            'include_module': tk.StringVar()
        })
        
        self.advanced_frame = AdvancedOptionsFrame(
            self.root,
            self.translate,
            self.options
        )
        self.advanced_frame.frame.pack(fill='x', pady=5, padx=10)
        
    def translate(self, key):
        return self.translations[self.current_language].get(key, key)
        
    def change_language(self, lang):
        self.current_language = lang
        self.update_translations()
        
    def update_translations(self):
        """Update all translatable widgets"""
        # Update basic widgets and frames
        for widget_name, widget in self.translatable_widgets.items():
            if hasattr(widget, 'config'):
                widget.config(text=self.translate(widget_name))
        
        # Update frame labels
        for frame_name in ['basic_options', 'file_selection', 'output']:
            if frame_name in self.widgets:
                self.widgets[frame_name].config(text=self.translate(frame_name))
        
        # Update advanced options
        if hasattr(self, 'advanced_frame'):
            self.advanced_frame.update_translations(self.current_language)
        
        # Update compile button
        if hasattr(self, 'compile_btn'):
            self.compile_btn.config(text=self.translate('compile'))
        
    def create_file_selection(self):
        file_frame = ttk.LabelFrame(self.root, text=self.translate("file_selection"))
        file_frame.pack(fill='x', pady=5)
        
        self.file_path = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path, width=70)
        self.file_entry.pack(side='left', padx=5, pady=5, expand=True, fill='x')
        
        browse_btn = ttk.Button(file_frame, text="...", width=3,
                              command=self.browse_file)
        browse_btn.pack(side='right', padx=5, pady=5)
        
    def create_basic_options(self):
        # Create a frame for basic options
        basic_frame = ttk.LabelFrame(self.root, text=self.translate("basic_options"))
        basic_frame.pack(fill='x', padx=10, pady=5)
        self.widgets['basic_options'] = basic_frame
        
        # Create left and right frames inside basic_frame
        left_frame = ttk.Frame(basic_frame)
        left_frame.pack(side='left', fill='x', expand=True, padx=5)
        
        right_frame = ttk.Frame(basic_frame)
        right_frame.pack(side='left', fill='x', expand=True, padx=5)
        
        # Initialize basic options if not already done
        if not hasattr(self, 'options'):
            self.options = {}
            
        self.options.update({
            'standalone': tk.BooleanVar(value=True),
            'onefile': tk.BooleanVar(value=True),
            'remove_output': tk.BooleanVar(value=True),
            'follow_imports': tk.BooleanVar(value=True),
            'show_progress': tk.BooleanVar(value=True),
            'show_memory': tk.BooleanVar(value=True)
        })
        
        # Left column options
        for option in ['standalone', 'onefile', 'remove_output']:
            cb = ttk.Checkbutton(
                left_frame,
                text=self.translate(option),
                variable=self.options[option]
            )
            cb.pack(anchor='w', pady=2)
            self.translatable_widgets[option] = cb  # Add to translatable widgets
        
        # Right column options
        for option in ['follow_imports', 'show_progress', 'show_memory']:
            cb = ttk.Checkbutton(
                right_frame,
                text=self.translate(option),
                variable=self.options[option]
            )
            cb.pack(anchor='w', pady=2)
            self.translatable_widgets[option] = cb  # Add to translatable widgets
            
    def create_compile_section(self):
        compile_frame = ttk.Frame(self.root)
        compile_frame.pack(fill='x', pady=10)
        
        self.compile_btn = ttk.Button(
            compile_frame,
            text=self.translate("compile"),
            command=self.compile
        )
        self.compile_btn.pack(pady=5)
        self.widgets["compile"] = self.compile_btn
        
        self.progress = ttk.Progressbar(compile_frame, mode='indeterminate')
        self.progress.pack(fill='x', pady=5)
        
    def create_output_section(self):
        output_frame = ttk.LabelFrame(self.root, text=self.translate("output"))
        output_frame.pack(fill='both', expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(output_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.output_text = tk.Text(output_frame, height=15, yscrollcommand=scrollbar.set)
        self.output_text.pack(fill='both', expand=True, padx=5, pady=5)
        scrollbar.config(command=self.output_text.yview)
        
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
            
        self.compile_btn.config(state='disabled')
        self.progress.start()
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, self.translate("compilation_started") + "\n")
        
        success, error = NuitkaCompiler.compile(
            self.file_path.get(),
            {k: v.get() for k, v in self.options.items()},
            lambda x: self.output_text.insert(tk.END, x),
            lambda: self.root.update()
        )
        
        self.progress.stop()
        self.compile_btn.config(state='normal')
        
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
    root = tk.Tk()
    app = NuitkaGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
