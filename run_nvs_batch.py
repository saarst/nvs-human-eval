import json
import subprocess
from pathlib import Path
import argparse
import os
import sys
from subprocess import Popen, PIPE

stream=True
# === Model-specific configs ===
MODEL_CONFIG = {
    "zero123": {
        "conda_env": "zero123",
        "script": "run_zero123.py",
        "output_dir": os.path.expanduser("~/humanEvaluation/generatedImages/zero123"),
        "work_dir": os.path.expanduser("~/zero123/zero123"),
        "extra_args": [
            "--ckpt_path", "105000.ckpt",
        ]
    },
    "zero123XL": {
        "conda_env": "zero123",  # same env
        "script": "run_zero123.py",  # same script
        "output_dir": os.path.expanduser("~/humanEvaluation/generatedImages/zero123XL"),
        "work_dir": os.path.expanduser("~/zero123/zero123"),
        "extra_args": [
            "--ckpt_path", "zero123-xl.ckpt",
        ]
    },
    # "openLRM": {
    #     "conda_env": "openlrm_env",
    #     "script": "scripts/run_openlrm.py",
    #     "output_dir": "renders/openlrm",
    #     "work_dir": "/path/to/openlrm",
    #     "extra_args": []  # or your model-specific flags
    # },
    # Add SEVA, zero2hero, etc. similarly
}

def main(model_name, json_path):
    if model_name not in MODEL_CONFIG:
        raise ValueError(f"Unknown model: {model_name}")

    config = MODEL_CONFIG[model_name]
    output_root = Path(config["output_dir"])
    output_root.mkdir(parents=True, exist_ok=True)

    with open(json_path, "r") as f:
        render_tasks = json.load(f)

    print(f"📦 Starting rendering for model '{model_name}' with {len(render_tasks)} tasks...")

    for task in render_tasks:
        obj = task["object"]
        src = task["source_angle"]
        tgt = task["target_angle"]
        delta = task["delta_angle"]

        output_path = output_root / f"{obj}_{src}_to_{tgt}.png"
        if output_path.exists():
            print(f"✅ Already exists: {output_path.name}")
            continue

        # Base command
        command = [
            "conda", "run", "-n", config["conda_env"], "python", "-u", config["script"],
            "--object", obj,
            "--source_angle", str(src),
            "--target_angle", str(tgt),
            "--output_path", str(output_path)
        ]

        # Add model-specific arguments
        if "extra_args" in config:
            command += config["extra_args"]

        print(f"🚀 Running: {output_path.name} (from {config['work_dir']})")
        if stream:
            process = Popen(command, cwd=config["work_dir"], stdout=PIPE, stderr=PIPE, text=True)

            # Stream stdout
            for line in process.stdout:
                print(line, end='')  # live print without extra newlines

            # Stream stderr after stdout is done
            for line in process.stderr:
                print(line, end='', file=sys.stderr)

            process.wait()

            if process.returncode != 0:
                print(f"❌ Subprocess failed for {output_path.name}")
            else:
                print(f"✅ Finished: {output_path.name}")

        else:
            subprocess.run(command, cwd=config["work_dir"], check=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="zero123", help="Model name (e.g., zero123)")
    # parser.add_argument("--json", default="json_tests/render_input_zero123.json", help="Path to JSON file")
    args = parser.parse_args()
    args.json = f"json_tests/render_input_{args.model}.json"

    print(f"🔧 Launching renderer: model={args.model}, json={args.json}")
    main(args.model, args.json)
