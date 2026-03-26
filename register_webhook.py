"""
Run this script ONCE after deploying to register your webhook URL with Telegram.
Usage: python register_webhook.py https://your-domain.com
       python register_webhook.py https://abc123.ngrok.io   (for local dev)
"""
import sys
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN not set in .env")
    sys.exit(1)

if len(sys.argv) < 2:
    print("Usage: python register_webhook.py <your_public_url>")
    sys.exit(1)

base_url = sys.argv[1].rstrip("/")
webhook_url = f"{base_url}/telegram/webhook"

resp = httpx.post(
    f"https://api.telegram.org/bot{TOKEN}/setWebhook",
    json={"url": webhook_url},
)
data = resp.json()

if data.get("ok"):
    print(f"✅ Webhook registered: {webhook_url}")
else:
    print(f"❌ Failed: {data}")
