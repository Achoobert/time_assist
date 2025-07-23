# there should be a pyQT dashboard that has these panels
# Display open issues, PRS, reviews, etc. 
# display logged work for current day from text file, with button to copy to clipboard
#  select options, and text Field to input new work-log. Reload ui on save
# button to  refresh github data, link to context.yml dashboards

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QLineEdit, QTabWidget, QMessageBox
)
from PyQt5.QtCore import Qt
import os

# Placeholder functions for data

def get_github_data():
    # TODO: Replace with real data loading
    return {
        'issues': ['Issue 1', 'Issue 2'],
        'prs': ['PR 1', 'PR 2'],
        'reviews': ['Review 1'],
    }

def get_today_worklog():
    # TODO: Replace with real file reading
    return "Sample work log for today."

def save_worklog_entry(entry):
    # TODO: Replace with real file writing
    print(f"Saving worklog entry: {entry}")
    return True

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Standup Reporter Dashboard')
        self.resize(800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # GitHub Data Panel
        github_data = get_github_data()
        github_panel = QTabWidget()
        for key, items in github_data.items():
            tab = QWidget()
            tab_layout = QVBoxLayout()
            for item in items:
                tab_layout.addWidget(QLabel(item))
            tab.setLayout(tab_layout)
            github_panel.addTab(tab, key.capitalize())
        layout.addWidget(github_panel)

        # Worklog Panel
        worklog_layout = QVBoxLayout()
        worklog_label = QLabel('Today\'s Work Log:')
        self.worklog_text = QTextEdit()
        self.worklog_text.setReadOnly(True)
        self.worklog_text.setText(get_today_worklog())
        copy_btn = QPushButton('Copy to Clipboard')
        copy_btn.clicked.connect(self.copy_worklog)
        worklog_layout.addWidget(worklog_label)
        worklog_layout.addWidget(self.worklog_text)
        worklog_layout.addWidget(copy_btn)
        layout.addLayout(worklog_layout)

        # New Worklog Entry
        entry_layout = QHBoxLayout()
        self.entry_field = QLineEdit()
        self.entry_field.setPlaceholderText('Enter new work-log entry...')
        save_btn = QPushButton('Save Entry')
        save_btn.clicked.connect(self.save_entry)
        entry_layout.addWidget(self.entry_field)
        entry_layout.addWidget(save_btn)
        layout.addLayout(entry_layout)

        # Refresh and context.yml link
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton('Refresh GitHub Data')
        refresh_btn.clicked.connect(self.refresh_github_data)
        context_btn = QPushButton('Open context.yml')
        context_btn.clicked.connect(self.open_context_yml)
        btn_layout.addWidget(refresh_btn)
        btn_layout.addWidget(context_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def copy_worklog(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.worklog_text.toPlainText())
        QMessageBox.information(self, 'Copied', 'Work log copied to clipboard!')

    def save_entry(self):
        entry = self.entry_field.text().strip()
        if entry:
            if save_worklog_entry(entry):
                QMessageBox.information(self, 'Saved', 'Entry saved!')
                self.entry_field.clear()
                self.worklog_text.setText(get_today_worklog())
            else:
                QMessageBox.warning(self, 'Error', 'Failed to save entry.')
        else:
            QMessageBox.warning(self, 'Empty', 'Please enter some text.')

    def refresh_github_data(self):
        # TODO: Implement real refresh logic
        QMessageBox.information(self, 'Refreshed', 'GitHub data refreshed (placeholder).')

    def open_context_yml(self):
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../context.yml'))
        if os.path.exists(path):
            os.system(f'open "{path}"')
        else:
            QMessageBox.warning(self, 'Not found', 'context.yml not found.')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec_())
