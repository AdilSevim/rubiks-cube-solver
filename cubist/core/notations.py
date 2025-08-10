"""
Notation parsing, formatting, and manipulation utilities.
"""

import re
from typing import List, Optional, Dict
from .moves import Move, MoveSequence


def parse_moves(notation: str) -> MoveSequence:
    """
    Parse move notation string into MoveSequence.
    
    Args:
        notation: String containing moves in Singmaster notation
        
    Returns:
        MoveSequence object
        
    Raises:
        ValueError: If notation contains invalid moves
    """
    return MoveSequence.parse(notation)


def format_moves(sequence: MoveSequence, 
                line_length: int = 80,
                moves_per_line: int = 15) -> str:
    """
    Format move sequence for display with line wrapping.
    
    Args:
        sequence: MoveSequence to format
        line_length: Maximum characters per line
        moves_per_line: Maximum moves per line
        
    Returns:
        Formatted string with line breaks
    """
    if len(sequence) == 0:
        return ""
    
    moves_str = str(sequence)
    moves_list = moves_str.split()
    
    lines = []
    current_line = []
    current_length = 0
    
    for move in moves_list:
        move_length = len(move) + (1 if current_line else 0)  # +1 for space
        
        if (len(current_line) >= moves_per_line or 
            current_length + move_length > line_length):
            if current_line:
                lines.append(" ".join(current_line))
                current_line = []
                current_length = 0
        
        current_line.append(move)
        current_length += move_length
    
    if current_line:
        lines.append(" ".join(current_line))
    
    return "\n".join(lines)


def simplify_sequence(sequence: MoveSequence) -> MoveSequence:
    """
    Simplify a move sequence by combining consecutive moves.
    
    Args:
        sequence: MoveSequence to simplify
        
    Returns:
        Simplified MoveSequence
    """
    return sequence.simplify()


def invert_sequence(sequence: MoveSequence) -> MoveSequence:
    """
    Get the inverse of a move sequence.
    
    Args:
        sequence: MoveSequence to invert
        
    Returns:
        Inverse MoveSequence
    """
    return sequence.inverse()


def combine_sequences(*sequences: MoveSequence) -> MoveSequence:
    """
    Combine multiple move sequences into one.
    
    Args:
        sequences: Variable number of MoveSequence objects
        
    Returns:
        Combined MoveSequence
    """
    combined = MoveSequence([])
    for seq in sequences:
        combined.extend(seq)
    return combined


def count_moves(sequence: MoveSequence) -> Dict[str, int]:
    """
    Count different types of moves in a sequence.
    
    Args:
        sequence: MoveSequence to analyze
        
    Returns:
        Dictionary with move counts
    """
    counts = {
        'total': len(sequence),
        'quarter_turns': 0,
        'half_turns': 0,
        'face_counts': {'R': 0, 'L': 0, 'U': 0, 'D': 0, 'F': 0, 'B': 0}
    }
    
    for move in sequence:
        move_str = str(move)
        face = move_str[0]
        
        counts['face_counts'][face] += 1
        
        if '2' in move_str:
            counts['half_turns'] += 1
        else:
            counts['quarter_turns'] += 1
    
    return counts


def extract_subsequence(sequence: MoveSequence, 
                       start: int, 
                       end: Optional[int] = None) -> MoveSequence:
    """
    Extract a subsequence from a move sequence.
    
    Args:
        sequence: Source MoveSequence
        start: Starting index (inclusive)
        end: Ending index (exclusive), None for end of sequence
        
    Returns:
        Extracted MoveSequence
    """
    if end is None:
        end = len(sequence)
    
    if start < 0 or start >= len(sequence):
        raise ValueError(f"Start index {start} out of range")
    
    if end < start or end > len(sequence):
        raise ValueError(f"End index {end} out of range")
    
    return MoveSequence(sequence.moves[start:end])


def find_patterns(sequence: MoveSequence, pattern: MoveSequence) -> List[int]:
    """
    Find all occurrences of a pattern within a sequence.
    
    Args:
        sequence: MoveSequence to search in
        pattern: MoveSequence pattern to find
        
    Returns:
        List of starting indices where pattern occurs
    """
    if len(pattern) == 0 or len(pattern) > len(sequence):
        return []
    
    matches = []
    pattern_moves = pattern.moves
    
    for i in range(len(sequence) - len(pattern) + 1):
        if sequence.moves[i:i + len(pattern)] == pattern_moves:
            matches.append(i)
    
    return matches


