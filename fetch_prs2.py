import requests
import os
import json
import time

owner = "barisohussein"
repo = "barisohussein"
branch = "master"
per_page = 100
page = 1

token = os.environ.get("GITHUB_TOKEN")
if not token:
    raise ValueError("Missing GITHUB_TOKEN environment variable")

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
    if response.status_code != 200:
        raise Exception(f"GitHub API error: {response.status_code} {response.text}")

    data = response.json()
    if not data:
        break

    for pr in data:
        if pr.get("merged_at"):
            # Fetch detailed info for this PR
            pr_detail_url = pr["url"]
            pr_detail_resp = requests.get(pr_detail_url, headers=headers)
            if pr_detail_resp.status_code != 200:
                print(f"Warning: Failed to fetch details for PR #{pr['number']}")
                continue
            pr_detail = pr_detail_resp.json()

            merged_prs.append({
                "id": pr_detail["id"],
                "number": pr_detail["number"],
                "title": pr_detail["title"],
                "user": pr_detail["user"]["login"],
                "merged_at": pr_detail["merged_at"],
                "merged_by": pr_detail["merged_by"]["login"] if pr_detail.get("merged_by") else None,
                "created_at": pr_detail["created_at"],
                "closed_at": pr_detail["closed_at"],
                "body": pr_detail["body"],
                "comments": pr_detail["comments"],
                "commits": pr_detail["commits"],
                "changed_files": pr_detail["changed_files"],
                "additions": pr_detail["additions"],
                "deletions": pr_detail["deletions"]
            })

            # Be kind to GitHub API rate limits
            time.sleep(0.1)

    page += 1

# Always overwrite the same file
filename = "merged_prs_latest.json"

with open(filename, "w") as f:
    json.dump(merged_prs, f, indent=2)

print(f"Saved {len(merged_prs)} merged PRs to {filename}")
