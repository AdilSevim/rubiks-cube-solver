"""
Move definitions and operations for Rubik's Cube using Singmaster notation.
"""

from enum import Enum, auto
from typing import List, Optional
import re


class Move(Enum):
    """Singmaster notation moves for 3x3 Rubik's Cube."""
    
    # Face turns
    R = auto()   # Right clockwise
    Rp = auto()  # Right counter-clockwise (R')
    R2 = auto()  # Right 180°
    
    L = auto()   # Left clockwise
    Lp = auto()  # Left counter-clockwise (L')
    L2 = auto()  # Left 180°
    
    U = auto()   # Up clockwise
    Up = auto()  # Up counter-clockwise (U')
    U2 = auto()  # Up 180°
    
    D = auto()   # Down clockwise
    Dp = auto()  # Down counter-clockwise (D')
    D2 = auto()  # Down 180°
    
    F = auto()   # Front clockwise
    Fp = auto()  # Front counter-clockwise (F')
    F2 = auto()  # Front 180°
    
    B = auto()   # Back clockwise
    Bp = auto()  # Back counter-clockwise (B')
    B2 = auto()  # Back 180°
    
    # Wide moves (lowercase)
    r = auto()   # Right wide clockwise
    rp = auto()  # Right wide counter-clockwise (r')
    r2 = auto()  # Right wide 180°
    
    l = auto()   # Left wide clockwise
    lp = auto()  # Left wide counter-clockwise (l')
    l2 = auto()  # Left wide 180°
    
    u = auto()   # Up wide clockwise
    up = auto()  # Up wide counter-clockwise (u')
    u2 = auto()  # Up wide 180°
    
    d = auto()   # Down wide clockwise
    dp = auto()  # Down wide counter-clockwise (d')
    d2 = auto()  # Down wide 180°
    
    f = auto()   # Front wide clockwise
    fp = auto()  # Front wide counter-clockwise (f')
    f2 = auto()  # Front wide 180°
    
    b = auto()   # Back wide clockwise
    bp = auto()  # Back wide counter-clockwise (b')
    b2 = auto()  # Back wide 180°

    def __str__(self) -> str:
        """String representation using standard notation."""
        move_map = {
            Move.R: "R", Move.Rp: "R'", Move.R2: "R2",
            Move.L: "L", Move.Lp: "L'", Move.L2: "L2",
            Move.U: "U", Move.Up: "U'", Move.U2: "U2",
            Move.D: "D", Move.Dp: "D'", Move.D2: "D2",
            Move.F: "F", Move.Fp: "F'", Move.F2: "F2",
            Move.B: "B", Move.Bp: "B'", Move.B2: "B2",
            # Wide moves
            Move.r: "r", Move.rp: "r'", Move.r2: "r2",
            Move.l: "l", Move.lp: "l'", Move.l2: "l2",
            Move.u: "u", Move.up: "u'", Move.u2: "u2",
            Move.d: "d", Move.dp: "d'", Move.d2: "d2",
            Move.f: "f", Move.fp: "f'", Move.f2: "f2",
            Move.b: "b", Move.bp: "b'", Move.b2: "b2",
        }
        return move_map[self]

    def inverse(self) -> "Move":
        """Return the inverse of this move."""
        inverse_map = {
            Move.R: Move.Rp, Move.Rp: Move.R, Move.R2: Move.R2,
            Move.L: Move.Lp, Move.Lp: Move.L, Move.L2: Move.L2,
            Move.U: Move.Up, Move.Up: Move.U, Move.U2: Move.U2,
            Move.D: Move.Dp, Move.Dp: Move.D, Move.D2: Move.D2,
            Move.F: Move.Fp, Move.Fp: Move.F, Move.F2: Move.F2,
            Move.B: Move.Bp, Move.Bp: Move.B, Move.B2: Move.B2,
            # Wide moves
            Move.r: Move.rp, Move.rp: Move.r, Move.r2: Move.r2,
            Move.l: Move.lp, Move.lp: Move.l, Move.l2: Move.l2,
            Move.u: Move.up, Move.up: Move.u, Move.u2: Move.u2,
            Move.d: Move.dp, Move.dp: Move.d, Move.d2: Move.d2,
            Move.f: Move.fp, Move.fp: Move.f, Move.f2: Move.f2,
            Move.b: Move.bp, Move.bp: Move.b, Move.b2: Move.b2,
        }
        return inverse_map[self]

    def apply(self, state: "CubeState") -> "CubeState":
        """Apply this move to a cube state and return the new state."""
        from .cube_state import CubeState
        return state.apply_move(self)

    @staticmethod
    def from_string(move_str: str) -> "Move":
        """Parse a move from string notation."""
        move_str = move_str.strip()
        string_map = {
            "R": Move.R, "R'": Move.Rp, "R2": Move.R2,
            "L": Move.L, "L'": Move.Lp, "L2": Move.L2,
            "U": Move.U, "U'": Move.Up, "U2": Move.U2,
            "D": Move.D, "D'": Move.Dp, "D2": Move.D2,
            "F": Move.F, "F'": Move.Fp, "F2": Move.F2,
            "B": Move.B, "B'": Move.Bp, "B2": Move.B2,
            # Wide moves
            "r": Move.r, "r'": Move.rp, "r2": Move.r2,
            "l": Move.l, "l'": Move.lp, "l2": Move.l2,
            "u": Move.u, "u'": Move.up, "u2": Move.u2,
            "d": Move.d, "d'": Move.dp, "d2": Move.d2,
            "f": Move.f, "f'": Move.fp, "f2": Move.f2,
            "b": Move.b, "b'": Move.bp, "b2": Move.b2,
        }
        if move_str not in string_map:
            raise ValueError(f"Invalid move notation: {move_str}")
        return string_map[move_str]


