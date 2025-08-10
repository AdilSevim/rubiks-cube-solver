"""
Color scheme management for Rubik's Cube visualization.
"""

from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class ColorScheme:
    """Color scheme for cube faces with hex color values."""
    
    # Standard WCA color scheme
    U: str = "#FFFFFF"  # Up - White
    D: str = "#FFD500"  # Down - Yellow  
    F: str = "#009E60"  # Front - Green
    B: str = "#0046AD"  # Back - Blue
    R: str = "#C41E3A"  # Right - Red
    L: str = "#FF5800"  # Left - Orange
    
    def __post_init__(self) -> None:
        """Validate hex color format."""
        for face, color in self.to_dict().items():
            if not self._is_valid_hex(color):
                raise ValueError(f"Invalid hex color for face {face}: {color}")
    
    @staticmethod
    def _is_valid_hex(color: str) -> bool:
        """Check if string is valid hex color."""
        if not color.startswith('#') or len(color) != 7:
            return False
        try:
            int(color[1:], 16)
            return True
        except ValueError:
            return False
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary mapping."""
        return {
            'U': self.U,
            'D': self.D, 
            'F': self.F,
            'B': self.B,
            'R': self.R,
            'L': self.L
        }
    
    @classmethod
    def from_dict(cls, colors: Dict[str, str]) -> "ColorScheme":
        """Create from dictionary mapping."""
        return cls(
            U=colors.get('U', cls.U),
            D=colors.get('D', cls.D),
            F=colors.get('F', cls.F), 
            B=colors.get('B', cls.B),
            R=colors.get('R', cls.R),
            L=colors.get('L', cls.L)
        )
    
    def get_rgb(self, face: str) -> Tuple[int, int, int]:
        """Get RGB values (0-255) for a face."""
        hex_color = self.to_dict()[face]
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def get_rgb_normalized(self, face: str) -> Tuple[float, float, float]:
        """Get normalized RGB values (0.0-1.0) for OpenGL."""
        r, g, b = self.get_rgb(face)
        return (r / 255.0, g / 255.0, b / 255.0)
    
    def copy(self) -> "ColorScheme":
        """Create a copy of this color scheme."""
        return ColorScheme(**self.to_dict())


# Predefined color schemes
DEFAULT_SCHEME = ColorScheme()

CLASSIC_SCHEME = ColorScheme(
    U="#FFFFFF",  # White
    D="#FFFF00",  # Yellow
    F="#00FF00",  # Green  
    B="#0000FF",  # Blue
    R="#FF0000",  # Red
    L="#FFA500"   # Orange
)

PASTEL_SCHEME = ColorScheme(
    U="#F8F8FF",  # Ghost White
    D="#FFFACD",  # Lemon Chiffon
    F="#F0FFF0",  # Honeydew
    B="#F0F8FF",  # Alice Blue
    R="#FFE4E1",  # Misty Rose
    L="#FFEFD5"   # Papaya Whip
)
