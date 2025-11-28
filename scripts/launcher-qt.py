#!/usr/bin/env python3
import sys
import subprocess
import os
import glob
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QPushButton, QLineEdit, QListWidget, 
                             QListWidgetItem)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QColor, QFont

class LauncherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.active_section = "APPS"
        self.init_data()
        self.init_ui()
        
    def init_data(self):
        self.data = {
            "CMD": [
                ("Terminal", "kitty"),
                ("Htop", "kitty -e htop"),
                ("Neofetch", "kitty -e neofetch"),
                ("File Manager", "thunar"),
                ("System Monitor", "kitty -e btop"),
            ],
            "SHORTCUT": [
                ("Lock Screen", "hyprlock"),
                ("Screenshot", "grim ~/Pictures/screenshot-$(date +%Y%m%d-%H%M%S).png"),
                ("Screenshot Area", "grim -g \"$(slurp)\" ~/Pictures/screenshot-$(date +%Y%m%d-%H%M%S).png"),
                ("Volume Up", "wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%+"),
                ("Volume Down", "wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"),
                ("Mute", "wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"),
            ],
            "APPS": self.get_applications(),
            "SITES": [
                ("YouTube", "xdg-open https://youtube.com"),
                ("GitHub", "xdg-open https://github.com"),
                ("Reddit", "xdg-open https://reddit.com"),
                ("Gmail", "xdg-open https://gmail.com"),
                ("Twitter", "xdg-open https://twitter.com"),
                ("Wikipedia", "xdg-open https://wikipedia.org"),
            ]
        }
    
    def get_applications(self):
        apps = []
        desktop_dirs = [
            '/usr/share/applications',
            '/usr/local/share/applications',
            os.path.expanduser('~/.local/share/applications')
        ]
        
        seen = set()
        
        for desktop_dir in desktop_dirs:
            if not os.path.exists(desktop_dir):
                continue
            
            for filepath in glob.glob(f'{desktop_dir}/*.desktop'):
                filename = os.path.basename(filepath)
                if filename in seen:
                    continue
                seen.add(filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        name = None
                        exec_cmd = None
                        no_display = False
                        
                        for line in f:
                            line = line.strip()
                            if line.startswith('Name=') and not name:
                                name = line.split('=', 1)[1]
                            elif line.startswith('Exec='):
                                exec_cmd = line.split('=', 1)[1]
                                for code in ['%U', '%F', '%u', '%f', '%i', '%c', '%k']:
                                    exec_cmd = exec_cmd.replace(code, '')
                                exec_cmd = exec_cmd.strip()
                            elif line.startswith('NoDisplay=true'):
                                no_display = True
                                break
                        
                        if name and exec_cmd and not no_display:
                            apps.append((name, exec_cmd))
                except:
                    pass
        
        return sorted(apps, key=lambda x: x[0].lower())
    
    def init_ui(self):
        self.setWindowTitle("Launcher")
        self.setFixedSize(800, 600)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # Set window background
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main vertical layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central.setLayout(main_layout)
        
        # Search box at the very top (full width)
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(f"Search {self.active_section}...")
        self.search_box.setFixedHeight(60)
        self.search_box.textChanged.connect(self.update_results)
        self.search_box.returnPressed.connect(self.execute_first)
        main_layout.addWidget(self.search_box)
        
        # Horizontal layout for buttons and results
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Left panel - 2x2 grid of buttons
        left_widget = QWidget()
        left_widget.setFixedWidth(400)
        from PyQt5.QtWidgets import QGridLayout
        left_layout = QGridLayout()
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setHorizontalSpacing(10)
        left_layout.setVerticalSpacing(10)
        left_widget.setLayout(left_layout)
        
        # Section buttons in 2x2 grid
        self.section_buttons = {}
        sections = [
            ["APPS", "SHORTCUT"],
            ["CMD", "SITES"]
        ]
        
        for row_idx, row in enumerate(sections):
            for col_idx, section in enumerate(row):
                btn = QPushButton(section)
                btn.setFixedSize(175, 175)
                btn.clicked.connect(lambda checked, s=section: self.switch_section(s))
                left_layout.addWidget(btn, row_idx, col_idx)
                self.section_buttons[section] = btn
        
        # Right panel - results
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(0)
        right_widget.setLayout(right_layout)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self.on_item_clicked)
        self.results_list.itemActivated.connect(self.on_item_clicked)
        right_layout.addWidget(self.results_list)
        
        # Add panels to content layout
        content_layout.addWidget(left_widget)
        content_layout.addWidget(right_widget)
        
        # Add content layout to main layout
        main_layout.addLayout(content_layout)
        
        # Apply styles
        self.apply_styles()
        
        # Initial update
        self.update_results()
        
        # Focus search box
        QTimer.singleShot(100, self.search_box.setFocus)
    
    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
                border: 3px solid #ff0000;
            }
            QPushButton {
                background-color: #000000;
                color: #ff0000;
                border: 1px solid #ff0000;
                font-size: 18px;
                font-weight: bold;
                font-family: 'JetBrainsMono Nerd Font';
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 0.1);
            }
            QPushButton[active="true"] {
                background-color: rgba(255, 0, 0, 0.3);
                color: #ffffff;
            }
            QLineEdit {
                background-color: #141414;
                color: #ff0000;
                border: 2px solid #ff0000;
                border-radius: 5px;
                padding: 10px;
                font-size: 16px;
                font-family: 'JetBrainsMono Nerd Font';
            }
            QListWidget {
                background-color: #000000;
                border: none;
                outline: none;
            }
            QListWidget::item {
                background-color: #141414;
                color: #ffffff;
                border: 1px solid #ff0000;
                border-radius: 3px;
                padding: 12px;
                margin: 3px 0px;
                font-family: 'JetBrainsMono Nerd Font';
            }
            QListWidget::item:hover {
                background-color: rgba(255, 0, 0, 0.2);
            }
            QListWidget::item:selected {
                background-color: rgba(255, 0, 0, 0.4);
            }
            QScrollBar:vertical {
                background: #141414;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #ff0000;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Set active button
        for btn in self.section_buttons.values():
            btn.setProperty("active", "false")
        self.section_buttons[self.active_section].setProperty("active", "true")
        self.section_buttons[self.active_section].style().unpolish(self.section_buttons[self.active_section])
        self.section_buttons[self.active_section].style().polish(self.section_buttons[self.active_section])
    
    def switch_section(self, section):
        self.active_section = section
        self.search_box.setPlaceholderText(f"Search {section}...")
        self.search_box.clear()
        
        # Update button styles
        for s, btn in self.section_buttons.items():
            btn.setProperty("active", "true" if s == section else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        
        self.update_results()
    
    def update_results(self):
        self.results_list.clear()
        query = self.search_box.text().lower()
        
        items = self.data[self.active_section]
        if query:
            items = [item for item in items if query in item[0].lower()]
        
        for name, cmd in items:
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, cmd)
            self.results_list.addItem(item)
    
    def on_item_clicked(self, item):
        cmd = item.data(Qt.UserRole)
        self.execute_command(cmd)
    
    def execute_first(self):
        if self.results_list.count() > 0:
            item = self.results_list.item(0)
            cmd = item.data(Qt.UserRole)
            self.execute_command(cmd)
    
    def execute_command(self, cmd):
        try:
            subprocess.Popen(cmd, shell=True, start_new_session=True)
            self.close()
        except Exception as e:
            print(f"Error: {e}")
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LauncherWindow()
    window.show()
    sys.exit(app.exec_())
