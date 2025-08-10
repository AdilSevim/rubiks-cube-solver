"""
PDF export functionality using reportlab.
"""

import time
from typing import List, Dict, Any, Optional
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.colors import black, white, red, green, blue, orange, yellow
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from ..core.cube_state import CubeState
from ..core.moves import MoveSequence
from ..core.color_scheme import ColorScheme


def export_pdf(filename: str,
               start_state: CubeState,
               sequence: MoveSequence,
               stats: Dict[str, Any],
               thumbnails: List[Any] = None,
               notes: List[str] = None,
               color_scheme: ColorScheme = None) -> None:
    """
    Export solve data to PDF format.
    
    Args:
        filename: Output PDF filename
        start_state: Initial cube state
        sequence: Solution move sequence
        stats: Solve statistics
        thumbnails: Optional thumbnail images
        notes: Optional tutorial notes
        color_scheme: Color scheme for visualization
    """
    if color_scheme is None:
        color_scheme = ColorScheme()
    
    # Create PDF document
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=black
    )
    
    story.append(Paragraph("Cubist - Rubik's Cube Solution", title_style))
    story.append(Spacer(1, 20))
    
    # Header information
    header_style = styles['Normal']
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    
    header_data = [
        ['Generated:', current_time],
        ['Solver:', stats.get('solver', 'Unknown')],
        ['Total Moves:', str(len(sequence))],
        ['Solve Time:', _format_time(stats.get('time', 0.0))],
        ['TPS:', f"{stats.get('tps', 0.0):.2f}"]
    ]
    
    header_table = Table(header_data, colWidths=[2*inch, 3*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 20))
    
    # Solution moves
    story.append(Paragraph("Solution Moves", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    # Format moves in rows
    moves_text = _format_moves_for_pdf(sequence)
    story.append(Paragraph(moves_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Move breakdown table
    if len(sequence) > 0:
        story.append(Paragraph("Move Breakdown", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        move_table_data = [['Step', 'Move', 'Description']]
        
        for i, move in enumerate(sequence.moves[:20]):  # Limit to first 20 moves
            description = _get_move_description(str(move))
            move_table_data.append([str(i+1), str(move), description])
        
        if len(sequence) > 20:
            move_table_data.append(['...', '...', f'({len(sequence) - 20} more moves)'])
        
        move_table = Table(move_table_data, colWidths=[0.5*inch, 0.8*inch, 3.7*inch])
        move_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#4a90e2'),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), ['#f8f8f8', white]),
            ('GRID', (0, 0), (-1, -1), 1, black),
        ]))
        
        story.append(move_table)
        story.append(Spacer(1, 20))
    
    # Tutorial notes (if provided)
    if notes:
        story.append(Paragraph("Tutorial Notes", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        for i, note in enumerate(notes):
            story.append(Paragraph(f"{i+1}. {note}", styles['Normal']))
            story.append(Spacer(1, 6))
        
        story.append(Spacer(1, 20))
    
    # Statistics summary
    story.append(Paragraph("Statistics Summary", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    stats_data = [
        ['Metric', 'Value'],
        ['Algorithm Efficiency', f"{len(sequence)} moves"],
        ['Execution Time', _format_time(stats.get('time', 0.0))],
        ['Turns Per Second', f"{stats.get('tps', 0.0):.2f}"],
        ['Solver Type', stats.get('solver', 'Unknown')]
    ]
    
    stats_table = Table(stats_data, colWidths=[2.5*inch, 2.5*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#28a745'),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), ['#f8f8f8', white]),
    ]))
    
    story.append(stats_table)
    story.append(Spacer(1, 20))
    
    # Footer
    footer_text = """
    <para align="center">
    <font size="10" color="gray">
    Generated by Cubist - 3×3 Rubik's Cube Solver & Tutor<br/>
    Visit our website for more solving tools and tutorials
    </font>
    </para>
    """
    story.append(Paragraph(footer_text, styles['Normal']))
    
    # Build PDF
    doc.build(story)


def _format_moves_for_pdf(sequence: MoveSequence) -> str:
    """Format move sequence for PDF display."""
    if len(sequence) == 0:
        return "No moves required - cube is already solved!"
    
    moves_str = str(sequence)
    
    # Break into lines of reasonable length
    words = moves_str.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 > 80:  # 80 chars per line
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                lines.append(word)
                current_length = 0
        else:
            current_line.append(word)
            current_length += len(word) + 1
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return '<br/>'.join(lines)


def _get_move_description(move_str: str) -> str:
    """Get description for a move."""
    descriptions = {
        'R': "Right face clockwise 90°",
        "R'": "Right face counter-clockwise 90°",
        'R2': "Right face 180°",
        'L': "Left face clockwise 90°",
        "L'": "Left face counter-clockwise 90°",
        'L2': "Left face 180°",
        'U': "Up face clockwise 90°",
        "U'": "Up face counter-clockwise 90°",
        'U2': "Up face 180°",
        'D': "Down face clockwise 90°",
        "D'": "Down face counter-clockwise 90°",
        'D2': "Down face 180°",
        'F': "Front face clockwise 90°",
        "F'": "Front face counter-clockwise 90°",
        'F2': "Front face 180°",
        'B': "Back face clockwise 90°",
        "B'": "Back face counter-clockwise 90°",
        'B2': "Back face 180°",
    }
    
    return descriptions.get(move_str, "Unknown move")


def _format_time(seconds: float) -> str:
    """Format time in MM:SS.ss format."""
    minutes = int(seconds // 60)
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:05.2f}"


def create_solve_report(filename: str, solve_data: Dict[str, Any]) -> None:
    """
    Create a comprehensive solve report PDF.
    
    Args:
        filename: Output filename
        solve_data: Dictionary containing all solve information
    """
    export_pdf(
        filename=filename,
        start_state=solve_data.get('start_state', CubeState.solved()),
        sequence=solve_data.get('solution', MoveSequence([])),
        stats=solve_data.get('stats', {}),
        thumbnails=solve_data.get('thumbnails', []),
        notes=solve_data.get('notes', []),
        color_scheme=solve_data.get('color_scheme', ColorScheme())
    )
