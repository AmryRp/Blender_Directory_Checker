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
                print(file_info)
                json_file_info = eval(file_info[1])
                self.table.setColumnCount(len(json_file_info.keys()))
                self.table.setHorizontalHeaderLabels(json_file_info.keys())
                for idx,data in enumerate(json_file_info.keys()):
                    self.table.setItem(row, idx, QTableWidgetItem(str(json_file_info.get(data))))
                # print(json_file_info)
                # file_name = json_file_info.get("Scene")
                # scenes = json_file_info.get("Scene")
                # render_samples = str(json_file_info.get("Render_Samples"))

                # self.table.setItem(row, 0, QTableWidgetItem(file_name))
                # self.table.setItem(row, 1, QTableWidgetItem(scenes))
                # self.table.setItem(row, 2, QTableWidgetItem(""))
                # self.table.setItem(row, 3, QTableWidgetItem(render_samples))
            else:
                self.table.setItem(row, 0, QTableWidgetItem(blend_file))
                self.table.setItem(row, 1, QTableWidgetItem(f"Error: {result.stderr}"))
                self.table.setItem(row, 2, QTableWidgetItem(""))
                self.table.setItem(row, 3, QTableWidgetItem(""))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    explorer = BlenderDirectoryExplorer()
    explorer.show()
    sys.exit(app.exec())
