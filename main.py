import os
import random
import asyncio
import discord
from discord.ext import commands, tasks
from flask import Flask
from threading import Thread

# ==================== WEB SERVER GIỮ BOT 24/7 ====================
app = Flask('')
@app.route('/')
def home(): return "Bot Tài Xỉu đang chạy!"
def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
Thread(target=run_web, daemon=True).start()

# ==================== CẤU HÌNH BOT ====================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# VÒNG LẶP TỰ ĐỘNG CHẠY TÀI XỈU
@tasks.loop(seconds=60)
async def tx_loop():
    channel = discord.utils.get(bot.get_all_channels(), name="tài-xỉu")
    if channel:
        d1, d2, d3 = random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)
        total = d1 + d2 + d3
        ket_qua = "TÀI" if total >= 11 else "XỈU"
        await channel.send(f"🎲 **TỰ ĐỘNG:** Kết quả ván này: **{d1}-{d2}-{d3}** ({total} - {ket_qua})")

@bot.event
async def on_ready():
    print(f"Bot {bot.user.name} đã online!")
    if not tx_loop.is_running():
        tx_loop.start()

@bot.command()
async def tx(ctx, choise: str):
    d1, d2, d3 = random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)
    total = d1 + d2 + d3
    res = "tai" if total >= 11 else "xiu"
    await ctx.send(f"🎲 Kết quả: {d1}-{d2}-{d3} ({total}) -> {res.upper()}")

# ==================== BẬT BOT ====================
TOKEN = "MTM0MTMzMzI0MTU4NjQ1MDQ4Mw.G4E08T.X2S9E74_3v3XtbX.7Y33XI_w0k20d9SC9uzK9YnouQDJ0uUFy0NAFg"
bot.run(TOKEN)
    
