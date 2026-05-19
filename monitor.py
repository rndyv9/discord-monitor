import os
import discum
import requests
import threading
from sseclient import SSEClient
import random
import time

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


def notify_system(text):

    requests.post(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=text.encode("utf-8"),
        headers={
            "Title": "Discord Monitor System",
            "Priority": "4"
        }
    )

def control_listener():

    url = f"https://ntfy.sh/{NTFY_TOPIC}/sse"

    messages = SSEClient(url)

    for msg in messages:

        data = msg.data.strip()

        print(f"RAW DATA: {repr(data)}")

        lower = data.lower()

        if "restartnow" in lower:

            print("Remote restart triggered")

            notify_system("Remote restart triggered")

            os._exit(1)

threading.Thread(
    target=control_listener,
    daemon=True
).start()

notify_system("Monitor started")

while True:

    try:

        print("Connecting...")

        notify_system("Connecting to Discord gateway")

        bot.gateway.run(auto_reconnect=True)

        notify_system("Gateway closed unexpectedly")

    except Exception as e:

        error_msg = f"Gateway crashed:\n{str(e)}"

        print(error_msg)

        notify_system(error_msg)

    delay = random.randint(10, 30)

    msg = f"Reconnect in {delay}s"

    print(msg)

    notify_system(msg)

    time.sleep(delay)
