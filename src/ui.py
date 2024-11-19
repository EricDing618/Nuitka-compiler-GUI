from PyQt6.QtWidgets import QPushButton

def create_theme_button(parent, translator=None):
    """Create and configure the theme toggle button"""
    theme_btn = QPushButton("🌙", parent)
    theme_btn.setFixedSize(30, 30)
    theme_btn.setStyleSheet("""
        QPushButton { 
            border-radius: 15px;
            font-size: 14px;
            padding: 0px;
        }
        QPushButton:hover {
            background-color: rgba(0, 120, 212, 0.1);
        }
    """)
    
    # Set tooltip based on language if translator is provided
    if translator:
        theme_btn.setToolTip(translator("switch_theme"))
    else:
        theme_btn.setToolTip("Switch Theme (Light/Dark)")
        
    return theme_btn

def get_theme_styles(is_dark: bool) -> str:
    """Get the stylesheet for the current theme"""
    if is_dark:
        return """
            QMainWindow { background-color: #1e1e1e; }
            QFrame { background-color: #2d2d2d; border-radius: 5px; padding: 5px; }
            QPushButton { background-color: #0078D4; color: white; border-radius: 3px; padding: 5px 15px; min-height: 25px; }
            QPushButton:hover { background-color: #1084D9; }
            QPushButton:pressed { background-color: #006CBD; }
            QLineEdit { padding: 5px; border: 1px solid #444; border-radius: 3px; min-height: 25px; background: #383838; color: #fff; }
            QCheckBox { spacing: 8px; color: #fff; }
            QProgressBar { border: 1px solid #444; border-radius: 3px; text-align: center; min-height: 20px; }
            QProgressBar::chunk { background-color: #0078D4; }
            QTextEdit { border: 1px solid #444; border-radius: 3px; background: #383838; color: #fff; }
            QScrollArea { border: none; background-color: transparent; }
            QLabel { color: #fff; }
            QComboBox { 
                background: #383838; 
                color: #fff; 
                border: 1px solid #444; 
                border-radius: 3px; 
                padding: 5px;
                min-height: 25px;
            }
            QComboBox:hover {
                border: 1px solid #666;
            }
            QComboBox:focus {
                border: 1px solid #0078D4;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow_white.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #383838;
                color: #fff;
                selection-background-color: #0078D4;
                selection-color: #fff;
                border: 1px solid #444;
                outline: none;
            }
            QMessageBox { background-color: #2d2d2d; color: #fff; }
            QMessageBox QLabel { color: #fff; }
            QMessageBox QPushButton { min-width: 80px; }
        """
    else:
        return """
            QMainWindow { background-color: #f0f0f0; }
            QFrame { background-color: white; border-radius: 5px; padding: 5px; }
            QPushButton { background-color: #0078D4; color: white; border-radius: 3px; padding: 5px 15px; min-height: 25px; }
            QPushButton:hover { background-color: #1084D9; }
            QPushButton:pressed { background-color: #006CBD; }
            QLineEdit { padding: 5px; border: 1px solid #ccc; border-radius: 3px; min-height: 25px; }
            QCheckBox { spacing: 8px; }
            QProgressBar { border: 1px solid #ccc; border-radius: 3px; text-align: center; min-height: 20px; }
            QProgressBar::chunk { background-color: #0078D4; }
            QTextEdit { border: 1px solid #ccc; border-radius: 3px; }
            QScrollArea { border: none; background-color: transparent; }
            QComboBox {
                background: white;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
                min-height: 25px;
            }
            QComboBox:hover {
                border: 1px solid #999;
            }
            QComboBox:focus {
                border: 1px solid #0078D4;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow_black.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                selection-background-color: #0078D4;
                selection-color: white;
                border: 1px solid #ccc;
                outline: none;
            }
            QMessageBox { background-color: #fff; }
            QMessageBox QPushButton { min-width: 80px; }
        """