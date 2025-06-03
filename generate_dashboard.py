import json
import pandas as pd

# Load JSON data file from the repo
with open("merged_prs_latest.json", "r") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Example aggregation: Number of PRs merged by user
pr_count_by_user = df.groupby("user").size().reset_index(name="pr_count")

# Convert to dictionary for saving
result = pr_count_by_user.to_dict(orient="records")

# Save to a new JSON file
with open("pr_summary.json", "w") as f:
    json.dump(result, f, indent=2)

print("Saved summarized PR data to pr_summary.json")
