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
        self.create_widgets()

    def get_localized_flags(self):
        """Get the Python flags with localized descriptions"""
        self.current_flag_mapping = {
            self.translator("flag_no_opt"): "-O0",
            self.translator("flag_basic_opt"): "-O1",
            self.translator("flag_extra_opt"): "-O2",
            self.translator("flag_no_assert"): "-OO",
            self.translator("flag_no_docstring"): "-OO",
            self.translator("flag_no_bytecode"): "-B",
            self.translator("flag_debug"): "-d",
            self.translator("flag_verbose"): "-v"
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
        fields = ['company_name', 'product_name', 'file_version', 'include_package']
        
        for field in fields:
            label = QLabel(self.translator(field))
            layout.addWidget(label)
            self.widgets[field] = label
            
            entry = QLineEdit()
            entry.setText(self.options[field])
            entry.textChanged.connect(lambda text, f=field: self.update_option(f, text))
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
        entry.setText(self.options[f'{option_name}_path'])
        entry.textChanged.connect(lambda text: self.update_option(f'{option_name}_path', text))
        frame_layout.addWidget(entry)
        
        browse_btn = QPushButton("...")
        browse_btn.setFixedWidth(30)
        browse_btn.clicked.connect(lambda: self.browse_file(option_name, file_type))
        frame_layout.addWidget(browse_btn)
        
        layout.addWidget(frame)

    def create_dir_selector(self, layout, option_name):
        frame = QFrame()
        frame_layout = QHBoxLayout(frame)
        
        label = QLabel(self.translator(option_name))
        frame_layout.addWidget(label)
        self.widgets[option_name] = label
        
        entry = QLineEdit()
        entry.setText(self.options[option_name])
        entry.textChanged.connect(lambda text: self.update_option(option_name, text))
        frame_layout.addWidget(entry)
        
        browse_btn = QPushButton("...")
        browse_btn.setFixedWidth(30)
        browse_btn.clicked.connect(lambda: self.browse_dir(option_name))
        frame_layout.addWidget(browse_btn)
        
        layout.addWidget(frame)

    def browse_file(self, option_name, file_type):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.translator(option_name),
            "",
            f"{option_name} files ({file_type});;All files (*.*)"
        )
        if filename:
            self.update_option(f'{option_name}_path', filename)

    def browse_dir(self, option_name):
        dirname = QFileDialog.getExistingDirectory(self)
        if dirname:
            self.update_option(option_name, dirname)

    def update_option(self, option, value):
        self.options[option] = value

    def on_flag_selected(self, display_text):
        """Handle flag selection from dropdown"""
        if display_text in self.current_flag_mapping:
            self.update_option('python_flag', self.current_flag_mapping[display_text])

    def update_translations(self, current_language):
        """Update translations for all widgets in the frame"""
        for widget_name, widget in self.widgets.items():
            if isinstance(widget, (QLabel, QCheckBox)):
                widget.setText(self.translator(widget_name))
        
        if self.flag_dropdown:
            current_value = self.flag_dropdown.currentText()
            localized_flags = self.get_localized_flags()
            self.flag_dropdown.clear()
            self.flag_dropdown.addItems(localized_flags.keys())
            self.flag_dropdown.setCurrentText(self.translator("flag_no_opt"))
            self.update_option('python_flag', self.current_flag_mapping[self.translator("flag_no_opt")])