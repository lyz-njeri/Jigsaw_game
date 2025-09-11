"""
Unit tests for the enhanced hint system data structures.
"""

import unittest
from datetime import datetime
from hint_system import (
    HintType, PuzzleRegion, FocalPoint, ColorRegion, Pattern,
    EdgeStructure, HintResult, CompositionData, CompletionPattern,
    HintStrategy
)

class TestDataStructures(unittest.TestCase):
    
    def test_puzzle_region_creation(self):
        """Test PuzzleRegion creation and methods."""
        region = PuzzleRegion(10, 20, 100, 80, [1, 2, 3])
        
        self.assertEqual(region.x, 10)
        self.assertEqual(region.y, 20)
        self.assertEqual(region.width, 100)
        self.assertEqual(region.height, 80)
        self.assertEqual(region.piece_ids, [1, 2, 3])
        
        # Test contains_point
        self.assertTrue(region.contains_point(50, 50))
        self.assertFalse(region.contains_point(5, 5))
        
    def test_puzzle_region_overlap(self):
        """Test PuzzleRegion overlap detection."""
        region1 = PuzzleRegion(0, 0, 50, 50, [1])
        region2 = PuzzleRegion(25, 25, 50, 50, [2])  # Overlaps
        region3 = PuzzleRegion(100, 100, 50, 50, [3])  # No overlap
        
        self.assertTrue(region1.overlaps_with(region2))
        self.assertFalse(region1.overlaps_with(region3))
        
    def test_hint_type_enum(self):
        """Test HintType enum values."""
        self.assertEqual(HintType.EDGE_STRUCTURE.value, "edge_structure")
        self.assertEqual(HintType.FOCAL_POINT.value, "focal_point")
        self.assertEqual(HintType.COLOR_REGION.value, "color_region")
        
    def test_focal_point_creation(self):
        """Test FocalPoint dataclass creation."""
        region = PuzzleRegion(10, 10, 50, 50, [1, 2])
        focal_point = FocalPoint(
            center_x=35,
            center_y=35,
            radius=25,
            importance=0.8,
            description="Main subject",
            region=region
        )
        
        self.assertEqual(focal_point.center_x, 35)
        self.assertEqual(focal_point.importance, 0.8)
        self.assertEqual(focal_point.description, "Main subject")
        
    def test_hint_result_creation(self):
        """Test HintResult dataclass creation."""
        region = PuzzleRegion(0, 0, 100, 100, [1, 2, 3])
        timestamp = datetime.now()
        
        hint_result = HintResult(
            hint_type=HintType.FOCAL_POINT,
            visual_data=None,
            description="Focus on the center",
            affected_regions=[region],
            confidence_score=0.9,
            timestamp=timestamp
        )
        
        self.assertEqual(hint_result.hint_type, HintType.FOCAL_POINT)
        self.assertEqual(hint_result.confidence_score, 0.9)
        self.assertEqual(len(hint_result.affected_regions), 1)

if __name__ == '__main__':
    unittest.main()