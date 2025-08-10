"""
Validation functions for checking cube state legality.
"""

from typing import List, Tuple, Dict
from collections import Counter
import numpy as np
from .cube_state import CubeState
from .color_scheme import ColorScheme


def validate_facelets(facelets: List[str]) -> Tuple[bool, List[str]]:
    """
    Validate a facelet representation of the cube.
    
    Args:
        facelets: List of 54 facelet colors
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Check facelet count
    if len(facelets) != 54:
        errors.append(f"Expected 54 facelets, got {len(facelets)}")
        return False, errors
    
    # Check color counts (should be 9 of each color)
    color_counts = Counter(facelets)
    
    if len(color_counts) != 6:
        errors.append(f"Expected exactly 6 different colors, got {len(color_counts)}")
    
    for color, count in color_counts.items():
        if count != 9:
            errors.append(f"Color {color} appears {count} times, expected 9")
    
    # If basic checks fail, return early
    if errors:
        return False, errors
    
    # Try to convert to cubie representation for advanced validation
    try:
        cube_state = CubeState.from_facelets(facelets)
        
        # Check corner twist sum
        corner_twist_sum = sum(cube_state.corner_orient) % 3
        if corner_twist_sum != 0:
            errors.append("Invalid corner twist sum (must be divisible by 3)")
        
        # Check edge flip sum
        edge_flip_sum = sum(cube_state.edge_orient) % 2
        if edge_flip_sum != 0:
            errors.append("Invalid edge flip sum (must be even)")
        
        # Check permutation parity
        corner_parity = _permutation_parity(cube_state.corner_perm)
        edge_parity = _permutation_parity(cube_state.edge_perm)
        
        if corner_parity != edge_parity:
            errors.append("Corner and edge permutation parities must match")
            
    except ValueError as e:
        errors.append(f"Invalid cube configuration: {str(e)}")
    
    return len(errors) == 0, errors


def _permutation_parity(perm: np.ndarray) -> int:
    """Calculate the parity of a permutation (0 for even, 1 for odd)."""
    n = len(perm)
    visited = [False] * n
    parity = 0
    
    for i in range(n):
        if not visited[i]:
            cycle_length = 0
            j = i
            while not visited[j]:
                visited[j] = True
                j = perm[j]
                cycle_length += 1
            
            if cycle_length % 2 == 0:
                parity ^= 1
    
    return parity


def validate_cube_state(state: CubeState) -> Tuple[bool, List[str]]:
    """
    Validate a CubeState object for legality.
    
    Args:
        state: CubeState to validate
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Check array lengths
    if len(state.corner_perm) != 8:
        errors.append(f"Corner permutation must have 8 elements, got {len(state.corner_perm)}")
    if len(state.corner_orient) != 8:
        errors.append(f"Corner orientation must have 8 elements, got {len(state.corner_orient)}")
    if len(state.edge_perm) != 12:
        errors.append(f"Edge permutation must have 12 elements, got {len(state.edge_perm)}")
    if len(state.edge_orient) != 12:
        errors.append(f"Edge orientation must have 12 elements, got {len(state.edge_orient)}")
    
    # Check permutation validity
    if not _is_valid_permutation(state.corner_perm, 8):
        errors.append("Invalid corner permutation")
    if not _is_valid_permutation(state.edge_perm, 12):
        errors.append("Invalid edge permutation")
    
    # Check orientation ranges
    for i, orient in enumerate(state.corner_orient):
        if orient not in [0, 1, 2]:
            errors.append(f"Corner {i} has invalid orientation {orient} (must be 0, 1, or 2)")
    
    for i, orient in enumerate(state.edge_orient):
        if orient not in [0, 1]:
            errors.append(f"Edge {i} has invalid orientation {orient} (must be 0 or 1)")
    
    # If basic checks fail, return early
    if errors:
        return False, errors
    
    # Check corner twist sum
    corner_twist_sum = sum(state.corner_orient) % 3
    if corner_twist_sum != 0:
        errors.append("Invalid corner twist sum (must be divisible by 3)")
    
    # Check edge flip sum
    edge_flip_sum = sum(state.edge_orient) % 2
    if edge_flip_sum != 0:
        errors.append("Invalid edge flip sum (must be even)")
    
    # Check permutation parity
    corner_parity = _permutation_parity(state.corner_perm)
    edge_parity = _permutation_parity(state.edge_perm)
    
    if corner_parity != edge_parity:
        errors.append("Corner and edge permutation parities must match")
    
    return len(errors) == 0, errors


def _is_valid_permutation(perm: np.ndarray, n: int) -> bool:
    """Check if array is a valid permutation of 0..n-1."""
    if len(perm) != n:
        return False
    
    expected = set(range(n))
    actual = set(perm)
    
    return expected == actual


def get_problematic_stickers(facelets: List[str]) -> List[int]:
    """
    Identify problematic sticker positions for UI highlighting.
    
    Args:
        facelets: List of 54 facelet colors
        
    Returns:
        List of sticker indices that are problematic
    """
    problematic = []
    
    if len(facelets) != 54:
        return list(range(len(facelets)))  # All positions if wrong count
    
    # Check for color count issues
    color_counts = Counter(facelets)
    
    # Find colors that appear wrong number of times
    wrong_colors = set()
    for color, count in color_counts.items():
        if count != 9:
            wrong_colors.add(color)
    
    # Mark all stickers with wrong colors as problematic
    for i, color in enumerate(facelets):
        if color in wrong_colors:
            problematic.append(i)
    
    # Try to identify specific cubie issues
    try:
        cube_state = CubeState.from_facelets(facelets)
        
        # Check for corner twist issues
        corner_twist_sum = sum(cube_state.corner_orient) % 3
        if corner_twist_sum != 0:
            # Mark corner stickers as potentially problematic
            corner_positions = [
                [0, 9, 20], [2, 18, 36], [8, 38, 47], [6, 45, 11],  # Top corners
                [29, 24, 15], [27, 42, 18], [35, 51, 44], [33, 17, 53]  # Bottom corners
            ]
            for corner in corner_positions:
                problematic.extend(corner)
        
        # Check for edge flip issues
        edge_flip_sum = sum(cube_state.edge_orient) % 2
        if edge_flip_sum != 0:
            # Mark edge stickers as potentially problematic
            edge_positions = [
                [1, 10], [5, 19], [7, 37], [3, 46],  # Top edges
                [28, 16], [32, 25], [34, 43], [30, 52],  # Bottom edges
                [23, 14], [21, 41], [39, 50], [48, 12]  # Middle edges
            ]
            for edge in edge_positions:
                problematic.extend(edge)
                
    except ValueError:
        # If conversion fails, mark all non-center stickers
        centers = [4, 13, 22, 31, 40, 49]
        problematic = [i for i in range(54) if i not in centers]
    
    return list(set(problematic))  # Remove duplicates


def create_validation_report(facelets: List[str]) -> Dict[str, any]:
    """
    Create a comprehensive validation report.
    
    Args:
        facelets: List of 54 facelet colors
        
    Returns:
        Dictionary with validation results and details
    """
    is_valid, errors = validate_facelets(facelets)
    problematic_stickers = get_problematic_stickers(facelets)
    
    color_counts = Counter(facelets) if len(facelets) == 54 else {}
    
    report = {
        'is_valid': is_valid,
        'errors': errors,
        'problematic_stickers': problematic_stickers,
        'color_counts': dict(color_counts),
        'total_stickers': len(facelets),
        'expected_stickers': 54
    }
    
    return report
