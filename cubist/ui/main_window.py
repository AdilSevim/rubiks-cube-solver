"""
Main window for Cubist application.
"""

from typing import Optional, Dict, List, Tuple
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTabWidget, QLabel, QStatusBar, QMessageBox, QProgressBar,
    QApplication, QGridLayout
)
from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtGui import QAction, QKeySequence, QIcon

from ..core.cube_state import CubeState
from ..core.moves import MoveSequence
from ..core.color_scheme import ColorScheme
from ..solvers.fast_kociemba import FastSolver
from ..solvers.tutor_lbl import TutorSolver
from ..solvers.research_ida import IDAStarSolver

from .render.renderer3d import Renderer3D
from .render.renderer2d import Renderer2D
from .playback.animation_controller import AnimationController
from .panels.control_panel import ControlPanel
from .panels.solution_list import SolutionList
from .panels.color_input_panel import ColorInputPanel
from .panels.stats_panel import StatsPanel


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()
        
        # Window properties
        self.setWindowTitle("Cubist - 3×3 Rubik's Cube Solver & Tutor")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Application state
        self.cube_state = CubeState.solved()
        self.color_scheme = ColorScheme()
        self.current_solution = MoveSequence([])
        self.current_solver = "Fast"
        
        # Solvers
        self.fast_solver = FastSolver()
        self.tutor_solver = TutorSolver()
        self.research_solver = IDAStarSolver()
        
        # Initialize UI components
        self._setup_ui()
        self._setup_menu_bar()
        self._setup_status_bar()
        self._setup_connections()
        
        # Apply theme
        self._apply_theme()
        
        # Status
        self.status_label.setText("Ready - Load a scramble or input colors to begin")
    
    def _setup_ui(self) -> None:
        """Set up the user interface layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # Create splitter for resizable panes
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left pane: 3D viewport
        self._setup_3d_pane(splitter)
        
        # Right pane: Control panels
        self._setup_control_pane(splitter)
        
        # Set splitter proportions (70% for 3D, 30% for controls)
        splitter.setSizes([1000, 400])
    
    def _setup_3d_pane(self, parent: QSplitter) -> None:
        """Set up the 3D visualization pane."""
        # Create container widget
        viewport_widget = QWidget()
        viewport_layout = QVBoxLayout(viewport_widget)
        viewport_layout.setContentsMargins(4, 4, 4, 4)
        
        # 3D renderer
        self.renderer_3d = Renderer3D()
        self.renderer_3d.set_state(self.cube_state)
        self.renderer_3d.set_color_scheme(self.color_scheme)
        
        # Animation controller
        self.animation_controller = AnimationController()
        
        # Add tab widget for 3D/2D views
        self.view_tabs = QTabWidget()
        self.view_tabs.addTab(self.renderer_3d, "3D View")
        
        # 2D renderer (optional)
        self.renderer_2d = Renderer2D()
        self.view_tabs.addTab(self.renderer_2d, "2D View")
        
        viewport_layout.addWidget(self.view_tabs)
        parent.addWidget(viewport_widget)
    
    def _setup_control_pane(self, parent: QSplitter) -> None:
        """Set up the control panels pane."""
        # Create container widget
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        control_layout.setContentsMargins(4, 4, 4, 4)
        control_layout.setSpacing(8)
        
        # Create tab widget for different control panels
        self.control_tabs = QTabWidget()
        
        # Control panel (solver selection, playback controls)
        self.control_panel = ControlPanel()
        self.control_tabs.addTab(self.control_panel, "Controls")
        
        # Color input panel
        self.color_input_panel = ColorInputPanel()
        self.control_tabs.addTab(self.color_input_panel, "Input")
        
        # Solution list panel
        self.solution_list = SolutionList()
        self.control_tabs.addTab(self.solution_list, "Solution")
        
        # Stats panel
        self.stats_panel = StatsPanel()
        self.control_tabs.addTab(self.stats_panel, "Stats")
        
        control_layout.addWidget(self.control_tabs)
        parent.addWidget(control_widget)
    
    def _setup_menu_bar(self) -> None:
        """Set up the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # New scramble
        new_action = QAction("&New Scramble", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self._generate_scramble)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        # Import/Export
        import_action = QAction("&Import...", self)
        import_action.setShortcut(QKeySequence.Open)
        import_action.triggered.connect(self._import_cube)
        file_menu.addAction(import_action)
        
        export_action = QAction("&Export...", self)
        export_action.setShortcut(QKeySequence.Save)
        export_action.triggered.connect(self._export_solution)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        reset_camera_action = QAction("&Reset Camera", self)
        reset_camera_action.setShortcut("Ctrl+R")
        reset_camera_action.triggered.connect(self.renderer_3d.reset_camera)
        view_menu.addAction(reset_camera_action)
        
        # Playback menu
        playback_menu = menubar.addMenu("&Playback")
        
        play_pause_action = QAction("&Play/Pause", self)
        play_pause_action.setShortcut(Qt.Key_Space)
        play_pause_action.triggered.connect(self.animation_controller.toggle_play_pause)
        playback_menu.addAction(play_pause_action)
        
        step_back_action = QAction("Step &Back", self)
        step_back_action.setShortcut(Qt.Key_Left)
        step_back_action.triggered.connect(self.animation_controller.step_back)
        playback_menu.addAction(step_back_action)
        
        step_forward_action = QAction("Step &Forward", self)
        step_forward_action.setShortcut(Qt.Key_Right)
        step_forward_action.triggered.connect(self.animation_controller.step_forward)
        playback_menu.addAction(step_forward_action)
        
        playback_menu.addSeparator()
        
        jump_start_action = QAction("Jump to &Start", self)
        jump_start_action.setShortcut(Qt.Key_Home)
        jump_start_action.triggered.connect(self.animation_controller.jump_to_start)
        playback_menu.addAction(jump_start_action)
        
        jump_end_action = QAction("Jump to &End", self)
        jump_end_action.setShortcut(Qt.Key_End)
        jump_end_action.triggered.connect(self.animation_controller.jump_to_end)
        playback_menu.addAction(jump_end_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About Cubist", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_status_bar(self) -> None:
        """Set up the status bar."""
        self.status_bar = self.statusBar()
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Solver info
        self.solver_label = QLabel("Solver: Fast")
        self.status_bar.addPermanentWidget(self.solver_label)
    
    def _setup_connections(self) -> None:
        """Set up signal-slot connections."""
        # Animation controller connections
        self.animation_controller.progress_changed.connect(self._on_animation_progress)
        self.animation_controller.step_changed.connect(self._on_step_changed)
        self.animation_controller.playback_finished.connect(self._on_playback_finished)
        
        # Control panel connections
        self.control_panel.solver_changed.connect(self._on_solver_changed)
        self.control_panel.solve_requested.connect(self._solve_cube)
        self.control_panel.scramble_requested.connect(self._generate_scramble)
        self.control_panel.speed_changed.connect(self.animation_controller.set_speed)
        
        # Color input connections
        self.color_input_panel.cube_state_changed.connect(self._on_cube_state_changed)
        self.color_input_panel.validation_requested.connect(self._validate_cube)
        
        # Solution list connections
        self.solution_list.step_selected.connect(self.animation_controller.seek_to)
        
        # 3D renderer connections
        self.renderer_3d.piece_clicked.connect(self._on_piece_clicked)
    
    def _apply_theme(self) -> None:
        """Apply the light professional theme."""
        style = """
        QMainWindow {
            background-color: #f5f5f5;
            color: #333333;
        }
        
        QTabWidget::pane {
            border: 1px solid #cccccc;
            background-color: white;
        }
        
        QTabBar::tab {
            background-color: #e0e0e0;
            border: 1px solid #cccccc;
            padding: 8px 16px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: white;
            border-bottom: 1px solid white;
        }
        
        QTabBar::tab:hover {
            background-color: #f0f0f0;
        }
        
        QPushButton {
            background-color: #ffffff;
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: 500;
        }
        
        QPushButton:hover {
            background-color: #f8f8f8;
            border-color: #999999;
        }
        
        QPushButton:pressed {
            background-color: #e8e8e8;
        }
        
        QPushButton:disabled {
            background-color: #f0f0f0;
            color: #999999;
            border-color: #dddddd;
        }
        
        QSlider::groove:horizontal {
            border: 1px solid #cccccc;
            height: 6px;
            background: #f0f0f0;
            border-radius: 3px;
        }
        
        QSlider::handle:horizontal {
            background: #4a90e2;
            border: 1px solid #3a7bc8;
            width: 16px;
            height: 16px;
            border-radius: 8px;
            margin: -6px 0;
        }
        
        QProgressBar {
            border: 1px solid #cccccc;
            border-radius: 4px;
            text-align: center;
            background-color: #f0f0f0;
        }
        
        QProgressBar::chunk {
            background-color: #4a90e2;
            border-radius: 3px;
        }
        """
        
        self.setStyleSheet(style)
    
    def _generate_scramble(self) -> None:
        """Generate a new scramble."""
        from ..core.scramble import generate_scramble
        
        try:
            scramble = generate_scramble()
            scrambled_state = scramble.apply_to(CubeState.solved())
            
            self.cube_state = scrambled_state
            self.renderer_3d.set_state(self.cube_state)
            self.color_input_panel.set_cube_state(self.cube_state)
            
            self.status_label.setText(f"Generated scramble: {scramble}")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to generate scramble: {str(e)}")
    
    def _solve_cube(self) -> None:
        """Solve the current cube state."""
        if self.cube_state.is_solved():
            QMessageBox.information(self, "Info", "Cube is already solved!")
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_label.setText("Solving cube...")
        
        try:
            if self.current_solver == "Fast":
                solution = self.fast_solver.solve(self.cube_state, self.color_scheme)
            elif self.current_solver == "Tutor":
                steps, solution = self.tutor_solver.solve(self.cube_state, self.color_scheme)
                # TODO: Handle tutorial steps
            elif self.current_solver == "Research":
                solution = self.research_solver.solve(self.cube_state)
            else:
                raise ValueError(f"Unknown solver: {self.current_solver}")
            
            self.current_solution = solution
            self.animation_controller.load_sequence(solution, self.cube_state)
            self.solution_list.set_solution(solution)
            self.stats_panel.update_stats(solution, self.current_solver)
            
            self.status_label.setText(f"Solution found: {len(solution)} moves")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to solve cube: {str(e)}")
            self.status_label.setText("Solve failed")
        
        finally:
            self.progress_bar.setVisible(False)
    
    def _validate_cube(self) -> None:
        """Validate the current cube state."""
        from ..core.validators import validate_cube_state
        
        is_valid, errors = validate_cube_state(self.cube_state)
        
        if is_valid:
            QMessageBox.information(self, "Validation", "Cube state is valid!")
        else:
            error_text = "\n".join(errors)
            QMessageBox.warning(self, "Validation Error", f"Invalid cube state:\n\n{error_text}")
    
    def _import_cube(self) -> None:
        """Import cube state from file."""
        # TODO: Implement file import
        pass
    
    def _export_solution(self) -> None:
        """Export solution to file."""
        # TODO: Implement solution export
        pass
    
    def _show_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Cubist",
            """
            <h3>Cubist v1.0.0</h3>
            <p>3×3 Rubik's Cube Solver & Tutor</p>
            <p>A comprehensive desktop application for solving and learning the Rubik's Cube.</p>
            <p><b>Features:</b></p>
            <ul>
            <li>Fast optimal solving (Kociemba algorithm)</li>
            <li>Step-by-step tutorial mode</li>
            <li>Research solver with visualization</li>
            <li>3D animation and playback controls</li>
            <li>PDF export and statistics</li>
            </ul>
            <p>Built with Python, PySide6, and OpenGL.</p>
            """
        )
    
    def _on_solver_changed(self, solver_name: str) -> None:
        """Handle solver selection change."""
        self.current_solver = solver_name
        self.solver_label.setText(f"Solver: {solver_name}")
    
    def _on_cube_state_changed(self, state: CubeState) -> None:
        """Handle cube state change from input panel."""
        self.cube_state = state
        self.renderer_3d.set_state(state)
        self.status_label.setText("Cube state updated")
    
    def _on_animation_progress(self, progress: float, current: int, total: int) -> None:
        """Handle animation progress update."""
        if total > 0:
            self.status_label.setText(f"Playing: {current}/{total} ({progress*100:.0f}%)")
    
    def _on_step_changed(self, step: int) -> None:
        """Handle animation step change."""
        # Update 3D renderer with current state
        current_state = self.animation_controller.get_current_state()
        self.renderer_3d.set_state(current_state)
        
        # Highlight current move in solution list
        self.solution_list.highlight_step(step)
    
    def _on_playback_finished(self) -> None:
        """Handle playback completion."""
        self.status_label.setText("Playback finished - Cube solved!")
    
    def _on_piece_clicked(self, piece_id: int) -> None:
        """Handle 3D cube piece click for direct facelet marking."""
        # Save current state before making changes
        self.color_input_panel._save_state()
        
        # Get the current color from the color input panel
        current_color = self.color_input_panel.current_color
        
        # Get facelet indices for the clicked piece
        facelet_indices = self._get_facelet_indices_for_piece(piece_id)
        
        # Convert current cube state to facelets
        facelets = self.cube_state.to_facelets(self.color_input_panel.color_scheme)
        
        # Update the facelets with the selected color for each facelet
        for facelet_index in facelet_indices:
            facelets[facelet_index] = current_color
        
        # Update the cube state from the modified facelets
        try:
            self.cube_state = CubeState.from_facelets(facelets)
            # Update the 3D renderer with the new state
            self.renderer_3d.set_state(self.cube_state)
            
            # Update the color input panel to reflect changes
            self.color_input_panel.update_facelets(facelets)
            
            # Update status
            self.status_label.setText(f"Status: Painted piece {piece_id} with color {current_color}")
        except ValueError as e:
            # Handle invalid cube state
            print(f"Error updating cube state: {e}")
            self.status_label.setText(f"Error: Invalid cube state - {e}")
    
    def _get_facelet_indices_for_piece(self, piece_id: int) -> List[int]:
        """Get the facelet indices for a given piece ID based on cube geometry with improved accuracy."""
        # Validate piece_id input
        if not isinstance(piece_id, int) or piece_id < 0 or piece_id > 26:
            return []
            
        # Mapping of cubie positions to facelet indices
        # The 3D renderer creates cubies in a specific order:
        # x: -1, 0, 1; y: -1, 0, 1; z: -1, 0, 1 (center cubie skipped)
        # This gives us 26 cubies with IDs 0-26
        
        # Define facelet indices for each cubie based on position
        # Format: [cubie_id] = [list of facelet indices]
        # Using standard cube notation:
        # U: Up, D: Down, L: Left, R: Right, F: Front, B: Back
        # Facelet indices: 0-8 (U), 9-17 (L), 18-26 (F), 27-35 (R), 36-44 (B), 45-53 (D)
        cubie_to_facelets = {
            # Back layer (z = -1)
            0: [0, 36, 9],   # UBL corner: U7, B9, L1
            1: [1, 37],      # UB edge: U8, B8
            2: [2, 38, 27],  # UBR corner: U9, B7, R1
            3: [3, 39],      # LB edge: L4, B6
            4: [4],          # L center: L5
            5: [5, 41],      # RB edge: R2, B4
            6: [6, 42, 15],  # DBL corner: D1, B3, L7
            7: [7, 43],      # DB edge: D2, B2
            8: [8, 44, 33],  # DBR corner: D3, B1, R3
            
            # Middle layer (z = 0)
            9: [10, 36],     # UL edge: U4, L1
            10: [13],        # L center: L5
            11: [16, 27],    # UR edge: U6, R1
            12: [37],        # L center: L2
            13: [],          # Center cubie (skipped)
            14: [41],        # R center: R2
            15: [28, 42],    # DL edge: D4, L7
            16: [31],        # D center: D5
            17: [34, 33],    # DR edge: D6, R3
            
            # Front layer (z = 1)
            18: [18, 9, 29], # UFL corner: F7, L3, U1
            19: [19, 12],    # UF edge: F4, U2
            20: [20, 27, 29], # UFR corner: F1, R1, U3
            21: [21, 39],    # FL edge: F6, L6
            22: [22],        # F center: F5
            23: [23, 41],    # FR edge: F2, R2
            24: [24, 15, 45], # DFL corner: F9, L9, D7
            25: [25, 43],    # DF edge: F8, D8
            26: [26, 33, 47], # DFR corner: F3, R3, D9
        }
        
        # Validate and return facelet indices for the given piece ID
        if piece_id in cubie_to_facelets:
            # Filter out any invalid facelet indices
            valid_indices = [idx for idx in cubie_to_facelets[piece_id] if 0 <= idx < 54]
            return valid_indices
        else:
            return []
    
    def closeEvent(self, event) -> None:
        """Handle window close event."""
        # Stop any ongoing animations or solving
        self.animation_controller.stop()
        if hasattr(self.research_solver, 'cancel'):
            self.research_solver.cancel()
        
        event.accept()
