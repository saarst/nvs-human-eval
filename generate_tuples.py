import numpy as np
import torch
import random
import json
from pathlib import Path
from collections import defaultdict

# === Step 1: Set seed ===
SEED = 42
np.random.seed(SEED)
torch.manual_seed(SEED)
random.seed(SEED)

# === Step 2: Load object names ===
with open("../pytorch3d/objects_val.txt", "r") as f:
    object_names = [line.strip() for line in f.readlines()]
assert len(object_names) == 40, "Expected 40 objects in the list"

# === Step 3: Generate comparisons ===
model_names = ["zero123", "zero123XL", "zero2hero", "SEVA", "openLRM"]
angles = list(range(16))
num_comparisons = 4

# Define small and large deltas in modular space
small_deltas = {1, 2, 3, 15, 14, 13}
large_deltas = {4, 5, 6, 7, 8, 9, 10, 11, 12}

# Generate all possible unordered model pairs
all_model_pairs = []
for i in range(len(model_names)):
    for j in range(i + 1, len(model_names)):
        all_model_pairs.append((model_names[i], model_names[j]))

def choose_angle_pair(valid_deltas):
    while True:
        a, b = np.random.choice(angles, size=2, replace=False)
        delta = (b - a) % 16
        if delta in valid_deltas:
            return a, b

all_tests = []

for obj in object_names:
    # Small rotation pair
    src_small, tgt_small = choose_angle_pair(small_deltas)
    # Large rotation pair
    src_large, tgt_large = choose_angle_pair(large_deltas)

    for (src, tgt) in [(src_small, tgt_small), (src_large, tgt_large)]:

        # Randomly choose 4 unique pairs (no duplicates)
        selected_pairs = random.sample(all_model_pairs, num_comparisons)
        for m1, m2 in selected_pairs:
            all_tests.append({
                "object": obj,
                "source_angle": int(src),
                "target_angle": int(tgt),
                "model1": m1,
                "model2": m2
            })

# === Step 4: Save single full test set as JSON ===
output_dir = Path("json_tests")
output_dir.mkdir(exist_ok=True)

random.shuffle(all_tests)
with open(output_dir / "all_eval_tasks.json", "w") as f:
    json.dump(all_tests, f, indent=2)

# === Step 5: Build per-model rendering inputs (src + tgt needed!) ===
model_render_tasks = defaultdict(set)

for entry in all_tests:
    obj = entry["object"]
    src = entry["source_angle"]
    tgt = entry["target_angle"]
    m1 = entry["model1"]
    m2 = entry["model2"]

    model_render_tasks[m1].add((obj, src, tgt))
    model_render_tasks[m2].add((obj, src, tgt))

# === Step 6: Save per-model render task lists as JSON and print their lengths ===
for model, tasks in model_render_tasks.items():
    render_list = [
        {
            "object": obj,
            "source_angle": int(src),
            "target_angle": int(tgt),
            "delta_angle": int((tgt - src) % 16)
        }
        for obj, src, tgt in sorted(tasks)
    ]
    
    json_path = output_dir / f"render_input_{model}.json"
    with open(json_path, "w") as f:
        json.dump(render_list, f, indent=2)

    print(f"📦 Model '{model}': {len(render_list)} render instructions saved → {json_path.name}")

# === Step 7: Create TaskCounts CSV for Google Sheet ===
import csv

task_set = set()
for entry in all_tests:
    m1, m2 = sorted([entry["model1"], entry["model2"]])
    task_set.add((entry["object"], entry["source_angle"], entry["target_angle"], m1, m2))

csv_path = output_dir / "task_counts_new.csv"
with open(csv_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Object", "SourceAngle", "TargetAngle", "Model1", "Model2", "Count"])
    for row in sorted(task_set):
        writer.writerow(list(row) + [0])

print(f"📄 TaskCounts CSV saved → {csv_path}")

