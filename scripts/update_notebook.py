"""Update metajudge_submission.ipynb with 100-item V2 dataset."""
import json
import csv
import io

REPO = "/home/user/workspace/metajudge"

# Load production files
with open(f"{REPO}/data/calibration.csv") as f:
    reader = csv.DictReader(f)
    cal_rows = list(reader)

answer_key = json.load(open(f"{REPO}/data/calibration_answer_key.json"))

# Build CALIBRATION_CSV string
csv_buf = io.StringIO()
writer = csv.DictWriter(csv_buf, fieldnames=["example_id", "prompt", "gold_answer", "difficulty"],
                         quoting=csv.QUOTE_MINIMAL)
writer.writeheader()
for row in cal_rows:
    writer.writerow(row)
csv_string = csv_buf.getvalue().strip()

# Build ANSWER_KEY dict string
ak_lines = []
for eid, spec in sorted(answer_key.items(), key=lambda x: int(x[0].split("_")[1])):
    # Map grader_rule to short form
    rule_map = {
        "numeric_equivalence": "numeric",
        "alias_match": "alias",
        "yes_no_match": "yes_no",
    }
    rule = rule_map.get(spec["grader_rule"], spec["grader_rule"])
    
    aliases_str = json.dumps(spec["aliases"])
    canonical = spec["gold_answer"]
    ak_lines.append(f'    "{eid}": {{"canonical": "{canonical}", "aliases": {aliases_str}, "rule": "{rule}"}},')

# Remove trailing comma from last line
if ak_lines:
    ak_lines[-1] = ak_lines[-1][:-1]  # remove trailing comma

# Build diff distribution string
diffs = {}
for row in cal_rows:
    d = row["difficulty"]
    diffs[d] = diffs.get(d, 0) + 1
dist_str = " / ".join(f"{diffs.get(d, 0)} {d}" for d in ["easy", "medium", "hard", "deceptive", "adversarial"])

# Build cell 3 source
cell3_source = f'''# Cell 3 — Dataset & Answer Key (embedded for Kaggle portability)
#
# 100-item V2 calibration set: {dist_str}
# Sources: authored_v2 (96), pool_upgrade (4)
# Sprint: expansion_sprint_v2 — see planning/expansion_sprint_v2.md

CALIBRATION_CSV = """{csv_string}"""

# Answer key: accepted aliases and grader rules for deterministic adjudication
ANSWER_KEY = {{

{chr(10).join(ak_lines)}
}}

# Parse CSV into list of dicts
import pandas as pd
dataset = pd.read_csv(io.StringIO(CALIBRATION_CSV))
print(f"Dataset loaded: {{len(dataset)}} items")
print(f"Difficulty distribution:\\n{{dataset['difficulty'].value_counts().to_string()}}")
print(f"Answer key entries: {{len(ANSWER_KEY)}}")'''

# Load notebook
nb = json.load(open(f"{REPO}/notebooks/metajudge_submission.ipynb"))

# Replace cell 3
nb["cells"][3]["source"] = cell3_source.split("\n")
# Fix: ipynb format requires each line to end with \n except the last
nb["cells"][3]["source"] = [line + "\n" for line in cell3_source.split("\n")]
# Remove trailing \n from the very last line
if nb["cells"][3]["source"]:
    nb["cells"][3]["source"][-1] = nb["cells"][3]["source"][-1].rstrip("\n")

# Also update cell 0 (markdown header) to reflect V2
cell0_src = "".join(nb["cells"][0]["source"])
cell0_src = cell0_src.replace("20-item pilot calibration set", "100-item V2 calibration set")
cell0_src = cell0_src.replace("20 calibration items", "100 calibration items")
nb["cells"][0]["source"] = [line + "\n" for line in cell0_src.split("\n")]
if nb["cells"][0]["source"]:
    nb["cells"][0]["source"][-1] = nb["cells"][0]["source"][-1].rstrip("\n")

# Update cell 6 comment if it references "20-item pilot"
cell6_src = "".join(nb["cells"][6]["source"])
cell6_src = cell6_src.replace("full 20-item pilot", "full 100-item V2 calibration set")
cell6_src = cell6_src.replace("20-item", "100-item")
nb["cells"][6]["source"] = [line + "\n" for line in cell6_src.split("\n")]
if nb["cells"][6]["source"]:
    nb["cells"][6]["source"][-1] = nb["cells"][6]["source"][-1].rstrip("\n")

# Save
with open(f"{REPO}/notebooks/metajudge_submission.ipynb", "w") as f:
    json.dump(nb, f, indent=1)

print("Notebook updated successfully!")
print(f"Cell 3: {len(nb['cells'][3]['source'])} lines")

# Verify the embedded CSV parses correctly
import pandas as pd
embedded_csv = csv_string
df = pd.read_csv(io.StringIO(embedded_csv))
print(f"Embedded CSV parses to {len(df)} rows")
print(f"Difficulty: {dict(df['difficulty'].value_counts())}")
print(f"IDs: {df['example_id'].iloc[0]} to {df['example_id'].iloc[-1]}")

