"""
2D renderer for Rubik's Cube net/isometric visualization.
"""

from typing import List, Tuple, Optional
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, QSize, QRect, QPoint
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPolygon

from ...core.cube_state import CubeState
from ...core.color_scheme import ColorScheme


class Renderer2D(QWidget):
    """2D renderer for cube visualization using net layout."""
    
    def __init__(self, parent=None) -> None:
        """Initialize the 2D renderer."""
        super().__init__(parent)
        
        # Cube state
        self.cube_state = CubeState.solved()
        self.color_scheme = ColorScheme()
        
        # Rendering settings
        self.sticker_size = 30
        self.gap_size = 2
        self.border_width = 2
        
        # Layout settings
        self.margin = 20
        self.face_spacing = 10
        
        # Highlighting
        self.highlighted_stickers = []
        
        # Set minimum size
        self.setMinimumSize(400, 300)
        
    def paintEvent(self, event) -> None:
        """Paint the 2D cube representation."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Clear background
        painter.fillRect(self.rect(), QColor(245, 245, 245))
        
        # Get facelets for rendering
        facelets = self.cube_state.to_facelets(self.color_scheme)
        
        # Draw cube net
        self._draw_cube_net(painter, facelets)
        
    def _draw_cube_net(self, painter: QPainter, facelets: List[str]) -> None:
        """Draw the cube as an unfolded net."""
        # Net layout positions (in grid units)
        # Standard net layout:
        #     [U]
        # [L] [F] [R] [B]
        #     [D]
        
        face_positions = {
            'U': (1, 0),  # Up
            'L': (0, 1),  # Left
            'F': (1, 1),  # Front
            'R': (2, 1),  # Right
            'B': (3, 1),  # Back
            'D': (1, 2),  # Down
        }
        
        face_size = 3 * self.sticker_size + 2 * self.gap_size
        
        # Calculate starting position to center the net
        net_width = 4 * face_size + 3 * self.face_spacing
        net_height = 3 * face_size + 2 * self.face_spacing
        
        start_x = (self.width() - net_width) // 2
        start_y = (self.height() - net_height) // 2
        
        # Draw each face
        face_names = ['U', 'R', 'F', 'D', 'L', 'B']
        for i, face_name in enumerate(face_names):
            if face_name in face_positions:
                grid_x, grid_y = face_positions[face_name]
                
                face_x = start_x + grid_x * (face_size + self.face_spacing)
                face_y = start_y + grid_y * (face_size + self.face_spacing)
                
                # Get facelets for this face (9 stickers)
                face_facelets = facelets[i*9:(i+1)*9]
                
                self._draw_face(painter, face_x, face_y, face_facelets, face_name)
    
    def _draw_face(self, painter: QPainter, x: int, y: int, 
                   face_facelets: List[str], face_name: str) -> None:
        """Draw a single face of the cube."""
        # Draw face background
        face_rect = QRect(x - 2, y - 2, 
                         3 * self.sticker_size + 2 * self.gap_size + 4,
                         3 * self.sticker_size + 2 * self.gap_size + 4)
        
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.setBrush(QBrush(QColor(240, 240, 240)))
        painter.drawRect(face_rect)
        
        # Draw face label
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QPen(QColor(100, 100, 100)))
        
        label_rect = QRect(x, y - 18, 3 * self.sticker_size + 2 * self.gap_size, 16)
        painter.drawText(label_rect, Qt.AlignCenter, face_name)
        
        # Draw stickers in 3x3 grid
        for row in range(3):
            for col in range(3):
                sticker_index = row * 3 + col
                if sticker_index < len(face_facelets):
                    sticker_x = x + col * (self.sticker_size + self.gap_size)
                    sticker_y = y + row * (self.sticker_size + self.gap_size)
                    
                    color = face_facelets[sticker_index]
                    self._draw_sticker(painter, sticker_x, sticker_y, color, sticker_index)
    
    def _draw_sticker(self, painter: QPainter, x: int, y: int, 
                     color: str, sticker_id: int) -> None:
        """Draw a single sticker."""
        sticker_rect = QRect(x, y, self.sticker_size, self.sticker_size)
        
        # Convert hex color to QColor
        qcolor = QColor(color)
        
        # Check if highlighted
        is_highlighted = sticker_id in self.highlighted_stickers
        
        # Draw sticker background
        painter.setBrush(QBrush(qcolor))
        
        if is_highlighted:
            # Highlighted border
            painter.setPen(QPen(QColor(255, 255, 0), 3))
        else:
            # Normal border
            painter.setPen(QPen(QColor(0, 0, 0), self.border_width))
        
        painter.drawRect(sticker_rect)
        
        # Add subtle gradient effect
        if not is_highlighted:
            gradient_rect = QRect(x + 2, y + 2, 
                                self.sticker_size - 4, self.sticker_size - 4)
            
            # Lighter version of the color
            lighter_color = qcolor.lighter(120)
            painter.setBrush(QBrush(lighter_color))
            painter.setPen(Qt.NoPen)
            painter.drawRect(gradient_rect)
    
    def set_state(self, state: CubeState) -> None:
        """Set the cube state to render."""
        self.cube_state = state
        self.update()
    
    def set_color_scheme(self, scheme: ColorScheme) -> None:
        """Set the color scheme for rendering."""
        self.color_scheme = scheme
        self.update()
    
    def highlight_stickers(self, sticker_ids: List[int]) -> None:
        """Highlight specific stickers."""
        self.highlighted_stickers = sticker_ids.copy()
        self.update()
    
    def clear_highlights(self) -> None:
        """Clear all sticker highlights."""
        self.highlighted_stickers.clear()
        self.update()
    
    def mousePressEvent(self, event) -> None:
        """Handle mouse clicks on stickers."""
        # TODO: Implement sticker clicking for color input
        pass
    
    def sizeHint(self) -> None:
        """Return preferred size."""
        face_size = 3 * self.sticker_size + 2 * self.gap_size
        net_width = 4 * face_size + 3 * self.face_spacing + 2 * self.margin
        net_height = 3 * face_size + 2 * self.face_spacing + 2 * self.margin
        
        return QSize(net_width, net_height)
