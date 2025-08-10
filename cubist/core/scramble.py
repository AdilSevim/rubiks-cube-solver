"""
WCA-compliant scramble generation for 3x3 Rubik's Cube.
"""

import random
from typing import List
from .moves import Move, MoveSequence


def generate_scramble(length: int = 25) -> MoveSequence:
    """
    Generate a WCA-compliant random scramble.
    
    Args:
        length: Number of moves in the scramble (default 25)
        
    Returns:
        MoveSequence representing the scramble
    """
    if length <= 0:
        return MoveSequence([])
    
    # Define move groups to avoid consecutive moves on same face or opposite faces
    move_groups = {
        'R': [Move.R, Move.Rp, Move.R2],
        'L': [Move.L, Move.Lp, Move.L2],
        'U': [Move.U, Move.Up, Move.U2],
        'D': [Move.D, Move.Dp, Move.D2],
        'F': [Move.F, Move.Fp, Move.F2],
        'B': [Move.B, Move.Bp, Move.B2]
    }
    
    # Opposite face pairs
    opposite_faces = {
        'R': 'L', 'L': 'R',
        'U': 'D', 'D': 'U', 
        'F': 'B', 'B': 'F'
    }
    
    faces = list(move_groups.keys())
    scramble_moves = []
    
    last_face = None
    second_last_face = None
    
    for _ in range(length):
        # Get valid faces (not same as last, not opposite of last two)
        valid_faces = []
        
        for face in faces:
            # Can't use same face as last move
            if face == last_face:
                continue
                
            # Can't use opposite face if last two moves were on opposite faces
            if (second_last_face is not None and 
                last_face is not None and
                face == second_last_face and 
                opposite_faces.get(face) == last_face):
                continue
                
            valid_faces.append(face)
        
        # Choose random valid face and move
        chosen_face = random.choice(valid_faces)
        chosen_move = random.choice(move_groups[chosen_face])
        
        scramble_moves.append(chosen_move)
        
        # Update face history
        second_last_face = last_face
        last_face = chosen_face
    
    return MoveSequence(scramble_moves)


def generate_easy_scramble(length: int = 15) -> MoveSequence:
    """
    Generate an easier scramble with fewer moves for beginners.
    
    Args:
        length: Number of moves in the scramble (default 15)
        
    Returns:
        MoveSequence representing the easy scramble
    """
    return generate_scramble(length)


def generate_pattern_scramble(pattern_name: str) -> MoveSequence:
    """
    Generate scrambles for specific cube patterns.
    
    Args:
        pattern_name: Name of the pattern to generate
        
    Returns:
        MoveSequence to create the pattern
    """
    patterns = {
        'checkerboard': "M2 E2 S2",
        'cube_in_cube': "F L F U' R U F2 L2 U' L' B D' B' L2 U",
        'superflip': "R U R' F' R U2 R' U' R U' R' F R2 U' R' U2 R U' R'",
        'four_spots': "F2 B2 R2 L2 U2 D2",
        'six_spots': "U D' R L' F B' U D'",
        'cross': "R2 L2 U2 D2 F2 B2",
        'plus': "R L' U D' F B'",
        'h_pattern': "M2 E2 S2",
        'tetris': "L R F B U D L R",
        'anaconda': "L U B' U' R L' B R' F B' D R"
    }
    
    if pattern_name.lower() not in patterns:
        raise ValueError(f"Unknown pattern: {pattern_name}")
    
    return MoveSequence.parse(patterns[pattern_name.lower()])


def is_valid_scramble(scramble: MoveSequence) -> bool:
    """
    Check if a scramble follows WCA guidelines.
    
    Args:
        scramble: MoveSequence to validate
        
    Returns:
        True if scramble is valid
    """
    if len(scramble) == 0:
        return True
    
    # Check for consecutive moves on same face
    for i in range(len(scramble) - 1):
        current_face = _get_move_face(scramble[i])
        next_face = _get_move_face(scramble[i + 1])
        
        if current_face == next_face:
            return False
    
    # Check for three consecutive moves on opposite faces
    for i in range(len(scramble) - 2):
        face1 = _get_move_face(scramble[i])
        face2 = _get_move_face(scramble[i + 1])
        face3 = _get_move_face(scramble[i + 2])
        
        opposite_faces = {
            'R': 'L', 'L': 'R',
            'U': 'D', 'D': 'U',
            'F': 'B', 'B': 'F'
        }
        
        if (face1 == face3 and 
            opposite_faces.get(face1) == face2):
            return False
    
    return True


def _get_move_face(move: Move) -> str:
    """Get the face letter from a move."""
    return str(move)[0]


def scramble_to_string(scramble: MoveSequence) -> str:
    """Convert scramble to standard string format."""
    return str(scramble)


def scramble_from_string(scramble_str: str) -> MoveSequence:
    """Parse scramble from string format."""
    return MoveSequence.parse(scramble_str)


class ScrambleGenerator:
    """Advanced scramble generator with state tracking."""
    
    def __init__(self, seed: int = None) -> None:
        """Initialize with optional random seed."""
        if seed is not None:
            random.seed(seed)
        self.last_scrambles: List[MoveSequence] = []
        self.max_history = 100
    
    def generate(self, length: int = 25, avoid_repetition: bool = True) -> MoveSequence:
        """
        Generate a scramble with optional repetition avoidance.
        
        Args:
            length: Number of moves
            avoid_repetition: Try to avoid recently generated scrambles
            
        Returns:
            MoveSequence scramble
        """
        max_attempts = 50
        attempts = 0
        
        while attempts < max_attempts:
            scramble = generate_scramble(length)
            
            if not avoid_repetition or scramble not in self.last_scrambles:
                # Add to history
                self.last_scrambles.append(scramble)
                if len(self.last_scrambles) > self.max_history:
                    self.last_scrambles.pop(0)
                
                return scramble
            
            attempts += 1
        
        # If we can't avoid repetition, just return a valid scramble
        scramble = generate_scramble(length)
        self.last_scrambles.append(scramble)
        if len(self.last_scrambles) > self.max_history:
            self.last_scrambles.pop(0)
        
        return scramble
    
    def generate_session(self, count: int, length: int = 25) -> List[MoveSequence]:
        """Generate multiple scrambles for a session."""
        return [self.generate(length) for _ in range(count)]
    
    def clear_history(self) -> None:
        """Clear scramble history."""
        self.last_scrambles.clear()
