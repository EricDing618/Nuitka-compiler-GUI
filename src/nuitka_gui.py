from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QCheckBox, QLineEdit, QFileDialog,
                            QProgressBar, QTextEdit, QScrollArea, QFrame,
                            QMessageBox, QComboBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from src.config import (DEFAULT_WINDOW_SIZE, DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES,
                       load_translations)
from src.compiler import NuitkaCompiler
from src.gui_components import AdvancedOptionsFrame

class CompilerThread(QThread):
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    progress_signal = pyqtSignal()

    def __init__(self, file_path, options):
        super().__init__()
        self.file_path = file_path
        self.options = options

    def run(self):
        try:
            success, error = NuitkaCompiler.compile(
                self.file_path,
                self.options,
                lambda x: self.output_signal.emit(x),
                lambda: self.progress_signal.emit()
            )
            self.finished_signal.emit(success, error)
        except Exception as e:
            self.finished_signal.emit(False, str(e))

class NuitkaGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_window()
        self.widgets = {}
        self.options = {}
        self.translatable_widgets = {}
        self.is_compiling = False
        self.load_translations()
        self.create_widgets()
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QFrame {
                background-color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #0078D4;
                color: white;
                border-radius: 3px;
                padding: 5px 15px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #1084D9;
            }
            QPushButton:pressed {
                background-color: #006CBD;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                min-height: 25px;
            }
            QCheckBox {
                spacing: 8px;
            }
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 3px;
                text-align: center;
                min-height: 20px;
            }
            QProgressBar::chunk {
                background-color: #0078D4;
            }
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
    def setup_window(self):
        self.setWindowTitle("Nuitka GUI Compiler")
        width, height = map(int, DEFAULT_WINDOW_SIZE.split('x'))
        self.resize(width, height)
        self.setMinimumSize(800, 600)
        
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

    def load_translations(self):
        try:
            self.translations = load_translations()
            self.current_language = DEFAULT_LANGUAGE
        except FileNotFoundError as e:
            QMessageBox.critical(self, "Error", str(e))
            self.close()
            
    def create_widgets(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        scroll_layout.setSpacing(20)
        
        # Create sections with localized titles
        sections = [
            ("language_selection", self.create_language_selection),
            ("file_selection", self.create_file_selection),
            ("basic_options", self.create_basic_options),
            ("advanced_options", self.create_advanced_options),
            ("compilation", self.create_compile_section),
            ("output", self.create_output_section)
        ]
        
        for section_key, section_creator in sections:
            section_frame = QFrame()
            section_frame.setObjectName("section-frame")
            section_layout = QVBoxLayout(section_frame)
            
            # Add localized section title
            title_label = QLabel(self.translate(section_key))
            title_label.setObjectName("section-title")
            title_label.setStyleSheet("""
                QLabel#section-title {
                    font-size: 14px;
                    font-weight: bold;
                    color: #333;
                    padding: 5px;
                    border-bottom: 1px solid #ddd;
                    margin-bottom: 5px;
                }
            """)
            section_layout.addWidget(title_label)
            self.translatable_widgets[section_key] = title_label
            
            # Add section content
            content = section_creator()
            section_layout.addWidget(content)
            
            scroll_layout.addWidget(section_frame)
        
        scroll.setWidget(scroll_widget)
        self.main_layout.addWidget(scroll)

    def create_language_selection(self):
        container = QFrame()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 5, 10, 5)
        
        for lang_code, lang_name in SUPPORTED_LANGUAGES.items():
            btn = QPushButton(lang_name)
            btn.clicked.connect(lambda checked, l=lang_code: self.change_language(l))
            btn.setFixedWidth(100)
            if lang_code == self.current_language:
                btn.setStyleSheet("""
                    background-color: #005A9E;
                    font-weight: bold;
                """)
            layout.addWidget(btn)
            self.widgets[f"lang_{lang_code}"] = btn
            
        layout.addStretch()
        return container

    def create_file_selection(self):
        container = QFrame()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 5, 10, 5)
        
        self.file_path = QLineEdit()
        self.file_path.setPlaceholderText(self.translate("select_file"))
        layout.addWidget(self.file_path)
        
        browse_btn = QPushButton("...")
        browse_btn.setFixedWidth(30)
        browse_btn.clicked.connect(self.browse_file)
        layout.addWidget(browse_btn)
        
        return container

    def create_basic_options(self):
        container = QFrame()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 5, 10, 5)
        
        options_frame = QFrame()
        options_layout = QHBoxLayout(options_frame)
        
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        
        # Initialize basic options
        self.options.update({
            'standalone': False,
            'onefile': False,
            'remove_output': False,
            'follow_imports': False,
            'show_progress': False,
            'show_memory': False
        })
        
        # Left column options
        for option in ['standalone', 'onefile', 'remove_output']:
            cb = QCheckBox(self.translate(option))
            cb.setChecked(self.options[option])
            cb.stateChanged.connect(lambda state, opt=option: self.update_option(opt, bool(state)))
            left_layout.addWidget(cb)
            self.translatable_widgets[option] = cb
            
            # Add tooltip
            if f"tooltip_{option}" in self.translations[self.current_language]:
                cb.setToolTip(self.translate(f"tooltip_{option}"))
        
        # Right column options
        for option in ['follow_imports', 'show_progress', 'show_memory']:
            cb = QCheckBox(self.translate(option))
            cb.setChecked(self.options[option])
            cb.stateChanged.connect(lambda state, opt=option: self.update_option(opt, bool(state)))
            right_layout.addWidget(cb)
            self.translatable_widgets[option] = cb
            
            # Add tooltip
            if f"tooltip_{option}" in self.translations[self.current_language]:
                cb.setToolTip(self.translate(f"tooltip_{option}"))
        
        options_layout.addWidget(left_frame)
        options_layout.addWidget(right_frame)
        layout.addWidget(options_frame)
        
        return container

    def create_advanced_options(self):
        # Initialize advanced options
        self.options.update({
            'enable_console': True,
            'windows_uac_admin': False,
            'windows_uac_uiaccess': False,
            'windows_icon_path': '',
            'company_name': '',
            'product_name': '',
            'file_version': '',
            'output_dir': '',
            'python_flag': '',
            'include_package': '',
            'include_module': ''
        })
        
        container = QFrame()
        layout = QVBoxLayout(container)
        
        self.advanced_frame = AdvancedOptionsFrame(container, self.translate, self.options)
        layout.addWidget(self.advanced_frame)
        
        return container

    def create_compile_section(self):
        container = QFrame()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 5, 10, 5)
        
        self.compile_btn = QPushButton(self.translate("compile"))
        self.compile_btn.setStyleSheet("""
            QPushButton {
                background-color: #107C10;
                font-size: 14px;
                font-weight: bold;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #138513;
            }
            QPushButton:pressed {
                background-color: #0E6A0E;
            }
        """)
        self.compile_btn.clicked.connect(self.compile)
        layout.addWidget(self.compile_btn)
        
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        
        return container

    def create_output_section(self):
        container = QFrame()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Remove redundant label since we have section title
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                font-family: Consolas, monospace;
                padding: 10px;
            }
        """)
        self.output_text.setMinimumHeight(200)
        layout.addWidget(self.output_text)
        
        return container

    def browse_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.translate("select_file"),
            "",
            "Python files (*.py);;All files (*.*)"
        )
        if filename:
            self.file_path.setText(filename)

    def update_option(self, option, value):
        self.options[option] = value

    def compile(self):
        if self.is_compiling:
            return
            
        if not self.file_path.text():
            QMessageBox.critical(
                self,
                self.translate("error"),
                self.translate("no_file_selected")
            )
            return
            
        self.is_compiling = True
        self.compile_btn.setEnabled(False)
        self.compile_btn.setText(self.translate("compilation_started"))
        self.progress.setRange(0, 0)  # Indeterminate progress
        self.output_text.clear()
        self.output_text.append(self.translate("compilation_started") + "\n")
        
        # Create and start compiler thread
        self.compiler_thread = CompilerThread(
            self.file_path.text(),
            self.options
        )
        self.compiler_thread.output_signal.connect(self.update_output)
        self.compiler_thread.finished_signal.connect(self.compilation_finished)
        self.compiler_thread.progress_signal.connect(self.update_progress)
        self.compiler_thread.start()

    def update_output(self, text):
        self.output_text.append(text)
        self.output_text.verticalScrollBar().setValue(
            self.output_text.verticalScrollBar().maximum()
        )

    def update_progress(self):
        # Called when progress signal is emitted
        pass

    def compilation_finished(self, success, error):
        self.is_compiling = False
        self.progress.setRange(0, 100)
        self.progress.setValue(100 if success else 0)
        self.compile_btn.setEnabled(True)
        self.compile_btn.setText(self.translate("compile"))
        
        if success:
            QMessageBox.information(
                self,
                self.translate("success"),
                self.translate("compilation_successful")
            )
        else:
            QMessageBox.critical(
                self,
                self.translate("error"),
                error or self.translate("compilation_failed")
            )

    def translate(self, key):
        return self.translations[self.current_language].get(key, key)
        
    def change_language(self, lang):
        old_lang = self.current_language
        self.current_language = lang
        self.update_translations()
        
        # Update window title
        self.setWindowTitle(f"Nuitka GUI - {SUPPORTED_LANGUAGES[lang]}")

    def update_translations(self):
        """Update all translatable widgets"""
        # Update section titles and other widgets
        for widget_name, widget in self.translatable_widgets.items():
            if isinstance(widget, (QLabel, QCheckBox, QPushButton)):
                widget.setText(self.translate(widget_name))
                
                # Update tooltips for checkboxes
                if isinstance(widget, QCheckBox) and f"tooltip_{widget_name}" in self.translations[self.current_language]:
                    widget.setToolTip(self.translate(f"tooltip_{widget_name}"))
        
        # Update file selection placeholder
        if hasattr(self, 'file_path'):
            self.file_path.setPlaceholderText(self.translate("select_file"))
        
        # Update compile button
        if hasattr(self, 'compile_btn'):
            self.compile_btn.setText(self.translate("compile"))
        
        # Update advanced options
        if hasattr(self, 'advanced_frame'):
            self.advanced_frame.update_translations(self.current_language)
        
        # Update language buttons
        for lang_code, btn in self.widgets.items():
            if lang_code.startswith("lang_"):
                code = lang_code.split("_")[1]
                if code == self.current_language:
                    btn.setStyleSheet("""
                        background-color: #005A9E;
                        font-weight: bold;
                    """)
                else:
                    btn.setStyleSheet("")

def main():
    from PyQt6.QtWidgets import QApplication
    import sys
    
    try:
        app = QApplication(sys.argv)
        window = NuitkaGUI()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        QMessageBox.critical(None, "Fatal Error", f"An unexpected error occurred: {str(e)}")