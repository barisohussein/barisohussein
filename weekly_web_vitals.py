import os
import requests
import matplotlib.pyplot as plt
import datetime
import smtplib
from email.message import EmailMessage

# --- 1. Fetch CrUX data ---
CRUX_API = os.environ["CRUX_API"]
API_KEY = CRUX_API
URL = f"https://chromeuxreport.googleapis.com/v1/records:queryHistoryRecord?key={API_KEY}"

payload = {
    "origin": "https://www.brooksrunning.com",
    "collectionPeriodCount": 25,
    "formFactor": "PHONE"   # Phone-only data
}

response = requests.post(URL, json=payload)
if response.status_code != 200:
    print("Error fetching data:", response.text)
    exit()

data = response.json()
metrics = data.get("record", {}).get("metrics", {})
periods = data.get("record", {}).get("collectionPeriods", [])
dates = [datetime.date(p["lastDate"]["year"], p["lastDate"]["month"], p["lastDate"]["day"]) for p in periods]

def extract_metric(metric_name):
    """Extract p75 timeseries safely"""
    return metrics.get(metric_name, {}).get("percentilesTimeseries", {}).get("p75s", [])

# Extract metrics
cls_p75 = extract_metric("cumulative_layout_shift")
lcp_p75 = extract_metric("largest_contentful_paint")
inp_p75 = extract_metric("interaction_to_next_paint")

# --- 2. Plot metrics ---
plt.style.use("ggplot")      # clean, minimal
plt.style.use("bmh")         # clean with grids
plt.style.use("classic")     # traditional matplotlib
fig, axs = plt.subplots(3, 1, figsize=(14, 14), sharex=True)
fig.subplots_adjust(top=0.88)

# --- TITLE + SUBTITLE ---
fig.suptitle(
    "Web Performance Report – BrooksRunning.com",
    fontsize=20, weight="bold", y=0.93
)
fig.text(
    0.5, 0.88,
    "25-week Chrome UX Report history (p75) for Phone users\n"
    "Metrics include Cumulative Layout Shift (CLS), Largest Contentful Paint (LCP), and Interaction to Next Paint (INP).",
    ha="center", fontsize=12, color="dimgray"
)

# Thresholds
thresholds = {
    "cls": [0.1, 0.25],
    "lcp": [2500, 4000],
    "inp": [200, 500]
}

# --- CLS (first) ---
axs[0].plot(dates, cls_p75, marker="^", linewidth=2, color="tab:red", label="CLS p75")
axs[0].axhline(thresholds["cls"][0], color="green", linestyle="--", label="Good ≤ 0.1")
axs[0].axhline(thresholds["cls"][1], color="orange", linestyle="--", label="Needs Improvement ≤ 0.25")

# Convert CLS values to floats
cls_p75 = [float(x) for x in cls_p75]

# Calculate max for flipped y-axis
max_val = max(cls_p75 + thresholds["cls"]) * 1.1
axs[0].set_ylim(max_val, 0)  # reversed axis, 0 at bottom

axs[0].set_title("Cumulative Layout Shift (CLS)", fontsize=14, weight="bold")
axs[0].set_ylabel("Score (p75)", fontsize=12)
axs[0].legend(loc="upper left", frameon=True)
axs[0].grid(alpha=0.3)


# --- LCP ---
axs[1].plot(dates, lcp_p75, marker="o", linewidth=2, color="tab:blue", label="LCP p75")
axs[1].axhline(thresholds["lcp"][0], color="green", linestyle="--", label="Good ≤ 2.5s")
axs[1].axhline(thresholds["lcp"][1], color="orange", linestyle="--", label="Needs Improvement ≤ 4s")
axs[1].set_title("Largest Contentful Paint (LCP)", fontsize=14, weight="bold")
axs[1].set_ylabel("Milliseconds (p75)", fontsize=12)
axs[1].legend(loc="upper left", frameon=True)
axs[1].grid(alpha=0.3)

# --- INP ---
axs[2].plot(dates, inp_p75, marker="s", linewidth=2, color="tab:green", label="INP p75")
axs[2].axhline(thresholds["inp"][0], color="green", linestyle="--", label="Good ≤ 200ms")
axs[2].axhline(thresholds["inp"][1], color="orange", linestyle="--", label="Needs Improvement ≤ 500ms")
axs[2].set_title("Interaction to Next Paint (INP)", fontsize=14, weight="bold")
axs[2].set_ylabel("Milliseconds (p75)", fontsize=12)
axs[2].set_xlabel("Date", fontsize=12)
axs[2].legend(loc="upper left", frameon=True)
axs[2].grid(alpha=0.3)

plt.xticks(rotation=45)
plt.tight_layout(rect=[0, 0, 1, 0.9])

# Save plot
plot_path = "/tmp/web_vitals_report.png"
plt.savefig(plot_path, dpi=150)
plt.close()

# --- 3. Send email via Gmail ---
EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
TO_EMAIL = "barisohussein3@gmail.com"  # change to your recipient

msg = EmailMessage()
msg['Subject'] = "Weekly Web Performance Report – BrooksRunning.com"
msg['From'] = EMAIL_ADDRESS
msg['To'] = TO_EMAIL
msg.set_content("Attached is the weekly Chrome UX Report for BrooksRunning.com (Phone users).")

# Attach the plot
with open(plot_path, "rb") as f:
    msg.add_attachment(f.read(), maintype='image', subtype='png', filename="web_vitals_report.png")

# Send email
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    smtp.send_message(msg)

print("Weekly report sent successfully!")
