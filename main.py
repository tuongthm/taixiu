import os
import random
import asyncio
import discord
from discord.ext import commands, tasks
from flask import Flask
from threading import Thread

# ==================== 1. WEB SERVER KEEP-ALIVE ====================
app = Flask('')

@app.route('/')
def home():
    return "Bot Discord 24/7 đang hoạt động mượt mà!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

Thread(target=run_web, daemon=True).start()

# ==================== 2. CẤU HÌNH BOT DISCORD ====================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# XÓA HẲN LỆNH HELP MẶC ĐỊNH BẰNG help_command=None
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

user_balances = {}

def get_bal(uid):
    return user_balances.get(uid, 2000)

def set_bal(uid, amount):
    user_balances[uid] = max(0, get_bal(uid) + amount)

# ==================== 3. VÒNG LẶP TỰ ĐỘNG CHẠY TÀI XỈU 24/7 ====================
@tasks.loop(seconds=60)
async def auto_tx_loop():
    channel = discord.utils.get(bot.get_all_channels(), name="tài-xỉu") or \
              discord.utils.get(bot.get_all_channels(), name="tai-xiu")
    if channel:
        d1, d2, d3 = random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)
        total = d1 + d2 + d3
        res = "TÀI" if total >= 11 else "XỈU"
        
        embed = discord.Embed(
            title="🎲 HỆ THỐNG TỰ ĐỘNG TÀI XỈU (60s)",
            description=f"Kết quả: **{d1} - {d2} - {d3}**\nTổng điểm: **{total}** ➔ **[{res}]**",
            color=discord.Color.gold()
        )
        await channel.send(embed=embed)

@bot.event
async def on_ready():
    print(f"==========================================")
    print(f"🤖 BOT {bot.user.name} ĐÃ ONLINE THÀNH CÔNG!")
    print(f"==========================================")
    await bot.change_presence(activity=discord.Game(name="!helpbot | Casino 24/7"))
    
    if not auto_tx_loop.is_running():
        auto_tx_loop.start()

# ==================== 4. CÁC LỆNH KINH TẾ (ECONOMY) ====================

@bot.command(name="sodu", aliases=["vi", "bal"])
async def check_balance(ctx, member: discord.Member = None):
    target = member or ctx.author
    bal = get_bal(target.id)
    await ctx.send(f"💳 Ví của **{target.display_name}**: `{bal:,}` xu")

@bot.command(name="diemdanh", aliases=["daily"])
async def daily_reward(ctx):
    reward = random.randint(1000, 5000)
    set_bal(ctx.author.id, reward)
    await ctx.send(f"🎁 **{ctx.author.display_name}** đã điểm danh và nhận được `{reward:,}` xu!")

@bot.command(name="chuyentien", aliases=["pay"])
async def transfer_money(ctx, member: discord.Member, amount: int):
    if member.id == ctx.author.id:
        await ctx.send("❌ Cốt không thể tự chuyển tiền cho chính mình!")
        return
    if amount <= 0:
        await ctx.send("❌ Số tiền chuyển phải lớn hơn 0!")
        return
    if get_bal(ctx.author.id) < amount:
        await ctx.send("❌ Số dư ví không đủ để chuyển!")
        return
    
    set_bal(ctx.author.id, -amount)
    set_bal(member.id, amount)
    await ctx.send(f"💸 **{ctx.author.display_name}** đã chuyển thành công `{amount:,}` xu cho **{member.display_name}**!")

# ==================== 5. CÁC LỆNH GAME CASINO ====================

@bot.command(name="tx", aliases=["taixiu"])
async def play_tx(ctx, choise: str, bet: int):
    choise = choise.lower()
    if choise not in ["tai", "tài", "xiu", "xỉu"]:
        await ctx.send("❌ Cú pháp đúng: `!tx <tai/xiu> <tiền_cược>` (Ví dụ: `!tx tai 500`)")
        return
    if bet <= 0 or bet > get_bal(ctx.author.id):
        await ctx.send("❌ Số tiền cược không hợp lệ hoặc cốt không đủ xu trong ví!")
        return

    d1, d2, d3 = random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)
    total = d1 + d2 + d3
    res = "tai" if total >= 11 else "xiu"
    win = (choise in ["tai", "tài"] and res == "tai") or (choise in ["xiu", "xỉu"] and res == "xiu")

    if win:
        set_bal(ctx.author.id, bet)
        await ctx.send(f"🎲 Xúc xắc: **{d1} - {d2} - {d3}** ({total} điểm - **{'TÀI' if res=='tai' else 'XỈU'}**)\n🎉 **{ctx.author.display_name}** đã ĐOÁN ĐÚNG! Nhận `+{bet:,}` xu.")
    else:
        set_bal(ctx.author.id, -bet)
        await ctx.send(f"🎲 Xúc xắc: **{d1} - {d2} - {d3}** ({total} điểm - **{'TÀI' if res=='tai' else 'XỈU'}**)\n😭 **{ctx.author.display_name}** đoán sai rồi! Mất `-{bet:,}` xu.")

@bot.command(name="baucua", aliases=["bc"])
async def play_bc(ctx, vat: str, bet: int):
    ds = ["bầu", "cua", "tôm", "cá", "gà", "nai"]
    vat = vat.lower()
    if vat not in ds:
        await ctx.send("❌ Linh vật không hợp lệ! Chọn: `bầu`, `cua`, `tôm`, `cá`, `gà`, `nai`.")
        return
    if bet <= 0 or bet > get_bal(ctx.author.id):
        await ctx.send("❌ Số tiền cược không hợp lệ hoặc cốt không đủ xu!")
        return

    kq = [random.choice(ds) for _ in range(3)]
    count = kq.count(vat)
    
    if count > 0:
        win = bet * count
        set_bal(ctx.author.id, win)
        await ctx.send(f"🎰 Mở bát: **{' - '.join(kq).upper()}**\n🎉 Trúng {count} con **{vat.upper()}**! Thắng `+{win:,}` xu.")
    else:
        set_bal(ctx.author.id, -bet)
        await ctx.send(f"🎰 Mở bát: **{' - '.join(kq).upper()}**\n😭 Không có con **{vat.upper()}** nào! Mất `-{bet:,}` xu.")

# ==================== 6. BẢNG HƯỚNG DẪN LỆNH ====================

@bot.command(name="helpbot", aliases=["trogiup"])
async def show_help(ctx):
    embed = discord.Embed(title="🤖 DANH SÁCH LỆNH BOT DISCORD", color=discord.Color.blue())
    embed.add_field(name="💰 Kinh tế & Tiền tệ", value="`!diemdanh` - Điểm danh nhận xu free mỗi ngày\n`!sodu` - Xem số dư tài khoản\n`!chuyentien @User <số_tiền>` - Chuyển xu cho người khác", inline=False)
    embed.add_field(name="🎲 Game Casino", value="`!tx <tai/xiu> <tiền>` - Chơi Tài Xỉu\n`!bc <con_vật> <tiền>` - Chơi Bầu Cua (Bầu, cua, tôm, cá, gà, nai)", inline=False)
    embed.add_field(name="⚡ Tính năng tự động", value="Bot tự động lắc Tài Xỉu và trả kết quả vào kênh `#tài-xỉu` mỗi 60 giây.", inline=False)
    await ctx.send(embed=embed)

# ==================== 7. BẬT BOT ====================
TOKEN = "MTUzMTMzMzI0MTU4NjQ1MDQ4Mw.GWu8Zm.malh4eYL1rDsRY7R_FupZO1eEz9_L-yp0EPsCU"
bot.run(TOKEN)
