# Cubist - 3×3 Rubik's Cube Solver & Tutor

Cubist is a comprehensive desktop application for solving and learning 3×3 Rubik's Cube puzzles. Built with Python and PySide6, it offers multiple solving algorithms, 3D visualization, and educational features.

## Developer’s Story
When I started this project, I was 13 years old, during the 2021 COVID-19 pandemic. At that time, I was trying to solve a Rubik’s Cube, but I was never successful, which made me feel quite frustrated. Motivated by this challenge, I decided to develop a Rubik’s Cube solver. 
I created the first version in 2021. Later, in 2025, I revisited the project, improved it significantly, and prepared it for public release.

## by Adil Sevim :)

## Features

### 🎯 Multiple Solving Algorithms
- **Fast Solver**: Uses Kociemba's two-phase algorithm for optimal solutions
- **Tutor Solver**: Step-by-step beginner method (Layer-by-Layer) with explanations
- **Research Solver**: Advanced IDA* search algorithm for educational purposes

### 🎨 Rich Visualization
- **3D Renderer**: Interactive OpenGL-based 3D cube with smooth animations
- **2D Net View**: Traditional cube net representation with highlighting
- **Animation Controls**: Play, pause, step-by-step, and speed control

### 📚 Educational Tools
- **Step-by-step Tutorials**: Detailed explanations for each solving phase
- **Move Highlighting**: Visual feedback showing which pieces are affected
- **Progress Tracking**: Statistics and solve history

### 🔧 Advanced Features
- **Scramble Generator**: WCA-compliant random scrambles
- **Manual Input**: Paint cube colors or enter facelet strings
- **Validation**: Comprehensive cube state validation with error reporting
- **Export Options**: Save solutions as PDF, JSON, or text files

## Installation

### Prerequisites
- Python 3.11 or higher
- Windows 10/11 (primary target platform)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Required Packages
- PySide6 (GUI framework)
- PyOpenGL (3D rendering)
- numpy (numerical computations)
- kociemba (fast solving algorithm)
- reportlab (PDF export)

## Usage

### Running the Application
```bash
python app.py
```

### Basic Workflow
1. **Input Cube State**:
   - Use the scramble generator for random puzzles
   - Paint colors manually using the color input panel
   - Enter facelet strings directly

2. **Choose Solver**:
   - **Fast**: For quick optimal solutions
   - **Tutor**: For learning step-by-step
   - **Research**: For algorithm exploration

3. **Solve and Learn**:
   - Watch 3D animations of the solution
   - Read step-by-step explanations
   - Control playback speed and direction

4. **Export Results**:
   - Save as PDF with detailed analysis
   - Export JSON for data processing
   - Generate text files for sharing

### Keyboard Shortcuts
- `Ctrl+N`: New scramble
- `Ctrl+S`: Solve cube
- `Ctrl+R`: Reset to solved state
- `Space`: Play/pause animation
- `Left/Right Arrow`: Step through moves
- `Ctrl+E`: Export solution

## Project Structure

```
cubist/
├── core/                 # Core cube logic
│   ├── cube_state.py    # Cube representation
│   ├── moves.py         # Move definitions and sequences
│   ├── validators.py    # Cube state validation
│   ├── scramble.py      # Scramble generation
│   └── notations.py     # Move notation utilities
├── solvers/             # Solving algorithms
│   ├── fast_kociemba.py # Kociemba two-phase solver
│   ├── tutor_lbl.py     # Beginner tutorial solver
│   └── research_ida.py  # IDA* research solver
├── ui/                  # User interface
│   ├── main_window.py   # Main application window
│   ├── render/          # 3D and 2D rendering
│   ├── panels/          # UI control panels
│   └── playback/        # Animation controller
└── export/              # Export functionality
    ├── pdf_export.py    # PDF generation
    ├── json_export.py   # JSON data export
    └── txt_export.py    # Text file export
	...
```

## Development

### Code Quality
The project uses modern Python practices:
- Full type hints with mypy checking
- Code formatting with black
- Linting with flake8
- Testing with pytest

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black cubist/
flake8 cubist/
mypy cubist/
```

## Technical Details

### Cube Representation
- **Cubie-based**: Internal representation using corner and edge permutations/orientations
- **Facelet-based**: UI representation using 54 individual stickers
- **Conversion**: Robust bidirectional conversion between representations

### Solving Algorithms
- **Kociemba**: Two-phase algorithm with pruning tables
- **Layer-by-Layer**: Beginner-friendly method with detailed explanations
- **IDA***: Iterative deepening A* with pattern database heuristics

### 3D Rendering
- OpenGL-based rendering with modern shader pipeline
- Smooth animations with quaternion interpolation
- Interactive camera controls (orbit, zoom, pan)

## Building Executable

To create a standalone Windows executable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed app.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Herbert Kociemba for the two-phase algorithm
- The World Cube Association for standardized notation
- The cubing community for algorithms and insights

---

**Cubist** - Making Rubik's Cube solving accessible to everyone! 

## Contact

**Adil Sevim** — Developer  
- GitHub: https://github.com/<AdilSevim>  
- LinkedIn: https://www.linkedin.com/in/adilsevim/  
- Email: <adilsevim18@gmail.com>
