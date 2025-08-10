"""
Unit tests for moves module.
"""

import pytest
from cubist.core.moves import Move, MoveSequence
from cubist.core.cube_state import CubeState


class TestMove:
    """Test cases for Move enum."""
    
    def test_move_string_representation(self):
        """Test string representation of moves."""
        assert str(Move.R) == "R"
        assert str(Move.Rp) == "R'"
        assert str(Move.R2) == "R2"
        assert str(Move.U) == "U"
        assert str(Move.Up) == "U'"
        assert str(Move.U2) == "U2"
    
    def test_move_parsing(self):
        """Test parsing moves from strings."""
        assert Move.from_string("R") == Move.R
        assert Move.from_string("R'") == Move.Rp
        assert Move.from_string("R2") == Move.R2
        assert Move.from_string("U") == Move.U
        assert Move.from_string("U'") == Move.Up
        assert Move.from_string("U2") == Move.U2
        
        # Test case insensitivity
        assert Move.from_string("r") == Move.R
        assert Move.from_string("u'") == Move.Up
    
    def test_move_parsing_invalid(self):
        """Test parsing invalid move strings."""
        with pytest.raises(ValueError):
            Move.from_string("X")
        
        with pytest.raises(ValueError):
            Move.from_string("R3")
        
        with pytest.raises(ValueError):
            Move.from_string("")
    
    def test_move_inverse(self):
        """Test move inverse property."""
        assert Move.R.inverse() == Move.Rp
        assert Move.Rp.inverse() == Move.R
        assert Move.R2.inverse() == Move.R2
        
        assert Move.U.inverse() == Move.Up
        assert Move.Up.inverse() == Move.U
        assert Move.U2.inverse() == Move.U2
        
        assert Move.F.inverse() == Move.Fp
        assert Move.Fp.inverse() == Move.F
        assert Move.F2.inverse() == Move.F2


