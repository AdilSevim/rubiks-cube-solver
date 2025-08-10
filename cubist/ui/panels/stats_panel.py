"""
Statistics panel for displaying solve metrics and performance data.
"""

import time
from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QTableWidget, QTableWidgetItem, QPushButton, QProgressBar
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from ...core.moves import MoveSequence


class StatsPanel(QWidget):
    """Panel for displaying solving statistics and metrics."""
    
    def __init__(self, parent=None) -> None:
        """Initialize the stats panel."""
        super().__init__(parent)
        
        # Stats data
        self.current_stats = {}
        self.solve_history = []
        self.start_time = None
        self.solve_timer = QTimer()
        self.solve_timer.timeout.connect(self._update_timer)
        
        self._setup_ui()
        self._reset_stats()
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Current solve stats group
        self._create_current_stats_group(layout)
        
        # Session stats group
        self._create_session_stats_group(layout)
        
        # History table group
        self._create_history_group(layout)
        
        # Export group
        self._create_export_group(layout)
    
    def _create_current_stats_group(self, parent_layout: QVBoxLayout) -> None:
        """Create current solve statistics group."""
        group = QGroupBox("Current Solve")
        layout = QVBoxLayout(group)
        
        # Stats grid
        stats_layout = QVBoxLayout()
        
        # Solver info
        solver_layout = QHBoxLayout()
        solver_layout.addWidget(QLabel("Solver:"))
        self.solver_label = QLabel("None")
        self.solver_label.setStyleSheet("font-weight: bold; color: #4a90e2;")
        solver_layout.addWidget(self.solver_label)
        solver_layout.addStretch()
        stats_layout.addLayout(solver_layout)
        
        # Move count
        moves_layout = QHBoxLayout()
        moves_layout.addWidget(QLabel("Moves:"))
        self.moves_label = QLabel("0")
        self.moves_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        moves_layout.addWidget(self.moves_label)
        moves_layout.addStretch()
        stats_layout.addLayout(moves_layout)
        
        # Time
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Time:"))
        self.time_label = QLabel("00:00.00")
        self.time_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #28a745;")
        time_layout.addWidget(self.time_label)
        time_layout.addStretch()
        stats_layout.addLayout(time_layout)
        
        # TPS (Turns per second)
        tps_layout = QHBoxLayout()
        tps_layout.addWidget(QLabel("TPS:"))
        self.tps_label = QLabel("0.00")
        self.tps_label.setStyleSheet("font-weight: bold;")
        tps_layout.addWidget(self.tps_label)
        tps_layout.addStretch()
        stats_layout.addLayout(tps_layout)
        
        layout.addLayout(stats_layout)
        parent_layout.addWidget(group)
    
    def _create_session_stats_group(self, parent_layout: QVBoxLayout) -> None:
        """Create session statistics group."""
        group = QGroupBox("Session Statistics")
        layout = QVBoxLayout(group)
        
        # Session stats
        session_layout = QVBoxLayout()
        
        # Solves count
        solves_layout = QHBoxLayout()
        solves_layout.addWidget(QLabel("Solves:"))
        self.session_solves_label = QLabel("0")
        self.session_solves_label.setStyleSheet("font-weight: bold;")
        solves_layout.addWidget(self.session_solves_label)
        solves_layout.addStretch()
        session_layout.addLayout(solves_layout)
        
        # Average moves
        avg_moves_layout = QHBoxLayout()
        avg_moves_layout.addWidget(QLabel("Avg Moves:"))
        self.avg_moves_label = QLabel("0.0")
        self.avg_moves_label.setStyleSheet("font-weight: bold;")
        avg_moves_layout.addWidget(self.avg_moves_label)
        avg_moves_layout.addStretch()
        session_layout.addLayout(avg_moves_layout)
        
        # Average time
        avg_time_layout = QHBoxLayout()
        avg_time_layout.addWidget(QLabel("Avg Time:"))
        self.avg_time_label = QLabel("00:00.00")
        self.avg_time_label.setStyleSheet("font-weight: bold;")
        avg_time_layout.addWidget(self.avg_time_label)
        avg_time_layout.addStretch()
        session_layout.addLayout(avg_time_layout)
        
        # Best solve
        best_layout = QHBoxLayout()
        best_layout.addWidget(QLabel("Best:"))
        self.best_label = QLabel("N/A")
        self.best_label.setStyleSheet("font-weight: bold; color: #28a745;")
        best_layout.addWidget(self.best_label)
        best_layout.addStretch()
        session_layout.addLayout(best_layout)
        
        layout.addLayout(session_layout)
        
        # Session controls
        controls_layout = QHBoxLayout()
        
        self.reset_session_button = QPushButton("🔄 Reset Session")
        controls_layout.addWidget(self.reset_session_button)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        parent_layout.addWidget(group)
    
    def _create_history_group(self, parent_layout: QVBoxLayout) -> None:
        """Create solve history group."""
        group = QGroupBox("Solve History")
        layout = QVBoxLayout(group)
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["#", "Solver", "Moves", "Time"])
        self.history_table.setMaximumHeight(150)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Set column widths
        header = self.history_table.horizontalHeader()
        header.setStretchLastSection(True)
        self.history_table.setColumnWidth(0, 40)   # #
        self.history_table.setColumnWidth(1, 80)   # Solver
        self.history_table.setColumnWidth(2, 60)   # Moves
        
        layout.addWidget(self.history_table)
        
        parent_layout.addWidget(group)
    
    def _create_export_group(self, parent_layout: QVBoxLayout) -> None:
        """Create export group."""
        group = QGroupBox("Export")
        layout = QVBoxLayout(group)
        
        export_layout = QHBoxLayout()
        
        self.export_pdf_button = QPushButton("📄 Export PDF")
        export_layout.addWidget(self.export_pdf_button)
        
        self.export_json_button = QPushButton("📊 Export JSON")
        export_layout.addWidget(self.export_json_button)
        
        self.export_txt_button = QPushButton("📝 Export TXT")
        export_layout.addWidget(self.export_txt_button)
        
        layout.addLayout(export_layout)
        parent_layout.addWidget(group)
        
        # Connect export buttons
        self.reset_session_button.clicked.connect(self._reset_session)
        self.export_pdf_button.clicked.connect(self._export_pdf)
        self.export_json_button.clicked.connect(self._export_json)
        self.export_txt_button.clicked.connect(self._export_txt)
    
    def update_stats(self, solution: MoveSequence, solver_name: str, 
                    solve_time: Optional[float] = None) -> None:
        """Update statistics with new solve data."""
        move_count = len(solution)
        
        if solve_time is None:
            solve_time = 0.0
        
        # Calculate TPS
        tps = move_count / max(solve_time, 0.001)
        
        # Update current stats
        self.current_stats = {
            'solver': solver_name,
            'moves': move_count,
            'time': solve_time,
            'tps': tps,
            'solution': solution
        }
        
        # Update display
        self._update_current_display()
        
        # Add to history
        self._add_to_history(self.current_stats)
        
        # Update session stats
        self._update_session_stats()
    
    def start_solve_timer(self) -> None:
        """Start the solve timer."""
        self.start_time = time.time()
        self.solve_timer.start(10)  # Update every 10ms
    
    def stop_solve_timer(self) -> float:
        """Stop the solve timer and return elapsed time."""
        if self.start_time is not None:
            elapsed = time.time() - self.start_time
            self.solve_timer.stop()
            self.start_time = None
            return elapsed
        return 0.0
    
    def _update_timer(self) -> None:
        """Update the timer display."""
        if self.start_time is not None:
            elapsed = time.time() - self.start_time
            self.time_label.setText(self._format_time(elapsed))
    
    def _update_current_display(self) -> None:
        """Update current solve display."""
        stats = self.current_stats
        
        self.solver_label.setText(stats.get('solver', 'None'))
        self.moves_label.setText(str(stats.get('moves', 0)))
        self.time_label.setText(self._format_time(stats.get('time', 0.0)))
        self.tps_label.setText(f"{stats.get('tps', 0.0):.2f}")
    
    def _add_to_history(self, stats: Dict[str, Any]) -> None:
        """Add solve to history."""
        self.solve_history.append(stats.copy())
        
        # Update history table
        row = self.history_table.rowCount()
        self.history_table.insertRow(row)
        
        # Add data to row
        self.history_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        self.history_table.setItem(row, 1, QTableWidgetItem(stats['solver']))
        self.history_table.setItem(row, 2, QTableWidgetItem(str(stats['moves'])))
        self.history_table.setItem(row, 3, QTableWidgetItem(self._format_time(stats['time'])))
        
        # Scroll to bottom
        self.history_table.scrollToBottom()
    
    def _update_session_stats(self) -> None:
        """Update session statistics."""
        if not self.solve_history:
            return
        
        # Calculate averages
        total_solves = len(self.solve_history)
        total_moves = sum(solve['moves'] for solve in self.solve_history)
        total_time = sum(solve['time'] for solve in self.solve_history)
        
        avg_moves = total_moves / total_solves
        avg_time = total_time / total_solves
        
        # Find best solve (by time)
        best_solve = min(self.solve_history, key=lambda x: x['time'])
        best_text = f"{best_solve['moves']} moves in {self._format_time(best_solve['time'])}"
        
        # Update display
        self.session_solves_label.setText(str(total_solves))
        self.avg_moves_label.setText(f"{avg_moves:.1f}")
        self.avg_time_label.setText(self._format_time(avg_time))
        self.best_label.setText(best_text)
    
    def _format_time(self, seconds: float) -> str:
        """Format time in MM:SS.ss format."""
        minutes = int(seconds // 60)
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:05.2f}"
    
    def _reset_stats(self) -> None:
        """Reset all statistics."""
        self.current_stats = {
            'solver': 'None',
            'moves': 0,
            'time': 0.0,
            'tps': 0.0,
            'solution': MoveSequence([])
        }
        self._update_current_display()
    
    def _reset_session(self) -> None:
        """Reset session statistics."""
        self.solve_history.clear()
        self.history_table.setRowCount(0)
        
        # Reset session display
        self.session_solves_label.setText("0")
        self.avg_moves_label.setText("0.0")
        self.avg_time_label.setText("00:00.00")
        self.best_label.setText("N/A")
    
    def _export_pdf(self) -> None:
        """Export statistics to PDF."""
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export PDF", "cubist_stats.pdf", "PDF Files (*.pdf)"
        )
        
        if filename:
            try:
                self._generate_pdf_report(filename)
                QMessageBox.information(self, "Success", f"Statistics exported to {filename}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to export PDF: {str(e)}")
    
    def _export_json(self) -> None:
        """Export statistics to JSON."""
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        import json
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export JSON", "cubist_stats.json", "JSON Files (*.json)"
        )
        
        if filename:
            try:
                data = {
                    'current_solve': self.current_stats,
                    'session_history': self.solve_history,
                    'export_timestamp': time.time()
                }
                
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                
                QMessageBox.information(self, "Success", f"Statistics exported to {filename}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to export JSON: {str(e)}")
    
    def _export_txt(self) -> None:
        """Export statistics to text file."""
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Text", "cubist_stats.txt", "Text Files (*.txt)"
        )
        
        if filename:
            try:
                self._generate_text_report(filename)
                QMessageBox.information(self, "Success", f"Statistics exported to {filename}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to export text: {str(e)}")
    
    def _generate_pdf_report(self, filename: str) -> None:
        """Generate PDF report."""
        # TODO: Implement PDF generation using reportlab
        raise NotImplementedError("PDF export not yet implemented")
    
    def _generate_text_report(self, filename: str) -> None:
        """Generate text report."""
        with open(filename, 'w') as f:
            f.write("Cubist - Solve Statistics Report\n")
            f.write("=" * 40 + "\n\n")
            
            # Current solve
            f.write("Current Solve:\n")
            f.write(f"  Solver: {self.current_stats['solver']}\n")
            f.write(f"  Moves: {self.current_stats['moves']}\n")
            f.write(f"  Time: {self._format_time(self.current_stats['time'])}\n")
            f.write(f"  TPS: {self.current_stats['tps']:.2f}\n")
            f.write(f"  Solution: {self.current_stats['solution']}\n\n")
            
            # Session stats
            if self.solve_history:
                f.write("Session Statistics:\n")
                f.write(f"  Total Solves: {len(self.solve_history)}\n")
                
                total_moves = sum(solve['moves'] for solve in self.solve_history)
                total_time = sum(solve['time'] for solve in self.solve_history)
                avg_moves = total_moves / len(self.solve_history)
                avg_time = total_time / len(self.solve_history)
                
                f.write(f"  Average Moves: {avg_moves:.1f}\n")
                f.write(f"  Average Time: {self._format_time(avg_time)}\n")
                
                best_solve = min(self.solve_history, key=lambda x: x['time'])
                f.write(f"  Best Solve: {best_solve['moves']} moves in {self._format_time(best_solve['time'])}\n\n")
                
                # History
                f.write("Solve History:\n")
                f.write("  #  | Solver   | Moves | Time     | TPS\n")
                f.write("  ---|----------|-------|----------|--------\n")
                
                for i, solve in enumerate(self.solve_history):
                    f.write(f"  {i+1:2d} | {solve['solver']:8s} | {solve['moves']:5d} | {self._format_time(solve['time']):8s} | {solve['tps']:6.2f}\n")
            
            f.write(f"\nGenerated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current solve statistics."""
        return self.current_stats.copy()
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        if not self.solve_history:
            return {
                'total_solves': 0,
                'avg_moves': 0.0,
                'avg_time': 0.0,
                'best_moves': 0,
                'best_time': 0.0
            }
        
        total_moves = sum(solve['moves'] for solve in self.solve_history)
        total_time = sum(solve['time'] for solve in self.solve_history)
        best_solve = min(self.solve_history, key=lambda x: x['time'])
        
        return {
            'total_solves': len(self.solve_history),
            'avg_moves': total_moves / len(self.solve_history),
            'avg_time': total_time / len(self.solve_history),
            'best_moves': best_solve['moves'],
            'best_time': best_solve['time']
        }