class MoveSequence:
    """A sequence of moves with parsing and manipulation capabilities."""
    
    def __init__(self, moves: List[Move]) -> None:
        """Initialize with a list of moves."""
        self.moves = moves.copy()
    
    def __len__(self) -> int:
        """Return the number of moves in the sequence."""
        return len(self.moves)
    
    def __iter__(self):
        """Iterate over moves."""
        return iter(self.moves)
    
    def __getitem__(self, index: int) -> Move:
        """Get move at index."""
        return self.moves[index]
    
    def __str__(self) -> str:
        """String representation of the move sequence."""
        return " ".join(str(move) for move in self.moves)
    
    def __eq__(self, other: object) -> bool:
        """Check equality with another MoveSequence."""
        if not isinstance(other, MoveSequence):
            return False
        return self.moves == other.moves
    
    @staticmethod
    def parse(move_string: str) -> "MoveSequence":
        """Parse a move sequence from string notation."""
        if not move_string.strip():
            return MoveSequence([])
        
        # Split by whitespace and filter empty strings
        move_tokens = [token.strip() for token in re.split(r'\s+', move_string.strip()) if token.strip()]
        
        moves = []
        for token in move_tokens:
            try:
                moves.append(Move.from_string(token))
            except ValueError as e:
                raise ValueError(f"Invalid move sequence: {e}")
        
        return MoveSequence(moves)
    
    def to_str(self) -> str:
        """Convert to string representation."""
        return str(self)
    
    def inverse(self) -> "MoveSequence":
        """Return the inverse sequence (reversed with each move inverted)."""
        return MoveSequence([move.inverse() for move in reversed(self.moves)])
    
    def simplify(self) -> "MoveSequence":
        """Simplify the sequence by combining consecutive moves of the same face."""
        if not self.moves:
            return MoveSequence([])
        
        simplified = []
        i = 0
        
        while i < len(self.moves):
            current_move = self.moves[i]
            face = self._get_face(current_move)
            count = self._get_turn_count(current_move)
            
            # Look ahead for same face moves
            j = i + 1
            while j < len(self.moves) and self._get_face(self.moves[j]) == face:
                count += self._get_turn_count(self.moves[j])
                j += 1
            
            # Normalize count (0, 1, 2, 3 -> 0, 1, 2, 1 respectively)
            count = count % 4
            if count == 3:
                count = -1  # Counter-clockwise
            
            # Add the simplified move if not identity
            if count != 0:
                simplified.append(self._create_move(face, count))
            
            i = j
        
        return MoveSequence(simplified)
    
    def _get_face(self, move: Move) -> str:
        """Get the face letter from a move."""
        move_str = str(move)
        return move_str[0]
    
    def _get_turn_count(self, move: Move) -> int:
        """Get the turn count from a move (1, -1, or 2)."""
        move_str = str(move)
        if "'" in move_str:
            return -1
        elif "2" in move_str:
            return 2
        else:
            return 1
    
    def _create_move(self, face: str, count: int) -> Move:
        """Create a move from face and turn count."""
        if count == 1:
            suffix = ""
        elif count == -1:
            suffix = "'"
        elif count == 2:
            suffix = "2"
        else:
            raise ValueError(f"Invalid turn count: {count}")
        
        return Move.from_string(f"{face}{suffix}")
    
    def append(self, move: Move) -> None:
        """Append a move to the sequence."""
        self.moves.append(move)
    
    def extend(self, other: "MoveSequence") -> None:
        """Extend with another sequence."""
        self.moves.extend(other.moves)
    
    def copy(self) -> "MoveSequence":
        """Return a copy of this sequence."""
        return MoveSequence(self.moves)
    
    def apply_to(self, state: "CubeState") -> "CubeState":
        """Apply this sequence to a cube state."""
        from .cube_state import CubeState
        current_state = state
        for move in self.moves:
            current_state = move.apply(current_state)
        return current_state
