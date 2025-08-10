"""
Unit tests for CubeState class.
"""

import pytest
import numpy as np
from cubist.core.cube_state import CubeState
from cubist.core.moves import Move
from cubist.core.color_scheme import ColorScheme


class TestCubeState:
    """Test cases for CubeState class."""
    
    def test_solved_state_creation(self):
        """Test creating a solved cube state."""
        state = CubeState.solved()
        
        assert state.is_solved()
        assert len(state.corner_perm) == 8
        assert len(state.corner_orient) == 8
        assert len(state.edge_perm) == 12
        assert len(state.edge_orient) == 12
        
        # Check that permutations are identity
        assert np.array_equal(state.corner_perm, np.arange(8))
        assert np.array_equal(state.edge_perm, np.arange(12))
        
        # Check that orientations are all zero
        assert np.array_equal(state.corner_orient, np.zeros(8))
        assert np.array_equal(state.edge_orient, np.zeros(12))
    
    def test_cube_state_equality(self):
        """Test cube state equality comparison."""
        state1 = CubeState.solved()
        state2 = CubeState.solved()
        state3 = CubeState([1, 0, 2, 3, 4, 5, 6, 7], [0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        
        assert state1 == state2
        assert state1 != state3
        assert state2 != state3
    
    def test_cube_state_cloning(self):
        """Test cube state cloning."""
        original = CubeState.solved()
        clone = original.clone()
        
        assert original == clone
        assert original is not clone
        assert original.corner_perm is not clone.corner_perm
        assert original.corner_orient is not clone.corner_orient
        assert original.edge_perm is not clone.edge_perm
        assert original.edge_orient is not clone.edge_orient
    
    def test_cube_state_hashing(self):
        """Test cube state hashing for use in sets/dicts."""
        state1 = CubeState.solved()
        state2 = CubeState.solved()
        state3 = CubeState([1, 0, 2, 3, 4, 5, 6, 7], [0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        
        # Equal states should have equal hashes
        assert hash(state1) == hash(state2)
        
        # Different states should (probably) have different hashes
        assert hash(state1) != hash(state3)
        
        # Should be usable in sets
        state_set = {state1, state2, state3}
        assert len(state_set) == 2  # state1 and state2 are equal
    
    def test_facelet_conversion_solved(self):
        """Test facelet conversion for solved state."""
        state = CubeState.solved()
        scheme = ColorScheme()
        
        facelets = state.to_facelets(scheme)
        
        # Should have 54 facelets
        assert len(facelets) == 54
        
        # Check that centers are correct colors
        centers = [facelets[4], facelets[13], facelets[22], facelets[31], facelets[40], facelets[49]]
        expected_centers = [scheme.U, scheme.R, scheme.F, scheme.D, scheme.L, scheme.B]
        assert centers == expected_centers
        
        # All facelets of same face should have same color
        for i in range(6):
            face_start = i * 9
            face_facelets = facelets[face_start:face_start + 9]
            assert all(f == face_facelets[0] for f in face_facelets)
    
    def test_facelet_roundtrip_conversion(self):
        """Test that facelet conversion is reversible for solved state."""
        original_state = CubeState.solved()
        scheme = ColorScheme()
        
        # Convert to facelets and back
        facelets = original_state.to_facelets(scheme)
        converted_state = CubeState.from_facelets(facelets)
        
        assert original_state == converted_state
    
    def test_move_application_r(self):
        """Test applying R move to solved state."""
        state = CubeState.solved()
        new_state = state.apply_move(Move.R)
        
        # Should not be solved anymore
        assert not new_state.is_solved()
        
        # Original state should be unchanged
        assert state.is_solved()
        
        # Applying R four times should return to solved
        current = state
        for _ in range(4):
            current = current.apply_move(Move.R)
        
        assert current.is_solved()
    
    def test_move_application_u(self):
        """Test applying U move to solved state."""
        state = CubeState.solved()
        new_state = state.apply_move(Move.U)
        
        assert not new_state.is_solved()
        
        # Applying U four times should return to solved
        current = state
        for _ in range(4):
            current = current.apply_move(Move.U)
        
        assert current.is_solved()
    
    def test_move_application_f(self):
        """Test applying F move to solved state."""
        state = CubeState.solved()
        new_state = state.apply_move(Move.F)
        
        assert not new_state.is_solved()
        
        # Applying F four times should return to solved
        current = state
        for _ in range(4):
            current = current.apply_move(Move.F)
        
        assert current.is_solved()
    
    def test_move_inverse_property(self):
        """Test that move and its inverse cancel out."""
        state = CubeState.solved()
        
        # Test R and R'
        after_r = state.apply_move(Move.R)
        after_r_prime = after_r.apply_move(Move.Rp)
        assert after_r_prime == state
        
        # Test U and U'
        after_u = state.apply_move(Move.U)
        after_u_prime = after_u.apply_move(Move.Up)
        assert after_u_prime == state
        
        # Test F and F'
        after_f = state.apply_move(Move.F)
        after_f_prime = after_f.apply_move(Move.Fp)
        assert after_f_prime == state
    
    def test_move_double_property(self):
        """Test that double moves work correctly."""
        state = CubeState.solved()
        
        # R2 should equal R R
        after_r2 = state.apply_move(Move.R2)
        after_r_r = state.apply_move(Move.R).apply_move(Move.R)
        assert after_r2 == after_r_r
        
        # U2 should equal U U
        after_u2 = state.apply_move(Move.U2)
        after_u_u = state.apply_move(Move.U).apply_move(Move.U)
        assert after_u2 == after_u_u
    
    def test_scramble_and_solve(self):
        """Test scrambling and solving back."""
        from cubist.core.moves import MoveSequence
        
        state = CubeState.solved()
        
        # Apply a known sequence
        sequence = MoveSequence.parse("R U R' U'")
        scrambled = sequence.apply_to(state)
        
        # Apply inverse sequence
        inverse_sequence = sequence.inverse()
        solved_again = inverse_sequence.apply_to(scrambled)
        
        assert solved_again == state
    
    def test_invalid_cube_state_creation(self):
        """Test creation with invalid parameters."""
        # Invalid array lengths
        with pytest.raises((ValueError, IndexError)):
            CubeState([0, 1, 2], [0, 0, 0], [0, 1, 2], [0, 0, 0])
        
        # Invalid orientation values
        with pytest.raises((ValueError, IndexError)):
            CubeState([0, 1, 2, 3, 4, 5, 6, 7], [0, 0, 0, 3, 0, 0, 0, 0],  # Invalid corner orientation
                     [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])


if __name__ == "__main__":
    pytest.main([__file__])
