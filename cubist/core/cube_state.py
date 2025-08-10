"""
Cube state representation using cubie-based model with facelet conversion.
"""

from typing import List, Tuple, Optional, Dict
import numpy as np
from dataclasses import dataclass
from .color_scheme import ColorScheme


@dataclass
class CubeState:
    """
    Cubie-based representation of a 3x3 Rubik's Cube state.
    
    Uses permutation and orientation arrays for corners and edges:
    - corner_perm[8]: permutation of 8 corners (0-7)
    - corner_orient[8]: orientation of each corner (0, 1, 2)
    - edge_perm[12]: permutation of 12 edges (0-11)  
    - edge_orient[12]: orientation of each edge (0, 1)
    """
    
    corner_perm: np.ndarray
    corner_orient: np.ndarray
    edge_perm: np.ndarray
    edge_orient: np.ndarray
    
    def __init__(self, 
                 corner_perm: Optional[List[int]] = None,
                 corner_orient: Optional[List[int]] = None,
                 edge_perm: Optional[List[int]] = None,
                 edge_orient: Optional[List[int]] = None) -> None:
        """Initialize cube state with optional arrays."""
        self.corner_perm = np.array(corner_perm if corner_perm else list(range(8)), dtype=np.int8)
        self.corner_orient = np.array(corner_orient if corner_orient else [0] * 8, dtype=np.int8)
        self.edge_perm = np.array(edge_perm if edge_perm else list(range(12)), dtype=np.int8)
        self.edge_orient = np.array(edge_orient if edge_orient else [0] * 12, dtype=np.int8)
    
    @staticmethod
    def solved() -> "CubeState":
        """Return a solved cube state."""
        return CubeState()
    
    def clone(self) -> "CubeState":
        """Create a deep copy of this cube state."""
        return CubeState(
            corner_perm=self.corner_perm.copy(),
            corner_orient=self.corner_orient.copy(),
            edge_perm=self.edge_perm.copy(),
            edge_orient=self.edge_orient.copy()
        )
    
    def is_solved(self) -> bool:
        """Check if the cube is in solved state."""
        return (np.array_equal(self.corner_perm, np.arange(8)) and
                np.array_equal(self.corner_orient, np.zeros(8)) and
                np.array_equal(self.edge_perm, np.arange(12)) and
                np.array_equal(self.edge_orient, np.zeros(12)))
    
    def __eq__(self, other: object) -> bool:
        """Check equality with another CubeState."""
        if not isinstance(other, CubeState):
            return False
        return (np.array_equal(self.corner_perm, other.corner_perm) and
                np.array_equal(self.corner_orient, other.corner_orient) and
                np.array_equal(self.edge_perm, other.edge_perm) and
                np.array_equal(self.edge_orient, other.edge_orient))
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries."""
        return hash((
            tuple(self.corner_perm),
            tuple(self.corner_orient),
            tuple(self.edge_perm),
            tuple(self.edge_orient)
        ))
    
    @staticmethod
    def from_facelets(facelets: List[str]) -> "CubeState":
        """
        Convert from facelet representation to cubie representation.
        
        Args:
            facelets: List of 54 facelet colors in order:
                     U1-U9, R1-R9, F1-F9, D1-D9, L1-L9, B1-B9
        
        Returns:
            CubeState object
        """
        if len(facelets) != 54:
            raise ValueError(f"Expected 54 facelets, got {len(facelets)}")
        
        # Define facelet to cubie mappings
        # Corner positions: (face1, pos1, face2, pos2, face3, pos3)
        corner_facelets = [
            (0, 0, 1, 0, 2, 2),  # URF
            (0, 2, 2, 0, 4, 2),  # UFL  
            (0, 8, 4, 0, 5, 2),  # ULB
            (0, 6, 5, 0, 1, 2),  # UBR
            (3, 2, 2, 8, 1, 6),  # DFR
            (3, 0, 4, 8, 2, 6),  # DLF
            (3, 6, 5, 8, 4, 6),  # DBL
            (3, 8, 1, 8, 5, 6),  # DRB
        ]
        
        # Edge positions: (face1, pos1, face2, pos2)
        edge_facelets = [
            (0, 1, 1, 1),  # UR
            (0, 5, 2, 1),  # UF
            (0, 7, 4, 1),  # UL
            (0, 3, 5, 1),  # UB
            (3, 1, 1, 7),  # DR
            (3, 5, 2, 7),  # DF
            (3, 7, 4, 7),  # DL
            (3, 3, 5, 7),  # DB
            (2, 5, 1, 3),  # FR
            (2, 3, 4, 5),  # FL
            (4, 3, 5, 5),  # BL
            (5, 3, 1, 5),  # BR
        ]
        
        # Get center colors to determine face mapping
        centers = [facelets[4], facelets[13], facelets[22], facelets[31], facelets[40], facelets[49]]
        
        # Find corner permutations and orientations
        corner_perm = []
        corner_orient = []
        
        for i, (f1, p1, f2, p2, f3, p3) in enumerate(corner_facelets):
            # Get the three colors of this corner
            colors = [facelets[f1*9 + p1], facelets[f2*9 + p2], facelets[f3*9 + p3]]
            
            # Find which solved corner this matches
            solved_corner = -1
            orientation = 0
            
            for j, (sf1, sp1, sf2, sp2, sf3, sp3) in enumerate(corner_facelets):
                solved_colors = [centers[sf1], centers[sf2], centers[sf3]]
                
                # Check all three orientations
                for orient in range(3):
                    rotated_colors = [colors[(k + orient) % 3] for k in range(3)]
                    if rotated_colors == solved_colors:
                        solved_corner = j
                        orientation = orient
                        break
                
                if solved_corner != -1:
                    break
            
            if solved_corner == -1:
                raise ValueError(f"Invalid corner at position {i}")
            
            corner_perm.append(solved_corner)
            corner_orient.append(orientation)
        
        # Find edge permutations and orientations
        edge_perm = []
        edge_orient = []
        
        for i, (f1, p1, f2, p2) in enumerate(edge_facelets):
            # Get the two colors of this edge
            colors = [facelets[f1*9 + p1], facelets[f2*9 + p2]]
            
            # Find which solved edge this matches
            solved_edge = -1
            orientation = 0
            
            for j, (sf1, sp1, sf2, sp2) in enumerate(edge_facelets):
                solved_colors = [centers[sf1], centers[sf2]]
                
                # Check both orientations
                if colors == solved_colors:
                    solved_edge = j
                    orientation = 0
                    break
                elif colors == [solved_colors[1], solved_colors[0]]:
                    solved_edge = j
                    orientation = 1
                    break
            
            if solved_edge == -1:
                raise ValueError(f"Invalid edge at position {i}")
            
            edge_perm.append(solved_edge)
            edge_orient.append(orientation)
        
        return CubeState(corner_perm, corner_orient, edge_perm, edge_orient)
    
    def to_facelets(self, scheme: ColorScheme) -> List[str]:
        """
        Convert from cubie representation to facelet representation.
        
        Args:
            scheme: Color scheme to use for conversion
            
        Returns:
            List of 54 facelet colors
        """
        # Initialize with center colors
        facelets = [''] * 54
        centers = ['U', 'R', 'F', 'D', 'L', 'B']
        center_positions = [4, 13, 22, 31, 40, 49]
        
        for i, center in enumerate(centers):
            facelets[center_positions[i]] = getattr(scheme, center)
        
        # Corner facelet mappings (same as in from_facelets)
        corner_facelets = [
            (0, 0, 1, 0, 2, 2),  # URF
            (0, 2, 2, 0, 4, 2),  # UFL  
            (0, 8, 4, 0, 5, 2),  # ULB
            (0, 6, 5, 0, 1, 2),  # UBR
            (3, 2, 2, 8, 1, 6),  # DFR
            (3, 0, 4, 8, 2, 6),  # DLF
            (3, 6, 5, 8, 4, 6),  # DBL
            (3, 8, 1, 8, 5, 6),  # DRB
        ]
        
        # Edge facelet mappings
        edge_facelets = [
            (0, 1, 1, 1),  # UR
            (0, 5, 2, 1),  # UF
            (0, 7, 4, 1),  # UL
            (0, 3, 5, 1),  # UB
            (3, 1, 1, 7),  # DR
            (3, 5, 2, 7),  # DF
            (3, 7, 4, 7),  # DL
            (3, 3, 5, 7),  # DB
            (2, 5, 1, 3),  # FR
            (2, 3, 4, 5),  # FL
            (4, 3, 5, 5),  # BL
            (5, 3, 1, 5),  # BR
        ]
        
        # Fill corner facelets
        for i in range(8):
            corner_pos = self.corner_perm[i]
            orientation = self.corner_orient[i]
            
            # Get solved corner colors
            sf1, sp1, sf2, sp2, sf3, sp3 = corner_facelets[corner_pos]
            solved_colors = [getattr(scheme, centers[sf1]), 
                           getattr(scheme, centers[sf2]), 
                           getattr(scheme, centers[sf3])]
            
            # Apply orientation
            oriented_colors = [solved_colors[(j - orientation) % 3] for j in range(3)]
            
            # Set facelet colors
            f1, p1, f2, p2, f3, p3 = corner_facelets[i]
            facelets[f1*9 + p1] = oriented_colors[0]
            facelets[f2*9 + p2] = oriented_colors[1]
            facelets[f3*9 + p3] = oriented_colors[2]
        
        # Fill edge facelets
        for i in range(12):
            edge_pos = self.edge_perm[i]
            orientation = self.edge_orient[i]
            
            # Get solved edge colors
            sf1, sp1, sf2, sp2 = edge_facelets[edge_pos]
            solved_colors = [getattr(scheme, centers[sf1]), 
                           getattr(scheme, centers[sf2])]
            
            # Apply orientation
            if orientation == 1:
                solved_colors = [solved_colors[1], solved_colors[0]]
            
            # Set facelet colors
            f1, p1, f2, p2 = edge_facelets[i]
            facelets[f1*9 + p1] = solved_colors[0]
            facelets[f2*9 + p2] = solved_colors[1]
        
        return facelets
    
    def apply_move(self, move: "Move") -> "CubeState":
        """Apply a move to this state and return the new state."""
        from .moves import Move
        
        # Move transformation tables
        # Each move defines how corners and edges are permuted and oriented
        
        # R move transformations
        if move == Move.R:
            return self._apply_r_move()
        elif move == Move.Rp:
            return self._apply_r_move()._apply_r_move()._apply_r_move()
        elif move == Move.R2:
            return self._apply_r_move()._apply_r_move()
        
        # Similar for other moves...
        # For brevity, implementing key moves first
        elif move == Move.U:
            return self._apply_u_move()
        elif move == Move.Up:
            return self._apply_u_move()._apply_u_move()._apply_u_move()
        elif move == Move.U2:
            return self._apply_u_move()._apply_u_move()
        
        elif move == Move.F:
            return self._apply_f_move()
        elif move == Move.Fp:
            return self._apply_f_move()._apply_f_move()._apply_f_move()
        elif move == Move.F2:
            return self._apply_f_move()._apply_f_move()
        
        # Wide moves (for now, treat as regular moves - simplified implementation)
        elif move == Move.r:
            return self._apply_r_move()
        elif move == Move.rp:
            return self._apply_r_move()._apply_r_move()._apply_r_move()
        elif move == Move.r2:
            return self._apply_r_move()._apply_r_move()
        elif move == Move.f:
            return self._apply_f_move()
        elif move == Move.fp:
            return self._apply_f_move()._apply_f_move()._apply_f_move()
        elif move == Move.f2:
            return self._apply_f_move()._apply_f_move()
        elif move == Move.u:
            return self._apply_u_move()
        elif move == Move.up:
            return self._apply_u_move()._apply_u_move()._apply_u_move()
        elif move == Move.u2:
            return self._apply_u_move()._apply_u_move()
        
        # Add other moves as needed
        else:
            # For now, return copy for unimplemented moves
            # TODO: Implement all remaining moves (L, D, B and their wide variants)
            return self.clone()
    
    def _apply_r_move(self) -> "CubeState":
        """Apply R move transformation."""
        new_state = self.clone()
        
        # R move corner permutation cycle: 0->3->7->4->0
        corner_cycle = [0, 3, 7, 4]
        temp_perm = new_state.corner_perm[corner_cycle[0]]
        temp_orient = new_state.corner_orient[corner_cycle[0]]
        
        for i in range(3):
            new_state.corner_perm[corner_cycle[i]] = new_state.corner_perm[corner_cycle[i+1]]
            new_state.corner_orient[corner_cycle[i]] = new_state.corner_orient[corner_cycle[i+1]]
        
        new_state.corner_perm[corner_cycle[3]] = temp_perm
        new_state.corner_orient[corner_cycle[3]] = temp_orient
        
        # R move edge permutation cycle: 0->8->4->11->0
        edge_cycle = [0, 8, 4, 11]
        temp_perm = new_state.edge_perm[edge_cycle[0]]
        temp_orient = new_state.edge_orient[edge_cycle[0]]
        
        for i in range(3):
            new_state.edge_perm[edge_cycle[i]] = new_state.edge_perm[edge_cycle[i+1]]
            new_state.edge_orient[edge_cycle[i]] = new_state.edge_orient[edge_cycle[i+1]]
        
        new_state.edge_perm[edge_cycle[3]] = temp_perm
        new_state.edge_orient[edge_cycle[3]] = temp_orient
        
        return new_state
    
    def _apply_u_move(self) -> "CubeState":
        """Apply U move transformation."""
        new_state = self.clone()
        
        # U move corner permutation cycle: 0->1->2->3->0
        corner_cycle = [0, 1, 2, 3]
        temp_perm = new_state.corner_perm[corner_cycle[0]]
        temp_orient = new_state.corner_orient[corner_cycle[0]]
        
        for i in range(3):
            new_state.corner_perm[corner_cycle[i]] = new_state.corner_perm[corner_cycle[i+1]]
            new_state.corner_orient[corner_cycle[i]] = new_state.corner_orient[corner_cycle[i+1]]
        
        new_state.corner_perm[corner_cycle[3]] = temp_perm
        new_state.corner_orient[corner_cycle[3]] = temp_orient
        
        # U move edge permutation cycle: 0->1->2->3->0
        edge_cycle = [0, 1, 2, 3]
        temp_perm = new_state.edge_perm[edge_cycle[0]]
        temp_orient = new_state.edge_orient[edge_cycle[0]]
        
        for i in range(3):
            new_state.edge_perm[edge_cycle[i]] = new_state.edge_perm[edge_cycle[i+1]]
            new_state.edge_orient[edge_cycle[i]] = new_state.edge_orient[edge_cycle[i+1]]
        
        new_state.edge_perm[edge_cycle[3]] = temp_perm
        new_state.edge_orient[edge_cycle[3]] = temp_orient
        
        return new_state
    
    def _apply_f_move(self) -> "CubeState":
        """Apply F move transformation."""
        new_state = self.clone()
        
        # F move corner permutation cycle: 0->4->5->1->0
        corner_cycle = [0, 4, 5, 1]
        temp_perm = new_state.corner_perm[corner_cycle[0]]
        temp_orient = new_state.corner_orient[corner_cycle[0]]
        
        for i in range(3):
            new_state.corner_perm[corner_cycle[i]] = new_state.corner_perm[corner_cycle[i+1]]
            # F move also changes corner orientation
            new_state.corner_orient[corner_cycle[i]] = (new_state.corner_orient[corner_cycle[i+1]] + 1) % 3
        
        new_state.corner_perm[corner_cycle[3]] = temp_perm
        new_state.corner_orient[corner_cycle[3]] = (temp_orient + 1) % 3
        
        # F move edge permutation cycle: 1->8->5->9->1
        edge_cycle = [1, 8, 5, 9]
        temp_perm = new_state.edge_perm[edge_cycle[0]]
        temp_orient = new_state.edge_orient[edge_cycle[0]]
        
        for i in range(3):
            new_state.edge_perm[edge_cycle[i]] = new_state.edge_perm[edge_cycle[i+1]]
            # F move flips certain edges
            if edge_cycle[i] in [1, 5]:  # UF and DF edges get flipped
                new_state.edge_orient[edge_cycle[i]] = (new_state.edge_orient[edge_cycle[i+1]] + 1) % 2
            else:
                new_state.edge_orient[edge_cycle[i]] = new_state.edge_orient[edge_cycle[i+1]]
        
        new_state.edge_perm[edge_cycle[3]] = temp_perm
        if edge_cycle[3] in [1, 5]:
            new_state.edge_orient[edge_cycle[3]] = (temp_orient + 1) % 2
        else:
            new_state.edge_orient[edge_cycle[3]] = temp_orient
        
        return new_state
