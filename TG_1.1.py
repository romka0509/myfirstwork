import tkinter as tk
from tkinter import ttk
from telethon import TelegramClient, events
import asyncio
import threading
import json
from asyncio import run_coroutine_threadsafe

CONFIG_FILE = "config.json"

class CustomEntry(tk.Entry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind('<Control-v>', self.paste_standard)
        self.bind('<Button-3>', self.show_context_menu)

    def paste_standard(self, event):
        super().event_generate("<<Paste>>")

    def show_context_menu(self, event):
        context_menu = tk.Menu(self, tearoff=0)
        context_menu.add_command(label="Вставить", command=lambda: self.event_generate("<<Paste>>"))
        context_menu.post(event.x_root, event.y_root)

def start_forwarding(api_id, api_hash, channel_id, keywords, selected_chats_ids):
    client = TelegramClient('forwarder', api_id, api_hash)

    async def main():
        async with client:
         @client.on(events.NewMessage(chats=chats))
         async def handler(event):
            for keyword in keywords:
                if keyword.lower() in event.message.text.lower():
                    await client.forward_messages(
                        entity=channel,
                        messages=event.message,
                        from_peer=event.message.peer_id,
                        silent=True,
                        with_my_score=False,
                        remove_caption=False,
                        as_album=False,
                        grouped=False,
                        send_copy=True,
                        context_info=event.message.reply_markup,
                        link_preview=False,
                    )
                    break

    def run_asyncio_loop():
        asyncio.set_event_loop(asyncio.new_event_loop())
        asyncio.get_event_loop().run_until_complete(main())

    threading.Thread(target=run_asyncio_loop, daemon=True).start()
    return client

def on_submit():
    api_id = api_id_entry.get()
    api_hash = api_hash_entry.get()
    channel_id = int(channel_id_entry.get())
    keywords = [keyword.strip() for keyword in keywords_entry.get().split(',')]
    selected_chats_ids = [int(chat_id) for chat_id in selected_chats_ids_entry.get().split(',')]

    config = {
        "api_id": api_id,
        "api_hash": api_hash,
        "channel_id": channel_id,
        "keywords": keywords,
        "selected_chats_ids": selected_chats_ids
    }

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

    global client
    client = start_forwarding(api_id, api_hash, channel_id, keywords, selected_chats_ids)
    stop_button.config(state="normal")
    submit_button.config(state="disabled")

def on_stop():
    global client
    if client:
        loop = asyncio.get_event_loop()
        run_coroutine_threadsafe(client.disconnect(), loop)
        client = None
    stop_button.config(state="disabled")
    submit_button.config(state="normal")

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {}
    return config

app = tk.Tk()
app.title("Telegram Message Forwarder")

config = load_config()
client = None

tk.Label(app, text="API ID:").grid(row=0, column=0)
api_id_entry = CustomEntry(app)
api_id_entry.insert(0, config.get("api_id", ""))
api_id_entry.grid(row=0, column=1)

tk.Label(app, text="API HASH:").grid(row=1, column=0)
api_hash_entry = CustomEntry(app)
api_hash_entry.insert(0, config.get("api_hash", ""))
api_hash_entry.grid(row=1, column=1)

tk.Label(app, text="ID канала:").grid(row=2, column=0)
channel_id_entry = CustomEntry(app)
channel_id_entry.insert(0, config.get("channel_id", ""))
channel_id_entry.grid(row=2, column=1)

tk.Label(app, text="Ключевые слова (через запятую):").grid(row=3, column=0)
keywords_entry = CustomEntry(app)
keywords_entry.insert(0, ", ".join(config.get("keywords", [])))
keywords_entry.grid(row=3, column=1)

tk.Label(app, text="ID выбранных чатов (через запятую):").grid(row=4, column=0)
selected_chats_ids_entry = CustomEntry(app)
selected_chats_ids_entry.insert(0, ", ".join(map(str, config.get("selected_chats_ids", []))))
selected_chats_ids_entry.grid(row=4, column=1)

submit_button = ttk.Button(app, text="Запустить", command=on_submit)
submit_button.grid(row=5, column=0, pady=10)

stop_button = ttk.Button(app, text="Остановить", command=on_stop, state="disabled")
stop_button.grid(row=5, column=1, pady=10)

app.mainloop()