import requests
import os
import json
from datetime import datetime
import time

owner = "barisohussein"
repo = "barisohussein"
branch = "master"
per_page = 100
page = 1

token = os.environ.get("GITHUB_TOKEN")

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github.v3+json"
}

merged_prs = []

while True:
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    params = {
        "state": "closed",
        "base": branch,
        "per_page": per_page,
        "page": page
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    if not data:
        break

    for pr in data:
        if pr.get("merged_at"):
            # Get full details for this PR to get additions, deletions, changed_files
            pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr['number']}"
            pr_response = requests.get(pr_url, headers=headers)
            pr_details = pr_response.json()

            merged_prs.append({
                "id": pr_details["id"],
                "number": pr_details["number"],
                "title": pr_details["title"],
                "user": pr_details["user"]["login"],
                "merged_at": pr_details["merged_at"],
                "additions": pr_details["additions"],
                "deletions": pr_details["deletions"],
                "changed_files": pr_details["changed_files"]
            })
            time.sleep(0.5)  # be kind to API rate limits

    page += 1

timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
filename = f"merged_prs_{timestamp}.json"

with open(filename, "w") as f:
    json.dump(merged_prs, f, indent=2)

print(f"Saved {len(merged_prs)} merged PRs to {filename}")
