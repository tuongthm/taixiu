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
intents.message_content = True # QUAN TRỌNG ĐỂ BOT ĐỌC LỆNH
bot = commands.Bot(command_prefix="!", intents=intents)

# VÒNG LẶP TỰ ĐỘNG CHẠY TÀI XỈU
@tasks.loop(seconds=60) # Cứ 60 giây chạy 1 ván
async def tx_loop():
    # Tìm kênh có tên 'tài-xỉu' hoặc 'tai-xiu'
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
        tx_loop.start() # Bắt đầu vòng lặp

# Lệnh kiểm tra thủ công (nếu cần)
@bot.command()
async def tx(ctx, choise: str):
    d1, d2, d3 = random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)
    total = d1 + d2 + d3
    res = "tai" if total >= 11 else "xiu"
    await ctx.send(f"🎲 Kết quả: {d1}-{d2}-{d3} ({total}) -> {res.upper()}")

# ==================== BẬT BOT ====================
# ĐỪNG QUÊN THAY TOKEN MỚI VÀO ĐÂY
TOKEN = "MTUzMTMzMzI0MTU4NjQ1MDQ4Mw.GH6om-.0SoocBsPayB-OMfJhnuXQeZkbZC1dmnhufTGWQ"
bot.run(TOKEN)
