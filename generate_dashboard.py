import json
import pandas as pd

# Load JSON data
with open("merged_prs_latest.json", "r") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Extract user login if user is a nested dict
if 'user' in df.columns and isinstance(df['user'][0], dict):
    df['user'] = df['user'].apply(lambda x: x.get('login', 'unknown'))

# Group and summarize
pr_count_by_user = df.groupby("user").size().reset_index(name="pr_count")

# Save result to JSON
pr_count_by_user.to_json("docs/pr_summary.json", orient="records", indent=2)

print("Saved summarized PR data to pr_summary.json")
