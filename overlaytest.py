from flask import Flask, render_template
from flask_socketio import SocketIO
from TikTokLive import TikTokLiveClient
from TikTokLive.events import GiftEvent
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# TikTok Live Client
client = TikTokLiveClient(unique_id="@am.psbl")

@app.route("/")
def index():
    return render_template("index.html")  # This will load the frontend overlay

# Listen for TikTok Gifts
@client.on(GiftEvent)
async def on_gift(event: GiftEvent):

    data = {
        "user": event.user.nickname,
        "gift": event.gift.name,
        "count": event.repeat_count,
        "image": event.gift.image.url_list[0]
    }

    if event.gift.streakable and not event.streaking:
        print(f"{event.user.unique_id} was send {event.repeat_count}x \"{event.gift.name}\"")
        for i in range(event.repeat_count):
            socketio.emit("new_gift", data)
            time.sleep(0.1)

    elif not event.gift.streakable:
        print(f"{event.user.unique_id} sent \"{event.gift.name}\"")
        socketio.emit("new_gift", data)

# Start Flask & TikTokLive
def run():
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    client.web.set_session_id("f5df2d553b0779aba4b98685dc1c92a4")
    from threading import Thread
    Thread(target=client.run).start()
    run()
