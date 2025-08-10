"""
Animation controller for managing cube move playback.
"""

from typing import List, Optional, Callable
from PySide6.QtCore import QObject, QTimer, Signal
from ...core.cube_state import CubeState
from ...core.moves import Move, MoveSequence


class AnimationController(QObject):
    """Controls animation playback of move sequences."""
    
    # Signals
    progress_changed = Signal(float, int, int)  # progress, current_step, total_steps
    playback_started = Signal()
    playback_paused = Signal()
    playback_stopped = Signal()
    playback_finished = Signal()
    step_changed = Signal(int)  # current step index
    
    def __init__(self, parent=None) -> None:
        """Initialize the animation controller."""
        super().__init__(parent)
        
        # Sequence and state management
        self.sequence = MoveSequence([])
        self.initial_state = CubeState.solved()
        self.state_history: List[CubeState] = []
        
        # Playback state
        self.current_step = 0
        self.is_playing = False
        self.is_paused = False
        self.speed_ms = 500  # milliseconds per move
        
        # Timer for automatic playback
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self._advance_step)
        
        # Callbacks
        self.progress_callback: Optional[Callable[[float, int, int], None]] = None
        
    def load_sequence(self, sequence: MoveSequence, initial_state: CubeState = None) -> None:
        """
        Load a move sequence for playback.
        
        Args:
            sequence: MoveSequence to play
            initial_state: Starting cube state (defaults to solved)
        """
        self.stop()
        
        self.sequence = sequence
        self.initial_state = initial_state or CubeState.solved()
        
        # Pre-compute all states for instant seeking
        self._compute_state_history()
        
        # Reset to beginning
        self.current_step = 0
        self._emit_progress()
    
    def _compute_state_history(self) -> None:
        """Pre-compute all cube states in the sequence."""
        self.state_history = [self.initial_state.clone()]
        
        current_state = self.initial_state.clone()
        for move in self.sequence:
            current_state = move.apply(current_state)
            self.state_history.append(current_state.clone())
    
    def play(self) -> None:
        """Start or resume playback."""
        if len(self.sequence) == 0:
            return
        
        if self.current_step >= len(self.sequence):
            # Already at end, restart from beginning
            self.current_step = 0
        
        self.is_playing = True
        self.is_paused = False
        self.playback_timer.start(self.speed_ms)
        
        self.playback_started.emit()
        self._emit_progress()
    
    def pause(self) -> None:
        """Pause playback."""
        if not self.is_playing:
            return
        
        self.is_paused = True
        self.playback_timer.stop()
        
        self.playback_paused.emit()
    
    def resume(self) -> None:
        """Resume paused playback."""
        if not self.is_paused:
            return
        
        self.is_paused = False
        self.playback_timer.start(self.speed_ms)
        
        self.playback_started.emit()
    
    def stop(self) -> None:
        """Stop playback and reset to beginning."""
        self.playback_timer.stop()
        self.is_playing = False
        self.is_paused = False
        self.current_step = 0
        
        self.playback_stopped.emit()
        self._emit_progress()
    
    def step_forward(self) -> None:
        """Advance one step forward with improved state handling."""
        # Validate we can move forward
        if self.current_step < len(self.sequence):
            self.current_step += 1
            self.step_changed.emit(self.current_step)
            self._emit_progress()
            
            # Handle reaching the end
            if self.current_step >= len(self.sequence):
                self._finish_playback()
        
        # Ensure we don't go beyond the sequence
        self.current_step = min(self.current_step, len(self.sequence))
    
    def step_back(self) -> None:
        """Go one step backward with improved state handling."""
        # Validate we can move backward
        if self.current_step > 0:
            self.current_step -= 1
            self.step_changed.emit(self.current_step)
            self._emit_progress()
        
        # Ensure we don't go before the beginning
        self.current_step = max(0, self.current_step)
    
    def seek_to(self, step_index: int) -> None:
        """
        Seek to a specific step with improved validation and state management.
        
        Args:
            step_index: Step index to seek to (0 = initial state)
        """
        # Validate input
        if not isinstance(step_index, int):
            return
        
        # Clamp step_index to valid range
        step_index = max(0, min(step_index, len(self.sequence)))
        
        # Update current step
        self.current_step = step_index
        
        # Emit signals for UI updates
        self.step_changed.emit(self.current_step)
        self._emit_progress()
        
        # Handle playback state when seeking
        if self.is_playing and not self.is_paused:
            # If we're playing and seek to the end, stop playback
            if self.current_step >= len(self.sequence):
                self._finish_playback()
            # If we're playing and seek to the beginning, restart timer
            elif self.current_step == 0 and len(self.sequence) > 0:
                self.playback_timer.start(self.speed_ms)
    
    def jump_to_start(self) -> None:
        """Jump to the beginning."""
        self.seek_to(0)
    
    def jump_to_end(self) -> None:
        """Jump to the end."""
        self.seek_to(len(self.sequence))
    
    def set_speed(self, ms_per_move: int) -> None:
        """
        Set playback speed.
        
        Args:
            ms_per_move: Milliseconds per move (100-2000)
        """
        self.speed_ms = max(100, min(2000, ms_per_move))
        
        # Update timer if currently playing
        if self.is_playing and not self.is_paused:
            self.playback_timer.setInterval(self.speed_ms)
    
    def get_current_state(self) -> CubeState:
        """Get the current cube state."""
        if self.current_step < len(self.state_history):
            return self.state_history[self.current_step].clone()
        return self.initial_state.clone()
    
    def get_current_move(self) -> Optional[Move]:
        """Get the current move (the one that will be/was just executed)."""
        if 0 < self.current_step <= len(self.sequence):
            return self.sequence[self.current_step - 1]
        return None
    
    def get_next_move(self) -> Optional[Move]:
        """Get the next move to be executed."""
        if self.current_step < len(self.sequence):
            return self.sequence[self.current_step]
        return None
    
    def get_progress(self) -> float:
        """Get current progress as a fraction (0.0 to 1.0)."""
        if len(self.sequence) == 0:
            return 1.0
        return self.current_step / len(self.sequence)
    
    def get_step_info(self) -> tuple[int, int]:
        """Get current step and total steps."""
        return self.current_step, len(self.sequence)
    
    def is_at_start(self) -> bool:
        """Check if at the beginning."""
        return self.current_step == 0
    
    def is_at_end(self) -> bool:
        """Check if at the end."""
        return self.current_step >= len(self.sequence)
    
    def toggle_play_pause(self) -> None:
        """Toggle between play and pause."""
        if self.is_playing and not self.is_paused:
            self.pause()
        else:
            self.play()
    
    def on_progress(self, callback: Callable[[float, int, int], None]) -> None:
        """Set progress callback."""
        self.progress_callback = callback
    
    def _advance_step(self) -> None:
        """Advance to next step (called by timer)."""
        if self.current_step < len(self.sequence):
            self.step_forward()
        else:
            self._finish_playback()
    
    def _finish_playback(self) -> None:
        """Handle playback completion."""
        self.playback_timer.stop()
        self.is_playing = False
        self.is_paused = False
        
        self.playback_finished.emit()
        self._emit_progress()
    
    def _emit_progress(self) -> None:
        """Emit progress signals."""
        progress = self.get_progress()
        current, total = self.get_step_info()
        
        self.progress_changed.emit(progress, current, total)
        
        if self.progress_callback:
            self.progress_callback(progress, current, total)
    
    def get_move_at_step(self, step: int) -> Optional[Move]:
        """Get the move at a specific step."""
        if 0 <= step < len(self.sequence):
            return self.sequence[step]
        return None
    
    def get_moves_range(self, start: int, end: int) -> MoveSequence:
        """Get a range of moves as a sequence."""
        if start < 0 or end > len(self.sequence) or start >= end:
            return MoveSequence([])
        
        return MoveSequence(self.sequence.moves[start:end])
    
    def insert_move(self, move: Move, position: int = None) -> None:
        """
        Insert a move at the specified position.
        
        Args:
            move: Move to insert
            position: Position to insert at (None = current position)
        """
        if position is None:
            position = self.current_step
        
        # Insert move into sequence
        moves = list(self.sequence.moves)
        moves.insert(position, move)
        
        # Reload sequence
        new_sequence = MoveSequence(moves)
        self.load_sequence(new_sequence, self.initial_state)
        
        # Adjust current step if needed
        if position <= self.current_step:
            self.current_step += 1
        
        self._emit_progress()
    
    def remove_move(self, position: int) -> None:
        """
        Remove a move at the specified position.
        
        Args:
            position: Position to remove from
        """
        if position < 0 or position >= len(self.sequence):
            return
        
        # Remove move from sequence
        moves = list(self.sequence.moves)
        moves.pop(position)
        
        # Reload sequence
        new_sequence = MoveSequence(moves)
        self.load_sequence(new_sequence, self.initial_state)
        
        # Adjust current step if needed
        if position < self.current_step:
            self.current_step -= 1
        elif position == self.current_step and self.current_step > 0:
            self.current_step -= 1
        
        self._emit_progress()
    
    def clear_sequence(self) -> None:
        """Clear the current sequence."""
        self.load_sequence(MoveSequence([]), self.initial_state)
