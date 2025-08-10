"""
Fast solver using Kociemba two-phase algorithm.
"""

from typing import Optional, Callable
import kociemba
from ..core.cube_state import CubeState
from ..core.moves import MoveSequence
from ..core.color_scheme import ColorScheme


class FastSolver:
    """Fast solver wrapper around Kociemba algorithm."""
    
    def __init__(self) -> None:
        """Initialize the fast solver."""
        self.name = "Fast (Kociemba Two-Phase)"
        self.description = "Optimal solver using Kociemba's two-phase algorithm"
    
    def solve(self, 
              state: CubeState, 
              scheme: ColorScheme = ColorScheme(),
              progress_callback: Optional[Callable[[str], None]] = None) -> MoveSequence:
        """
        Solve the cube using Kociemba algorithm.
        
        Args:
            state: CubeState to solve
            scheme: Color scheme for facelet conversion
            progress_callback: Optional callback for progress updates
            
        Returns:
            MoveSequence solution
            
        Raises:
            ValueError: If cube state is invalid or unsolvable
        """
        if progress_callback:
            progress_callback("Converting cube state...")
        
        # Convert to facelet representation for Kociemba
        facelets = state.to_facelets(scheme)
        
        # Convert to Kociemba format (URFDLB order with specific color mapping)
        kociemba_string = self._convert_to_kociemba_format(facelets, scheme)
        
        if progress_callback:
            progress_callback("Running Kociemba algorithm...")
        
        try:
            # Solve using Kociemba
            solution_string = kociemba.solve(kociemba_string)
            
            if solution_string.startswith("Error"):
                raise ValueError(f"Kociemba solver error: {solution_string}")
            
            if progress_callback:
                progress_callback("Parsing solution...")
            
            # Parse solution
            if solution_string.strip():
                solution = MoveSequence.parse(solution_string)
            else:
                solution = MoveSequence([])  # Already solved
            
            if progress_callback:
                progress_callback("Solution complete!")
            
            return solution
            
        except Exception as e:
            raise ValueError(f"Failed to solve cube: {str(e)}")
    
    def _convert_to_kociemba_format(self, facelets: list[str], scheme: ColorScheme) -> str:
        """
        Convert facelets to Kociemba format string.
        
        Kociemba expects: URFDLB face order with colors as single characters.
        Our format: URFDLB with hex colors.
        
        Args:
            facelets: List of 54 facelet colors
            scheme: Color scheme for mapping
            
        Returns:
            Kociemba format string
        """
        # Create color mapping from hex to single characters
        color_map = {
            scheme.U: 'U',  # White -> U
            scheme.R: 'R',  # Red -> R  
            scheme.F: 'F',  # Green -> F
            scheme.D: 'D',  # Yellow -> D
            scheme.L: 'L',  # Orange -> L
            scheme.B: 'B'   # Blue -> B
        }
        
        # Convert each facelet
        kociemba_facelets = []
        for facelet in facelets:
            if facelet not in color_map:
                raise ValueError(f"Unknown color in facelets: {facelet}")
            kociemba_facelets.append(color_map[facelet])
        
        return ''.join(kociemba_facelets)
    
    def is_available(self) -> bool:
        """Check if Kociemba solver is available."""
        try:
            # Test with solved cube
            test_cube = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
            result = kociemba.solve(test_cube)
            return not result.startswith("Error")
        except Exception:
            return False
    
    def get_info(self) -> dict[str, any]:
        """Get solver information."""
        return {
            'name': self.name,
            'description': self.description,
            'type': 'optimal',
            'average_moves': '20-25',
            'speed': 'very_fast',
            'available': self.is_available()
        }


def solve_facelets(facelets: list[str]) -> MoveSequence:
    """
    Convenience function to solve from facelet representation.
    
    Args:
        facelets: List of 54 facelet colors
        
    Returns:
        MoveSequence solution
    """
    state = CubeState.from_facelets(facelets)
    solver = FastSolver()
    return solver.solve(state)
