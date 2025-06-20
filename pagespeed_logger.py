import requests
import pandas as pd
from datetime import datetime
import os
API_KEY = os.environ.get("API_KEY")

URL = "https://www.brooksrunning.com/en_us"
CSV_LOG = "pagespeed_scores.csv"

def get_pagespeed_data(url, api_key, strategy, throttling_method=None):
    api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    params = {
        "url": url,
        "key": api_key,
        "strategy": strategy,
    }
    if throttling_method:
        params["throttlingMethod"] = throttling_method
    response = requests.get(api_url, params=params)
    response.raise_for_status()
    return response.json()

def extract_scores(data):
    lighthouse = data["lighthouseResult"]
    categories = lighthouse["categories"]
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "url": lighthouse["finalUrl"],
        "strategy": lighthouse["configSettings"]["formFactor"],
        "performance": categories["performance"]["score"] * 100
    }

def log_to_csv(rows, path):
    import pathlib
    path_obj = pathlib.Path(path)
    if path_obj.exists():
        df_existing = pd.read_csv(path)
        df_new = pd.DataFrame(rows)
        df = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df = pd.DataFrame(rows)
    df.to_csv(path, index=False)

def main():
    results = []
    # Slow mobile
    data_slow = get_pagespeed_data(URL, API_KEY, "mobile")
    scores_slow = extract_scores(data_slow)
    scores_slow["test_type"] = "mobile_slow"
    results.append(scores_slow)

    # Fast mobile (no throttling)
    data_fast = get_pagespeed_data(URL, API_KEY, "mobile", throttling_method="provided")
    scores_fast = extract_scores(data_fast)
    scores_fast["test_type"] = "mobile_fast"
    results.append(scores_fast)

    log_to_csv(results, CSV_LOG)
    print("✅ Logged scores:", results)

if __name__ == "__main__":
    main()
