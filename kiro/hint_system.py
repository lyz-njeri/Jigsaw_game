"""
Enhanced Jigsaw Puzzle Hint System

This module provides an intelligent hint system that helps players understand
the bigger picture of their jigsaw puzzle through contextual analysis and
progressive revelation.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Any, Optional, Tuple
import pygame
import numpy as np
from datetime import datetime, timedelta

class HintType(Enum):
    """Types of hints available in the enhanced hint system."""
    EDGE_STRUCTURE = "edge_structure"
    FOCAL_POINT = "focal_point"
    COLOR_REGION = "color_region"
    PATTERN_MATCH = "pattern_match"
    COMPOSITION_OVERVIEW = "composition_overview"
    PROGRESS_GUIDANCE = "progress_guidance"

@dataclass
class PuzzleRegion:
    """Represents a rectangular region within the puzzle."""
    x: int
    y: int
    width: int
    height: int
    piece_ids: List[int]

    def contains_point(self, px: int, py: int) -> bool:
        """Check if a point is within this region."""
        return (self.x <= px <= self.x + self.width and
                self.y <= py <= self.y + self.height)

    def overlaps_with(self, other: 'PuzzleRegion') -> bool:
        """Check if this region overlaps with another region."""
        return not (self.x + self.width < other.x or
                   other.x + other.width < self.x or
                   self.y + self.height < other.y or
                   other.y + other.height < self.y)

@dataclass
class FocalPoint:
    """Represents a focal point or area of interest in the image."""
    center_x: int
    center_y: int
    radius: int
    importance: float  # 0.0 to 1.0
    description: str
    region: PuzzleRegion

@dataclass
class ColorRegion:
    """Represents a region with similar colors or patterns."""
    dominant_color: Tuple[int, int, int]  # RGB values
    region: PuzzleRegion
    color_variance: float
    pattern_type: str  # "solid", "gradient", "texture", "pattern"

@dataclass
class Pattern:
    """Represents a visual pattern in the image."""
    pattern_type: str
    confidence: float
    region: PuzzleRegion
    characteristics: dict@data
class EdgeStructure:
    """Represents the edge structure of the puzzle."""
    corner_pieces: List[int]  # piece IDs
    edge_pieces: List[int]    # piece IDs
    border_regions: List[PuzzleRegion]

@dataclass
class HintResult:
    """Result of a hint request containing all necessary display information."""
    hint_type: HintType
    visual_data: Any  # Could be overlay surface, coordinates, etc.
    description: str
    affected_regions: List[PuzzleRegion]
    confidence_score: float
    timestamp: datetime

@dataclass
class CompositionData:
    """Complete analysis data for the puzzle image composition."""
    focal_points: List[FocalPoint]
    color_regions: List[ColorRegion]
    edge_structure: EdgeStructure
    dominant_patterns: List[Pattern]
    complexity_score: float
    analysis_timestamp: datetime

@dataclass
class CompletionPattern:
    """Represents patterns in how the player is completing the puzzle."""
    completion_percentage: float
    completed_regions: List[PuzzleRegion]
    suggested_next_regions: List[PuzzleRegion]
    completion_strategy: str  # "edges_first", "color_groups", "random", etc.

class HintStrategy(Enum):
    """Different strategies for providing hints based on progress."""
    STRUCTURAL_FOCUS = "structural_focus"      # Focus on edges and corners
    COMPOSITIONAL_FOCUS = "compositional_focus"  # Focus on main subjects
    DETAIL_FOCUS = "detail_focus"              # Focus on specific areas
    COMPLETION_FOCUS = "completion_focus"      # Focus on remaining pieces
