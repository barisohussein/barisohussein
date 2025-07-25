import requests
import os
import json
from datetime import datetime

owner = "barisohussein"    # replace with your GitHub username or org
repo = "barisohussein"         # replace with your repo name
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
            merged_prs.append({
                "id": pr["id"],
                "number": pr["number"],
                "title": pr["title"],
                "user": pr["user"]["login"],
                "merged_at": pr["merged_at"]
            })

    page += 1

timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
filename = f"merged_prs_{timestamp}.json"

with open(filename, "w") as f:
    json.dump(merged_prs, f, indent=2)

print(f"Saved {len(merged_prs)} merged PRs to {filename}")
