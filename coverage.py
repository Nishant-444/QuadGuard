# Note for Future Nishant - spatial helper module for 2D quadrant calculations.
# maps (x, y) coordinates to quadrant indices 0..3 for regional coverage tracking.

def quadrant(x: float, y: float) -> int:
    """
    Returns quadrant index 0..3:
    0 = SW (x < 50, y < 50)
    1 = NW (x < 50, y >= 50)
    2 = SE (x >= 50, y < 50)
    3 = NE (x >= 50, y >= 50)
    Formula: 2 * (x >= 50) + (y >= 50)
    """
    return 2 * int(x >= 50) + int(y >= 50)
