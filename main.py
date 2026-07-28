import os

try:
    import discord
    from discord.ext import commands
    from discord.ui import Button, View, Modal, TextInput
except ImportError:
    os.system('pip install discord.py')
    import discord
    from discord.ext import commands
    from discord.ui import Button, View, Modal, TextInput

import random
import asyncio
import json

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='?', intents=intents)

# --- QUẢN LÝ TIỀN TỆ (FILE JSON) ---
DATA_FILE = "money.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_balance(user_id):
    data = load_data()
    uid = str(user_id)
    if uid not in data:
        data[uid] = 10000  # Tặng sẵn 10.000 Xu cho tân thủ
        save_data(data)
    return data[uid]

def update_balance(user_id, amount):
    data = load_data()
    uid = str(user_id)
    current = get_balance(user_id)
    data[uid] = current + amount
    save_data(data)
    return data[uid]


# --- STEP 1: GIAO DIỆN MỞ BÀN CƯỢC ---
class MoBanCuocView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="💰 ĐẶT CƯỢC NGAY", style=discord.ButtonStyle.success)
    async def btn_dat_cuoc(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(NhapTienModal())


# --- STEP 3: XỬ LÝ LẮC XÍ NGẦU & TỰ ĐỘNG TẠO VÁN MỚI ---
class ChonTaiXiuView(View):
    def __init__(self, user_id, bet_amount):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.bet_amount = bet_amount

    async def xu_ly_lac_xiu(self, interaction: discord.Interaction, lua_chon: str):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Đây không phải bàn cược của cốt!", ephemeral=True)
            return

        bal = get_balance(self.user_id)
        if bal < self.bet_amount:
            await interaction.response.send_message("❌ Cốt không đủ Xu để cược rồi!", ephemeral=True)
            return

        d1, d2, d3 = random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)
        tong = d1 + d2 + d3
        ket_qua = "xiu" if tong <= 10 else "tai"
        ten_kq = "XỈU" if ket_qua == "xiu" else "TÀI"

        if lua_chon == ket_qua:
            win_money = int(self.bet_amount * 0.95)
            new_bal = update_balance(self.user_id, win_money)
            thong_bao = f"🎉 **THẮNG RỒI!** Cốt cộng thêm **+{win_money:,} Xu**!"
            mau_frame = discord.Color.green()
        else:
            new_bal = update_balance(self.user_id, -self.bet_amount)
            thong_bao = f"😭 **THUA RỒI!** Cốt bị trừ **-{self.bet_amount:,} Xu**!"
            mau_frame = discord.Color.red()

        for item in self.children:
            item.disabled = True

        embed = discord.Embed(title="🎲 KẾT QUẢ TÀI XỈU 🎲", color=mau_frame)
        embed.add_field(name="Người chơi", value=interaction.user.mention, inline=False)
        embed.add_field(name="Mức cược", value=f"**{self.bet_amount:,} Xu**", inline=True)
        embed.add_field(name="Đã chọn", value=f"**{'TÀI' if lua_chon == 'tai' else 'XỈU'}**", inline=True)
        embed.add_field(name="Xúc xắc", value=f"🎲 {d1} - {d2} - {d3}", inline=False)
        embed.add_field(name="Tổng điểm", value=f"**{tong}** điểm ➔ **{ten_kq}**", inline=False)
        embed.add_field(name="Kết quả", value=thong_bao, inline=False)
        embed.add_field(name="Số dư ví", value=f"💰 **{new_bal:,} Xu**", inline=False)

        await interaction.response.edit_message(embed=embed, view=self)

        await asyncio.sleep(1.5)
        embed_moi = discord.Embed(
            title="🎰 SÒNG BẠC TÀI XỈU (VÁN MỚI) 🎰",
            description="Bấm nút **`💰 ĐẶT CƯỢC NGAY`** bên dưới để vào ván tiếp theo!",
            color=discord.Color.gold()
        )
        await interaction.channel.send(embed=embed_moi, view=MoBanCuocView())

    @discord.ui.button(label="🎲 ĐẶT TÀI (11-18)", style=discord.ButtonStyle.danger)
    async def btn_tai(self, interaction: discord.Interaction, button: Button):
        await self.xu_ly_lac_xiu(interaction, "tai")

    @discord.ui.button(label="🎲 ĐẶT XỈU (3-10)", style=discord.ButtonStyle.primary)
    async def btn_xiu(self, interaction: discord.Interaction, button: Button):
        await self.xu_ly_lac_xiu(interaction, "xiu")


# --- STEP 2: CỬA SỔ (MODAL) NHẬP SỐ TIỀN ---
class NhapTienModal(Modal, title="💰 NHẬP SỐ TIỀN CƯỢC"):
    so_tien_input = TextInput(
        label="Nhập số Xu cốt muốn cược (Hoặc gõ 'all'):",
        placeholder="Ví dụ: 1000, 5000, all...",
        required=True,
        max_length=15
    )

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        bal = get_balance(user_id)
        val = self.so_tien_input.value.strip().lower()

        if val == 'all':
            bet_amount = bal
        else:
            try:
                bet_amount = int(val)
            except ValueError:
                await interaction.response.send_message("❌ Số tiền nhập vào phải là số! Ví dụ: 2000", ephemeral=True)
                return

        if bet_amount <= 0:
            await interaction.response.send_message("❌ Số tiền cược phải lớn hơn 0 Xu!", ephemeral=True)
            return

        if bet_amount > bal:
            await interaction.response.send_message(f"❌ Cốt không đủ Xu! Ví cốt chỉ có **{bal:,} Xu**.", ephemeral=True)
            return

        view_chon = ChonTaiXiuView(user_id=user_id, bet_amount=bet_amount)
        embed = discord.Embed(
            title="🎰 CHỌN TÀI HOẶC XỈU 🎰",
            description=f"Người chơi: {interaction.user.mention}\nTiền cược đã chốt: **{bet_amount:,} Xu**\n\nBấm nút **TÀI** hoặc **XỈU** bên dưới để lắc bài!",
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed, view=view_chon)


@bot.event
async def on_ready():
    print(f'=== Bot {bot.user} ĐÃ ONLINE TỰ ĐỘNG LẶP VÁN! ===')

@bot.command(name='taixiu', aliases=['tx'])
async def taixiu(ctx):
    embed = discord.Embed(
        title="🎰 SÒNG BẠC TÀI XỈU 🎰",
        description="Bấm vào nút **`💰 ĐẶT CƯỢC NGAY`** bên dưới để nhập số tiền cược nha cốt!",
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed, view=MoBanCuocView())

@bot.command(name='sodu', aliases=['bal', 'cash', 'tien'])
async def sodu(ctx):
    bal = get_balance(ctx.author.id)
    embed = discord.Embed(
        title="💳 VÍ TIỀN CỦA CỐT",
        description=f"Hiện tại {ctx.author.mention} đang có: **{bal:,} Xu**",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)


# Lấy TOKEN từ biến môi trường
TOKEN = os.getenv("TOKEN")

bot.run(TOKEN)
  
