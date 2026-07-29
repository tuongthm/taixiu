import os
import random
import asyncio
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

# ==================== WEB SERVER CHỐNG TIMED OUT ====================
app = Flask('')

@app.route('/')
def home():
    return "Bot Discord đang chạy 24/7!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

keep_alive()

# ==================== CẤU HÌNH BOT DISCORD ====================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

user_balances = {}

def get_bal(uid):
    return user_balances.get(uid, 2000)

def set_bal(uid, amount):
    user_balances[uid] = max(0, get_bal(uid) + amount)

@bot.event
async def on_ready():
    print(f"=== BOT {bot.user.name} ĐÃ ONLINE ĐẦY ĐỦ TÍNH NĂNG! ===")
    await bot.change_presence(activity=discord.Game(name="!helpbot | All-in-One"))

# ==================== KINH TẾ & CASINO ====================

@bot.command(name="sodu", aliases=["vi", "bal"])
async def check_balance(ctx, member: discord.Member = None):
    target = member or ctx.author
    bal = get_bal(target.id)
    await ctx.send(f"💳 Ví của **{target.display_name}**: `{bal:,}` xu")

@bot.command(name="diemdanh", aliases=["daily"])
async def daily_reward(ctx):
    reward = random.randint(1000, 5000)
    set_bal(ctx.author.id, reward)
    await ctx.send(f"🎁 **{ctx.author.display_name}** đã điểm danh và nhận `{reward:,}` xu!")

@bot.command(name="tx", aliases=["taixiu"])
async def play_tx(ctx, choise: str, bet: int):
    choise = choise.lower()
    if choise not in ["tai", "tài", "xiu", "xỉu"] or bet <= 0 or bet > get_bal(ctx.author.id):
        await ctx.send("❌ Đặt cược không hợp lệ hoặc không đủ xu!")
        return

    d1, d2, d3 = random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)
    total = d1 + d2 + d3
    res = "tai" if total >= 11 else "xiu"
    win = (choise in ["tai", "tài"] and res == "tai") or (choise in ["xiu", "xỉu"] and res == "xiu")

    if win:
        set_bal(ctx.author.id, bet)
        await ctx.send(f"🎲 Kết quả: **{d1}-{d2}-{d3}** ({total} - {'TÀI' if res=='tai' else 'XỈU'})\n🎉 **{ctx.author.display_name}** THẮNG `+{bet:,}` xu!")
    else:
        set_bal(ctx.author.id, -bet)
        await ctx.send(f"🎲 Kết quả: **{d1}-{d2}-{d3}** ({total} - {'TÀI' if res=='tai' else 'XỈU'})\n😭 **{ctx.author.display_name}** THUA `-{bet:,}` xu!")

@bot.command(name="baucua", aliases=["bc"])
async def play_bc(ctx, vat: str, bet: int):
    ds = ["bầu", "cua", "tôm", "cá", "gà", "nai"]
    vat = vat.lower()
    if vat not in ds or bet <= 0 or bet > get_bal(ctx.author.id):
        await ctx.send("❌ Con linh vật không hợp lệ hoặc không đủ xu!")
        return

    kq = [random.choice(ds) for _ in range(3)]
    count = kq.count(vat)
    if count > 0:
        win = bet * count
        set_bal(ctx.author.id, win)
        await ctx.send(f"🎰 Mở bát: **{' - '.join(kq).upper()}**\n🎉 Trúng {count} con **{vat.upper()}**! Thắng `+{win:,}` xu!")
    else:
        set_bal(ctx.author.id, -bet)
        await ctx.send(f"🎰 Mở bát: **{' - '.join(kq).upper()}**\n😭 Không có con **{vat.upper()}** nào! Mất `-{bet:,}` xu.")

@bot.command(name="helpbot")
async def show_help(ctx):
    embed = discord.Embed(title="🤖 BOT TAIXIU - LỆNH", color=discord.Color.green())
    embed.add_field(name="💰 Kinh tế", value="`!sodu`, `!diemdanh`", inline=False)
    embed.add_field(name="🎲 Game", value="`!tx <tai/xiu> <tiền>`, `!bc <bầu/cua/tôm/cá/gà/nai> <tiền>`", inline=False)
    await ctx.send(embed=embed)

# ==================== BẬT BOT ====================
TOKEN = "MTUzMTMzMzI0MTU4NjQ1MDQ4Mw.GCSKt5.5FFT1HtSkXEBWVFouZ9rXvc-29mRmEm1ILv2eM"
bot.run(TOKEN)
