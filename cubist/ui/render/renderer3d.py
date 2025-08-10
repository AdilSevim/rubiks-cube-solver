"""
3D OpenGL renderer for Rubik's Cube visualization.
"""

from typing import List, Optional, Tuple
import math
import numpy as np
from PySide6.QtCore import QTimer, Signal, QPropertyAnimation, QEasingCurve, Qt
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QMatrix4x4, QVector3D, QQuaternion
from OpenGL.GL import *
from OpenGL.GLU import *

from ...core.cube_state import CubeState
from ...core.moves import Move
from ...core.color_scheme import ColorScheme


class Renderer3D(QOpenGLWidget):
    """3D OpenGL renderer for Rubik's Cube."""
    
    # Signals
    animation_finished = Signal()
    piece_clicked = Signal(int)  # Piece ID
    piece_hovered = Signal(int)  # Piece ID
    
    def __init__(self, parent=None) -> None:
        """Initialize the 3D renderer."""
        super().__init__(parent)
        
        # Cube state
        self.cube_state = CubeState.solved()
        self.color_scheme = ColorScheme()
        
        # Camera parameters
        self.camera_distance = 8.0
        self.camera_rotation_x = -25.0
        self.camera_rotation_y = 45.0
        self.camera_pan_x = 0.0
        self.camera_pan_y = 0.0
        
        # Mouse interaction
        self.last_mouse_pos = None
        self.mouse_sensitivity = 0.5
        
        # Animation
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        self.animation_duration = 500  # ms
        self.animation_progress = 0.0
        self.animating_move = None
        self.animation_start_state = None
        
        # Connect signals
        self.piece_hovered.connect(self._on_piece_hovered)
        
        # Highlighting
        self.highlighted_pieces = []
        self.hovered_piece = -1  # No piece hovered by default
        
        # Rendering settings
        self.show_wireframe = False
        self.lighting_enabled = True
        self.smooth_shading = True
        
        # Cube geometry
        self.cubie_size = 0.9
        self.gap_size = 0.05
        
    def initializeGL(self) -> None:
        """Initialize OpenGL settings."""
        # Enable depth testing
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        
        # Enable face culling
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        
        # Set clear color (light gray background)
        glClearColor(0.95, 0.95, 0.95, 1.0)
        
        # Enable lighting
        if self.lighting_enabled:
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            
            # Light position
            light_pos = [5.0, 5.0, 5.0, 1.0]
            glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
            
            # Light colors
            glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
            glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
            glLightfv(GL_LIGHT0, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])
        
        # Material properties
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.3, 0.3, 0.3, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 32.0)
        
        # Enable color material
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
        
    def resizeGL(self, width: int, height: int) -> None:
        """Handle window resize."""
        glViewport(0, 0, width, height)
        
        # Set up projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        aspect = width / height if height > 0 else 1.0
        gluPerspective(45.0, aspect, 0.1, 100.0)
        
        glMatrixMode(GL_MODELVIEW)
        
    def paintGL(self) -> None:
        """Render the cube."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Set up camera
        glTranslatef(self.camera_pan_x, self.camera_pan_y, -self.camera_distance)
        glRotatef(self.camera_rotation_x, 1.0, 0.0, 0.0)
        glRotatef(self.camera_rotation_y, 0.0, 1.0, 0.0)
        
        # Render cube
        self._render_cube()
        
    def _render_cube(self) -> None:
        """Render the 3x3x3 cube."""
        # Get current facelets for rendering
        facelets = self.cube_state.to_facelets(self.color_scheme)
        
        # Render each cubie
        cubie_index = 0
        for x in range(-1, 2):
            for y in range(-1, 2):
                for z in range(-1, 2):
                    # Skip center cubie (invisible)
                    if x == 0 and y == 0 and z == 0:
                        continue
                    
                    position = (x * (self.cubie_size + self.gap_size),
                               y * (self.cubie_size + self.gap_size),
                               z * (self.cubie_size + self.gap_size))
                    
                    self._render_cubie(position, cubie_index, facelets)
                    cubie_index += 1
    
    def _render_cubie(self, position: Tuple[float, float, float], 
                     cubie_id: int, facelets: List[str]) -> None:
        """Render a single cubie at the given position."""
        glPushMatrix()
        glTranslatef(*position)
        
        # Apply highlighting if this is the hovered piece
        if cubie_id == self.hovered_piece:
            # Scale up slightly to make it appear highlighted
            glScalef(1.05, 1.05, 1.05)
        
        # Draw the faces of the cubie
        self._draw_cubie_faces(cubie_id, facelets)
        
        # Draw wireframe if enabled
        if self.show_wireframe:
            self._draw_cubie_wireframe()
        
        glPopMatrix()
    
    def _draw_cubie_faces(self, cubie_id: int, facelets: List[str]) -> None:
        """Draw the visible faces of a cubie."""
        size = self.cubie_size / 2
        
        # Face definitions: (normal, vertices, facelet_indices)
        faces = [
            # Front face (positive Z)
            ((0, 0, 1), [(-size, -size, size), (size, -size, size), 
                        (size, size, size), (-size, size, size)], self._get_front_facelets(cubie_id)),
            # Back face (negative Z)
            ((0, 0, -1), [(size, -size, -size), (-size, -size, -size),
                         (-size, size, -size), (size, size, -size)], self._get_back_facelets(cubie_id)),
            # Right face (positive X)
            ((1, 0, 0), [(size, -size, size), (size, -size, -size),
                        (size, size, -size), (size, size, size)], self._get_right_facelets(cubie_id)),
            # Left face (negative X)
            ((-1, 0, 0), [(-size, -size, -size), (-size, -size, size),
                         (-size, size, size), (-size, size, -size)], self._get_left_facelets(cubie_id)),
            # Top face (positive Y)
            ((0, 1, 0), [(-size, size, size), (size, size, size),
                        (size, size, -size), (-size, size, -size)], self._get_top_facelets(cubie_id)),
            # Bottom face (negative Y)
            ((0, -1, 0), [(-size, -size, -size), (size, -size, -size),
                         (size, -size, size), (-size, -size, size)], self._get_bottom_facelets(cubie_id)),
        ]
        
        for normal, vertices, facelet_idx in faces:
            if facelet_idx is not None and facelet_idx < len(facelets):
                # Set color based on facelet
                color = self._hex_to_rgb(facelets[facelet_idx])
                glColor3f(*color)
                
                # Draw face
                glBegin(GL_QUADS)
                glNormal3f(*normal)
                for vertex in vertices:
                    glVertex3f(*vertex)
                glEnd()
                
                # Draw black edges
                glDisable(GL_LIGHTING)
                glColor3f(0.0, 0.0, 0.0)
                glLineWidth(2.0)
                glBegin(GL_LINE_LOOP)
                for vertex in vertices:
                    glVertex3f(*vertex)
                glEnd()
                glEnable(GL_LIGHTING)
    
    def _draw_cubie_wireframe(self) -> None:
        """Draw wireframe outline of cubie."""
        size = self.cubie_size / 2
        
        # Draw cube wireframe
        glBegin(GL_LINES)
        # Bottom face
        glVertex3f(-size, -size, -size)
        glVertex3f(size, -size, -size)
        glVertex3f(size, -size, -size)
        glVertex3f(size, -size, size)
        glVertex3f(size, -size, size)
        glVertex3f(-size, -size, size)
        glVertex3f(-size, -size, size)
        glVertex3f(-size, -size, -size)
        
        # Top face
        glVertex3f(-size, size, -size)
        glVertex3f(size, size, -size)
        glVertex3f(size, size, -size)
        glVertex3f(size, size, size)
        glVertex3f(size, size, size)
        glVertex3f(-size, size, size)
        glVertex3f(-size, size, size)
        glVertex3f(-size, size, -size)
        
        # Vertical edges
        glVertex3f(-size, -size, -size)
        glVertex3f(-size, size, -size)
        glVertex3f(size, -size, -size)
        glVertex3f(size, size, -size)
        glVertex3f(size, -size, size)
        glVertex3f(size, size, size)
        glVertex3f(-size, -size, size)
        glVertex3f(-size, size, size)
        glEnd()
    
    def _get_front_facelets(self, cubie_id: int) -> Optional[int]:
        """Get facelet index for front face of cubie."""
        # Define facelet indices for front face of each cubie
        front_facelets = [
            20, 23, 26,  # Front face cubies (F1, F2, F3)
            19, 22, 25,  # Front face cubies (F4, F5, F6)
            18, 21, 24,  # Front face cubies (F7, F8, F9)
            47, 50, 53,  # Right face cubies (R7, R8, R9) - adjacent to front
            46, 49, 52,  # Right face cubies (R4, R5, R6) - adjacent to front
            45, 48, 51,  # Right face cubies (R1, R2, R3) - adjacent to front
            38, 41, 44,  # Left face cubies (L7, L8, L9) - adjacent to front
            37, 40, 43,  # Left face cubies (L4, L5, L6) - adjacent to front
            36, 39, 42,  # Left face cubies (L1, L2, L3) - adjacent to front
            9, 12, 15,   # Up face cubies (U7, U8, U9) - adjacent to front
            10, 13, 16,  # Up face cubies (U4, U5, U6) - adjacent to front
            11, 14, 17,  # Up face cubies (U1, U2, U3) - adjacent to front
            27, 30, 33,  # Down face cubies (D1, D2, D3) - adjacent to front
            28, 31, 34,  # Down face cubies (D4, D5, D6) - adjacent to front
            29, 32, 35,  # Down face cubies (D7, D8, D9) - adjacent to front
            8, 5, 2,     # Back face cubies (B9, B6, B3) - adjacent to front
            7, 4, 1,     # Back face cubies (B8, B5, B2) - adjacent to front
            6, 3, 0      # Back face cubies (B7, B4, B1) - adjacent to front
        ]
        
        if 0 <= cubie_id < len(front_facelets):
            return front_facelets[cubie_id]
        return None
    
    def _get_back_facelets(self, cubie_id: int) -> Optional[int]:
        """Get facelet index for back face of cubie."""
        # Define facelet indices for back face of each cubie
        back_facelets = [
            6, 3, 0,     # Back face cubies (B7, B4, B1)
            7, 4, 1,     # Back face cubies (B8, B5, B2)
            8, 5, 2,     # Back face cubies (B9, B6, B3)
            45, 48, 51,  # Left face cubies (L1, L2, L3) - adjacent to back
            46, 49, 52,  # Left face cubies (L4, L5, L6) - adjacent to back
            47, 50, 53,  # Left face cubies (L7, L8, L9) - adjacent to back
            53, 50, 47,  # Right face cubies (R9, R6, R3) - adjacent to back
            52, 49, 46,  # Right face cubies (R8, R5, R2) - adjacent to back
            51, 48, 45,  # Right face cubies (R7, R4, R1) - adjacent to back
            2, 1, 0,     # Up face cubies (U9, U8, U7) - adjacent to back
            5, 4, 3,     # Up face cubies (U6, U5, U4) - adjacent to back
            8, 7, 6,     # Up face cubies (U3, U2, U1) - adjacent to back
            35, 34, 33,  # Down face cubies (D9, D8, D7) - adjacent to back
            32, 31, 30,  # Down face cubies (D6, D5, D4) - adjacent to back
            29, 28, 27,  # Down face cubies (D3, D2, D1) - adjacent to back
            18, 21, 24,  # Front face cubies (F7, F8, F9) - adjacent to back
            19, 22, 25,  # Front face cubies (F4, F5, F6) - adjacent to back
            20, 23, 26   # Front face cubies (F1, F2, F3) - adjacent to back
        ]
        
        if 0 <= cubie_id < len(back_facelets):
            return back_facelets[cubie_id]
        return None
    
    def _get_right_facelets(self, cubie_id: int) -> Optional[int]:
        """Get facelet index for right face of cubie."""
        # Define facelet indices for right face of each cubie
        right_facelets = [
            47, 50, 53,  # Right face cubies (R1, R2, R3)
            46, 49, 52,  # Right face cubies (R4, R5, R6)
            45, 48, 51,  # Right face cubies (R7, R8, R9)
            20, 23, 26,  # Front face cubies (F3, F6, F9) - adjacent to right
            19, 22, 25,  # Front face cubies (F2, F5, F8) - adjacent to right
            18, 21, 24,  # Front face cubies (F1, F4, F7) - adjacent to right
            38, 41, 44,  # Back face cubies (B7, B4, B1) - adjacent to right
            37, 40, 43,  # Back face cubies (B8, B5, B2) - adjacent to right
            36, 39, 42,  # Back face cubies (B9, B6, B3) - adjacent to right
            11, 14, 17,  # Up face cubies (U3, U6, U9) - adjacent to right
            10, 13, 16,  # Up face cubies (U2, U5, U8) - adjacent to right
            9, 12, 15,   # Up face cubies (U1, U4, U7) - adjacent to right
            29, 32, 35,  # Down face cubies (D7, D4, D1) - adjacent to right
            28, 31, 34,  # Down face cubies (D8, D5, D2) - adjacent to right
            27, 30, 33,  # Down face cubies (D9, D6, D3) - adjacent to right
            44, 41, 38,  # Left face cubies (L9, L6, L3) - adjacent to right
            43, 40, 37,  # Left face cubies (L8, L5, L2) - adjacent to right
            42, 39, 36   # Left face cubies (L7, L4, L1) - adjacent to right
        ]
        
        if 0 <= cubie_id < len(right_facelets):
            return right_facelets[cubie_id]
        return None
    
    def _get_left_facelets(self, cubie_id: int) -> Optional[int]:
        """Get facelet index for left face of cubie."""
        # Define facelet indices for left face of each cubie
        left_facelets = [
            38, 41, 44,  # Left face cubies (L1, L2, L3)
            37, 40, 43,  # Left face cubies (L4, L5, L6)
            36, 39, 42,  # Left face cubies (L7, L8, L9)
            18, 21, 24,  # Back face cubies (B3, B6, B9) - adjacent to left
            19, 22, 25,  # Back face cubies (B2, B5, B8) - adjacent to left
            20, 23, 26,  # Back face cubies (B1, B4, B7) - adjacent to left
            47, 50, 53,  # Front face cubies (F7, F4, F1) - adjacent to left
            46, 49, 52,  # Front face cubies (F8, F5, F2) - adjacent to left
            45, 48, 51,  # Front face cubies (F9, F6, F3) - adjacent to left
            9, 12, 15,   # Up face cubies (U7, U4, U1) - adjacent to left
            10, 13, 16,  # Up face cubies (U8, U5, U2) - adjacent to left
            11, 14, 17,  # Up face cubies (U9, U6, U3) - adjacent to left
            27, 30, 33,  # Down face cubies (D1, D4, D7) - adjacent to left
            28, 31, 34,  # Down face cubies (D2, D5, D8) - adjacent to left
            29, 32, 35,  # Down face cubies (D3, D6, D9) - adjacent to left
            51, 48, 45,  # Right face cubies (R3, R6, R9) - adjacent to left
            52, 49, 46,  # Right face cubies (R2, R5, R8) - adjacent to left
            53, 50, 47   # Right face cubies (R1, R4, R7) - adjacent to left
        ]
        
        if 0 <= cubie_id < len(left_facelets):
            return left_facelets[cubie_id]
        return None
    
    def _get_top_facelets(self, cubie_id: int) -> Optional[int]:
        """Get facelet index for top face of cubie."""
        # Define facelet indices for top face of each cubie
        top_facelets = [
            9, 12, 15,   # Up face cubies (U1, U2, U3)
            10, 13, 16,  # Up face cubies (U4, U5, U6)
            11, 14, 17,  # Up face cubies (U7, U8, U9)
            20, 23, 26,  # Front face cubies (F1, F2, F3) - adjacent to up
            19, 22, 25,  # Front face cubies (F4, F5, F6) - adjacent to up
            18, 21, 24,  # Front face cubies (F7, F8, F9) - adjacent to up
            38, 41, 44,  # Back face cubies (B1, B2, B3) - adjacent to up
            37, 40, 43,  # Back face cubies (B4, B5, B6) - adjacent to up
            36, 39, 42,  # Back face cubies (B7, B8, B9) - adjacent to up
            47, 50, 53,  # Right face cubies (R1, R2, R3) - adjacent to up
            46, 49, 52,  # Right face cubies (R4, R5, R6) - adjacent to up
            45, 48, 51,  # Right face cubies (R7, R8, R9) - adjacent to up
            53, 50, 47,  # Left face cubies (L3, L2, L1) - adjacent to up
            52, 49, 46,  # Left face cubies (L6, L5, L4) - adjacent to up
            51, 48, 45,  # Left face cubies (L9, L8, L7) - adjacent to up
            27, 30, 33,  # Down face cubies (D1, D2, D3) - adjacent to up
            28, 31, 34,  # Down face cubies (D4, D5, D6) - adjacent to up
            29, 32, 35   # Down face cubies (D7, D8, D9) - adjacent to up
        ]
        
        if 0 <= cubie_id < len(top_facelets):
            return top_facelets[cubie_id]
        return None
    
    def _get_bottom_facelets(self, cubie_id: int) -> Optional[int]:
        """Get facelet index for bottom face of cubie."""
        # Define facelet indices for bottom face of each cubie
        bottom_facelets = [
            27, 30, 33,  # Down face cubies (D1, D2, D3)
            28, 31, 34,  # Down face cubies (D4, D5, D6)
            29, 32, 35,  # Down face cubies (D7, D8, D9)
            20, 23, 26,  # Front face cubies (F7, F8, F9) - adjacent to down
            19, 22, 25,  # Front face cubies (F4, F5, F6) - adjacent to down
            18, 21, 24,  # Front face cubies (F1, F2, F3) - adjacent to down
            38, 41, 44,  # Back face cubies (B7, B8, B9) - adjacent to down
            37, 40, 43,  # Back face cubies (B4, B5, B6) - adjacent to down
            36, 39, 42,  # Back face cubies (B1, B2, B3) - adjacent to down
            45, 48, 51,  # Right face cubies (R7, R8, R9) - adjacent to down
            46, 49, 52,  # Right face cubies (R4, R5, R6) - adjacent to down
            47, 50, 53,  # Right face cubies (R1, R2, R3) - adjacent to down
            51, 48, 45,  # Left face cubies (L9, L8, L7) - adjacent to down
            52, 49, 46,  # Left face cubies (L6, L5, L4) - adjacent to down
            53, 50, 47,  # Left face cubies (L3, L2, L1) - adjacent to down
            9, 12, 15,   # Up face cubies (U1, U2, U3) - adjacent to down
            10, 13, 16,  # Up face cubies (U4, U5, U6) - adjacent to down
            11, 14, 17   # Up face cubies (U7, U8, U9) - adjacent to down
        ]
        
        if 0 <= cubie_id < len(bottom_facelets):
            return bottom_facelets[cubie_id]
        return None
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[float, float, float]:
        """Convert hex color to RGB tuple (0.0-1.0)."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    
    def set_state(self, state: CubeState) -> None:
        """Set the cube state to render with improved validation and update handling."""
        # Validate input
        if not isinstance(state, CubeState):
            return
        
        # Check if state actually changed
        if self.cube_state is not None and state == self.cube_state:
            return  # No change, no need to update
        
        # Stop any ongoing animation when setting a new state
        if self.animation_timer.isActive():
            self.animation_timer.stop()
            self.animating_move = None
            self.animation_start_state = None
            self.animation_progress = 0.0
        
        # Set the new state
        self.cube_state = state
        
        # Trigger a redraw
        self.update()
    
    def animate_move(self, move: Move, duration_ms: int = 500) -> None:
        """Animate a move on the cube with improved validation and error handling."""
        # Validate inputs
        if not isinstance(move, Move):
            return
        
        if not isinstance(duration_ms, int) or duration_ms <= 0:
            duration_ms = 500
        
        # Stop any existing animation
        if self.animation_timer.isActive():
            self.animation_timer.stop()
        
        self.animating_move = move
        self.animation_start_state = self.cube_state.clone()
        self.animation_duration = duration_ms
        self.animation_progress = 0.0
        
        # Validate that we have a start state
        if self.animation_start_state is None:
            return
        
        # Start animation with 60 FPS target
        self.animation_timer.start(16)
    
    def _update_animation(self) -> None:
        """Update animation frame with smoother interpolation."""
        # Handle edge cases
        if self.animating_move is None or self.animation_start_state is None:
            self.animation_timer.stop()
            return
        
        # Update progress with bounds checking
        self.animation_progress += 16.0 / self.animation_duration
        
        # Ensure progress stays within bounds
        self.animation_progress = min(1.0, max(0.0, self.animation_progress))
        
        # Apply easing function for smoother animation
        # Using ease-in-out cubic function
        if self.animation_progress < 0.5:
            eased_progress = 4 * self.animation_progress * self.animation_progress * self.animation_progress
        else:
            f = (2 * self.animation_progress) - 2
            eased_progress = 0.5 * f * f * f + 1
        
        # Update the cube state during animation
        if self.animation_progress >= 1.0:
            # Animation complete
            self.animation_progress = 1.0
            self.animation_timer.stop()
            
            # Apply the move to the actual state
            self.cube_state = self.animating_move.apply(self.animation_start_state)
            self.animating_move = None
            self.animation_start_state = None
            
            self.animation_finished.emit()
        
        self.update()
    
    def seek_to(self, step_index: int) -> None:
        """Seek to a specific step in the solution."""
        # TODO: Implement step seeking with history
        pass
    
    def highlight_pieces(self, piece_ids: List[int]) -> None:
        """Highlight specific pieces with validation and update trigger."""
        # Validate input
        if not isinstance(piece_ids, list):
            return
        
        # Filter valid piece IDs
        valid_ids = [pid for pid in piece_ids if isinstance(pid, int) and 0 <= pid <= 26]
        self.highlighted_pieces = valid_ids
        self.update()
    
    def clear_highlights(self) -> None:
        """Clear all piece highlights."""
        self.highlighted_pieces = []
        self.hovered_piece = -1
        self.update()
    
    def _on_piece_hovered(self, piece_id: int) -> None:
        """Handle piece hover events with validation."""
        # Validate piece_id
        if not isinstance(piece_id, int) or not (piece_id == -1 or (0 <= piece_id <= 26)):
            return
        
        self.hovered_piece = piece_id
        self.update()
    
    def set_color_scheme(self, scheme: ColorScheme) -> None:
        """Set the color scheme for rendering."""
        self.color_scheme = scheme
        self.update()
    
    def reset_camera(self) -> None:
        """Reset camera to default position."""
        self.camera_distance = 8.0
        self.camera_rotation_x = -25.0
        self.camera_rotation_y = 45.0
        self.camera_pan_x = 0.0
        self.camera_pan_y = 0.0
        self.update()
    
    def mousePressEvent(self, event) -> None:
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            # Implement raycasting to detect which piece was clicked
            piece_id = self._pick_piece(event.pos())
            if piece_id is not None:
                self.piece_clicked.emit(piece_id)
        
        self.last_mouse_pos = event.pos()
    
    def mouseMoveEvent(self, event) -> None:
        """Handle mouse move events for camera control and hover detection with improved stability."""
        # Detect hovered piece even when no buttons are pressed
        if not event.buttons():
            hovered_piece = self._pick_piece(event.pos())
            if hovered_piece is not None:
                self.piece_hovered.emit(hovered_piece)
            else:
                self.piece_hovered.emit(-1)  # No piece hovered
        
        # Handle case where last_mouse_pos is None
        if self.last_mouse_pos is None:
            self.last_mouse_pos = event.pos()
            return
        
        # Calculate delta with bounds checking
        if event.pos() is None or self.last_mouse_pos is None:
            return
            
        dx = event.pos().x() - self.last_mouse_pos.x()
        dy = event.pos().y() - self.last_mouse_pos.y()
        
        # Apply sensitivity with bounds checking
        if abs(dx) > 1000 or abs(dy) > 1000:  # Prevent large jumps
            self.last_mouse_pos = event.pos()
            return
        
        if event.buttons() & Qt.LeftButton:
            # Rotate camera with smoother sensitivity
            self.camera_rotation_y += dx * self.mouse_sensitivity * 0.5
            self.camera_rotation_x += dy * self.mouse_sensitivity * 0.5
            
            # Clamp vertical rotation with smoother limits
            self.camera_rotation_x = max(-89.9, min(89.9, self.camera_rotation_x))
            
        elif event.buttons() & Qt.RightButton:
            # Pan camera with smoother movement
            self.camera_pan_x += dx * 0.005
            self.camera_pan_y -= dy * 0.005
            
            # Limit pan distance to prevent getting lost
            self.camera_pan_x = max(-5.0, min(5.0, self.camera_pan_x))
            self.camera_pan_y = max(-5.0, min(5.0, self.camera_pan_y))
        
        self.last_mouse_pos = event.pos()
        self.update()
    
    def wheelEvent(self, event) -> None:
        """Handle mouse wheel events for zoom with improved sensitivity and bounds."""
        if event.angleDelta() is None:
            return
            
        delta = event.angleDelta().y() / 120.0
        
        # Apply zoom with smoother sensitivity
        zoom_factor = delta * 0.3
        self.camera_distance -= zoom_factor
        
        # Clamp distance with more reasonable bounds
        self.camera_distance = max(2.0, min(30.0, self.camera_distance))
        
        self.update()
    
    def _pick_piece(self, mouse_pos) -> Optional[int]:
        """Pick a piece based on mouse position using raycasting with improved accuracy."""
        # Handle edge case where width or height is zero
        if self.width() <= 0 or self.height() <= 0:
            return None
        
        # Convert mouse position to normalized device coordinates
        x = (2.0 * mouse_pos.x()) / self.width() - 1.0
        y = 1.0 - (2.0 * mouse_pos.y()) / self.height()
        
        # Get the current modelview and projection matrices
        modelview = self._get_modelview_matrix()
        projection = self._get_projection_matrix()
        
        # Create inverse matrices for unprojecting
        try:
            mv_inv = np.linalg.inv(modelview)
            proj_inv = np.linalg.inv(projection)
        except np.linalg.LinAlgError:
            return None
        
        # Create near and far points in clip space
        near_point = np.array([x, y, -1.0, 1.0])
        far_point = np.array([x, y, 1.0, 1.0])
        
        # Unproject to world coordinates
        try:
            near_world = mv_inv @ proj_inv @ near_point
            far_world = mv_inv @ proj_inv @ far_point
        except Exception:
            return None
        
        # Convert to 3D points (handle division by zero)
        if near_world[3] == 0 or far_world[3] == 0:
            return None
            
        near_world = near_world[:3] / near_world[3]
        far_world = far_world[:3] / far_world[3]
        
        # Create ray direction (handle zero length)
        ray_dir = far_world - near_world
        ray_length = np.linalg.norm(ray_dir)
        if ray_length == 0:
            return None
        ray_dir = ray_dir / ray_length
        
        # Test intersection with each cubie
        closest_piece = None
        closest_distance = float('inf')
        
        # Define cubie positions (same as in _render_cube)
        positions = []
        for x in range(-1, 2):
            for y in range(-1, 2):
                for z in range(-1, 2):
                    if x == 0 and y == 0 and z == 0:
                        continue  # Skip center piece
                    positions.append((x, y, z))
        
        # Test each cubie for intersection using axis-aligned bounding box (AABB) test
        for i, pos in enumerate(positions):
            # Calculate cubie center position with scaling
            scaled_pos = np.array([
                pos[0] * (self.cubie_size + self.gap_size),
                pos[1] * (self.cubie_size + self.gap_size),
                pos[2] * (self.cubie_size + self.gap_size)
            ], dtype=float)
            
            # Create AABB for the cubie
            half_size = self.cubie_size / 2.0
            min_bound = scaled_pos - half_size
            max_bound = scaled_pos + half_size
            
            # Ray-AABB intersection test
            t_min = (min_bound[0] - near_world[0]) / ray_dir[0] if ray_dir[0] != 0 else (-np.inf if near_world[0] >= min_bound[0] and near_world[0] <= max_bound[0] else np.inf)
            t_max = (max_bound[0] - near_world[0]) / ray_dir[0] if ray_dir[0] != 0 else (-np.inf if near_world[0] >= min_bound[0] and near_world[0] <= max_bound[0] else np.inf)
            
            if t_min > t_max:
                t_min, t_max = t_max, t_min
                
            ty_min = (min_bound[1] - near_world[1]) / ray_dir[1] if ray_dir[1] != 0 else (-np.inf if near_world[1] >= min_bound[1] and near_world[1] <= max_bound[1] else np.inf)
            ty_max = (max_bound[1] - near_world[1]) / ray_dir[1] if ray_dir[1] != 0 else (-np.inf if near_world[1] >= min_bound[1] and near_world[1] <= max_bound[1] else np.inf)
            
            if ty_min > ty_max:
                ty_min, ty_max = ty_max, ty_min
                
            if (t_min > ty_max) or (ty_min > t_max):
                continue
                
            t_min = max(t_min, ty_min)
            t_max = min(t_max, ty_max)
            
            tz_min = (min_bound[2] - near_world[2]) / ray_dir[2] if ray_dir[2] != 0 else (-np.inf if near_world[2] >= min_bound[2] and near_world[2] <= max_bound[2] else np.inf)
            tz_max = (max_bound[2] - near_world[2]) / ray_dir[2] if ray_dir[2] != 0 else (-np.inf if near_world[2] >= min_bound[2] and near_world[2] <= max_bound[2] else np.inf)
            
            if tz_min > tz_max:
                tz_min, tz_max = tz_max, tz_min
                
            if (t_min > tz_max) or (tz_min > t_max):
                continue
                
            t_min = max(t_min, tz_min)
            t_max = min(t_max, tz_max)
            
            # Check if intersection is in front of camera
            if t_min >= 0:
                # Check if this is closer than previous hits
                if t_min < closest_distance:
                    closest_distance = t_min
                    closest_piece = i
        
        return closest_piece
    
    def _get_modelview_matrix(self) -> np.ndarray:
        """Get current modelview matrix."""
        # Set up camera transformation
        modelview = np.eye(4)
        
        # Apply camera transformations
        # Translation
        modelview[3, 0] = self.camera_pan_x
        modelview[3, 1] = self.camera_pan_y
        modelview[3, 2] = -self.camera_distance
        
        # Rotation around Y axis
        cos_y = math.cos(math.radians(self.camera_rotation_y))
        sin_y = math.sin(math.radians(self.camera_rotation_y))
        rot_y = np.array([
            [cos_y, 0, sin_y, 0],
            [0, 1, 0, 0],
            [-sin_y, 0, cos_y, 0],
            [0, 0, 0, 1]
        ])
        modelview = rot_y @ modelview
        
        # Rotation around X axis
        cos_x = math.cos(math.radians(self.camera_rotation_x))
        sin_x = math.sin(math.radians(self.camera_rotation_x))
        rot_x = np.array([
            [1, 0, 0, 0],
            [0, cos_x, -sin_x, 0],
            [0, sin_x, cos_x, 0],
            [0, 0, 0, 1]
        ])
        modelview = rot_x @ modelview
        
        return modelview
    
    def _get_projection_matrix(self) -> np.ndarray:
        """Get current projection matrix."""
        # Simple perspective projection matrix
        aspect = self.width() / self.height() if self.height() > 0 else 1.0
        fovy = math.radians(45.0)
        near = 0.1
        far = 100.0
        
        f = 1.0 / math.tan(fovy / 2.0)
        
        projection = np.array([
            [f / aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)],
            [0, 0, -1, 0]
        ])
        
        return projection
