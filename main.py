"""
BFF Fabric Flattener
A Windows GUI tool for flattening 3D models using Boundary First Flattening
for 3D printing on stretchable fabrics.
"""

import sys
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QTextEdit, QGroupBox,
    QProgressBar, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,
    QMessageBox, QTabWidget, QFormLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextCursor, QIcon


class BFFProcessor(QThread):
    """Background thread for running BFF processing"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, input_file: str, output_file: str, options: dict):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.options = options
        self.bff_executable = self._find_bff_executable()
    
    def _find_bff_executable(self) -> Optional[str]:
        """Locate BFF executable"""
        # Check bundled location
        if getattr(sys, 'frozen', False):
            app_path = Path(sys._MEIPASS)
        else:
            app_path = Path(__file__).parent
        
        bff_path = app_path / "bff" / "bff-command-line.exe"
        if bff_path.exists():
            return str(bff_path)
        
        # Check PATH
        from shutil import which
        bff_in_path = which("bff-command-line")
        if bff_in_path:
            return bff_in_path
        
        return None
    
    def run(self):
        """Execute BFF processing"""
        if not self.bff_executable:
            self.finished.emit(False, "BFF executable not found. Please ensure bff-command-line.exe is in the 'bff' folder.")
            return
        
        try:
            # Build command
            cmd = [self.bff_executable, self.input_file, self.output_file]
            
            # Add options
            if self.options.get('auto_cut', True):
                cmd.append('--autoCut')
            
            if self.options.get('normalize', True):
                cmd.append('--normalize')
            
            if self.options.get('cone_singularities', False):
                cmd.extend(['--nCones', str(self.options.get('num_cones', 8))])
            
            self.progress.emit(f"Running: {' '.join(cmd)}")
            
            # Execute BFF
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                self.progress.emit("BFF processing completed successfully!")
                
                # Convert to SVG if requested
                if self.options.get('export_svg', True):
                    self._convert_to_svg(self.output_file)
                
                self.finished.emit(True, "Processing completed successfully!")
            else:
                error_msg = f"BFF failed:\n{result.stderr}"
                self.progress.emit(error_msg)
                self.finished.emit(False, error_msg)
                
        except Exception as e:
            error_msg = f"Error during processing: {str(e)}"
            self.progress.emit(error_msg)
            self.finished.emit(False, error_msg)
    
    def _convert_to_svg(self, obj_file: str):
        """Convert OBJ texture coordinates to SVG"""
        try:
            self.progress.emit("Converting to SVG...")
            svg_file = obj_file.rsplit('.', 1)[0] + '.svg'
            
            # Parse OBJ file for texture coordinates
            vertices = []
            faces = []
            
            with open(obj_file, 'r') as f:
                for line in f:
                    if line.startswith('vt '):
                        # Texture coordinate
                        parts = line.strip().split()
                        u, v = float(parts[1]), float(parts[2])
                        vertices.append((u, v))
                    elif line.startswith('f '):
                        # Face (we need texture coordinate indices)
                        parts = line.strip().split()[1:]
                        face_verts = []
                        for part in parts:
                            # Format: v/vt/vn or v/vt or just v
                            indices = part.split('/')
                            if len(indices) >= 2 and indices[1]:
                                vt_idx = int(indices[1]) - 1  # OBJ is 1-indexed
                                face_verts.append(vt_idx)
                        if face_verts:
                            faces.append(face_verts)
            
            if not vertices:
                self.progress.emit("No texture coordinates found in output")
                return
            
            # Calculate bounds
            min_u = min(v[0] for v in vertices)
            max_u = max(v[0] for v in vertices)
            min_v = min(v[1] for v in vertices)
            max_v = max(v[1] for v in vertices)
            
            # SVG parameters
            padding = 10
            scale = 500
            width = (max_u - min_u) * scale + 2 * padding
            height = (max_v - min_v) * scale + 2 * padding
            
            # Create SVG
            svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<g id="flattened-mesh" stroke="black" stroke-width="0.5" fill="none">
'''
            
            # Draw faces
            for face in faces:
                if len(face) < 3:
                    continue
                points = []
                for idx in face:
                    if 0 <= idx < len(vertices):
                        u, v = vertices[idx]
                        x = (u - min_u) * scale + padding
                        y = (max_v - v) * scale + padding  # Flip V
                        points.append(f"{x:.2f},{y:.2f}")
                
                if points:
                    points_str = " ".join(points)
                    svg_content += f'  <polygon points="{points_str}" />\n'
            
            svg_content += '''</g>
</svg>'''
            
            with open(svg_file, 'w') as f:
                f.write(svg_content)
            
            self.progress.emit(f"SVG exported: {svg_file}")
            
        except Exception as e:
            self.progress.emit(f"SVG conversion warning: {str(e)}")


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.input_file = None
        self.output_file = None
        self.processor = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("BFF Fabric Flattener")
        self.setMinimumSize(800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Boundary First Flattening for Fabric 3D Printing")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Tabs
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Input/Output tab
        io_tab = self._create_io_tab()
        tabs.addTab(io_tab, "Input/Output")
        
        # Options tab
        options_tab = self._create_options_tab()
        tabs.addTab(options_tab, "Options")
        
        # Log output
        log_group = QGroupBox("Processing Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Process button
        self.process_btn = QPushButton("Process Model")
        self.process_btn.setMinimumHeight(40)
        self.process_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.process_btn.clicked.connect(self.process_model)
        layout.addWidget(self.process_btn)
        
        self.log("Ready. Load a 3D model (OBJ format) to begin.")
    
    def _create_io_tab(self) -> QWidget:
        """Create input/output tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Input file
        input_group = QGroupBox("Input 3D Model")
        input_layout = QVBoxLayout()
        
        input_btn_layout = QHBoxLayout()
        self.input_label = QLabel("No file selected")
        self.input_label.setWordWrap(True)
        input_btn_layout.addWidget(self.input_label, 1)
        
        input_btn = QPushButton("Browse...")
        input_btn.clicked.connect(self.select_input_file)
        input_btn_layout.addWidget(input_btn)
        
        input_layout.addLayout(input_btn_layout)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Output file
        output_group = QGroupBox("Output Location")
        output_layout = QVBoxLayout()
        
        output_btn_layout = QHBoxLayout()
        self.output_label = QLabel("Will be set automatically")
        self.output_label.setWordWrap(True)
        output_btn_layout.addWidget(self.output_label, 1)
        
        output_btn = QPushButton("Browse...")
        output_btn.clicked.connect(self.select_output_file)
        output_btn_layout.addWidget(output_btn)
        
        output_layout.addLayout(output_btn_layout)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        layout.addStretch()
        return widget
    
    def _create_options_tab(self) -> QWidget:
        """Create options tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Auto-cut option
        self.auto_cut_cb = QCheckBox()
        self.auto_cut_cb.setChecked(True)
        self.auto_cut_cb.setToolTip("Automatically cut mesh if topology is not disk-like")
        layout.addRow("Auto-cut mesh:", self.auto_cut_cb)
        
        # Normalize option
        self.normalize_cb = QCheckBox()
        self.normalize_cb.setChecked(True)
        self.normalize_cb.setToolTip("Normalize output to unit square")
        layout.addRow("Normalize output:", self.normalize_cb)
        
        # Cone singularities
        self.cone_cb = QCheckBox()
        self.cone_cb.setChecked(False)
        self.cone_cb.setToolTip("Use cone singularities to reduce area distortion")
        layout.addRow("Use cone singularities:", self.cone_cb)
        
        self.num_cones_spin = QSpinBox()
        self.num_cones_spin.setRange(1, 20)
        self.num_cones_spin.setValue(8)
        self.num_cones_spin.setEnabled(False)
        self.cone_cb.toggled.connect(self.num_cones_spin.setEnabled)
        layout.addRow("Number of cones:", self.num_cones_spin)
        
        # Export SVG
        self.svg_cb = QCheckBox()
        self.svg_cb.setChecked(True)
        self.svg_cb.setToolTip("Export flattened pattern as SVG vector file")
        layout.addRow("Export SVG:", self.svg_cb)
        
        return widget
    
    def select_input_file(self):
        """Select input 3D model file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select 3D Model",
            "",
            "3D Models (*.obj);;All Files (*)"
        )
        
        if file_path:
            self.input_file = file_path
            self.input_label.setText(file_path)
            
            # Auto-set output file
            if not self.output_file:
                output_path = file_path.rsplit('.', 1)[0] + '_flattened.obj'
                self.output_file = output_path
                self.output_label.setText(output_path)
            
            self.log(f"Input file selected: {file_path}")
    
    def select_output_file(self):
        """Select output file location"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Flattened Model",
            self.output_file or "flattened.obj",
            "OBJ Files (*.obj);;All Files (*)"
        )
        
        if file_path:
            self.output_file = file_path
            self.output_label.setText(file_path)
            self.log(f"Output file set: {file_path}")
    
    def process_model(self):
        """Start model processing"""
        if not self.input_file:
            QMessageBox.warning(self, "No Input", "Please select an input 3D model first.")
            return
        
        if not self.output_file:
            QMessageBox.warning(self, "No Output", "Please specify an output location.")
            return
        
        # Gather options
        options = {
            'auto_cut': self.auto_cut_cb.isChecked(),
            'normalize': self.normalize_cb.isChecked(),
            'cone_singularities': self.cone_cb.isChecked(),
            'num_cones': self.num_cones_spin.value(),
            'export_svg': self.svg_cb.isChecked()
        }
        
        # Disable UI
        self.process_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        self.log("Starting processing...")
        
        # Start processing thread
        self.processor = BFFProcessor(self.input_file, self.output_file, options)
        self.processor.progress.connect(self.log)
        self.processor.finished.connect(self.on_processing_finished)
        self.processor.start()
    
    def on_processing_finished(self, success: bool, message: str):
        """Handle processing completion"""
        self.process_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.log("=" * 50)
            self.log("Processing complete!")
            
            # Offer to open output location
            reply = QMessageBox.question(
                self,
                "Open Output",
                "Would you like to open the output folder?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                import platform
                output_dir = os.path.dirname(self.output_file)
                if platform.system() == 'Windows':
                    os.startfile(output_dir)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', output_dir])
                else:  # Linux
                    subprocess.run(['xdg-open', output_dir])
        else:
            QMessageBox.critical(self, "Error", message)
    
    def log(self, message: str):
        """Add message to log"""
        self.log_text.append(message)
        self.log_text.moveCursor(QTextCursor.MoveOperation.End)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
