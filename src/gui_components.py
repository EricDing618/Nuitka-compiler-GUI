from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QCheckBox, QComboBox,
                            QFileDialog)

class AdvancedOptionsFrame(QFrame):
    def __init__(self, parent, translator, options):
        super().__init__(parent)
        self.translator = translator
        self.options = options
        self.widgets = {}
        self.flag_dropdown = None
        self.current_flag_mapping = {}
        
        # Add default options with corrected python_flag value
        self.options.update({
            'build_name': '',
            'windows_icon_path': '',
            'output_dir': '',
            'python_flag': 'O',
            'company_name': '',
            'product_name': '',
            'file_version': '',
            'include_package': '',
            'include_module': ''
        })
        
        self.create_widgets()
        
    def safe_disconnect(self, widget):
        """Safely disconnect all signals from a widget"""
        try:
            widget.disconnect()
        except Exception:
            pass

    def get_localized_flags(self):
        """Get the Python flags with localized descriptions"""
        self.current_flag_mapping = {
            self.translator("flag_no_opt"): "",  # No optimization
            self.translator("flag_basic_opt"): "O",  # Basic optimization
            self.translator("flag_extra_opt"): "OO",  # Extra optimization
            self.translator("flag_no_bytecode"): "B",  # No bytecode
            self.translator("flag_debug"): "d",  # Debug mode
            self.translator("flag_verbose"): "v"  # Verbose mode
        }
        return self.current_flag_mapping

    def create_widgets(self):
        layout = QVBoxLayout(self)
        
        title = QLabel(self.translator("advanced_options"))
        layout.addWidget(title)
        
        # Create container for two columns
        options_container = QFrame()
        options_layout = QHBoxLayout(options_container)
        
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        self.create_left_options(left_layout)
        
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        self.create_right_options(right_layout)
        
        options_layout.addWidget(left_frame)
        options_layout.addWidget(right_frame)
        layout.addWidget(options_container)

    def create_left_options(self, layout):
        # Add build name
        self.add_build_name(layout)
        
        # Add metadata fields
        fields = ['company_name', 'product_name', 'file_version', 'include_package']
        
        for field in fields:
            label = QLabel(self.translator(field))
            layout.addWidget(label)
            self.widgets[field] = label
            
            entry = QLineEdit()
            entry.setText(self.options[field])
            entry.textChanged.connect(lambda text, f=field: self.update_option(f, text))
            layout.addWidget(entry)

    def add_build_name(self, layout):
        label = QLabel(self.translator('build_name'))
        layout.addWidget(label)
        self.widgets['build_name'] = label
        
        entry = QLineEdit()
        entry.setText(self.options['build_name'])
        entry.textChanged.connect(
            lambda text: self.update_option('build_name', text))
        layout.addWidget(entry)

    def create_right_options(self, layout):
        # Text fields
        fields = ['include_module']
        for field in fields:
            label = QLabel(self.translator(field))
            layout.addWidget(label)
            self.widgets[field] = label
            
            entry = QLineEdit()
            entry.setText(self.options[field])
            entry.textChanged.connect(lambda text, f=field: self.update_option(f, text))
            layout.addWidget(entry)
        
        # Python Flag dropdown
        flag_frame = QFrame()
        flag_layout = QHBoxLayout(flag_frame)
        
        flag_label = QLabel(self.translator('python_flag'))
        flag_layout.addWidget(flag_label)
        self.widgets['python_flag'] = flag_label
        
        localized_flags = self.get_localized_flags()
        self.flag_dropdown = QComboBox()
        self.flag_dropdown.addItems(localized_flags.keys())
        self.flag_dropdown.currentTextChanged.connect(self.on_flag_selected)
        flag_layout.addWidget(self.flag_dropdown)
        
        layout.addWidget(flag_frame)
        
        # Python Flag dropdown styling
        self.flag_dropdown.setFixedWidth(200)  # Set fixed width
        self.flag_dropdown.setMaxVisibleItems(8)  # Show max 8 items in dropdown
        
        # C Compiler dropdown
        compiler_frame = QFrame()
        compiler_layout = QHBoxLayout(compiler_frame)
        
        compiler_label = QLabel(self.translator('c_compiler'))
        compiler_layout.addWidget(compiler_label)
        self.widgets['c_compiler'] = compiler_label
        
        # Define available C compilers
        self.compiler_mapping = {
            'MinGW64 (default)': 'mingw64',
            'MSVC': 'msvc',
            'MinGW32': 'mingw32',
            'Clang': 'clang'
        }
        
        self.compiler_dropdown = QComboBox()
        self.compiler_dropdown.addItems(self.compiler_mapping.keys())
        self.compiler_dropdown.currentTextChanged.connect(self.on_compiler_selected)
        compiler_layout.addWidget(self.compiler_dropdown)
        
        layout.addWidget(compiler_frame)
        
        # C Compiler dropdown styling
        self.compiler_dropdown.setFixedWidth(200)  # Set fixed width
        self.compiler_dropdown.setMaxVisibleItems(8)  # Show max 8 items in dropdown
        
        # Checkboxes
        checkboxes = ['enable_console', 'windows_uac_admin', 'windows_uac_uiaccess']
        for cb in checkboxes:
            checkbox = QCheckBox(self.translator(cb))
            checkbox.setChecked(self.options[cb])
            checkbox.stateChanged.connect(lambda state, opt=cb: self.update_option(opt, bool(state)))
            layout.addWidget(checkbox)
            self.widgets[cb] = checkbox
        
        # Special buttons
        self.create_file_selector(layout, "windows_icon", "*.ico")
        self.create_dir_selector(layout, "output_dir")

    def create_file_selector(self, layout, option_name, file_type):
        frame = QFrame()
        frame_layout = QHBoxLayout(frame)
        
        label = QLabel(self.translator(option_name))
        frame_layout.addWidget(label)
        self.widgets[option_name] = label
        
        entry = QLineEdit()
        path_key = f'{option_name}_path'
        entry.setText(self.options.get(path_key, ''))
        
        # Add placeholder text
        entry.setPlaceholderText(self.translator('select_file'))
        
        entry.textChanged.connect(lambda text: self.update_option(path_key, text))
        frame_layout.addWidget(entry)
        
        browse_btn = QPushButton("...")
        browse_btn.setFixedWidth(30)
        browse_btn.clicked.connect(lambda: self.browse_file(option_name, file_type))
        frame_layout.addWidget(browse_btn)
        
        # Store entry widget for later access
        self.widgets[f'{option_name}_entry'] = entry
        
        layout.addWidget(frame)

    def create_dir_selector(self, layout, option_name):
        frame = QFrame()
        frame_layout = QHBoxLayout(frame)
        
        label = QLabel(self.translator(option_name))
        frame_layout.addWidget(label)
        self.widgets[option_name] = label
        
        entry = QLineEdit()
        entry.setText(self.options.get(option_name, ''))
        
        # Add placeholder text
        entry.setPlaceholderText(self.translator('select_file'))
        
        entry.textChanged.connect(lambda text: self.update_option(option_name, text))
        frame_layout.addWidget(entry)
        
        browse_btn = QPushButton("...")
        browse_btn.setFixedWidth(30)
        browse_btn.clicked.connect(lambda: self.browse_dir(option_name))
        frame_layout.addWidget(browse_btn)
        
        # Store entry widget for later access
        self.widgets[f'{option_name}_entry'] = entry
        
        layout.addWidget(frame)

    def browse_file(self, option_name, file_type):
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self,
                self.translator(option_name),
                "",
                f"{option_name} files ({file_type});;All files (*.*)"
            )
            if filename:
                path_key = f'{option_name}_path'
                self.update_option(path_key, filename)
                # Update entry widget if it exists
                if path_key in self.widgets:
                    self.widgets[path_key].setText(filename)
        except Exception as e:
            print(f"Error in browse_file: {e}")

    def browse_dir(self, option_name):
        try:
            dirname = QFileDialog.getExistingDirectory(
                self,
                self.translator(option_name),
                ""
            )
            if dirname:
                self.update_option(option_name, dirname)
                # Update entry widget if it exists
                if f'{option_name}_entry' in self.widgets:
                    self.widgets[f'{option_name}_entry'].setText(dirname)
        except Exception as e:
            print(f"Error in browse_dir: {e}")

    def update_option(self, option, value):
        """Safely update option value"""
        try:
            self.options[option] = value
        except Exception as e:
            print(f"Error updating option {option}: {e}")

    def on_flag_selected(self, display_text):
        """Handle flag selection from dropdown"""
        if display_text in self.current_flag_mapping:
            self.update_option('python_flag', self.current_flag_mapping[display_text])

    def on_compiler_selected(self, display_text):
        """Handle C compiler selection from dropdown"""
        if display_text in self.compiler_mapping:
            self.update_option('c_compiler', self.compiler_mapping[display_text])

    def update_translations(self, current_language):
        """Update translations for all widgets in the frame"""
        try:
            # Update labels and checkboxes
            for widget_name, widget in self.widgets.items():
                if isinstance(widget, (QLabel, QCheckBox)):
                    widget.setText(self.translator(widget_name))
                elif isinstance(widget, QLineEdit):
                    # Update placeholders for file/dir selectors
                    if widget_name.endswith('_entry'):
                        widget.setPlaceholderText(self.translator('select_file'))
            
            # Update Python flag dropdown
            if self.flag_dropdown:
                current_value = self.options.get('python_flag', '')
                self.safe_disconnect(self.flag_dropdown)
                localized_flags = self.get_localized_flags()
                self.flag_dropdown.clear()
                self.flag_dropdown.addItems(localized_flags.keys())
                
                # Find and set the current value
                current_text = next(
                    (k for k, v in localized_flags.items() if v == current_value),
                    list(localized_flags.keys())[0]
                )
                self.flag_dropdown.setCurrentText(current_text)
                
        except Exception as e:
            print(f"Error updating translations: {e}")