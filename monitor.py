import os
import discum
import requests

TOKEN = os.getenv("DISCORD_TOKEN")
NTFY_TOPIC = os.getenv("NTFY_TOPIC")

KEYWORDS = os.getenv("KEYWORDS", "").lower().split(",")

bot = discum.Client(token=TOKEN)

def notify(text):

    requests.post(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=text.encode("utf-8"),
        headers={
            "Title": "Discord Alert",
            "Priority": "5"
        }
    )

@bot.gateway.command
def on_message(resp):

    if resp.event.message:

        m = resp.parsed.auto()

        content = m.get("content", "")

        if not content:
            return

        lower = content.lower()

        for keyword in KEYWORDS:

            if keyword in lower:

                text = (
                    f"Keyword: {keyword}\n"
                    f"User: {m['author']['username']}\n"
                    f"Message:\n{content}"
                )

                print(text)

                notify(text)

                break

bot.gateway.run(auto_reconnect=True)
