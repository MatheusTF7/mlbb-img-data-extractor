"""MLBB Screenshot Region Definitions.

This module defines all the screen regions for extracting data from
Mobile Legends Bang Bang end-game screenshots.

All coordinates are defined as percentages (0-100) of the image dimensions
to maintain responsiveness across different image resolutions.
Reference resolution: 2400x1080px
"""

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class Region:
    """Represents a region in the image using percentage coordinates."""
    x: float  # X position as percentage (0-100)
    y: float  # Y position as percentage (0-100)
    w: float  # Width as percentage
    h: float  # Height as percentage

    def to_pixels(self, image_width: int, image_height: int) -> Tuple[int, int, int, int]:
        """
        Convert percentage coordinates to pixel coordinates.
        
        Args:
            image_width: Width of the image in pixels
            image_height: Height of the image in pixels
            
        Returns:
            Tuple of (x, y, width, height) in pixels
        """
        px_x = int((self.x / 100) * image_width)
        px_y = int((self.y / 100) * image_height)
        px_w = int((self.w / 100) * image_width)
        px_h = int((self.h / 100) * image_height)
        return (px_x, px_y, px_w, px_h)


# =============================================================================
# MATCH INFORMATION REGIONS
# =============================================================================

# Game result detection area: VICTORY or DEFEAT
RESULT_REGION = Region(
    x=40.02235885969815,
    y=3.1055900621118013,
    w=19.8993851313583,
    h=10.683229813664596
)

# My team score (left side score)
MY_TEAM_SCORE_REGION = Region(
    x=32.4762437115707,
    y=5.093167701863354,
    w=4.974846282839574,
    h=8.571428571428571
)

# Adversary team score (right side score)
ADVERSARY_SCORE_REGION = Region(
    x=62.60480715483511,
    y=5.217391304347826,
    w=4.807154835103411,
    h=7.95031055900621
)

# Match duration (mm:ss format)
DURATION_REGION = Region(
    x=77.24986025712688,
    y=11.428571428571429,
    w=4.583566238121861,
    h=4.099378881987576
)

# =============================================================================
# PLAYER ROW REGIONS (5 players on my team - left side)
# =============================================================================

# Base region for all 5 player rows
MY_TEAM_AREA = Region(
    x=13.527110117384014,
    y=20.869565217391305,
    w=36.50083845723868,
    h=63.975155279503106
)


@dataclass
class PlayerRowRegions:
    """Contains all sub-regions for a single player row."""
    full_row: Region
    nickname: Region
    stats: Region  # kills deaths assists gold
    medal: Region
    ratio: Region


# Player 1 (Row 1)
PLAYER_1 = PlayerRowRegions(
    full_row=Region(
        x=13.527110117384014,
        y=20.869565217391305,
        w=36.50083845723868,
        h=12.795031055900623
    ),
    nickname=Region(
        x=21.07322526551146,
        y=22.111801242236034,
        w=10.564561207378427,
        h=4.223602484472046
    ),
    stats=Region(
        x=31.134712129681386,
        y=21.987577639751557,
        w=12.129681386249304,
        h=4.223602484472046
    ),
    medal=Region(
        x=43.76746785913918,
        y=22.608695652173918,
        w=3.856903297931809,
        h=7.453416149068319
    ),
    ratio=Region(
        x=43.76746785913918,
        y=29.316770186335408,
        w=3.856903297931809,
        h=4.223602484472046
    )
)

# Player 2 (Row 2)
PLAYER_2 = PlayerRowRegions(
    full_row=Region(
        x=13.583007266629403,
        y=33.66459627329193,
        w=36.50083845723868,
        h=12.795031055900623
    ),
    nickname=Region(
        x=20.961430967020682,
        y=34.782608695652186,
        w=10.564561207378427,
        h=4.223602484472046
    ),
    stats=Region(
        x=31.190609278926775,
        y=34.53416149068323,
        w=12.129681386249304,
        h=4.223602484472046
    ),
    medal=Region(
        x=43.82336500838457,
        y=35.1552795031056,
        w=3.856903297931809,
        h=7.577639751552791
    ),
    ratio=Region(
        x=43.71157070989379,
        y=42.236024844720504,
        w=3.856903297931809,
        h=4.223602484472046
    )
)

# Player 3 (Row 3)
PLAYER_3 = PlayerRowRegions(
    full_row=Region(
        x=13.527110117384014,
        y=46.33540372670808,
        w=36.50083845723868,
        h=12.795031055900623
    ),
    nickname=Region(
        x=20.961430967020682,
        y=47.32919254658386,
        w=10.564561207378427,
        h=4.223602484472046
    ),
    stats=Region(
        x=31.02291783119061,
        y=47.577639751552795,
        w=12.129681386249304,
        h=4.223602484472046
    ),
    medal=Region(
        x=43.71157070989379,
        y=48.19875776397516,
        w=3.856903297931809,
        h=7.453416149068319
    ),
    ratio=Region(
        x=43.71157070989379,
        y=54.90683229813665,
        w=3.856903297931809,
        h=4.223602484472046
    )
)

# Player 4 (Row 4)
PLAYER_4 = PlayerRowRegions(
    full_row=Region(
        x=13.415315818893237,
        y=59.25465838509317,
        w=36.50083845723868,
        h=12.795031055900623
    ),
    nickname=Region(
        x=21.01732811626607,
        y=60.372670807453424,
        w=10.564561207378427,
        h=4.223602484472046
    ),
    stats=Region(
        x=30.967020681945222,
        y=60.24844720496894,
        w=12.129681386249304,
        h=4.223602484472046
    ),
    medal=Region(
        x=43.6556735606484,
        y=61.36645962732919,
        w=3.856903297931809,
        h=7.453416149068319
    ),
    ratio=Region(
        x=43.76746785913918,
        y=67.95031055900621,
        w=3.856903297931809,
        h=4.223602484472046
    )
)

# Player 5 (Row 5)
PLAYER_5 = PlayerRowRegions(
    full_row=Region(
        x=13.527110117384014,
        y=71.92546583850933,
        w=36.50083845723868,
        h=12.795031055900623
    ),
    nickname=Region(
        x=20.961430967020682,
        y=73.16770186335404,
        w=10.564561207378427,
        h=4.223602484472046
    ),
    stats=Region(
        x=31.02291783119061,
        y=73.04347826086956,
        w=12.129681386249304,
        h=4.223602484472046
    ),
    medal=Region(
        x=43.71157070989379,
        y=73.54037267080746,
        w=3.856903297931809,
        h=7.453416149068319
    ),
    ratio=Region(
        x=43.71157070989379,
        y=80.62111801242236,
        w=3.856903297931809,
        h=4.223602484472046
    )
)

# List of all player regions for easy iteration
ALL_PLAYERS = [PLAYER_1, PLAYER_2, PLAYER_3, PLAYER_4, PLAYER_5]


def get_player_region(player_index: int) -> PlayerRowRegions:
    """
    Get the region definitions for a specific player row.
    
    Args:
        player_index: Player position (0-4, from top to bottom)
        
    Returns:
        PlayerRowRegions for the specified player
        
    Raises:
        IndexError: If player_index is out of range
    """
    if player_index < 0 or player_index > 4:
        raise IndexError(f"Player index must be 0-4, got {player_index}")
    return ALL_PLAYERS[player_index]
