"""
Color input panel for manually setting cube colors.
"""

from typing import List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel, 
    QPushButton, QComboBox, QTextEdit, QButtonGroup, QMessageBox
)
from PySide6.QtCore import Signal, Qt, QSize, QPoint
from PySide6.QtGui import QPainter, QPen, QBrush, QColor
from ...core.cube_state import CubeState
from ...core.color_scheme import ColorScheme
from ...core.validators import validate_facelets, get_problematic_stickers


class CubePaintWidget(QWidget):
    """Clickable cube net widget for painting colors."""
    
    facelet_clicked = Signal(int)  # Emits facelet index when clicked
    
    def __init__(self, facelets: List[str], color_scheme: ColorScheme):
        super().__init__()
        self.facelets = facelets
        self.color_scheme = color_scheme
        self.sticker_size = 30  # Increased sticker size for better visibility
        self.gap = 3  # Increased gap for better separation
        
        # Face layout in net format
        # Net layout:     U
        #               L F R B
        #                 D
        self.face_positions = {
            'U': (1, 0),  # Up
            'L': (0, 1),  # Left
            'F': (1, 1),  # Front
            'R': (2, 1),  # Right
            'B': (3, 1),  # Back
            'D': (1, 2),  # Down
        }
        
        self.setMouseTracking(True)
        
    def paintEvent(self, event):
        """Paint the cube net with clickable stickers."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        face_order = ['U', 'R', 'F', 'D', 'L', 'B']
        
        # Calculate total dimensions for centering
        total_width = 4 * (3 * self.sticker_size + 2 * self.gap) + 3 * 10
        total_height = 3 * (3 * self.sticker_size + 2 * self.gap) + 2 * 10
        
        # Calculate offset to center the net in the widget
        widget_width = self.width()
        widget_height = self.height()
        offset_x = max(0, (widget_width - total_width) // 2)
        offset_y = max(0, (widget_height - total_height) // 2)
        
        for face_idx, face in enumerate(face_order):
            face_x, face_y = self.face_positions[face]
            
            # Calculate face position in pixels with centering offset
            face_pixel_x = offset_x + face_x * (3 * self.sticker_size + 2 * self.gap) + face_x * 10
            face_pixel_y = offset_y + face_y * (3 * self.sticker_size + 2 * self.gap) + face_y * 10
            
            # Draw 3x3 stickers for this face
            for row in range(3):
                for col in range(3):
                    sticker_idx = face_idx * 9 + row * 3 + col
                    
                    x = face_pixel_x + col * (self.sticker_size + self.gap)
                    y = face_pixel_y + row * (self.sticker_size + self.gap)
                    
                    # Get sticker color
                    color = QColor(self.facelets[sticker_idx])
                    
                    # Draw sticker with rounded corners for better appearance
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(color)
                    painter.drawRoundedRect(x, y, self.sticker_size, self.sticker_size, 3, 3)
                    
                    # Draw border
                    painter.setPen(QPen(QColor("#333333"), 1))
                    painter.setBrush(Qt.NoBrush)
                    painter.drawRoundedRect(x, y, self.sticker_size, self.sticker_size, 3, 3)
                    
                    # Draw facelet index for debugging (optional)
                    # painter.setPen(QPen(QColor("#000000"), 1))
                    # painter.setFont(QFont("Arial", 6))
                    # painter.drawText(x, y, self.sticker_size, self.sticker_size, Qt.AlignCenter, str(sticker_idx))
    
    def mousePressEvent(self, event):
        """Handle mouse clicks on stickers."""
        if event.button() == Qt.LeftButton:
            sticker_idx = self._get_sticker_at_position(event.position().toPoint())
            if sticker_idx >= 0:
                self.facelet_clicked.emit(sticker_idx)
    
    def _get_sticker_at_position(self, pos: QPoint) -> int:
        """Get sticker index at mouse position."""
        face_order = ['U', 'R', 'F', 'D', 'L', 'B']
        
        for face_idx, face in enumerate(face_order):
            face_x, face_y = self.face_positions[face]
            
            # Calculate face position in pixels
            face_pixel_x = face_x * (3 * self.sticker_size + 2 * self.gap) + face_x * 10
            face_pixel_y = face_y * (3 * self.sticker_size + 2 * self.gap) + face_y * 10
            
            # Check if click is within this face
            face_width = 3 * self.sticker_size + 2 * self.gap
            face_height = 3 * self.sticker_size + 2 * self.gap
            
            if (face_pixel_x <= pos.x() <= face_pixel_x + face_width and
                face_pixel_y <= pos.y() <= face_pixel_y + face_height):
                
                # Find which sticker within the face
                rel_x = pos.x() - face_pixel_x
                rel_y = pos.y() - face_pixel_y
                
                col = rel_x // (self.sticker_size + self.gap)
                row = rel_y // (self.sticker_size + self.gap)
                
                if 0 <= row < 3 and 0 <= col < 3:
                    return face_idx * 9 + row * 3 + col
        
        return -1  # No sticker found
    
    def update_facelets(self, facelets: List[str]):
        """Update facelet colors and repaint."""
        self.facelets = facelets
        self.update()
    
    def sizeHint(self):
        """Provide size hint for layout."""
        # Calculate the actual width and height needed for the net layout
        # Width: 4 faces + 3 gaps between faces + margins
        net_width = 4 * (3 * self.sticker_size + 2 * self.gap) + 3 * 10
        # Height: 3 faces + 2 gaps between faces + margins
        net_height = 3 * (3 * self.sticker_size + 2 * self.gap) + 2 * 10
        return QSize(net_width, net_height)


class ColorInputPanel(QWidget):
    """Panel for inputting cube colors manually."""
    
    # Signals
    cube_state_changed = Signal(CubeState)
    validation_requested = Signal()
    color_scheme_changed = Signal(ColorScheme)
    
    def __init__(self, parent=None) -> None:
        """Initialize the color input panel."""
        super().__init__(parent)
        
        # Cube state
        self.cube_state = CubeState.solved()
        self.facelets = self.cube_state.to_facelets(ColorScheme())
        self.color_scheme = ColorScheme()
        self.current_color = self.color_scheme.U  # Default to Up face color
        
        # Undo/Redo functionality
        self.undo_stack = []  # Stack to store previous states
        self.redo_stack = []  # Stack to store undone states
        
        # UI elements
        self.paint_widget = None
        self.paint_group = None
        self.text_group = None
        self.validation_label = None
        self.current_color_button = None
        self.color_buttons = {}
        
        # Input mode
        self.input_mode_group = None
        self.paint_mode_button = None
        self.text_mode_button = None
        self.three_d_mode_button = None
        
        # Text input
        self.text_input = None
        self.preset_combo = None
        
        self._setup_ui()
        self._setup_connections()
    
    def _setup_connections(self) -> None:
        """Set up signal connections for UI elements."""
        # Connect color palette buttons
        for face, button in self.color_buttons.items():
            # Use a closure to capture the face value
            def make_handler(f):
                return lambda: self._select_color(f)
            button.clicked.connect(make_handler(face))
        
        # Connect current color button
        if self.current_color_button:
            self.current_color_button.clicked.connect(lambda: self._on_color_selected(self.current_color))
        
        # Connect preset combo box
        if self.preset_combo:
            self.preset_combo.currentTextChanged.connect(self._on_preset_changed)
        
        # Connect input mode buttons
        if self.text_mode_button and self.paint_mode_button:
            self.text_mode_button.clicked.connect(lambda: self._on_input_mode_changed(self.text_mode_button))
            self.paint_mode_button.clicked.connect(lambda: self._on_input_mode_changed(self.paint_mode_button))
        
        # Connect text input elements
        if self.text_input and self.apply_text_button:
            self.apply_text_button.clicked.connect(self._apply_text_input)
            self.clear_text_button.clicked.connect(self._clear_text_input)
        
        # Connect validation buttons
        if self.validate_button:
            self.validate_button.clicked.connect(self._validate_cube)
        
        # Connect action buttons
        if self.reset_button:
            self.reset_button.clicked.connect(self._reset_to_solved)
        if self.random_button:
            self.random_button.clicked.connect(self._generate_random_colors)
        if self.undo_button:
            self.undo_button.clicked.connect(self.undo)
        if self.redo_button:
            self.redo_button.clicked.connect(self.redo)
        
        # Connect paint widget
        if self.paint_widget:
            self.paint_widget.facelet_clicked.connect(self._on_facelet_clicked)
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Color palette group
        self._create_color_palette_group(layout)
        
        # Input method selection
        self._create_input_method_group(layout)
        
        # Text input group
        self._create_text_input_group(layout)
        
        # Validation group
        self._create_validation_group(layout)
    
    def _create_color_palette_group(self, parent_layout: QVBoxLayout) -> None:
        """Create color palette selection group."""
        group = QGroupBox("Color Palette")
        layout = QVBoxLayout(group)
        
        # Current color scheme display
        scheme_layout = QGridLayout()
        
        self.color_buttons = {}
        faces = ['U', 'D', 'F', 'B', 'R', 'L']
        face_names = ['Up (White)', 'Down (Yellow)', 'Front (Green)', 
                     'Back (Blue)', 'Right (Red)', 'Left (Orange)']
        
        for i, (face, name) in enumerate(zip(faces, face_names)):
            # Color button
            color_button = QPushButton()
            color_button.setMinimumSize(30, 30)
            color_button.setMaximumSize(30, 30)
            self._update_color_button(color_button, getattr(self.color_scheme, face))
            color_button.clicked.connect(lambda checked, c=getattr(self.color_scheme, face): self._on_color_selected(c))
            self.color_buttons[face] = color_button
            
            # Label
            label = QLabel(name)
            
            row = i // 3
            col = (i % 3) * 2
            scheme_layout.addWidget(color_button, row, col)
            scheme_layout.addWidget(label, row, col + 1)
        
        layout.addLayout(scheme_layout)
        
        # Preset schemes
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Presets:"))
        
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["Default WCA", "Classic", "Pastel"])
        preset_layout.addWidget(self.preset_combo)
        
        reset_colors_button = QPushButton("Reset Colors")
        preset_layout.addWidget(reset_colors_button)
        preset_layout.addStretch()
        
        layout.addLayout(preset_layout)
        
        parent_layout.addWidget(group)
    
    def _create_input_method_group(self, parent_layout: QVBoxLayout) -> None:
        """Create input method selection group."""
        group = QGroupBox("Input Method")
        layout = QVBoxLayout(group)
        
        # Method selection
        method_layout = QHBoxLayout()
        
        self.paint_mode_button = QPushButton("🎨 2D Paint Mode")
        self.paint_mode_button.setCheckable(True)
        self.paint_mode_button.setChecked(True)
        method_layout.addWidget(self.paint_mode_button)
        
        self.text_mode_button = QPushButton("📝 Text Mode")
        self.text_mode_button.setCheckable(True)
        method_layout.addWidget(self.text_mode_button)
        
        self.three_d_mode_button = QPushButton("🧊 3D Mode")
        self.three_d_mode_button.setCheckable(True)
        method_layout.addWidget(self.three_d_mode_button)
        
        # Button group for exclusive selection
        self.input_mode_group = QButtonGroup()
        self.input_mode_group.addButton(self.paint_mode_button, 0)
        self.input_mode_group.addButton(self.text_mode_button, 1)
        self.input_mode_group.addButton(self.three_d_mode_button, 2)
        
        method_layout.addStretch()
        layout.addLayout(method_layout)
        
        # Current color indicator
        current_color_layout = QHBoxLayout()
        current_color_layout.addWidget(QLabel("Current Color:"))
        
        self.current_color_button = QPushButton()
        self.current_color_button.setMinimumSize(30, 30)
        self.current_color_button.setMaximumSize(30, 30)
        self._update_color_button(self.current_color_button, self.current_color)
        current_color_layout.addWidget(self.current_color_button)
        
        current_color_layout.addStretch()
        layout.addLayout(current_color_layout)
        
        # Paint widget (clickable cube net)
        self.paint_widget = CubePaintWidget(self.facelets, self.color_scheme)
        self.paint_widget.setMinimumSize(350, 300)  # Increased minimum size
        self.paint_widget.facelet_clicked.connect(self._on_facelet_clicked)
        layout.addWidget(self.paint_widget)
        
        parent_layout.addWidget(group)
    
    def _create_text_input_group(self, parent_layout: QVBoxLayout) -> None:
        """Create text input group."""
        self.text_group = QGroupBox("Text Input")
        layout = QVBoxLayout(self.text_group)
        
        # Instructions
        instructions = QLabel(
            "Enter 54 colors using letters: W(White), Y(Yellow), G(Green), B(Blue), R(Red), O(Orange)\n"
            "Order: U1-U9, R1-R9, F1-F9, D1-D9, L1-L9, B1-B9"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666666; font-size: 11px;")
        layout.addWidget(instructions)
        
        # Text input
        self.text_input = QTextEdit()
        self.text_input.setMaximumHeight(80)
        self.text_input.setPlaceholderText("UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB")
        layout.addWidget(self.text_input)
        
        # Text input buttons
        text_buttons_layout = QHBoxLayout()
        
        self.apply_text_button = QPushButton("Apply Text")
        text_buttons_layout.addWidget(self.apply_text_button)
        
        self.clear_text_button = QPushButton("Clear")
        text_buttons_layout.addWidget(self.clear_text_button)
        
        text_buttons_layout.addStretch()
        layout.addLayout(text_buttons_layout)
        
        parent_layout.addWidget(self.text_group)
    
    def _create_validation_group(self, parent_layout: QVBoxLayout) -> None:
        """Create validation group."""
        group = QGroupBox("Validation")
        layout = QVBoxLayout(group)
        
        # Validation status
        self.validation_label = QLabel("Status: Ready for validation")
        self.validation_label.setStyleSheet("color: #666666;")
        layout.addWidget(self.validation_label)
        
        # Validate button
        validate_layout = QHBoxLayout()
        
        self.validate_button = QPushButton("✓ Validate Cube")
        self.validate_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        validate_layout.addWidget(self.validate_button)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        self.reset_button = QPushButton("🔄 Reset to Solved")
        actions_layout.addWidget(self.reset_button)
        
        self.random_button = QPushButton("🎲 Random Colors")
        actions_layout.addWidget(self.random_button)
        
        # Add undo/redo buttons
        self.undo_button = QPushButton("↩ Undo")
        self.undo_button.setEnabled(False)  # Disabled by default
        actions_layout.addWidget(self.undo_button)
        
        self.redo_button = QPushButton("↪ Redo")
        self.redo_button.setEnabled(False)  # Disabled by default
        actions_layout.addWidget(self.redo_button)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        parent_layout.addWidget(group)
        
        # Apply styles to color buttons
        for button in self.color_buttons.values():
            button.setStyleSheet("""QPushButton {
                background-color: #f0f0f0;
                border: 2px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                border: 2px solid #999999;
            }
            """)
    
    def _select_color(self, face: str) -> None:
        """Select a color for painting."""
        self.current_color = getattr(self.color_scheme, face)
        self._update_color_button(self.current_color_button, self.current_color)
    
    def _on_preset_changed(self, preset_name: str) -> None:
        """Handle preset color scheme change."""
        if preset_name == "Default WCA":
            self.color_scheme = ColorScheme()
        elif preset_name == "Classic":
            from ...core.color_scheme import CLASSIC_SCHEME
            self.color_scheme = CLASSIC_SCHEME
        elif preset_name == "Pastel":
            from ...core.color_scheme import PASTEL_SCHEME
            self.color_scheme = PASTEL_SCHEME
        
        # Update color buttons
        for face, button in self.color_buttons.items():
            self._update_color_button(button, getattr(self.color_scheme, face))
        
        # Update current color
        self.current_color = self.color_scheme.U
        self._update_color_button(self.current_color_button, self.current_color)
        
        # Update cube display
        self._update_cube_state()
        
        self.color_scheme_changed.emit(self.color_scheme)
    
    def _on_input_mode_changed(self, button: QPushButton) -> None:
        """Handle input mode change."""
        # Enable/disable appropriate controls
        is_paint_mode = button == self.paint_mode_button
        is_text_mode = button == self.text_mode_button
        is_3d_mode = button == self.three_d_mode_button
        
        # Show/hide paint widget based on mode
        self.paint_widget.setVisible(is_paint_mode)
        
        # Show/hide text input based on mode
        self.text_group.setVisible(is_text_mode)
        
        # For 3D mode, we'll show instructions
        if is_3d_mode:
            # Hide paint widget in 3D mode
            self.paint_widget.setVisible(False)
            # Hide text input in 3D mode
            self.text_group.setVisible(False)
            # Show instructions for 3D mode
            self._show_3d_mode_instructions()
        
        # Update status message
        if is_paint_mode:
            self.validation_label.setText("Status: 2D Paint mode active. Click on stickers to color them.")
        elif is_text_mode:
            self.validation_label.setText("Status: Text mode active. Enter colors using letter notation.")
        elif is_3d_mode:
            self.validation_label.setText("Status: 3D mode active. Click on the 3D cube to color facelets.")
        
        self.validation_label.setStyleSheet("color: #007bff;")
    
    def _apply_text_input(self) -> None:
        """Apply text input to cube state."""
        text = self.text_input.toPlainText().strip().upper()
        
        if len(text) != 54:
            QMessageBox.warning(self, "Invalid Input", 
                              f"Expected 54 characters, got {len(text)}")
            return
        
        # Convert letter notation to hex colors
        try:
            facelets = self._convert_letters_to_colors(text)
            self.facelets = facelets
            self._update_cube_state()
            
            self.validation_label.setText("Status: Text input applied")
            self.validation_label.setStyleSheet("color: #28a745;")
            
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", str(e))
    
    def _convert_letters_to_colors(self, text: str) -> List[str]:
        """Convert letter notation to hex colors."""
        letter_to_color = {
            'W': self.color_scheme.U,  # White
            'Y': self.color_scheme.D,  # Yellow
            'G': self.color_scheme.F,  # Green
            'B': self.color_scheme.B,  # Blue
            'R': self.color_scheme.R,  # Red
            'O': self.color_scheme.L   # Orange
        }
        
        facelets = []
        for char in text:
            if char not in letter_to_color:
                raise ValueError(f"Invalid color letter: {char}")
            facelets.append(letter_to_color[char])
        
        return facelets
    
    def _clear_text_input(self) -> None:
        """Clear text input."""
        self.text_input.clear()
    
    def _validate_cube(self) -> None:
        """Validate current cube state."""
        is_valid, errors = validate_facelets(self.facelets)
        
        if is_valid:
            self.validation_label.setText("Status: ✓ Valid cube state")
            self.validation_label.setStyleSheet("color: #28a745; font-weight: bold;")
            QMessageBox.information(self, "Validation", "Cube state is valid!")
        else:
            self.validation_label.setText("Status: ✗ Invalid cube state")
            self.validation_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            
            error_text = "\n".join(errors)
            QMessageBox.warning(self, "Validation Error", 
                              f"Invalid cube state:\n\n{error_text}")
            
            # Highlight problematic stickers
            problematic = get_problematic_stickers(self.facelets)
            # TODO: Highlight problematic stickers in 2D/3D view
        
        self.validation_requested.emit()
    
    def _reset_to_solved(self) -> None:
        """Reset cube to solved state."""
        self.cube_state = CubeState.solved()
        self.facelets = self.cube_state.to_facelets(self.color_scheme)
        self._update_display()
        
        self.validation_label.setText("Status: Reset to solved state")
        self.validation_label.setStyleSheet("color: #28a745;")
        
        self.cube_state_changed.emit(self.cube_state)
    
    def _generate_random_colors(self) -> None:
        """Generate random colors for the cube."""
        # TODO: Implement random color generation
        pass
    
    def _on_color_selected(self, color: str) -> None:
        """Handle color selection from palette."""
        self.current_color = color
        self._update_color_button(self.current_color_button, color)
        
        # Update status
        self.validation_label.setText(f"Status: Selected color {color}")
        self.validation_label.setStyleSheet("color: #007bff;")
    
    def _on_facelet_clicked(self, facelet_index: int) -> None:
        """Handle facelet click in paint mode."""
        if self.paint_mode_button.isChecked():
            # Save current state before making changes
            self._save_state()
            
            # Set the clicked facelet to current color
            self.facelets[facelet_index] = self.current_color
            
            # Update paint widget
            self.paint_widget.update_facelets(self.facelets)
            
            # Update cube state
            self._update_cube_state()
            
            # Update validation status
            self.validation_label.setText(f"Status: Painted facelet {facelet_index}")
            self.validation_label.setStyleSheet("color: #007bff;")
    
    def _update_cube_state(self) -> None:
        """Update cube state from current facelets."""
        try:
            self.cube_state = CubeState.from_facelets(self.facelets)
            self.cube_state_changed.emit(self.cube_state)
        except ValueError as e:
            # Invalid cube state
            self.validation_label.setText(f"Status: Invalid - {str(e)}")
            self.validation_label.setStyleSheet("color: #dc3545;")
    
    def _save_state(self) -> None:
        """Save current state to undo stack."""
        # Save a copy of the current state
        state_copy = {
            'cube_state': CubeState.from_facelets(self.cube_state.to_facelets(self.color_scheme)),
            'facelets': self.facelets.copy()
        }
        self.undo_stack.append(state_copy)
        
        # Clear redo stack when making new changes
        self.redo_stack.clear()
    
    def undo(self) -> None:
        """Undo the last operation."""
        if self.undo_stack:
            # Save current state to redo stack
            current_state = {
                'cube_state': CubeState.from_facelets(self.cube_state.to_facelets(self.color_scheme)),
                'facelets': self.facelets.copy()
            }
            self.redo_stack.append(current_state)
            
            # Restore previous state
            previous_state = self.undo_stack.pop()
            self.cube_state = previous_state['cube_state']
            self.facelets = previous_state['facelets'].copy()
            
            # Update UI
            self._update_display()
            self.paint_widget.update_facelets(self.facelets)
            self.cube_state_changed.emit(self.cube_state)
            
            self.validation_label.setText("Status: Undid last operation")
            self.validation_label.setStyleSheet("color: #007bff;")
    
    def redo(self) -> None:
        """Redo the last undone operation."""
        if self.redo_stack:
            # Save current state to undo stack
            current_state = {
                'cube_state': CubeState.from_facelets(self.cube_state.to_facelets(self.color_scheme)),
                'facelets': self.facelets.copy()
            }
            self.undo_stack.append(current_state)
            
            # Restore next state
            next_state = self.redo_stack.pop()
            self.cube_state = next_state['cube_state']
            self.facelets = next_state['facelets'].copy()
            
            # Update UI
            self._update_display()
            self.paint_widget.update_facelets(self.facelets)
            self.cube_state_changed.emit(self.cube_state)
            
            self.validation_label.setText("Status: Redid last operation")
            self.validation_label.setStyleSheet("color: #007bff;")
    
    def can_undo(self) -> bool:
        """Check if undo is possible."""
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is possible."""
        return len(self.redo_stack) > 0
    
    def _convert_colors_to_letters(self, colors: List[str]) -> str:
        """Convert hex colors to letter notation."""
        color_to_letter = {
            self.color_scheme.U: 'U',  # White
            self.color_scheme.D: 'D',  # Yellow
            self.color_scheme.F: 'F',  # Green
            self.color_scheme.B: 'B',  # Blue
            self.color_scheme.R: 'R',  # Red
            self.color_scheme.L: 'L',  # Orange
        }
        
        # For colors not in the scheme, try to match them
        result = []
        for color in colors:
            if color in color_to_letter:
                result.append(color_to_letter[color])
            else:
                # Default to 'W' for unknown colors
                result.append('W')
        
        return ''.join(result)
    
    def update_facelets(self, facelets: List[str]) -> None:
        """Update facelets and refresh display."""
        self.facelets = facelets.copy()
        self._update_display()
        if self.paint_widget:
            self.paint_widget.update_facelets(facelets)
    
    def _update_display(self) -> None:
        """Update display with current cube state."""
        # Update text input
        letters = self._convert_colors_to_letters(self.facelets)
        self.text_input.setPlainText(letters)
    
    def _show_3d_mode_instructions(self) -> None:
        """Show instructions for 3D mode."""
        # In 3D mode, we don't need additional UI elements in the panel
        # The user will interact directly with the 3D cube in the main view
        # We just need to make sure the 3D view is visible and active
        pass
    
    def _update_color_button(self, button: QPushButton, color: str) -> None:
        """Update a color button's appearance."""
        button.setStyleSheet(f"""
            background-color: {color};
            border: 2px solid #333333;
            border-radius: 4px;
        """)
        
        # Store the color as a property
        button.setProperty("color", color)
    
    def set_color_scheme(self, scheme: ColorScheme) -> None:
        """Set color scheme."""
        self.color_scheme = scheme
        
        # Update color buttons
        for face, button in self.color_buttons.items():
            self._update_color_button(button, getattr(scheme, face))
        
        # Update current color
        self.current_color = scheme.U
        self._update_color_button(self.current_color_button, self.current_color)
        
        # Update cube display
        self.facelets = self.cube_state.to_facelets(scheme)
        self._update_display()
