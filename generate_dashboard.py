import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load JSON data file from the repo
with open("merged_prs_latest.json", "r") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Example visualization: Number of PRs merged by user
pr_count_by_user = df.groupby("user").size().reset_index(name="pr_count")

# Bar chart of PRs merged by user
bar_fig = px.bar(
    pr_count_by_user,
    x="user",
    y="pr_count",
    title="Number of Merged PRs by User",
    labels={"user": "GitHub User", "pr_count": "Merged PR Count"}
)

# Create a table with all columns from the original data
table_fig = go.Figure(data=[go.Table(
    header=dict(values=list(df.columns), fill_color='lightgrey', align='left'),
    cells=dict(values=[df[col] for col in df.columns], fill_color='white', align='left')
)])
table_fig.update_layout(title="Merged PR Details")

# Create a dashboard with two rows: bar chart and table
combined_fig = make_subplots(
    rows=2, cols=1,
    specs=[[{"type": "xy"}], [{"type": "table"}]],
    subplot_titles=("Merged PRs by User", "Detailed PR Data")
)

# Add bar chart to first row
combined_fig.add_trace(bar_fig['data'][0], row=1, col=1)

# Add table to second row
combined_fig.add_trace(table_fig['data'][0], row=2, col=1)

# Final layout tweaks
combined_fig.update_layout(height=900, showlegend=False)

# Save HTML dashboard to current directory as index.html
combined_fig.write_html("indexed.html", full_html=True, include_plotlyjs='cdn')

print("Dashboard with table saved as index.html")
