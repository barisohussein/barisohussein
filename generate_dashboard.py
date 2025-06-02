import json
import pandas as pd
import plotly.express as px

# Load JSON data file from the repo
with open("merged_prs_20250602_041846.json", "r") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Example visualization: Number of PRs merged by user
pr_count_by_user = df.groupby("user").size().reset_index(name="pr_count")

fig = px.bar(pr_count_by_user, x="user", y="pr_count",
             title="Number of Merged PRs by User",
             labels={"user": "GitHub User", "pr_count": "Merged PR Count"})

fig.write_html("pr_dashboard.html", full_html=True, include_plotlyjs='cdn')

print("Dashboard saved as pr_dashboard.html")
