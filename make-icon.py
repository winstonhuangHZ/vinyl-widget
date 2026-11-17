#!/usr/bin/env python3
"""Build the macOS .icns from the checked-in, editable icon design preview.

The design spec and SVG layers are in design/vinyl-icon. Pillow and Apple's
iconutil are only needed when regenerating the icon, not when building the app.
"""
from pathlib import Path
import subprocess
import sys
import tempfile

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required to regenerate the icon: pip3 install pillow")

root = Path(__file__).resolve().parent
source = root / "design/vinyl-icon/vinyl-icon.preview.png"
destination = root / "Resources/AppIcon.icns"
source_image = Image.open(source).convert("RGBA")
if source_image.size != (1024, 1024):
    sys.exit(f"Expected a 1024×1024 source icon, got {source_image.size}")

# A legacy .icns has no system-applied Mac icon inset.  Center the rounded
# artwork in the same 824-point footprint used by common macOS app icons.
image = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
artwork = source_image.resize((824, 824), Image.Resampling.LANCZOS)
image.alpha_composite(artwork, (100, 100))

destination.parent.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix="vinyl-icon-") as temporary:
    iconset = Path(temporary) / "AppIcon.iconset"
    iconset.mkdir()
    for size in (16, 32, 128, 256, 512):
        for factor in (1, 2):
            suffix = "@2x" if factor == 2 else ""
            image.resize((size * factor, size * factor), Image.Resampling.LANCZOS).save(
                iconset / f"icon_{size}x{size}{suffix}.png"
            )
    subprocess.run(["iconutil", "-c", "icns", str(iconset), "-o", str(destination)], check=True)
print(f"wrote {destination}")
