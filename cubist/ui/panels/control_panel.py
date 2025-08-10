"""
Main control panel for solver selection and playback controls.
"""

from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QComboBox,
    QPushButton, QSlider, QLabel, QProgressBar, QSpacerItem,
    QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon


class ControlPanel(QWidget):
    """Main control panel widget."""
    
    # Signals
    solver_changed = Signal(str)
    solve_requested = Signal()
    scramble_requested = Signal()
    speed_changed = Signal(int)
    
    def __init__(self, parent=None) -> None:
        """Initialize the control panel."""
        super().__init__(parent)
        
        self.current_solver = "Fast"
        self.animation_speed = 500  # ms per move
        
        self._setup_ui()
        self._setup_connections()
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Solver selection group
        self._create_solver_group(layout)
        
        # Action buttons group
        self._create_action_group(layout)
        
        # Playback controls group
        self._create_playback_group(layout)
        
        # Speed control group
        self._create_speed_group(layout)
        
        # Add stretch to push everything to top
        layout.addStretch()
    
    def _create_solver_group(self, parent_layout: QVBoxLayout) -> None:
        """Create solver selection group."""
        group = QGroupBox("Solver Model")
        layout = QVBoxLayout(group)
        
        # Solver combo box
        self.solver_combo = QComboBox()
        self.solver_combo.addItems(["Fast", "Tutor", "Research"])
        self.solver_combo.setCurrentText(self.current_solver)
        layout.addWidget(self.solver_combo)
        
        # Solver description
        self.solver_description = QLabel()
        self.solver_description.setWordWrap(True)
        self.solver_description.setStyleSheet("color: #666666; font-size: 11px;")
        self._update_solver_description()
        layout.addWidget(self.solver_description)
        
        parent_layout.addWidget(group)
    
    def _create_action_group(self, parent_layout: QVBoxLayout) -> None:
        """Create main action buttons group."""
        group = QGroupBox("Actions")
        layout = QVBoxLayout(group)
        
        # Solve button
        self.solve_button = QPushButton("🧩 Solve Cube")
        self.solve_button.setMinimumHeight(40)
        self.solve_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:pressed {
                background-color: #2968a3;
            }
        """)
        layout.addWidget(self.solve_button)
        
        # Scramble button
        self.scramble_button = QPushButton("🎲 Generate Scramble")
        self.scramble_button.setMinimumHeight(35)
        layout.addWidget(self.scramble_button)
        
        parent_layout.addWidget(group)
    
    def _create_playback_group(self, parent_layout: QVBoxLayout) -> None:
        """Create playback controls group."""
        group = QGroupBox("Playback")
        layout = QVBoxLayout(group)
        
        # Main playback buttons row
        button_row1 = QHBoxLayout()
        
        self.play_pause_button = QPushButton("▶️ Play")
        self.play_pause_button.setMinimumHeight(35)
        button_row1.addWidget(self.play_pause_button)
        
        self.stop_button = QPushButton("⏹️ Stop")
        self.stop_button.setMinimumHeight(35)
        button_row1.addWidget(self.stop_button)
        
        layout.addLayout(button_row1)
        
        # Step control buttons row
        button_row2 = QHBoxLayout()
        
        self.step_back_button = QPushButton("⏮️ Step Back")
        button_row2.addWidget(self.step_back_button)
        
        self.step_forward_button = QPushButton("⏭️ Step Forward")
        button_row2.addWidget(self.step_forward_button)
        
        layout.addLayout(button_row2)
        
        # Jump buttons row
        button_row3 = QHBoxLayout()
        
        self.jump_start_button = QPushButton("⏪ Start")
        button_row3.addWidget(self.jump_start_button)
        
        self.jump_end_button = QPushButton("⏩ End")
        button_row3.addWidget(self.jump_end_button)
        
        layout.addLayout(button_row3)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Progress label
        self.progress_label = QLabel("0 / 0 moves")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("color: #666666; font-size: 11px;")
        layout.addWidget(self.progress_label)
        
        parent_layout.addWidget(group)
    
    def _create_speed_group(self, parent_layout: QVBoxLayout) -> None:
        """Create animation speed control group."""
        group = QGroupBox("Animation Speed")
        layout = QVBoxLayout(group)
        
        # Speed slider
        speed_layout = QHBoxLayout()
        
        speed_layout.addWidget(QLabel("Slow"))
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(100)   # 100ms (very fast)
        self.speed_slider.setMaximum(1200)  # 1200ms (very slow)
        self.speed_slider.setValue(self.animation_speed)
        self.speed_slider.setTickPosition(QSlider.TicksBelow)
        self.speed_slider.setTickInterval(200)
        speed_layout.addWidget(self.speed_slider)
        
        speed_layout.addWidget(QLabel("Fast"))
        
        layout.addLayout(speed_layout)
        
        # Speed value label
        self.speed_label = QLabel(f"{self.animation_speed}ms per move")
        self.speed_label.setAlignment(Qt.AlignCenter)
        self.speed_label.setStyleSheet("color: #666666; font-size: 11px;")
        layout.addWidget(self.speed_label)
        
        parent_layout.addWidget(group)
    
    def _setup_connections(self) -> None:
        """Set up signal-slot connections."""
        # Solver selection
        self.solver_combo.currentTextChanged.connect(self._on_solver_changed)
        
        # Action buttons
        self.solve_button.clicked.connect(self.solve_requested.emit)
        self.scramble_button.clicked.connect(self.scramble_requested.emit)
        
        # Speed control
        self.speed_slider.valueChanged.connect(self._on_speed_changed)
    
    def _on_solver_changed(self, solver_name: str) -> None:
        """Handle solver selection change."""
        self.current_solver = solver_name
        self._update_solver_description()
        self.solver_changed.emit(solver_name)
    
    def _on_speed_changed(self, value: int) -> None:
        """Handle speed slider change."""
        # Invert the value so higher slider position = faster speed
        self.animation_speed = 1300 - value
        self.speed_label.setText(f"{self.animation_speed}ms per move")
        self.speed_changed.emit(self.animation_speed)
    
    def _update_solver_description(self) -> None:
        """Update solver description text."""
        descriptions = {
            "Fast": "Optimal solver using Kociemba's two-phase algorithm. Finds solutions in ~20 moves quickly.",
            "Tutor": "Step-by-step beginner method with explanations. Learn layer-by-layer solving technique.",
            "Research": "IDA* search algorithm with visualization. Demonstrates search tree exploration."
        }
        
        description = descriptions.get(self.current_solver, "")
        self.solver_description.setText(description)
    
    def update_progress(self, progress: float, current: int, total: int) -> None:
        """Update playback progress display."""
        self.progress_bar.setValue(int(progress * 100))
        self.progress_label.setText(f"{current} / {total} moves")
    
    def set_playback_state(self, is_playing: bool, is_paused: bool = False) -> None:
        """Update playback button states."""
        if is_playing and not is_paused:
            self.play_pause_button.setText("⏸️ Pause")
        else:
            self.play_pause_button.setText("▶️ Play")
    
    def set_solving_state(self, is_solving: bool) -> None:
        """Update UI state during solving."""
        self.solve_button.setEnabled(not is_solving)
        self.solver_combo.setEnabled(not is_solving)
        
        if is_solving:
            self.solve_button.setText("🔄 Solving...")
        else:
            self.solve_button.setText("🧩 Solve Cube")
