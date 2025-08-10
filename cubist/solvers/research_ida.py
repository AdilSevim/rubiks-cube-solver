"""
Research solver using IDA* (Iterative Deepening A*) algorithm.
"""

from typing import Optional, Callable, Set, List
from dataclasses import dataclass
import time
from ..core.cube_state import CubeState
from ..core.moves import Move, MoveSequence


@dataclass
class SearchProgress:
    """Progress information for IDA* search."""
    depth: int
    nodes_expanded: int
    best_bound: int
    elapsed_time: float
    current_phase: str


class IDAStarSolver:
    """Research solver using IDA* search with heuristics."""
    
    def __init__(self) -> None:
        """Initialize the IDA* solver."""
        self.name = "Research (IDA*)"
        self.description = "Iterative deepening A* search with pattern database heuristics"
        self.max_depth = 25
        self.max_time = 300  # 5 minutes timeout
        self._cancelled = False
        
        # All possible moves
        self.moves = [
            Move.R, Move.Rp, Move.R2,
            Move.L, Move.Lp, Move.L2,
            Move.U, Move.Up, Move.U2,
            Move.D, Move.Dp, Move.D2,
            Move.F, Move.Fp, Move.F2,
            Move.B, Move.Bp, Move.B2
        ]
    
    def solve(self, 
              state: CubeState,
              progress_callback: Optional[Callable[[SearchProgress], None]] = None) -> MoveSequence:
        """
        Solve the cube using IDA* search.
        
        Args:
            state: CubeState to solve
            progress_callback: Optional callback for progress updates
            
        Returns:
            MoveSequence solution
            
        Raises:
            ValueError: If no solution found or search cancelled
        """
        if state.is_solved():
            return MoveSequence([])
        
        self._cancelled = False
        start_time = time.time()
        
        # Initial bound is the heuristic estimate
        bound = self._heuristic(state)
        nodes_expanded = 0
        
        for depth in range(1, self.max_depth + 1):
            if self._cancelled:
                raise ValueError("Search cancelled by user")
            
            if time.time() - start_time > self.max_time:
                raise ValueError("Search timeout exceeded")
            
            # Progress update
            if progress_callback:
                progress = SearchProgress(
                    depth=depth,
                    nodes_expanded=nodes_expanded,
                    best_bound=bound,
                    elapsed_time=time.time() - start_time,
                    current_phase=f"Searching depth {depth}"
                )
                progress_callback(progress)
            
            # Perform depth-limited search
            result = self._search(state, 0, bound, [], set(), start_time)
            
            if isinstance(result, list):  # Found solution
                if progress_callback:
                    final_progress = SearchProgress(
                        depth=len(result),
                        nodes_expanded=nodes_expanded,
                        best_bound=bound,
                        elapsed_time=time.time() - start_time,
                        current_phase="Solution found!"
                    )
                    progress_callback(final_progress)
                
                return MoveSequence(result)
            
            # Update bound for next iteration
            bound = result
            nodes_expanded += 1
        
        raise ValueError("No solution found within maximum depth")
    
    def _search(self, 
                state: CubeState, 
                g: int, 
                bound: int, 
                path: List[Move], 
                visited: Set[CubeState],
                start_time: float) -> any:
        """
        Recursive IDA* search function.
        
        Args:
            state: Current cube state
            g: Cost from start to current state
            bound: Current depth bound
            path: Current move path
            visited: Set of visited states
            start_time: Search start time
            
        Returns:
            List of moves if solution found, otherwise new bound
        """
        if self._cancelled or time.time() - start_time > self.max_time:
            return float('inf')
        
        # Calculate f = g + h
        h = self._heuristic(state)
        f = g + h
        
        if f > bound:
            return f
        
        if state.is_solved():
            return path
        
        if state in visited:
            return float('inf')
        
        visited.add(state)
        min_bound = float('inf')
        
        # Try all possible moves
        for move in self.moves:
            # Avoid redundant moves (don't undo the last move)
            if path and self._is_redundant(move, path[-1]):
                continue
            
            new_state = move.apply(state)
            new_path = path + [move]
            
            result = self._search(new_state, g + 1, bound, new_path, visited, start_time)
            
            if isinstance(result, list):  # Solution found
                visited.remove(state)
                return result
            
            if result < min_bound:
                min_bound = result
        
        visited.remove(state)
        return min_bound
    
    def _heuristic(self, state: CubeState) -> int:
        """
        Calculate heuristic estimate of moves to solve.
        
        This is a simple admissible heuristic based on:
        - Corner orientation sum
        - Edge orientation sum
        - Basic position counting
        
        Args:
            state: CubeState to evaluate
            
        Returns:
            Heuristic estimate
        """
        if state.is_solved():
            return 0
        
        h = 0
        
        # Corner orientation heuristic
        corner_twist = sum(state.corner_orient)
        if corner_twist > 0:
            h = max(h, (corner_twist + 2) // 3)  # At least this many moves needed
        
        # Edge orientation heuristic
        edge_flip = sum(state.edge_orient)
        if edge_flip > 0:
            h = max(h, (edge_flip + 1) // 2)  # At least this many moves needed
        
        # Corner permutation heuristic
        corner_out_of_place = sum(1 for i, pos in enumerate(state.corner_perm) if pos != i)
        if corner_out_of_place > 0:
            h = max(h, (corner_out_of_place + 2) // 3)
        
        # Edge permutation heuristic
        edge_out_of_place = sum(1 for i, pos in enumerate(state.edge_perm) if pos != i)
        if edge_out_of_place > 0:
            h = max(h, (edge_out_of_place + 3) // 4)
        
        return max(h, 1)  # At least 1 move if not solved
    
    def _is_redundant(self, move1: Move, move2: Move) -> bool:
        """Check if two consecutive moves are redundant."""
        # Don't allow same face moves consecutively (they should be combined)
        face1 = str(move1)[0]
        face2 = str(move2)[0]
        
        if face1 == face2:
            return True
        
        # Don't allow opposite face moves in certain orders
        opposite_faces = {
            'R': 'L', 'L': 'R',
            'U': 'D', 'D': 'U',
            'F': 'B', 'B': 'F'
        }
        
        # Avoid R L R type sequences
        if opposite_faces.get(face1) == face2:
            return True
        
        return False
    
    def cancel(self) -> None:
        """Cancel the current search."""
        self._cancelled = True
    
    def is_cancelled(self) -> bool:
        """Check if search was cancelled."""
        return self._cancelled
    
    def get_info(self) -> dict[str, any]:
        """Get solver information."""
        return {
            'name': self.name,
            'description': self.description,
            'type': 'research',
            'average_moves': '20-30',
            'speed': 'slow',
            'max_depth': self.max_depth,
            'timeout': self.max_time
        }


def ida_solve(state: CubeState, 
              on_progress: Optional[Callable[[SearchProgress], None]] = None) -> MoveSequence:
    """
    Convenience function for IDA* solving.
    
    Args:
        state: CubeState to solve
        on_progress: Optional progress callback
        
    Returns:
        MoveSequence solution
    """
    solver = IDAStarSolver()
    return solver.solve(state, on_progress)
