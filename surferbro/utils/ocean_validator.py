"""Validate ocean designs and create proper defaults."""

import json
import numpy as np
from pathlib import Path


def validate_ocean_design(design_path: str) -> dict:
    """
    Validate an ocean design and report issues.

    Returns:
        dict with 'valid', 'errors', 'warnings'
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }

    try:
        with open(design_path, 'r') as f:
            design = json.load(f)
    except Exception as e:
        result['valid'] = False
        result['errors'].append(f"Cannot read file: {e}")
        return result

    # Check for sand/beach
    has_sand = False
    has_shallow = False
    has_deep = False

    for row in design['grid']:
        for cell in row:
            if cell['type'] == 'sand':
                has_sand = True
            if cell['type'] == 'ocean':
                if cell['depth'] < 2.0:
                    has_shallow = True
                if cell['depth'] > 5.0:
                    has_deep = True

    if not has_sand:
        result['errors'].append("No sand/beach found! Surfer needs a starting point.")
        result['valid'] = False

    if not has_shallow:
        result['warnings'].append("No shallow water (< 2m). Waves won't break properly.")

    if not has_deep:
        result['warnings'].append("No deep water (> 5m). Limited wave formation.")

    if not has_sand and not has_shallow:
        result['errors'].append("Ocean is too deep everywhere. Need beach or shallow water.")
        result['valid'] = False

    return result


def create_proper_beach_ocean(width=200, height=120, filename="proper_beach_ocean.json"):
    """
    Create a proper ocean design with beach and depth gradient.

    Args:
        width: Grid width
        height: Grid height
        filename: Output filename
    """
    grid = []

    for y in range(height):
        row = []
        for x in range(width):
            # Create depth gradient from beach to deep ocean
            # y=0 is shore, y=height is far ocean

            # Beach area (first 15% of map)
            if y < height * 0.15:
                cell = {"type": "sand", "depth": 0}

            # Shallow water (15-25% of map) - good for starting
            elif y < height * 0.25:
                depth = (y - height * 0.15) / (height * 0.1) * 1.5  # 0 to 1.5m
                cell = {"type": "ocean", "depth": depth}

            # Wave zone (25-50% of map) - waves break here
            elif y < height * 0.50:
                depth = 1.5 + (y - height * 0.25) / (height * 0.25) * 3.5  # 1.5 to 5m
                cell = {"type": "ocean", "depth": depth}

            # Deep ocean (50-100% of map) - waves form here
            else:
                depth = 5 + (y - height * 0.50) / (height * 0.50) * 10.0  # 5 to 15m
                cell = {"type": "ocean", "depth": depth}

            row.append(cell)
        grid.append(row)

    design = {
        "width": width,
        "height": height,
        "gridSize": 5,
        "grid": grid,
        "timestamp": "2025-10-26T00:00:00.000Z",
        "_note": "Proper beach ocean with depth gradient for surfing"
    }

    output_path = Path("ocean_designs") / filename
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(design, f, indent=2)

    print(f"✓ Created proper ocean design: {output_path}")
    print(f"  - Beach area: 0-{int(height*0.15)} rows")
    print(f"  - Shallow water: {int(height*0.15)}-{int(height*0.25)} rows (0-1.5m)")
    print(f"  - Wave zone: {int(height*0.25)}-{int(height*0.50)} rows (1.5-5m)")
    print(f"  - Deep ocean: {int(height*0.50)}-{height} rows (5-15m)")

    return str(output_path)


if __name__ == "__main__":
    # Create a proper ocean
    ocean_path = create_proper_beach_ocean()

    # Validate it
    result = validate_ocean_design(ocean_path)
    print(f"\nValidation: {'✓ VALID' if result['valid'] else '✗ INVALID'}")
    if result['errors']:
        print("Errors:", result['errors'])
    if result['warnings']:
        print("Warnings:", result['warnings'])
