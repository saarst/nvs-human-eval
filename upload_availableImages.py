import json
import csv
from pathlib import Path

# === CONFIG ===
eval_json_path = Path("json_tests/all_eval_tasks.json")
generated_root = Path("generatedImages")  # where rendered images are stored
csv_output = "AvailableImages.csv"
upload_to_google = True

# === Step 1: Load tasks ===
with open(eval_json_path, "r") as f:
    tasks = json.load(f)

# === Step 2: Check which images exist ===
image_set = set()

for task in tasks:
    obj = task["object"]
    src = task["source_angle"]
    tgt = task["target_angle"]
    m1 = task["model1"]
    m2 = task["model2"]

    filename = f"{obj}_{src}_to_{tgt}.png"

    path1 = generated_root / m1 / filename
    path2 = generated_root / m2 / filename

    if path1.exists():
        image_set.add((obj, src, tgt, m1))
    if path2.exists():
        image_set.add((obj, src, tgt, m2))

# === Step 3: Save CSV ===
rows = sorted(image_set)
with open(csv_output, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Object", "Source_Angle", "Target_Angle", "Model"])
    writer.writerows(rows)

print(f"✅ Done: {len(image_set)} image references saved to {csv_output}")

if upload_to_google:
    from oauth2client.service_account import ServiceAccountCredentials
    import gspread

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("gspread_key.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open("NVS Evaluation")  # <- name of your Google Sheet
    worksheet = sheet.worksheet("AvailableImages")  # <- name of your tab

    worksheet.clear()
    worksheet.append_rows([["Object", "Source_Angle", "Target_Angle", "Model"]] + rows)
    print(f"☁️ Uploaded to Google Sheet: NVS Evaluation → AvailableImages")