class TestMoveSequence:
    """Test cases for MoveSequence class."""
    
    def test_empty_sequence(self):
        """Test empty move sequence."""
        seq = MoveSequence([])
        
        assert len(seq) == 0
        assert str(seq) == ""
        assert list(seq) == []
    
    def test_sequence_creation(self):
        """Test creating move sequences."""
        moves = [Move.R, Move.U, Move.Rp, Move.Up]
        seq = MoveSequence(moves)
        
        assert len(seq) == 4
        assert list(seq) == moves
        assert str(seq) == "R U R' U'"
    
    def test_sequence_parsing(self):
        """Test parsing move sequences from strings."""
        seq = MoveSequence.parse("R U R' U'")
        expected = [Move.R, Move.U, Move.Rp, Move.Up]
        
        assert list(seq) == expected
        assert str(seq) == "R U R' U'"
    
    def test_sequence_parsing_complex(self):
        """Test parsing complex move sequences."""
        seq = MoveSequence.parse("R U2 R' D R U' R' D'")
        expected = [Move.R, Move.U2, Move.Rp, Move.D, Move.R, Move.Up, Move.Rp, Move.Dp]
        
        assert list(seq) == expected
    
    def test_sequence_parsing_with_whitespace(self):
        """Test parsing sequences with various whitespace."""
        seq1 = MoveSequence.parse("R  U   R'    U'")
        seq2 = MoveSequence.parse("R U R' U'")
        seq3 = MoveSequence.parse("  R U R' U'  ")
        
        expected = [Move.R, Move.U, Move.Rp, Move.Up]
        
        assert list(seq1) == expected
        assert list(seq2) == expected
        assert list(seq3) == expected
    
    def test_sequence_parsing_empty(self):
        """Test parsing empty sequences."""
        seq1 = MoveSequence.parse("")
        seq2 = MoveSequence.parse("   ")
        
        assert len(seq1) == 0
        assert len(seq2) == 0
    
    def test_sequence_parsing_invalid(self):
        """Test parsing invalid sequences."""
        with pytest.raises(ValueError):
            MoveSequence.parse("R X U")
        
        with pytest.raises(ValueError):
            MoveSequence.parse("R U3 R'")
    
    def test_sequence_inverse(self):
        """Test sequence inverse."""
        seq = MoveSequence.parse("R U R' U'")
        inv = seq.inverse()
        
        expected = MoveSequence.parse("U R U' R'")
        assert list(inv) == list(expected)
    
    def test_sequence_inverse_empty(self):
        """Test inverse of empty sequence."""
        seq = MoveSequence([])
        inv = seq.inverse()
        
        assert len(inv) == 0
    
    def test_sequence_simplification_basic(self):
        """Test basic sequence simplification."""
        # R R R R should simplify to empty
        seq = MoveSequence([Move.R, Move.R, Move.R, Move.R])
        simplified = seq.simplify()
        assert len(simplified) == 0
        
        # R R R should simplify to R'
        seq = MoveSequence([Move.R, Move.R, Move.R])
        simplified = seq.simplify()
        assert list(simplified) == [Move.Rp]
        
        # R R should simplify to R2
        seq = MoveSequence([Move.R, Move.R])
        simplified = seq.simplify()
        assert list(simplified) == [Move.R2]
    
    def test_sequence_simplification_cancellation(self):
        """Test sequence simplification with cancellation."""
        # R R' should cancel out
        seq = MoveSequence([Move.R, Move.Rp])
        simplified = seq.simplify()
        assert len(simplified) == 0
        
        # R' R should cancel out
        seq = MoveSequence([Move.Rp, Move.R])
        simplified = seq.simplify()
        assert len(simplified) == 0
        
        # R2 R2 should cancel out
        seq = MoveSequence([Move.R2, Move.R2])
        simplified = seq.simplify()
        assert len(simplified) == 0
    
    def test_sequence_application_to_cube(self):
        """Test applying sequence to cube state."""
        state = CubeState.solved()
        seq = MoveSequence.parse("R U R' U'")
        
        new_state = seq.apply_to(state)
        
        # Should not be solved after scramble
        assert not new_state.is_solved()
        
        # Original state should be unchanged
        assert state.is_solved()
    
    def test_sequence_application_empty(self):
        """Test applying empty sequence to cube."""
        state = CubeState.solved()
        seq = MoveSequence([])
        
        new_state = seq.apply_to(state)
        
        # Should still be solved
        assert new_state.is_solved()
        assert new_state == state
    
    def test_sequence_concatenation(self):
        """Test concatenating sequences."""
        seq1 = MoveSequence.parse("R U")
        seq2 = MoveSequence.parse("R' U'")
        
        combined = seq1 + seq2
        expected = MoveSequence.parse("R U R' U'")
        
        assert list(combined) == list(expected)
    
    def test_sequence_equality(self):
        """Test sequence equality."""
        seq1 = MoveSequence.parse("R U R' U'")
        seq2 = MoveSequence.parse("R U R' U'")
        seq3 = MoveSequence.parse("R U R'")
        
        assert seq1 == seq2
        assert seq1 != seq3
        assert seq2 != seq3
    
    def test_sequence_indexing(self):
        """Test sequence indexing."""
        seq = MoveSequence.parse("R U R' U'")
        
        assert seq[0] == Move.R
        assert seq[1] == Move.U
        assert seq[2] == Move.Rp
        assert seq[3] == Move.Up
        
        # Test negative indexing
        assert seq[-1] == Move.Up
        assert seq[-2] == Move.Rp
    
    def test_sequence_slicing(self):
        """Test sequence slicing."""
        seq = MoveSequence.parse("R U R' U' F D")
        
        sub_seq = seq[1:4]
        expected = MoveSequence.parse("U R' U'")
        
        assert list(sub_seq) == list(expected)
    
    def test_sequence_round_trip_application(self):
        """Test that sequence and its inverse cancel out."""
        state = CubeState.solved()
        seq = MoveSequence.parse("R U R' U' F R F' U F' U' F")
        
        # Apply sequence then its inverse
        scrambled = seq.apply_to(state)
        solved_again = seq.inverse().apply_to(scrambled)
        
        assert solved_again == state


if __name__ == "__main__":
    pytest.main([__file__])
