import json
import os
from pathlib import Path
from zipfile import ZipFile

# === Paths ===
json_path = Path("json_tests/render_input_zero2hero.json")
image_root = Path.home() / "pytorch3d" / "merged_images"
zip_output_path = Path("zero2hero_sources.zip")

# === Load JSON ===
with open(json_path, "r") as f:
    data = json.load(f)

# === Collect required image paths ===
needed_paths = set()
for entry in data:
    obj = entry["object"]
    angle = entry["source_angle"]
    img_path = image_root / obj / f"image_{angle}.png"
    if img_path.exists():
        needed_paths.add(img_path)
    else:
        print(f"⚠️ Missing: {img_path}")

# === Create ZIP ===
with ZipFile(zip_output_path, "w") as zipf:
    for path in sorted(needed_paths):
        arcname = path.relative_to(image_root.parent)  # Relative path inside zip
        zipf.write(path, arcname)

print(f"✅ Done: {len(needed_paths)} images zipped to {zip_output_path}")
