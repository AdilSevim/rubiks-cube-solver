"""
JSON export functionality for solve data.
"""

import json
import time
from typing import Dict, Any, List, Optional
from ..core.cube_state import CubeState
from ..core.moves import MoveSequence
from ..core.color_scheme import ColorScheme


def export_json(filename: str,
                start_state: CubeState,
                sequence: MoveSequence,
                stats: Dict[str, Any],
                color_scheme: ColorScheme = None,
                notes: List[str] = None) -> None:
    """
    Export solve data to JSON format.
    
    Args:
        filename: Output JSON filename
        start_state: Initial cube state
        sequence: Solution move sequence
        stats: Solve statistics
        color_scheme: Color scheme used
        notes: Optional tutorial notes
    """
    if color_scheme is None:
        color_scheme = ColorScheme()
    
    # Create JSON data structure
    data = {
        "metadata": {
            "version": "1.0.0",
            "format": "cubist_solve_data",
            "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": time.time()
        },
        "solve_info": {
            "solver": stats.get('solver', 'Unknown'),
            "total_moves": len(sequence),
            "solve_time": stats.get('time', 0.0),
            "tps": stats.get('tps', 0.0),
            "date": time.strftime("%Y-%m-%d"),
            "time": time.strftime("%H:%M:%S")
        },
        "cube_data": {
            "initial_state": _cube_state_to_dict(start_state),
            "final_state": _cube_state_to_dict(_apply_sequence_to_state(start_state, sequence)),
            "color_scheme": color_scheme.to_dict()
        },
        "solution": {
            "moves": [str(move) for move in sequence.moves],
            "move_count": len(sequence),
            "notation": "singmaster",
            "sequence_string": str(sequence)
        },
        "statistics": {
            "execution_time": stats.get('time', 0.0),
            "moves_per_second": stats.get('tps', 0.0),
            "algorithm_efficiency": len(sequence),
            "solver_type": stats.get('solver', 'Unknown')
        }
    }
    
    # Add tutorial notes if provided
    if notes:
        data["tutorial"] = {
            "has_notes": True,
            "notes": notes,
            "note_count": len(notes)
        }
    else:
        data["tutorial"] = {
            "has_notes": False
        }
    
    # Add move analysis
    data["analysis"] = _analyze_sequence(sequence)
    
    # Write to file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _cube_state_to_dict(state: CubeState) -> Dict[str, Any]:
    """Convert CubeState to dictionary representation."""
    return {
        "corner_permutation": state.corner_perm.tolist(),
        "corner_orientation": state.corner_orient.tolist(),
        "edge_permutation": state.edge_perm.tolist(),
        "edge_orientation": state.edge_orient.tolist(),
        "is_solved": state.is_solved()
    }


def _apply_sequence_to_state(state: CubeState, sequence: MoveSequence) -> CubeState:
    """Apply move sequence to cube state."""
    return sequence.apply_to(state)


def _analyze_sequence(sequence: MoveSequence) -> Dict[str, Any]:
    """Analyze move sequence for patterns and statistics."""
    if len(sequence) == 0:
        return {
            "total_moves": 0,
            "face_distribution": {},
            "move_types": {},
            "patterns": []
        }
    
    # Count moves by face
    face_counts = {}
    move_type_counts = {"quarter_turns": 0, "half_turns": 0}
    
    for move in sequence:
        move_str = str(move)
        face = move_str[0]
        
        face_counts[face] = face_counts.get(face, 0) + 1
        
        if '2' in move_str:
            move_type_counts["half_turns"] += 1
        else:
            move_type_counts["quarter_turns"] += 1
    
    # Look for common patterns
    patterns = _find_common_patterns(sequence)
    
    return {
        "total_moves": len(sequence),
        "face_distribution": face_counts,
        "move_types": move_type_counts,
        "patterns": patterns,
        "efficiency_score": _calculate_efficiency_score(sequence)
    }