def replace_pattern(sequence: MoveSequence, 
                   pattern: MoveSequence, 
                   replacement: MoveSequence) -> MoveSequence:
    """
    Replace all occurrences of a pattern with a replacement.
    
    Args:
        sequence: MoveSequence to modify
        pattern: Pattern to replace
        replacement: Replacement sequence
        
    Returns:
        Modified MoveSequence
    """
    if len(pattern) == 0:
        return sequence.copy()
    
    result_moves = []
    i = 0
    
    while i < len(sequence):
        # Check if pattern matches at current position
        if (i + len(pattern) <= len(sequence) and 
            sequence.moves[i:i + len(pattern)] == pattern.moves):
            # Add replacement
            result_moves.extend(replacement.moves)
            i += len(pattern)
        else:
            # Add current move
            result_moves.append(sequence.moves[i])
            i += 1
    
    return MoveSequence(result_moves)


def analyze_efficiency(sequence: MoveSequence) -> Dict[str, any]:
    """
    Analyze the efficiency of a move sequence.
    
    Args:
        sequence: MoveSequence to analyze
        
    Returns:
        Dictionary with efficiency metrics
    """
    if len(sequence) == 0:
        return {
            'total_moves': 0,
            'efficiency_score': 1.0,
            'redundancies': [],
            'suggestions': []
        }
    
    simplified = sequence.simplify()
    redundancies = []
    suggestions = []
    
    # Check for obvious redundancies
    if len(simplified) < len(sequence):
        redundancies.append(f"Can be simplified from {len(sequence)} to {len(simplified)} moves")
        suggestions.append("Use sequence.simplify() to reduce move count")
    
    # Check for repeated patterns
    move_counts = count_moves(sequence)
    for face, count in move_counts['face_counts'].items():
        if count > len(sequence) * 0.3:  # More than 30% of moves on one face
            suggestions.append(f"High frequency of {face} moves ({count}) - consider alternative algorithms")
    
    # Calculate efficiency score (lower is better)
    efficiency_score = len(sequence) / max(1, len(simplified))
    
    return {
        'total_moves': len(sequence),
        'simplified_moves': len(simplified),
        'efficiency_score': efficiency_score,
        'redundancies': redundancies,
        'suggestions': suggestions,
        'move_distribution': move_counts['face_counts']
    }


def convert_notation(sequence: MoveSequence, 
                    from_notation: str = "singmaster",
                    to_notation: str = "singmaster") -> str:
    """
    Convert between different notation systems.
    
    Args:
        sequence: MoveSequence to convert
        from_notation: Source notation system
        to_notation: Target notation system
        
    Returns:
        String in target notation
        
    Note: Currently only supports Singmaster notation
    """
    if from_notation != "singmaster" or to_notation != "singmaster":
        raise NotImplementedError("Only Singmaster notation is currently supported")
    
    return str(sequence)


def validate_notation(notation: str) -> bool:
    """
    Validate if a notation string is syntactically correct.
    
    Args:
        notation: String to validate
        
    Returns:
        True if notation is valid
    """
    try:
        MoveSequence.parse(notation)
        return True
    except ValueError:
        return False


def get_notation_help() -> str:
    """
    Get help text for Singmaster notation.
    
    Returns:
        Help string explaining notation
    """
    return """
Singmaster Notation for 3x3 Rubik's Cube:

Face Letters:
  R = Right face    L = Left face
  U = Up face       D = Down face  
  F = Front face    B = Back face

Move Types:
  R  = Clockwise 90° turn
  R' = Counter-clockwise 90° turn  
  R2 = 180° turn

Examples:
  R U R' U'     = Right up, right prime, up prime
  F2 B2 R2 L2   = Four 180° turns
  R U2 R' D R   = Mixed quarter and half turns

Spaces between moves are optional but recommended for readability.
"""


class NotationParser:
    """Advanced notation parser with error reporting."""
    
    def __init__(self) -> None:
        """Initialize parser."""
        self.errors: List[str] = []
    
    def parse(self, notation: str) -> Optional[MoveSequence]:
        """
        Parse notation with detailed error reporting.
        
        Args:
            notation: String to parse
            
        Returns:
            MoveSequence if successful, None if errors occurred
        """
        self.errors.clear()
        
        try:
            return MoveSequence.parse(notation)
        except ValueError as e:
            self.errors.append(str(e))
            return None
    
    def get_errors(self) -> List[str]:
        """Get list of parsing errors."""
        return self.errors.copy()
    
    def has_errors(self) -> bool:
        """Check if there were parsing errors."""
        return len(self.errors) > 0
