"""
Solution list panel for displaying and navigating move sequences.
"""

from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QTextEdit, QGroupBox, QSplitter
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ...core.moves import MoveSequence


class SolutionList(QWidget):
    """Panel for displaying and interacting with solution moves."""
    
    # Signals
    step_selected = Signal(int)  # Step index selected
    move_clicked = Signal(int)   # Move index clicked
    
    def __init__(self, parent=None) -> None:
        """Initialize the solution list panel."""
        super().__init__(parent)
        
        self.current_solution = MoveSequence([])
        self.current_step = 0
        
        self._setup_ui()
        self._setup_connections()
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Solution info group
        self._create_info_group(layout)
        
        # Create splitter for move list and details
        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter)
        
        # Move list group
        self._create_move_list_group(splitter)
        
        # Move details group
        self._create_details_group(splitter)
        
        # Set splitter proportions
        splitter.setSizes([300, 150])
    
    def _create_info_group(self, parent_layout: QVBoxLayout) -> None:
        """Create solution information group."""
        group = QGroupBox("Solution Info")
        layout = QVBoxLayout(group)
        
        # Solution stats
        self.stats_label = QLabel("No solution loaded")
        self.stats_label.setStyleSheet("font-weight: bold; color: #333333;")
        layout.addWidget(self.stats_label)
        
        # Quick actions
        actions_layout = QHBoxLayout()
        
        self.copy_button = QPushButton("📋 Copy Moves")
        self.copy_button.setEnabled(False)
        actions_layout.addWidget(self.copy_button)
        
        self.clear_button = QPushButton("🗑️ Clear")
        self.clear_button.setEnabled(False)
        actions_layout.addWidget(self.clear_button)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        parent_layout.addWidget(group)
    
    def _create_move_list_group(self, parent_splitter) -> None:
        """Create move list group."""
        group = QGroupBox("Move Sequence")
        layout = QVBoxLayout(group)
        
        # Move list widget
        self.move_list = QListWidget()
        self.move_list.setAlternatingRowColors(True)
        self.move_list.setSelectionMode(QListWidget.SingleSelection)
        
        # Set font for better readability
        font = QFont("Consolas", 11)
        if not font.exactMatch():
            font = QFont("Courier New", 11)
        self.move_list.setFont(font)
        
        layout.addWidget(self.move_list)
        
        parent_splitter.addWidget(group)
    
    def _create_details_group(self, parent_splitter) -> None:
        """Create move details group."""
        group = QGroupBox("Move Details")
        layout = QVBoxLayout(group)
        
        # Details text area
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(120)
        self.details_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f8f8;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        layout.addWidget(self.details_text)
        
        parent_splitter.addWidget(group)
    
    def _setup_connections(self) -> None:
        """Set up signal-slot connections."""
        self.move_list.currentRowChanged.connect(self._on_move_selected)
        self.move_list.itemClicked.connect(self._on_move_clicked)
        self.copy_button.clicked.connect(self._copy_moves)
        self.clear_button.clicked.connect(self._clear_solution)
    
    def set_solution(self, solution: MoveSequence) -> None:
        """Set the solution to display."""
        self.current_solution = solution
        self._update_display()
    
    def _update_display(self) -> None:
        """Update the display with current solution."""
        # Clear existing items
        self.move_list.clear()
        
        if len(self.current_solution) == 0:
            self.stats_label.setText("No solution loaded")
            self.copy_button.setEnabled(False)
            self.clear_button.setEnabled(False)
            self.details_text.clear()
            return
        
        # Update stats
        move_count = len(self.current_solution)
        self.stats_label.setText(f"Solution: {move_count} moves")
        
        # Enable buttons
        self.copy_button.setEnabled(True)
        self.clear_button.setEnabled(True)
        
        # Add moves to list
        for i, move in enumerate(self.current_solution):
            item_text = f"{i+1:2d}. {str(move)}"
            item = QListWidgetItem(item_text)
            
            # Set item data
            item.setData(Qt.UserRole, i)
            
            # Style based on position
            if i == self.current_step:
                item.setBackground(Qt.lightGray)
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            
            self.move_list.addItem(item)
        
        # Update details for first move
        if self.current_solution:
            self._update_move_details(0)
    
    def _update_move_details(self, move_index: int) -> None:
        """Update move details display."""
        if move_index < 0 or move_index >= len(self.current_solution):
            self.details_text.clear()
            return
        
        move = self.current_solution[move_index]
        move_str = str(move)
        
        # Generate move description
        descriptions = {
            'R': "Right face clockwise 90°",
            "R'": "Right face counter-clockwise 90°", 
            'R2': "Right face 180°",
            'L': "Left face clockwise 90°",
            "L'": "Left face counter-clockwise 90°",
            'L2': "Left face 180°",
            'U': "Up face clockwise 90°",
            "U'": "Up face counter-clockwise 90°",
            'U2': "Up face 180°",
            'D': "Down face clockwise 90°",
            "D'": "Down face counter-clockwise 90°",
            'D2': "Down face 180°",
            'F': "Front face clockwise 90°",
            "F'": "Front face counter-clockwise 90°",
            'F2': "Front face 180°",
            'B': "Back face clockwise 90°",
            "B'": "Back face counter-clockwise 90°",
            'B2': "Back face 180°",
        }
        
        description = descriptions.get(move_str, "Unknown move")
        
        details = f"""
<b>Move {move_index + 1}: {move_str}</b><br>
<i>{description}</i><br><br>
<b>Position:</b> {move_index + 1} of {len(self.current_solution)}<br>
<b>Remaining:</b> {len(self.current_solution) - move_index - 1} moves
        """
        
        self.details_text.setHtml(details.strip())
    
    def highlight_step(self, step_index: int) -> None:
        """Highlight a specific step in the list."""
        self.current_step = step_index
        
        # Update list item highlighting
        for i in range(self.move_list.count()):
            item = self.move_list.item(i)
            font = item.font()
            
            if i == step_index:
                item.setBackground(Qt.yellow)
                font.setBold(True)
            else:
                item.setBackground(Qt.transparent)
                font.setBold(False)
            
            item.setFont(font)
        
        # Scroll to current item
        if 0 <= step_index < self.move_list.count():
            self.move_list.setCurrentRow(step_index)
            self.move_list.scrollToItem(self.move_list.item(step_index))
    
    def _on_move_selected(self, row: int) -> None:
        """Handle move selection in list."""
        if row >= 0:
            self._update_move_details(row)
    
    def _on_move_clicked(self, item: QListWidgetItem) -> None:
        """Handle move item click."""
        move_index = item.data(Qt.UserRole)
        if move_index is not None:
            self.step_selected.emit(move_index)
            self.move_clicked.emit(move_index)
    
    def _copy_moves(self) -> None:
        """Copy move sequence to clipboard."""
        if self.current_solution:
            from PySide6.QtGui import QGuiApplication
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(str(self.current_solution))
    
    def _clear_solution(self) -> None:
        """Clear the current solution."""
        self.set_solution(MoveSequence([]))
    
    def get_selected_move_index(self) -> Optional[int]:
        """Get the currently selected move index."""
        current_row = self.move_list.currentRow()
        if current_row >= 0:
            item = self.move_list.item(current_row)
            return item.data(Qt.UserRole)
        return None
    
    def select_move(self, move_index: int) -> None:
        """Select a specific move in the list."""
        if 0 <= move_index < self.move_list.count():
            self.move_list.setCurrentRow(move_index)
    
    def get_move_at_index(self, index: int) -> Optional[str]:
        """Get move string at specific index."""
        if 0 <= index < len(self.current_solution):
            return str(self.current_solution[index])
        return None