def _find_common_patterns(sequence: MoveSequence) -> List[Dict[str, Any]]:
    """Find common algorithmic patterns in the sequence."""
    patterns = []
    moves = [str(move) for move in sequence]
    
    # Look for sexy move (R U R' U')
    sexy_pattern = ["R", "U", "R'", "U'"]
    sexy_count = _count_pattern_occurrences(moves, sexy_pattern)
    if sexy_count > 0:
        patterns.append({
            "name": "Sexy Move",
            "pattern": "R U R' U'",
            "occurrences": sexy_count,
            "description": "Common right-hand algorithm"
        })
    
    # Look for sledgehammer (R' F R F')
    sledge_pattern = ["R'", "F", "R", "F'"]
    sledge_count = _count_pattern_occurrences(moves, sledge_pattern)
    if sledge_count > 0:
        patterns.append({
            "name": "Sledgehammer",
            "pattern": "R' F R F'",
            "occurrences": sledge_count,
            "description": "Common corner manipulation"
        })
    
    # Look for T-perm pattern
    tperm_pattern = ["R", "U", "R'", "F'", "R", "U", "R'", "U'", "R'", "F", "R2", "U'", "R'"]
    tperm_count = _count_pattern_occurrences(moves, tperm_pattern)
    if tperm_count > 0:
        patterns.append({
            "name": "T-Perm",
            "pattern": "R U R' F' R U R' U' R' F R2 U' R'",
            "occurrences": tperm_count,
            "description": "PLL algorithm for T permutation"
        })
    
    return patterns


def _count_pattern_occurrences(moves: List[str], pattern: List[str]) -> int:
    """Count how many times a pattern occurs in the move list."""
    count = 0
    pattern_len = len(pattern)
    
    for i in range(len(moves) - pattern_len + 1):
        if moves[i:i + pattern_len] == pattern:
            count += 1
    
    return count


def _calculate_efficiency_score(sequence: MoveSequence) -> float:
    """Calculate efficiency score for the sequence (0-1, higher is better)."""
    if len(sequence) == 0:
        return 1.0
    
    # Simple efficiency based on move count
    # Optimal solve is around 20 moves, beginner methods are 50-100
    move_count = len(sequence)
    
    if move_count <= 20:
        return 1.0  # Optimal
    elif move_count <= 30:
        return 0.9  # Very good
    elif move_count <= 50:
        return 0.7  # Good
    elif move_count <= 80:
        return 0.5  # Average
    else:
        return 0.3  # Needs improvement


def import_json(filename: str) -> Dict[str, Any]:
    """
    Import solve data from JSON file.
    
    Args:
        filename: JSON file to import
        
    Returns:
        Dictionary containing solve data
    """
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data


def validate_json_format(data: Dict[str, Any]) -> bool:
    """
    Validate that JSON data has correct format.
    
    Args:
        data: JSON data to validate
        
    Returns:
        True if format is valid
    """
    required_keys = ["metadata", "solve_info", "cube_data", "solution"]
    
    for key in required_keys:
        if key not in data:
            return False
    
    # Check metadata
    if "format" not in data["metadata"]:
        return False
    
    if data["metadata"]["format"] != "cubist_solve_data":
        return False
    
    # Check solution format
    if "moves" not in data["solution"]:
        return False
    
    return True


def convert_legacy_format(old_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert legacy JSON format to current format.
    
    Args:
        old_data: Old format data
        
    Returns:
        Converted data in current format
    """
    # This would handle conversion from older JSON formats
    # For now, just return the data as-is
    return old_data


def export_session_data(filename: str, session_data: List[Dict[str, Any]]) -> None:
    """
    Export multiple solves as session data.
    
    Args:
        filename: Output filename
        session_data: List of solve data dictionaries
    """
    data = {
        "metadata": {
            "version": "1.0.0",
            "format": "cubist_session_data",
            "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": time.time()
        },
        "session_info": {
            "total_solves": len(session_data),
            "date": time.strftime("%Y-%m-%d"),
            "duration": "unknown"  # Could be calculated if start/end times available
        },
        "solves": session_data,
        "statistics": _calculate_session_stats(session_data)
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _calculate_session_stats(session_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate statistics for a session."""
    if not session_data:
        return {}
    
    move_counts = [solve.get("solve_info", {}).get("total_moves", 0) for solve in session_data]
    solve_times = [solve.get("solve_info", {}).get("solve_time", 0.0) for solve in session_data]
    
    return {
        "average_moves": sum(move_counts) / len(move_counts) if move_counts else 0,
        "average_time": sum(solve_times) / len(solve_times) if solve_times else 0,
        "best_moves": min(move_counts) if move_counts else 0,
        "worst_moves": max(move_counts) if move_counts else 0,
        "best_time": min(solve_times) if solve_times else 0,
        "worst_time": max(solve_times) if solve_times else 0
    }
