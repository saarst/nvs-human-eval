import json
from pathlib import Path

def validate_model_renders(model_name, render_root="generatedImages", task_root="json_tests"):
    render_json = Path(task_root) / f"render_input_{model_name}.json"
    render_dir = Path(render_root) / model_name

    if not render_json.exists():
        print(f"❌ Missing input file: {render_json}")
        return

    with open(render_json, "r") as f:
        tasks = json.load(f)

    missing = []
    for task in tasks:
        obj = task["object"]
        src = task["source_angle"]
        tgt = task["target_angle"]
        filename = f"{obj}_{src}_to_{tgt}.png"
        if not (render_dir / filename).exists():
            missing.append(filename)

    print(f"🧪 Validation for model: {model_name}")
    print(f"✅ Found {len(tasks) - len(missing)} / {len(tasks)} images")
    # if missing:
    #     print("❌ Missing files:")
    #     for fname in missing:
    #         print(f"  - {fname}")
    # else:
    #     print("🎉 All expected images are present!")

# === Example usage ===
if __name__ == "__main__":
    model_names = ["zero123", "zero123XL", "zero2hero", "SEVA", "openLRM"]
    for model in model_names:
        validate_model_renders(model)
