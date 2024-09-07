import sys
import os
import subprocess
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt

class BlenderDirectoryExplorer(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Blender Directory Explorer")
        self.setGeometry(300, 300, 800, 600)

        layout = QVBoxLayout()

        self.open_button = QPushButton("Open Directory", self)
        self.open_button.clicked.connect(self.open_directory_dialog)
        layout.addWidget(self.open_button)

        self.dir_label = QLabel("No directory selected", self)
        layout.addWidget(self.dir_label)

        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["File Name", "Scenes", "Objects", "Render Samples"])
        layout.addWidget(self.table)
        self.save_settings = {}
        
        # Signal to detect changes in the table cells
        self.table.itemChanged.connect(self.on_item_changed)
        self.setLayout(layout)

    def open_directory_dialog(self):
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Directory", ""
        )
        if dir_path:
            self.dir_label.setText(f"Selected directory: {dir_path}")
            self.load_blend_files_in_directory(dir_path)

    def load_blend_files_in_directory(self, dir_path):
        blend_files = [f for f in os.listdir(dir_path) if f.endswith(".blend")]
        if not blend_files:
            self.table.setRowCount(0)
            self.table.setHorizontalHeaderLabels(["File Name", "Scenes", "Objects", "Render Samples"])
            return

        self.table.setRowCount(len(blend_files))

        for row, blend_file in enumerate(blend_files):
            file_path = os.path.join(dir_path, blend_file)
            result = subprocess.run(
                ["python", "blender_loader.py", file_path],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                file_info = result.stdout.split('_Result')
                
            json_file_info = eval(file_info[1])
            self.table.setColumnCount(len(json_file_info.keys()) + 2)  # +2 for the buttons
            self.table.setHorizontalHeaderLabels(list(json_file_info.keys()) + ["","Save File"])
            file_name= json_file_info.get('FileName')
            self.save_settings[file_name] = json_file_info
            # Fill in the data from the JSON info
            for idx, data in enumerate(json_file_info.keys()):
                self.table.setItem(row, idx, QTableWidgetItem(str(json_file_info.get(data))))
            modified_blend_file_path = str(json_file_info.get('FilePath'))

            # Add the "Save File" button
            save_file_button = QPushButton("Save File", self)
            settings = self.save_settings[file_name]
            save_file_button.clicked.connect(lambda _, path=modified_blend_file_path, file_name=file_name: self.save_blend_file(path, file_name))
            self.table.setCellWidget(row, len(json_file_info.keys()) + 1, save_file_button)
            # print(eval(file_info[1]))
            if result.returncode != 0:
                save_file_button = QPushButton("Save File", self)
                save_file_button.setDisabled(True)
                self.table.setCellWidget(row, len(json_file_info.keys()) + 1, save_file_button)
            # print(self.save_settings)
        
    def on_item_changed(self, item):
        row = item.row()
        col = item.column()
        value = item.text()

        # Debugging information
        print(f"Item changed: Row {row}, Column {col}, New Value: {value}")

        # Ensure the row is valid and the table has items
        if row < 0 or col < 0 or row >= self.table.rowCount() or col >= self.table.columnCount():
            print(f"Invalid row or column index: Row {row}, Column {col}")
            return

        # Get the file name from column 0
        file_name_item = self.table.item(row, 1)
        if file_name_item:
            file_name = file_name_item.text()
            if file_name in self.save_settings:
                column_key = self.table.horizontalHeaderItem(col).text()
                if column_key in self.save_settings[file_name]:
                    self.save_settings[file_name][column_key] = value
                    # print(f"Updated {file_name} - {column_key}: {value}")
                else:
                    print(f"Column key {column_key} not found in save settings.")
            else:
                print(f"File name {file_name} not found in save settings.")
        else:
            print(f"File name item not found for row {row}.")

    def save_settings_button(self, row):
        # Get the data from the table and save the settings
        file_name_item = self.table.item(row, 0)  # Assuming the file name is in column 0
        if file_name_item:
            file_name = file_name_item.text()
            if file_name in self.save_settings:
                # Save settings for the corresponding file
                settings = self.save_settings[file_name]
                print(f"Saving settings for {file_name}: {settings}")        
                
    def save_blend_file(self, file_path, file_name):
        try:
            # Define a temporary file path for saving the modified .blend file
            settings = self.save_settings[file_name]
            print(settings)
            result = subprocess.run(
                ["python", "blender_save_script.py", str(settings)],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print(f"File saved to {file_path}")
            else:
                print(f"Error: {result.stderr}")
        except Exception as e:
            print(f"Failed to save Blender file: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    explorer = BlenderDirectoryExplorer()
    explorer.show()
    sys.exit(app.exec())
