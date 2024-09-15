import sys
import os
import subprocess
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, 
    QLabel, QTableWidget, QTableWidgetItem, QComboBox, QHBoxLayout
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import json

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
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Select", "File Name", "Scenes", "Objects", "Render Samples"])
        layout.addWidget(self.table)
        self.save_settings = {}
        
        # Create an HBoxLayout for the custom directory selection
        custom_dir_layout = QHBoxLayout()

        # Label to show selected custom directory
        self.custom_save_dir = QLabel("No directory selected", self)
        custom_dir_layout.addWidget(self.custom_save_dir)

        # Custom save directory button
        self.custom_dir_button = QPushButton("Select Custom Save Directory", self)
        self.custom_dir_button.clicked.connect(self.select_custom_directory)
        custom_dir_layout.addWidget(self.custom_dir_button)
        
        # Add the HBoxLayout (row) to the main vertical layout
        layout.addLayout(custom_dir_layout)
        
        # Batch save button
        self.batch_save_button = QPushButton("Batch Save Selected Files", self)
        self.batch_save_button.clicked.connect(self.batch_save_files)
        layout.addWidget(self.batch_save_button)
        
        # Signal to detect changes in the table cells
        self.table.itemChanged.connect(self.on_item_changed)
        self.setLayout(layout)

    def select_custom_directory(self):
        # Open a directory dialog to select the custom save directory
        selected_dir = QFileDialog.getExistingDirectory(self, "Select Save Directory", "")
        if selected_dir:
            self.custom_save_dir.setText(f"{selected_dir}")
    
    def batch_save_files(self):
        # Debug: Check if the custom save directory is selected
        if self.custom_save_dir.text() == "No directory selected":
            print("[DEBUG] No custom save directory selected.")
            return

        print(f"[DEBUG] Custom save directory: {self.custom_save_dir.text()}")

        # Iterate through the table rows to check for selected files
        for row in range(self.table.rowCount()):
            # Debug: Indicate which row is being processed
            print(f"[DEBUG] Processing row {row}")

            # Get the checkbox in the first column
            check_box = self.table.item(row, 0)
            if check_box is None:
                print(f"[DEBUG] No checkbox found in row {row}")
                continue
            
            # Debug: Check if the checkbox is checked
            if check_box.checkState() == Qt.Checked:
                print(f"[DEBUG] Checkbox in row {row} is checked.")
            else:
                print(f"[DEBUG] Checkbox in row {row} is not checked.")
                continue

            # Get the file name from the second column
            file_name_item = self.table.item(row, 2)
            if file_name_item is None:
                print(f"[DEBUG] No file name found in row {row}")
                continue

            file_name = file_name_item.text()
            print(f"[DEBUG] File name in row {row}: {file_name}")

            # Check if the file name exists in the save settings
            if file_name in self.save_settings:
                settings = self.save_settings[file_name]
                file_path = os.path.join(self.custom_save_dir.text(), file_name)
                
                # Debug: Show file path and settings being saved
                print(f"[DEBUG] Saving file {file_name} to {file_path} with settings: {settings}")
                self.save_blend_file(file_path, file_name)
            else:
                print(f"[DEBUG] No settings found for file {file_name}")


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
            self.table.setHorizontalHeaderLabels(["Select", "File Name", "Scenes", "Objects", "Render Samples"])
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
                preview_path = os.path.join(dir_path, f"{os.path.splitext(blend_file)[0]}.blend_thumbnail.png")
                # Generate thumbnail image
                
                try:
                    json_file_info = eval(file_info[1])
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {str(e)}")
                    continue
                self.table.setColumnCount(len(json_file_info.keys()) + 3)  # +2 for the buttons
                self.table.setHorizontalHeaderLabels(["Select",] +list(json_file_info.keys()) + ["Save File","Preview"])
                file_name= json_file_info.get('FileName')
                check_box = QTableWidgetItem()
                check_box.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                check_box.setCheckState(Qt.Unchecked)
                self.table.setItem(row, 0, check_box)
                self.save_settings[file_name] = json_file_info
                # Fill in the data from the JSON info
                for idx, data in enumerate(json_file_info.keys()):
                    value = json_file_info.get(data)

                    # Create a dropdown if the value is boolean (True/False)
                    if (value == "FFMPEG"):
                        combo_box = QComboBox()
                        combo_box.addItems(["FFMPEG", "PNG"])
                        combo_box.setCurrentText("FFMPEG" if value else "PNG")
                        combo_box.currentIndexChanged.connect(
                            lambda index, file_name=file_name, key=data: self.on_combo_box_format_changed(file_name, key, index)
                        )
                        self.table.setCellWidget(row, idx+1, combo_box)
                    if isinstance(value, bool):
                        combo_box = QComboBox()
                        combo_box.addItems(["True", "False"])
                        combo_box.setCurrentText("True" if value else "False")
                        combo_box.currentIndexChanged.connect(
                            lambda index, file_name=file_name, key=data: self.on_combo_box_changed(file_name, key, index)
                        )
                        self.table.setCellWidget(row, idx+1, combo_box)
                    else:
                        self.table.setItem(row, idx+1, QTableWidgetItem(str(value)))
                modified_blend_file_path = str(json_file_info.get('FilePath'))

                # Add the "Save File" button
                save_file_button = QPushButton("Save File", self)
                settings = self.save_settings[file_name]
                save_file_button.clicked.connect(lambda _, path=modified_blend_file_path, file_name=file_name: self.save_blend_file(path, file_name))
                self.table.setCellWidget(row, len(json_file_info.keys()) + 1, save_file_button)
                
                pix = self.generate_thumbnail(file_path, preview_path)
                preview_label = QLabel()
                preview_label.setPixmap(pix.scaled(64, 64, Qt.KeepAspectRatio))
                self.table.setCellWidget(row, len(json_file_info.keys()) + 2, preview_label)
                
            # print(eval(file_info[1]))
            if result.returncode != 0:
                save_file_button = QPushButton("Save File", self)
                save_file_button.setDisabled(True)
                self.table.setCellWidget(row, len(json_file_info.keys()) + 1, save_file_button)
            # print(self.save_settings)
    
    def on_combo_box_format_changed(self, file_name, key, index):
        # This function handles changes to the combo box (True/False dropdown)
        new_value = "FFMPEG" if index == 0 else "PNG"
        self.save_settings[file_name][key] = new_value
        print(f"Updated {file_name} - {key}: {new_value}")
    
    def on_combo_box_changed(self, file_name, key, index):
        # This function handles changes to the combo box (True/False dropdown)
        new_value = True if index == 0 else False
        self.save_settings[file_name][key] = new_value
        print(f"Updated {file_name} - {key}: {new_value}")
        
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
        file_name_item = self.table.item(row, 2)
        if file_name_item:
            file_name = file_name_item.text()
            if file_name in self.save_settings:
                column_key = self.table.horizontalHeaderItem(col).text()
                if column_key in self.save_settings[file_name]:
                    self.save_settings[file_name][column_key] = value
                    # print(f"Updated {file_name} - {column_key}: {value}")
        #         else:
        #             print(f"Column key {column_key} not found in save settings.")
        #     else:
        #         print(f"File name {file_name} not found in save settings.")
        # else:
        #     print(f"File name item not found for row {row}.")

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
                ["python", "blender_save_script.py",file_path, str(settings)],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print(f"File saved to {file_path}")
            else:
                print(f"Error: {result.stderr}")
        except Exception as e:
            print(f"Failed to save Blender file: {str(e)}")
            
    def generate_thumbnail(self, blend_file, preview_path):
        # Call the Blender script to generate a thumbnail
        if os.path.exists(preview_path):
            return QPixmap(preview_path)
        
        result = subprocess.run(
            ["python", "render_thumbnail.py", blend_file, os.path.dirname(preview_path)],
            check=True
        )
        # print(result)
        if os.path.exists(preview_path) and result.returncode == 0:
            return QPixmap(preview_path)
        else:
            raise FileNotFoundError(f"Thumbnail not found at {preview_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    explorer = BlenderDirectoryExplorer()
    explorer.show()
    sys.exit(app.exec())
