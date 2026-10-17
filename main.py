import discord
from discord.ext import commands
import random
from collections import Counter
import asyncio
from PIL import Image, ImageDraw, ImageFont
import io
import math
from flask import Flask
import threading

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot đang chạy!"

def run_web():
    app.run(host="0.0.0.0", port=8080)

# Chạy Flask song song
threading.Thread(target=run_web).start()

# --- THIẾT LẬP BOT ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

games = {}

# --- TỪ ĐIỂN DỮ LIỆU VÀ HÌNH ẢNH (GIỮ NGUYÊN 100%) ---
CARD_SKILLS = {
    'Bỏ qua (Skip)': 'Kết thúc 1 lượt rút của bạn mà không cần rút.',
    'Tấn công (Attack)': 'Kết thúc lượt không rút bài, ép người kế tiếp phải rút 2 lượt.',
    'Tráo bài (Shuffle)': 'Trộn lại xấp nọc.',
    'Nhìn trộm (See the future)': 'Xem bí mật 3 lá bài trên cùng của nọc.',
    'Tháo Gỡ (Defuse)': 'Cứu bạn khỏi Mèo Nổ thường.',
    'Mèo Nổ (Exploding Kitten)': 'BÙM! Bị loại nếu không có Tháo Gỡ.',
    'Bom Nguyên Tử (Atomic Bomb)': 'Lấy mọi lá Mèo Nổ thường để lên đầu nọc.',
    'Tìm kiếm (Search)': 'Xem 5 lá trên cùng, chọn 1 lá lấy lên tay, xào lại các lá còn lại.',
    'Hủy bài (Discard)': 'Chọn 1 người chơi để hủy ngẫu nhiên 2 lá bài của họ.',
    'Sao chép (Copycat)': 'Bắt chước chức năng của lá bài gần nhất vừa được sử dụng.',
    'Mèo Nổ Sập (Úp)': 'Cứu mạng 1 lần. Chuyển thành trạng thái (Ngửa) và nhét lại vào xấp.',
    'Mèo Nổ Sập (Ngửa)': 'BÙM! Chết ngay lập tức, không thể dùng Tháo Gỡ!',
    'Cướp bài (Steal)': 'Cướp ngẫu nhiên 1 lá bài trên tay của người khác.',
    'Biến đổi tương lai (Alter)': 'Xem và thay đổi thứ tự của 3 lá bài đầu tiên.',
    'Xin xỏ (Favor)': 'Ép 1 người phải chủ động tự chọn 1 lá bài để cho bạn.',
    'Đổi chiều (Reverse)': 'Đảo ngược chiều đánh của vòng chơi.',
    'Rút từ đáy (Draw bottom)': 'Rút lá bài dưới đáy nọc thay vì lá trên cùng.',
    'Mèo Tacocat': 'Tích lũy để đánh cặp đôi.',
    'Mèo Cattermelon': 'Tích lũy để đánh cặp đôi.',
    'Mèo Khoai Tây': 'Tích lũy để đánh cặp đôi.',
    'Mèo Râu Bạc': 'Tích lũy để đánh cặp đôi.',
    'Mèo Cầu Vồng': 'Tích lũy để đánh cặp đôi.',
    'Mèo hoang (Feral Cat)': 'Thay thế bất kỳ bài mèo thường nào để tạo combo.',
    'Sưu tầm rác (Garbage Collection)': 'Mọi người (kể cả bạn) chọn 1 lá bỏ lại vào nọc, sau đó xào nọc.',
    'Mèo sọc (Streaking Kitten)': 'Bị động: Cho phép bạn giữ bí mật 1 quả Mèo Nổ trên tay.',
    'Siêu bỏ lượt (Super Skip)': 'Kết thúc ngay lập tức TẤT CẢ các lượt rút bài hiện tại của bạn.',
    'Chặn (Nope)': 'Vô hiệu hóa tác dụng của lá bài vừa đánh. Có thể đánh bất kỳ lúc nào!',
    'Chống xào bài': 'Dồn tất cả Mèo Nổ lên đầu nọc, khóa chức năng xào bài.',
    'Kháng xào bài': 'Khóa nọc, không ai có thể xào bài cho đến khi có người bốc bài.',
    'Tự vả': 'Bạn tự cộng thêm 3 lượt bốc bài cho bản thân.',
    'Vả đơn': 'Kết thúc lượt, người kế tiếp chịu toàn bộ số lượt còn lại của bạn + 1 lượt.',
    'Vả đôi': 'Kết thúc lượt, người kế tiếp chịu toàn bộ số lượt còn lại của bạn + 2 lượt.',
    'Vả ba': 'Kết thúc lượt, người kế tiếp chịu toàn bộ số lượt còn lại của bạn + 3 lượt.'
}

CARD_IMAGES = {
    'Bỏ qua (Skip)': 'https://cdn.discordapp.com/attachments/1522930842270171257/1529819277723701259/IMG_20260723_185324.jpg?ex=6a6352ba&is=6a62013a&hm=8d8a964204cb36fa81e585550cc36b307cad9e06006c90cc1b6b2cd36a41a2a1&',
    'Tấn công (Attack)': 'https://cdn.discordapp.com/attachments/1522930842270171257/1529821421348454541/IMG_20260723_190330.jpg?ex=6a6354b9&is=6a620339&hm=c87176a29c625e3bc879066acea45f944d89531654340f66219af000ebe2b537&',
    'Tráo bài (Shuffle)': 'https://cdn.discordapp.com/attachments/1522930842270171257/1529818912919781497/IMG_20260723_185259.jpg?ex=6a635263&is=6a6200e3&hm=a25e23938c8a0178e23fb80816ea2aa01a48dc873d765d307dea419261a63c10&',
    'Nhìn trộm (See the future)': 'https://cdn.discordapp.com/attachments/1522930842270171257/1529819214070812732/IMG_20260723_185318.jpg?ex=6a6352ab&is=6a62012b&hm=48a217ac300152c739c169abc3c1c9d6d771381bda979a446ff346dd708e4301&',
    'Tháo Gỡ (Defuse)': 'https://cdn.discordapp.com/attachments/1522930842270171257/1529821460858671224/IMG_20260723_190307.jpg?ex=6a6354c2&is=6a620342&hm=0b14d50e5e0899f2ee0d59a5e79b619c2a20a989896dfa76973ca8a4ca8f98b2&',
    'Mèo Nổ (Exploding Kitten)': 'https://cdn.discordapp.com/attachments/1522930842270171257/1529819318597058580/IMG_20260723_185326.jpg?ex=6a6352c4&is=6a620144&hm=404037bdd6deb4431ee0d777d447eed4814a3aa9bc617911f8f6b27e375707eb&',
    'Bom Nguyên Tử (Atomic Bomb)': 'https://cdn.discordapp.com/attachments/1522930842270171257/1529819438885638204/IMG_20260723_185331.jpg?ex=6a6352e0&is=6a620160&hm=11c4941c7edd7f8489cad7b47a9b985acf9765bfcc1ece9ea3b61a2d2000ce09&',
    'Tìm kiếm (Search)': 'https://cdn.discordapp.com/attachments/1522930842270171257/1529819250892734535/IMG_20260723_185320.jpg?ex=6a6352b4&is=6a620134&hm=c30cc8f0205bf59c82fce9749bdc6059f1594862ec0a88a6d6e747a3c122ab43&',
    'Hủy bài (Discard)': 'https://cdn.discordapp.com/attachments/1522930842270171257/1529822233457856642/IMG_20260723_190642.jpg?ex=6a63557b&is=6a6203fb&hm=b00296258ae337daaf6fa06c06bb7d61012a0e54e07ee7c9fcafc90b011155d6&',
    'Sao chép (Copycat)': 'https://cdn.discordapp.com/attachments/1522930842270171257/1529821517192499291/IMG_20260723_190255.jpg?ex=6a6354d0&is=6a620350&hm=18383e35a3e3c64168afd2ab72adcb399097615afac45bd6f52b4607c5db2db6&',
    'Mèo Nổ Sập (Úp)': 'https://cdn.discordapp.com/attachments/1522930842270171257/1529819533509005492/IMG_20260723_185342.jpg?ex=6a6352f7&is=6a620177&hm=c98be6cbf758b007b51d22f59095884f07965acf13383bfd30d9d5c8e5d00e08&',
    'Mèo Nổ Sập (Ngửa)': 'https://cdn.discordapp.com/attachments/1522930842270171257/1529819533509005492/IMG_20260723_185342.jpg?ex=6a6352f7&is=6a620177&hm=c98be6cbf758b007b51d22f59095884f07965acf13383bfd30d9d5c8e5d00e08&',
    'Cướp bài (Steal)': 'https://cdn.discordapp.com/attachments/1522930842270171257/1529819486717214800/IMG_20260723_185336.jpg?ex=6a6352ec&is=6a62016c&hm=a6ea35a47457cf8a123f36e9d932742c51150405d7b1c12ec380ff9759d68097&',
    'Biến đổi tương lai (Alter)': 'https://cdn.discordapp.com/attachments/1522930842270171257/1529819345679548467/IMG_20260723_185328.jpg?ex=6a6352ca&is=6a62014a&hm=df70277aaa844c9a1a70843a2de55cc3b1e86b6c7f73d0f063f125176a2ebd14&',
    'Xin xỏ (Favor)': 'https://cdn.discordapp.com/attachments/1522930842270171257/1529819510222356645/IMG_20260723_185340.jpg?ex=6a6352f1&is=6a620171&hm=075e4456bf358c778a63e6740988fda216b2418df1b487d650dbdc9e1ca809ae&',
    'Đổi chiều (Reverse)': 'https://cdn.discordapp.com/attachments/1522930842270171257/1529819412448809040/IMG_20260723_185330.jpg?ex=6a6352da&is=6a62015a&hm=81105b589c4eee2b24ac19d9535e19d4ce30f1d2ec4b63d857001c15bea375cf&',
    'Rút từ đáy (Draw bottom)': 'https://cdn.discordapp.com/attachments/1522930842270171257/1529819097960026122/IMG_20260723_185308.jpg?ex=6a63528f&is=6a62010f&hm=2effceae1d5a1f59136a0b1c3dea543fae3dcceec2ec4acabae0738186e72916&',
    'Mèo Tacocat': 'https://cdn.discordapp.com/attachments/1522930842270171257/1529819184467415070/IMG_20260723_185316.jpg?ex=6a6352a4&is=6a620124&hm=e9b668734b8bd25ea9972790c51b98012a8b625a77deca5a995cf9e6a26d577c&',
    'Mèo Cattermelon': 'https://cdn.discordapp.com/attachments/1522930842270171257/1529818949842370620/IMG_20260723_185301.jpg?ex=6a63526c&is=6a6200ec&hm=5030339d6290335e5ba8cc7b8a006b84ae573a7551dfb159e01dee9cb878d63a&',
    'Mèo Khoai Tây': 'https://cdn.discordapp.com/attachments/1522930842270171257/1529819127064166460/IMG_20260723_185312.jpg?ex=6a635296&is=6a620116&hm=b50d049cb93e807543e7c6665cf67e266ab053db3e1ded0c946decde4a850434&',
    'Mèo Râu Bạc': 'https://cdn.discordapp.com/attachments/1522930842270171257/1529819155854000158/IMG_20260723_185314.jpg?ex=6a63529d&is=6a62011d&hm=a2669267b62b3a9521fac962e4ddfcb202d8a66787d9632210adca2b6e31b7eb&',
    'Mèo Cầu Vồng': 'https://cdn.discordapp.com/attachments/1522930842270171257/1529819024622358538/IMG_20260723_185306.jpg?ex=6a63527e&is=6a6200fe&hm=3bc40fa4ea8e14557ebb2c5ee14ff9b045629c62965b539ba93a8fbbf5dd7481&',
    'Mèo hoang (Feral Cat)': 'https://cdn.discordapp.com/attachments/1522930842270171257/1531999156514586666/IMG_20260729_191146.jpg?ex=6a6b40e6&is=6a69ef66&hm=a93ac7bdffc562de7faadc9e64ba7436965220f62d1b54793982b2caf9556caa&',
    'Sưu tầm rác (Garbage Collection)': 'https://cdn.discordapp.com/attachments/1522930842270171257/1531998172614758500/IMG_20260729_191208.jpg?ex=6a6b3ffb&is=6a69ee7b&hm=c7d59483d2689ef8b408ccae8e698cb9fc358a3dfd6fec97ba9dc5e25d1aca94&',
    'Mèo sọc (Streaking Kitten)': 'https://cdn.discordapp.com/attachments/1522930842270171257/1531998131623821332/IMG_20260729_191206.jpg?ex=6a6b3ff1&is=6a69ee71&hm=2cb6b11881307396db3fe2e27f1ac00142db227ae13bd9bba2c51076df1dffc7&',
    'Siêu bỏ lượt (Super Skip)': 'https://cdn.discordapp.com/attachments/1522930842270171257/1531999086188691719/IMG_20260729_191203.jpg?ex=6a6b40d5&is=6a69ef55&hm=defaaa42db73315279a12b7733443e67afb70d0e17a6137f2939529119989c58&',
    'Chặn (Nope)': 'https://cdn.discordapp.com/attachments/1522930842270171257/1531998193825480704/IMG_20260729_191212.jpg?ex=6a6b4000&is=6a69ee80&hm=954000440c5c899b64d261c476d25e771971cfe7b15758cd9de9225302b2ca54&',
    'Chống xào bài': 'https://cdn.discordapp.com/attachments/1522930842270171257/1531998235441365172/IMG_20260729_191214.jpg?ex=6a6b400a&is=6a69ee8a&hm=2b346fd8a86251b225b98d715038ff692eb94fce083aee8548342dba8b88b3ff&',
    'Kháng xào bài': 'https://cdn.discordapp.com/attachments/1522930842270171257/1531997978989039647/IMG_20260729_191152.jpg?ex=6a6b3fcd&is=6a69ee4d&hm=c1a9d71a82725463bd01dbcf3db01be60763875188a88f9f1e421dbaa5eadabc&',
    'Tự vả': 'https://cdn.discordapp.com/attachments/1522930842270171257/1531998089274200105/IMG_20260729_191200.jpg?ex=6a6b3fe7&is=6a69ee67&hm=437fadf3f53444c39d63da7b5593ddc15f433ac39f9d2d51a1388ae825012b24&',
    'Vả đơn': 'https://cdn.discordapp.com/attachments/1522930842270171257/1531998058391277618/IMG_20260729_191156.jpg?ex=6a6b3fe0&is=6a69ee60&hm=2778ab45b4c23d8fbfe9ccd59b6b1c77c07d012e2e18175abb37aa6ce03f8a39&',
    'Vả đôi': 'https://cdn.discordapp.com/attachments/1522930842270171257/1531997952284033104/IMG_20260729_191149.jpg?ex=6a6b3fc6&is=6a69ee46&hm=f0a63daba6796002cd0f37134ece8203c14593aee3f39f4f39e1eaf0f48564bf&',
    'Vả ba': 'https://cdn.discordapp.com/attachments/1522930842270171257/1531998029102448700/IMG_20260729_191154.jpg?ex=6a6b3fd9&is=6a69ee59&hm=563295d9eafc1ccc9a20254a5cc869c0492725a90f2210b330ef9ff79ff41e7c&',
}

# --- CÁC HÀM TIỆN ÍCH GIAO DIỆN (GIỮ NGUYÊN 100%) ---
def format_hand(hand_list):
    if not hand_list: return "Tay bạn đang trống không!"
    counts = Counter(hand_list)
    return "\n".join([f"{i+1}. **{card}** x{qty}" for i, (card, qty) in enumerate(counts.items())])

def create_card_embed(description, card_name=None, color=discord.Color.blue()):
    embed = discord.Embed(description=description, color=color)
    if card_name and card_name in CARD_IMAGES and CARD_IMAGES[card_name] != 'LINK_ANH_O_DAY':
        embed.set_thumbnail(url=CARD_IMAGES[card_name])
    return embed

def get_game_embed(game):
    if not game.players: return None
    current_player_name = game.players[game.current_turn].mention
    
    if getattr(game, 'is_danger_100', False):
        embed = discord.Embed(
            title="⚠️ CẢNH BÁO MỨC ĐỘ NGUY HIỂM: 100% ⚠️",
            description=f" Lượt hiện tại: {current_player_name} (Cần rút {game.turns_left} lá)",
            color=0x8B0000 
        )
        embed.set_thumbnail(url="https://media.tenor.com/q2l24D5Y6B0AAAAi/black-cat-stare.gif") 
    else:
        embed = discord.Embed(
            title="🃏 Bàn chơi hiện tại",
            description=f"👉 Lượt hiện tại: {current_player_name} (Cần rút {game.turns_left} lá)",
            color=0x00FF00 
        )
    
    embed.set_image(url="attachment://table.png")
    return embed

def create_table_image(game):
    width, height = 800, 450
    img = Image.new('RGB', (width, height), color='#5C3A21')
    draw = ImageDraw.Draw(img)

    for i in range(0, height, 30):
        draw.line([(0, i), (width, i + 15)], fill='#4A2E1B', width=4)
        draw.line([(0, i + 10), (width, i - 5)], fill='#6B4426', width=2)

    deck_count = len(game.deck)
    bombs_left = game.deck.count('Mèo Nổ (Exploding Kitten)') + game.deck.count('Mèo Nổ Sập (Úp)') + game.deck.count('Mèo Nổ Sập (Ngửa)')
    
    if getattr(game, 'is_danger_100', False): bomb_chance = 100.0
    else: bomb_chance = (bombs_left / deck_count * 100) if deck_count > 0 else 0.0

    draw.line([(380, 260), (320, 280), (210, 280), (210, 270)], fill='#FF3B30', width=6, joint='curve')
    draw.ellipse([200, 275, 220, 290], fill='#CC241D')

    deck_x1, deck_y1, deck_x2, deck_y2 = 360, 90, 520, 310
    if deck_count > 0:
        stack_height = min(deck_count, 10)
        for i in range(stack_height):
            draw.rounded_rectangle([deck_x1 - i, deck_y1 - i, deck_x2 - i, deck_y2 - i], radius=12, fill='#B31B1B', outline='#8A1515', width=1)
        draw.rounded_rectangle([deck_x1 - stack_height, deck_y1 - stack_height, deck_x2 - stack_height, deck_y2 - stack_height], radius=12, fill='#FF3B30', outline='#FFFFFF', width=2)
        draw.ellipse([410 - stack_height, 170 - stack_height, 470 - stack_height, 220 - stack_height], fill='#FF8C00')
        draw.polygon([(415 - stack_height, 180 - stack_height), (420 - stack_height, 150 - stack_height), (435 - stack_height, 175 - stack_height)], fill='#FF8C00')
        draw.polygon([(465 - stack_height, 180 - stack_height), (460 - stack_height, 150 - stack_height), (445 - stack_height, 175 - stack_height)], fill='#FF8C00')

    draw.rounded_rectangle([370, 330, 510, 360], radius=6, fill='#222222', outline='#111111', width=2)
    
    gauge_cx, gauge_cy = 210, 190
    gauge_r = 75
    border_color = '#FF0000' if getattr(game, 'is_danger_100', False) else '#CCCCCC'
    draw.ellipse([gauge_cx - gauge_r - 8, gauge_cy - gauge_r - 8, gauge_cx + gauge_r + 8, gauge_cy + gauge_r + 8], fill='#EEEEEE', outline=border_color, width=5)
    draw.ellipse([gauge_cx - gauge_r, gauge_cy - gauge_r, gauge_cx + gauge_r, gauge_cy + gauge_r], fill='#FFFFFF')
    
    draw.pieslice([gauge_cx - gauge_r + 5, gauge_cy - gauge_r + 5, gauge_cx + gauge_r - 5, gauge_cy + gauge_r - 5], 180, 240, fill='#EAEAEA')
    draw.pieslice([gauge_cx - gauge_r + 5, gauge_cy - gauge_r + 5, gauge_cx + gauge_r - 5, gauge_cy + gauge_r - 5], 240, 300, fill='#FFB347')
    draw.pieslice([gauge_cx - gauge_r + 5, gauge_cy - gauge_r + 5, gauge_cx + gauge_r - 5, gauge_cy + gauge_r - 5], 300, 360, fill='#FF4C4C')
    draw.chord([gauge_cx - gauge_r + 5, gauge_cy - gauge_r + 5, gauge_cx + gauge_r - 5, gauge_cy + gauge_r - 5], 0, 180, fill='#FFFFFF')

    angle_deg = 180 + (bomb_chance / 100.0) * 180
    angle_rad = math.radians(angle_deg)
    needle_length = 60
    nx = gauge_cx + needle_length * math.cos(angle_rad)
    ny = gauge_cy + needle_length * math.sin(angle_rad)
    
    draw.line([(gauge_cx, gauge_cy), (nx, ny)], fill='#CC0000', width=6)
    draw.ellipse([gauge_cx - 10, gauge_cy - 10, gauge_cx + 10, gauge_cy + 10], fill='#333333', outline='#AA0000', width=2)

    draw.rounded_rectangle([150, 95, 270, 125], radius=5, fill='#FFFFFF')
    draw.rounded_rectangle([40, 170, 130, 210], radius=8, fill='#F8F8F8', outline='#DDDDDD', width=3)
    draw.rounded_rectangle([550, 40, 780, 410], radius=15, fill='#000000CC', outline='#FF8C00', width=2)

    try:
        font_large = ImageFont.truetype("Acb.ttf", 26)
        font_med = ImageFont.truetype("Acb.ttf", 18)
        font_small = ImageFont.truetype("Acb.ttf", 14)
        font_bold = ImageFont.truetype("Acb.ttf", 20)
    except:
        font_large = font_med = font_small = font_bold = ImageFont.load_default()

    draw.text((55, 178), f"{bomb_chance:.0f} %", font=font_large, fill="#CC0000")
    draw.text((160, 102), "TI LE KABOOM", font=font_small, fill="#CC0000")
    draw.text((388, 338), f"CON {deck_count} LA", font=font_med, fill="#FFFFFF")

    draw.text((570, 55), "[ NGUOI SONG ]", font=font_bold, fill="#FFCC00")
    
    y_offset = 90
    for idx, player in enumerate(game.players):
        display_name = (player.display_name[:15] + '..') if len(player.display_name) > 15 else player.display_name
        if idx == game.current_turn: draw.text((570, y_offset), f">> {display_name}", font=font_med, fill="#00FF00")
        else: draw.text((570, y_offset), f"- {display_name}", font=font_med, fill="#FFFFFF")
        y_offset += 30

    draw.line([(570, y_offset + 10), (760, y_offset + 10)], fill='#555555', width=2)
    
    y_offset += 25
    draw.text((570, y_offset), "[ NGUOI TIẾP THEO ]", font=font_bold, fill="#00E5FF")
    
    if len(game.players) > 0:
        next_turn_idx = (game.current_turn + game.direction) % len(game.players)
        next_player = game.players[next_turn_idx]
        next_name = (next_player.display_name[:15] + '..') if len(next_player.display_name) > 15 else next_player.display_name
        draw.text((570, y_offset + 30), f"-> {next_name}", font=font_large, fill="#FFFFFF")
        draw.text((570, y_offset + 70), f"Can rut: {game.turns_left} la", font=font_med, fill="#FF6666")

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return discord.File(buffer, filename='table.png')

# --- LOGIC TRÒ CHƠI ---
class ExplodingKittensGame:
    def __init__(self):
        self.players = []
        self.deck = []
        self.discard_pile = []
        self.hands = {}
        self.is_started = False
        self.current_turn = 0
        self.total_defuse = 6
        self.turns_left = 1 
        self.last_played_card = None 
        self.direction = 1
        self.can_shuffle = True 
        self.is_danger_100 = False 
        self.main_message = None 

    def setup_deck(self):
        num_players = len(self.players)
        target_size = 20 if num_players == 2 else 30 + (num_players - 3) * 5
            
        multiplier = max(1, num_players // 2)
        all_possible_cards = (
            ['Bỏ qua (Skip)'] * (4 * multiplier) + ['Tấn công (Attack)'] * (4 * multiplier) +
            ['Tráo bài (Shuffle)'] * (4 * multiplier) + ['Nhìn trộm (See the future)'] * (4 * multiplier) +
            ['Bom Nguyên Tử (Atomic Bomb)'] * (2 * multiplier) + ['Tìm kiếm (Search)'] * (3 * multiplier) +
            ['Hủy bài (Discard)'] * (3 * multiplier) + ['Sao chép (Copycat)'] * (3 * multiplier) +
            ['Cướp bài (Steal)'] * (3 * multiplier) + ['Biến đổi tương lai (Alter)'] * (3 * multiplier) +
            ['Xin xỏ (Favor)'] * (4 * multiplier) + ['Đổi chiều (Reverse)'] * (3 * multiplier) +
            ['Rút từ đáy (Draw bottom)'] * (3 * multiplier) +
            ['Mèo Tacocat'] * 4 + ['Mèo Cattermelon'] * 4 + ['Mèo Khoai Tây'] * 4 +
            ['Mèo Râu Bạc'] * 4 + ['Mèo Cầu Vồng'] * 4 +
            ['Mèo hoang (Feral Cat)'] * 4 + ['Sưu tầm rác (Garbage Collection)'] * 2 +
            ['Mèo sọc (Streaking Kitten)'] * 1 + ['Siêu bỏ lượt (Super Skip)'] * 2 +
            ['Chặn (Nope)'] * (5 * multiplier) + ['Chống xào bài'] * 2 + ['Kháng xào bài'] * 2 +
            ['Tự vả'] * 2 + ['Vả đơn'] * 3 + ['Vả đôi'] * 2 + ['Vả ba'] * 1
        )
        random.shuffle(all_possible_cards)
        
        drawn_by_players = 4 * num_players
        defuse_added = max(0, self.total_defuse - num_players)
        bombs_added = max(0, num_players - 1)
        
        initial_needed = target_size + drawn_by_players - defuse_added - bombs_added
        self.deck = all_possible_cards[:initial_needed]

    def advance_turn(self):
        self.turns_left -= 1
        if self.turns_left <= 0:
            self.current_turn = (self.current_turn + self.direction) % len(self.players)
            self.turns_left = 1 
            return True 
        return False

    async def update_board(self, channel):
        if self.main_message:
            try: await self.main_message.delete()
            except: pass
        self.main_message = await channel.send(embed=get_game_embed(self), file=create_table_image(self), view=GameActionView(self))

    async def handle_bomb_explosion(self, channel, player, drawn_card, from_search=False, top_5_deck=None):
        if drawn_card == 'Mèo Nổ Sập (Ngửa)':
            await channel.send(embed=create_card_embed(f"🌋 {player.mention} rút trúng **MÈO NỔ SẬP (NGỬA)**! ĐĂNG XUẤT NGAY LẬP TỨC 💀", drawn_card, discord.Color.red()))
            self.players.remove(player)
        elif drawn_card == 'Mèo Nổ (Exploding Kitten)':
            if 'Tháo Gỡ (Defuse)' in self.hands[player]:
                self.hands[player].remove('Tháo Gỡ (Defuse)')
                await channel.send(embed=create_card_embed(f"💥 {player.mention} bốc trúng **Mèo Nổ** nhưng đã **Tháo Gỡ** thành công! (Bom bị giấu lại vào nọc)", 'Tháo Gỡ (Defuse)', discord.Color.green()))
                if from_search and top_5_deck is not None: top_5_deck.append('Mèo Nổ (Exploding Kitten)')
                else: self.deck.insert(random.randint(0, len(self.deck)), 'Mèo Nổ (Exploding Kitten)')
            else:
                await channel.send(embed=create_card_embed(f"💥 {player.mention} bốc trúng **Mèo Nổ** và KHÔNG CÓ THÁO GỠ! 💀", drawn_card, discord.Color.red()))
                self.players.remove(player)
        elif drawn_card == 'Mèo Nổ Sập (Úp)':
            await channel.send(embed=create_card_embed(f"⚠️ {player.mention} đã rút trúng **MÈO NỔ SẬP (ÚP)**! Lần này bạn được sống.\n🔄 Bom đã lật mặt thành **(Ngửa)** và nhét lại vào nọc.", drawn_card, discord.Color.orange()))
            if from_search and top_5_deck is not None: top_5_deck.append('Mèo Nổ Sập (Ngửa)')
            else: self.deck.insert(random.randint(0, len(self.deck)), 'Mèo Nổ Sập (Ngửa)')


# ====================================================================================
# --- HỆ THỐNG GIAO DIỆN & COMBO MỚI ---
# ====================================================================================

class LobbyView(discord.ui.View):
    def __init__(self, game):
        super().__init__(timeout=None)
        self.game = game

    @discord.ui.button(label="Tham Gia", style=discord.ButtonStyle.green, custom_id="join", emoji="🖐️")
    async def join_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.game.is_started: return await interaction.response.send_message("🚫 Trò chơi đã bắt đầu!", ephemeral=True)
        if interaction.user in self.game.players: return await interaction.response.send_message("Bạn đã tham gia rồi!", ephemeral=True)
        
        self.game.players.append(interaction.user)
        await interaction.response.send_message(f"✅ {interaction.user.mention} đã tham gia! (Tổng: {len(self.game.players)})")

    @discord.ui.button(label="Bắt Đầu Game", style=discord.ButtonStyle.blurple, custom_id="start", emoji="🚀")
    async def start_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(self.game.players) < 2: return await interaction.response.send_message("Cần ít nhất 2 người!", ephemeral=True)
        if self.game.is_started: return
        
        self.game.is_started = True
        self.game.setup_deck()
        
        for player in self.game.players:
            self.game.hands[player] = ['Tháo Gỡ (Defuse)']
            for _ in range(4): self.game.hands[player].append(self.game.deck.pop())
                
        defuse_left = self.game.total_defuse - len(self.game.players)
        if defuse_left > 0: self.game.deck.extend(['Tháo Gỡ (Defuse)'] * defuse_left)

        total_lethal = len(self.game.players) - 1
        if 'Mèo sọc (Streaking Kitten)' in self.game.deck or any('Mèo sọc' in c for h in self.game.hands.values() for c in h): total_lethal += 1 

        if total_lethal > 0:
            if len(self.game.players) == 2 and total_lethal == 1: self.game.deck.extend(['Mèo Nổ (Exploding Kitten)'] * total_lethal)
            else:
                self.game.deck.append('Mèo Nổ Sập (Úp)')
                self.game.deck.extend(['Mèo Nổ (Exploding Kitten)'] * max(0, total_lethal - 1))
            
        random.shuffle(self.game.deck)

        for player in self.game.players:
            try: await player.send(f"🎉 **GAME BẮT ĐẦU!**\n🃏 **Bài trên tay:**\n{format_hand(self.game.hands[player])}")
            except: pass

        await interaction.message.delete()
        await interaction.channel.send("🎉 **Trò chơi bắt đầu!** ")
        await self.game.update_board(interaction.channel)

class GameActionView(discord.ui.View):
    def __init__(self, game):
        super().__init__(timeout=None)
        self.game = game

    @discord.ui.button(label="Xem Bài ", style=discord.ButtonStyle.secondary, custom_id="hand", emoji="🃏")
    async def hand_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user not in self.game.players: return await interaction.response.send_message("Bạn không chơi ván này!", ephemeral=True)
        try:
            await interaction.user.send(f"🃏 **Bài của bạn:**\n{format_hand(self.game.hands[interaction.user])}")
            await interaction.response.send_message("✅ Đã gửi bài vào inbox của bạn!", ephemeral=True)
        except: await interaction.response.send_message("⚠️ Hãy mở tin nhắn riêng (DM) để bot gửi bài!", ephemeral=True)

    @discord.ui.button(label="Rút Bài", style=discord.ButtonStyle.danger, custom_id="draw", emoji="📥")
    async def draw_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        current_player = self.game.players[self.game.current_turn]
        if interaction.user not in self.game.players: return await interaction.response.send_message("Bạn không chơi ván này!", ephemeral=True)
        if interaction.user != current_player: return await interaction.response.send_message(f"❌ Đang là lượt của {current_player.mention}", ephemeral=True)

        await interaction.response.defer()
        
        self.game.is_danger_100 = False 
        self.game.can_shuffle = True 
        drawn_card = self.game.deck.pop(0)
        
        if 'Mèo Nổ' in drawn_card:
            if drawn_card == 'Mèo Nổ (Exploding Kitten)' and 'Mèo sọc (Streaking Kitten)' in self.game.hands[current_player]:
                self.game.hands[current_player].append(drawn_card)
                try: await current_player.send("🤫 Bạn bốc trúng **Mèo Nổ** nhưng nhờ có **Mèo sọc**, bạn đã ôm gọn quả bom vào tay an toàn!")
                except: pass
                await interaction.channel.send(f"😌 {current_player.mention} đã rút bài an toàn.")
            else:
                await self.game.handle_bomb_explosion(interaction.channel, current_player, drawn_card)
        else:
            self.game.hands[current_player].append(drawn_card)
            try: 
                dm_embed = discord.Embed(description=f"📥 Bạn rút được: **{drawn_card}**", color=discord.Color.blue())
                if drawn_card in CARD_IMAGES and CARD_IMAGES[drawn_card] != 'LINK_ANH_O_DAY': dm_embed.set_image(url=CARD_IMAGES[drawn_card])
                await current_player.send(embed=dm_embed)
            except: pass
            await interaction.channel.send(f"😌 {current_player.mention} đã rút bài an toàn.")

        if current_player not in self.game.players:
            if len(self.game.players) == 1:
                await interaction.channel.send(f"🏆 **GAME KẾT THÚC!** {self.game.players[0].mention} SỐNG SÓT CUỐI CÙNG!")
                del games[interaction.channel.id]
                return
            if self.game.current_turn >= len(self.game.players): self.game.current_turn = 0
            self.game.turns_left = 1 
            await self.game.update_board(interaction.channel)
        else: 
            is_next = self.game.advance_turn()
            if is_next: await self.game.update_board(channel=interaction.channel)
            else: await interaction.channel.send(f"⚠️ Vẫn còn {self.game.turns_left} lượt rút nữa!")

    @discord.ui.button(label="Đánh Bài", style=discord.ButtonStyle.primary, custom_id="play", emoji="🔥")
    async def play_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        current_player = self.game.players[self.game.current_turn]
        if interaction.user not in self.game.players: return await interaction.response.send_message("Bạn không tham gia ván này!", ephemeral=True)
        if interaction.user != current_player: return await interaction.response.send_message(f"❌ Đang là lượt của {current_player.mention}", ephemeral=True)
        if not self.game.hands[interaction.user]: return await interaction.response.send_message("Tay bạn đang trống không!", ephemeral=True)

        await interaction.response.send_message("Vui lòng chọn các lá bài cần đánh (Có thể chọn từ 1 đến 5 lá):", view=PlaySelectView(self.game, interaction.user), ephemeral=True)


class NopeView(discord.ui.View):
    def __init__(self, game):
        super().__init__(timeout=5.0)
        self.game = game
        self.nope_active = False

    @discord.ui.button(label="Chặn (Nope)!", style=discord.ButtonStyle.danger, emoji="🚫")
    async def nope_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user not in self.game.players: return
        hand = self.game.hands.get(interaction.user, [])
        nope_card = next((c for c in hand if 'Chặn' in c), None)
        
        if nope_card:
            self.game.hands[interaction.user].remove(nope_card)
            self.game.discard_pile.append(nope_card)
            self.nope_active = not self.nope_active
            status = "🚫 ĐÃ BỊ CHẶN (NOPE)!" if self.nope_active else "✅ ĐÃ ĐƯỢC THÔNG QUA (YUP)!"
            await interaction.channel.send(f"🛑 {interaction.user.mention} ném ra **{nope_card}**!\nTrạng thái lá bài: {status}")
            await interaction.response.defer()
        else:
            await interaction.response.send_message("Bạn không có lá Chặn (Nope) trên tay!", ephemeral=True)


class PlaySelectView(discord.ui.View):
    def __init__(self, game, player):
        super().__init__(timeout=60)
        self.game = game
        self.player = player
        
        hand = game.hands[player]
        options = []
        for i, card in enumerate(hand[:25]): # Discord giới hạn tối đa 25 option trong Select
            options.append(discord.SelectOption(label=f"{i+1}. {card}", value=f"{i}:{card}"))
        
        self.select = discord.ui.Select(placeholder="Chọn từ 1 đến 5 lá bài...", min_values=1, max_values=min(5, len(options)), options=options)
        self.select.callback = self.on_select
        self.add_item(self.select)

    async def on_select(self, interaction: discord.Interaction):
        values = self.select.values
        indices = [int(v.split(':')[0]) for v in values]
        played_cards = [v.split(':', 1)[1] for v in values]
        num_played = len(played_cards)
        
        # 1. Đánh đơn (1 lá)
        if num_played == 1:
            card = played_cards[0]
            if card in ['Tháo Gỡ (Defuse)', 'Mèo Nổ (Exploding Kitten)', 'Mèo sọc (Streaking Kitten)', 'Chặn (Nope)', 'Mèo Nổ Sập (Úp)', 'Mèo Nổ Sập (Ngửa)']:
                return await interaction.response.send_message(f"🚫 Bạn không thể chủ động đánh lá **{card}** theo cách này!", ephemeral=True)
            
            if any(cat in card for cat in ['Tacocat', 'Cattermelon', 'Khoai Tây', 'Râu Bạc', 'Cầu Vồng', 'Mèo hoang (Feral Cat)']):
                for idx in sorted(indices, reverse=True):
                    self.game.hands[self.player].pop(idx)
                self.game.discard_pile.append(card)
                return await interaction.response.edit_message(content=f"🐱 {self.player.mention} vừa đánh lẻ lá bài **{card}** vô hại!", view=None)
            
            await interaction.response.edit_message(content="✅ Đang xử lý...", view=None)
            await execute_play_logic(interaction.channel, self.game, self.player, played_cards, indices, None)

        # 2. Đánh đôi (2 lá giống nhau hoặc kết hợp Mèo hoang) -> Cướp 1 lá ngẫu nhiên
        elif num_played == 2:
            c1, c2 = played_cards[0], played_cards[1]
            is_cat_1 = any(cat in c1 for cat in ['Tacocat', 'Cattermelon', 'Khoai Tây', 'Râu Bạc', 'Cầu Vồng', 'Mèo hoang (Feral Cat)'])
            is_cat_2 = any(cat in c2 for cat in ['Tacocat', 'Cattermelon', 'Khoai Tây', 'Râu Bạc', 'Cầu Vồng', 'Mèo hoang (Feral Cat)'])
            
            valid_pair = (c1 == c2) or ('Mèo hoang (Feral Cat)' in [c1, c2] and (is_cat_1 or is_cat_2))
            if c1 in ['Tháo Gỡ (Defuse)', 'Mèo Nổ (Exploding Kitten)', 'Mèo Nổ Sập (Úp)', 'Mèo Nổ Sập (Ngửa)', 'Chặn (Nope)', 'Mèo sọc (Streaking Kitten)'] or not valid_pair:
                return await interaction.response.send_message("❌ Đánh Đôi yêu cầu 2 lá giống hệt nhau (hoặc 1 lá Mèo + 1 Mèo hoang) và không phải lá đặc biệt!", ephemeral=True)
            
            await interaction.response.edit_message(content="🎯 Vui lòng chọn người chơi mục tiêu để cướp bài:", view=TargetSelectView(self.game, self.player, played_cards, indices, combo_type=2))

        # 3. Đánh 3 lá giống nhau -> Gọi tên lá bài muốn lấy
        elif num_played == 3:
            non_feral = [c for c in played_cards if c != 'Mèo hoang (Feral Cat)']
            valid_triple = (len(set(non_feral)) <= 1) and (len(non_feral) > 0)
            
            if played_cards[0] in ['Tháo Gỡ (Defuse)', 'Mèo Nổ (Exploding Kitten)', 'Mèo Nổ Sập (Úp)', 'Mèo Nổ Sập (Ngửa)', 'Chặn (Nope)', 'Mèo sọc (Streaking Kitten)'] or not valid_triple:
                return await interaction.response.send_message("❌ Đánh 3 lá yêu cầu 3 lá giống hệt nhau (hoặc kết hợp Mèo hoang) và không phải lá đặc biệt!", ephemeral=True)
            
            await interaction.response.edit_message(content="🎯 Vui lòng chọn người chơi mục tiêu để gọi tên lá bài muốn lấy:", view=TargetSelectView(self.game, self.player, played_cards, indices, combo_type=3))

        # 5. Đánh 5 lá khác nhau -> Chọn 1 lá bất kỳ từ bộ bài bỏ (discard pile)
        elif num_played == 5:
            if len(set(played_cards)) != 5:
                return await interaction.response.send_message("❌ Đánh 5 lá yêu cầu **5 lá bài hoàn toàn khác nhau**!", ephemeral=True)
            
            if not self.game.discard_pile:
                return await interaction.response.send_message("❌ Bộ bài bỏ (discard pile) đang trống!", ephemeral=True)
            
            await interaction.response.edit_message(content="♻️ Chọn 1 lá bài bất kỳ từ bộ bài bỏ:", view=DiscardSelectView(self.game, self.player, played_cards, indices))
        else:
            return await interaction.response.send_message("❌ Số lượng lá bài không hợp lệ (hệ thống chỉ hỗ trợ đánh 1, 2, 3 hoặc 5 lá)!", ephemeral=True)


class TargetSelectView(discord.ui.View):
    def __init__(self, game, player, played_cards, indices, combo_type):
        super().__init__(timeout=60)
        self.game = game
        self.player = player
        self.played_cards = played_cards
        self.indices = indices
        self.combo_type = combo_type
        
        options = [discord.SelectOption(label=p.display_name, value=str(p.id)) for p in game.players if p != player]
        if not options: options = [discord.SelectOption(label="Không có mục tiêu hợp lệ", value="none")]

        self.select = discord.ui.Select(placeholder="Chọn người chơi mục tiêu...", min_values=1, max_values=1, options=options)
        self.select.callback = self.on_select
        self.add_item(self.select)

    async def on_select(self, interaction: discord.Interaction):
        if self.select.values[0] == "none": return await interaction.response.send_message("Không có mục tiêu hợp lệ!", ephemeral=True)
        target = discord.utils.get(self.game.players, id=int(self.select.values[0]))
        
        if self.combo_type == 2:
            # Xử lý cướp ngẫu nhiên 1 lá (2 lá giống nhau)
            await interaction.response.edit_message(content="✅ Đang xử lý cướp bài...", view=None)
            for idx in sorted(self.indices, reverse=True):
                self.game.hands[self.player].pop(idx)
            for c in self.played_cards:
                self.game.discard_pile.append(c)
            
            nope_view = NopeView(self.game)
            await interaction.channel.send(f"⏳ {self.player.mention} đánh Combo 2 lá để cướp bài của {target.mention}.\n", view=nope_view)
            await asyncio.sleep(5)
            
            if nope_view.nope_active:
                return await interaction.channel.send(embed=create_card_embed(f"❌ Combo Đánh Đôi của {self.player.mention} đã bị vô hiệu hóa!", 'Chặn (Nope)', discord.Color.dark_theme()))
            
            if not self.game.hands[target]:
                return await interaction.channel.send(f"❌ Mục tiêu {target.mention} đã hết bài trên tay!")
            
            stolen_card = random.choice(self.game.hands[target])
            self.game.hands[target].remove(stolen_card)
            
            if stolen_card == 'Mèo sọc (Streaking Kitten)' and 'Mèo Nổ (Exploding Kitten)' in self.game.hands[target]:
                await interaction.channel.send(embed=create_card_embed(f"⚠️ {target.mention} bị cướp mất **Mèo sọc** nên quả Mèo Nổ trên tay lập tức KÍCH HOẠT!", 'Mèo Nổ (Exploding Kitten)', discord.Color.red()))
                self.game.hands[target].remove('Mèo Nổ (Exploding Kitten)')
                await self.game.handle_bomb_explosion(interaction.channel, target, 'Mèo Nổ (Exploding Kitten)')
            
            if stolen_card == 'Mèo Nổ (Exploding Kitten)' and 'Mèo sọc (Streaking Kitten)' not in self.game.hands[self.player]:
                await interaction.channel.send(embed=create_card_embed(f"💥 {self.player.mention} lỡ tay cướp trúng **Mèo Nổ** đang bị giấu!", 'Mèo Nổ (Exploding Kitten)', discord.Color.red()))
                await self.game.handle_bomb_explosion(interaction.channel, self.player, 'Mèo Nổ (Exploding Kitten)')
            else:
                self.game.hands[self.player].append(stolen_card)
                try: await self.player.send(f"🤫 Bạn đã cướp được lá: **{stolen_card}**")
                except: pass
            
            await interaction.channel.send(embed=create_card_embed(f"👥 {self.player.mention} kích hoạt **COMBO ĐÁNH ĐÔI**!\nĐã cướp bí mật 1 lá của {target.mention}!", self.played_cards[0]))
            await self.game.update_board(interaction.channel)

        elif self.combo_type == 3:
            # Mở modal gọi tên lá bài (3 lá giống nhau)
            await interaction.response.send_modal(CallOutModal(self.game, self.player, self.played_cards, self.indices, target))


class CallOutModal(discord.ui.Modal, title="Gọi tên lá bài muốn lấy"):
    card_name_input = discord.ui.TextInput(label="Tên lá bài muốn đòi", placeholder="VD: Tháo Gỡ (Defuse) hoặc Bỏ qua (Skip)", required=True)

    def __init__(self, game, player, played_cards, indices, target):
        super().__init__()
        self.game = game
        self.player = player
        self.played_cards = played_cards
        self.indices = indices
        self.target = target

    async def on_submit(self, interaction: discord.Interaction):
        called_card = self.card_name_input.value.strip()
        await interaction.response.send_message(f"🎯 {self.player.mention} đánh 3 lá và gọi tên lá: **{called_card}** từ {self.target.mention}!", ephemeral=False)
        
        for idx in sorted(self.indices, reverse=True):
            self.game.hands[self.player].pop(idx)
        for c in self.played_cards:
            self.game.discard_pile.append(c)
        
        nope_view = NopeView(self.game)
        await interaction.channel.send(f"⏳ Đang chờ người chơi khác Chặn (Nope)...", view=nope_view)
        await asyncio.sleep(5)
        
        if nope_view.nope_active:
            return await interaction.channel.send(embed=create_card_embed(f"❌ Combo 3 lá của {self.player.mention} đã bị vô hiệu hóa!", 'Chặn (Nope)', discord.Color.dark_theme()))
        
        target_hand = self.game.hands[self.target]
        matched_card = next((c for c in target_hand if called_card.lower() in c.lower() or c.lower() in called_card.lower()), None)
        
        if matched_card:
            target_hand.remove(matched_card)
            
            if matched_card == 'Mèo sọc (Streaking Kitten)' and 'Mèo Nổ (Exploding Kitten)' in target_hand:
                await interaction.channel.send(embed=create_card_embed(f"⚠️ {self.target.mention} phải đưa **Mèo sọc** nên quả Mèo Nổ trên tay lập tức KÍCH HOẠT!", 'Mèo Nổ (Exploding Kitten)', discord.Color.red()))
                target_hand.remove('Mèo Nổ (Exploding Kitten)')
                await self.game.handle_bomb_explosion(interaction.channel, self.target, 'Mèo Nổ (Exploding Kitten)')
            
            if matched_card == 'Mèo Nổ (Exploding Kitten)' and 'Mèo sọc (Streaking Kitten)' not in self.game.hands[self.player]:
                await interaction.channel.send(embed=create_card_embed(f"💥 {self.player.mention} nhận phải quả **Mèo Nổ** từ việc đòi bài!", 'Mèo Nổ (Exploding Kitten)', discord.Color.red()))
                await self.game.handle_bomb_explosion(interaction.channel, self.player, 'Mèo Nổ (Exploding Kitten)')
            else:
                self.game.hands[self.player].append(matched_card)
                try:
                    await self.target.send(f"⚠️ Bạn có lá **{matched_card}** nên đã phải đưa cho {self.player.name}.")
                    await self.player.send(f"🎉 {self.target.name} có lá **{matched_card}** và đã chuyển cho bạn!")
                except: pass
            
            await interaction.channel.send(embed=create_card_embed(f"✅ {self.target.mention} CÓ lá **{matched_card}** và buộc phải đưa cho {self.player.mention}!", matched_card, discord.Color.green()))
        else:
            await interaction.channel.send(embed=create_card_embed(f"❌ {self.target.mention} KHÔNG CÓ lá bài **{called_card}**. {self.player.mention} không nhận được gì!", discord.Color.orange()))
        
        await self.game.update_board(interaction.channel)


class DiscardSelectView(discord.ui.View):
    def __init__(self, game, player, played_cards, indices):
        super().__init__(timeout=60)
        self.game = game
        self.player = player
        self.played_cards = played_cards
        self.indices = indices
        
        unique_discard = list(Counter(game.discard_pile).keys())
        options = [discord.SelectOption(label=c, value=c) for c in unique_discard[:25]]
        
        self.select = discord.ui.Select(placeholder="Chọn 1 lá bài từ bộ bài bỏ...", min_values=1, max_values=1, options=options)
        self.select.callback = self.on_select
        self.add_item(self.select)

    async def on_select(self, interaction: discord.Interaction):
        chosen_card = self.select.values[0]
        
        await interaction.response.edit_message(content=f"♻️ {self.player.mention} đánh 5 lá khác nhau và chọn lấy lá **{chosen_card}** từ bộ bài bỏ!", view=None)
        
        for idx in sorted(self.indices, reverse=True):
            self.game.hands[self.player].pop(idx)
        for c in self.played_cards:
            self.game.discard_pile.append(c)
        
        nope_view = NopeView(self.game)
        await interaction.channel.send(f"⏳ Đang chờ người chơi khác Chặn (Nope)...", view=nope_view)
        await asyncio.sleep(5)
        
        if nope_view.nope_active:
            return await interaction.channel.send(embed=create_card_embed(f"❌ Combo 5 lá của {self.player.mention} đã bị vô hiệu hóa!", 'Chặn (Nope)', discord.Color.dark_theme()))
        
        if chosen_card in self.game.discard_pile:
            self.game.discard_pile.remove(chosen_card)
            self.game.hands[self.player].append(chosen_card)
            try: await self.player.send(f"🎉 Bạn đã lấy lại lá **{chosen_card}** từ bộ bài bỏ!")
            except: pass
            await interaction.channel.send(embed=create_card_embed(f"✨ {self.player.mention} đã lấy thành công lá **{chosen_card}** từ bộ bài bỏ!", chosen_card, discord.Color.gold()))
        else:
            await interaction.channel.send("❌ Lá bài đó không còn trong bộ bài bỏ nữa!")
        
        await self.game.update_board(interaction.channel)


# --- THỰC THI LOGIC ĐÁNH ĐƠN (1 LÁ) ---
async def execute_play_logic(channel, game, current_player, played_cards, indices, target=None):
    actual_card_name = played_cards[0]
    card_idx = indices[0]

    card_to_execute = actual_card_name
    if actual_card_name == 'Sao chép (Copycat)':
        if not game.last_played_card: return await channel.send("❌ Chưa có ai đánh bài hành động để sao chép!")
        card_to_execute = game.last_played_card
        await channel.send(embed=create_card_embed(f"🎭 {current_player.mention} dùng **Sao chép** để thực hiện kỹ năng của **{card_to_execute}**!", 'Sao chép (Copycat)', discord.Color.purple()))

    if card_to_execute in ['Tráo bài (Shuffle)', 'Sưu tầm rác (Garbage Collection)'] and not getattr(game, 'can_shuffle', True):
        return await channel.send("❌ Nọc đang bị ếm bùa **Kháng xào bài**. Bạn không thể đánh lá này!")

    game.hands[current_player].pop(card_idx)
    game.discard_pile.append(actual_card_name)
    
    can_be_noped = card_to_execute not in ['Tháo Gỡ (Defuse)', 'Mèo Nổ (Exploding Kitten)', 'Chặn (Nope)', 'Mèo Nổ Sập (Úp)', 'Mèo Nổ Sập (Ngửa)', 'Mèo sọc (Streaking Kitten)'] and not any(cat in card_to_execute for cat in ['Tacocat', 'Cattermelon', 'Khoai Tây', 'Râu Bạc', 'Cầu Vồng', 'Mèo hoang (Feral Cat)'])

    if can_be_noped:
        nope_view = NopeView(game)
        await channel.send(f"⏳ {current_player.mention} vừa đánh **{card_to_execute}**.", view=nope_view)
        await asyncio.sleep(5)
        
        if nope_view.nope_active:
            return await channel.send(embed=create_card_embed(f"❌ Kỹ năng lá bài **{card_to_execute}** của {current_player.mention} đã bị vô hiệu hóa hoàn toàn!", 'Chặn (Nope)', discord.Color.dark_theme()))

    if actual_card_name != 'Sao chép (Copycat)': game.last_played_card = actual_card_name

    # --- KỸ NĂNG LÁ BÀI ĐƠN ---
    if card_to_execute == 'Bỏ qua (Skip)':
        is_next = game.advance_turn()
        await channel.send(embed=create_card_embed(f"⏭️ {current_player.mention} dùng **Bỏ qua**!", actual_card_name))
        if is_next: await game.update_board(channel)
        else: await channel.send(f"⚠️ Vẫn còn {game.turns_left} lượt rút nữa!")

    elif card_to_execute == 'Siêu bỏ lượt (Super Skip)':
        game.turns_left = 1 
        is_next = game.advance_turn()
        await channel.send(embed=create_card_embed(f"⏭️🦸‍♂️ {current_player.mention} dùng **Siêu bỏ lượt**!", actual_card_name, discord.Color.blue()))
        if is_next: await game.update_board(channel)

    elif card_to_execute == 'Tấn công (Attack)':
        game.current_turn = (game.current_turn + game.direction) % len(game.players)
        game.turns_left = 2 
        await channel.send(embed=create_card_embed(f"⚔️ {current_player.mention} dùng **Tấn công**!\n➡️ Ép {game.players[game.current_turn].mention} rút **2 LẦN**!", actual_card_name, discord.Color.red()))
        await game.update_board(channel)

    elif card_to_execute == 'Tự vả':
        game.turns_left += 3
        await channel.send(embed=create_card_embed(f"👋 {current_player.mention} kích hoạt **Tự vả**! Tự cộng thêm 3 lượt bốc bài.", actual_card_name, discord.Color.dark_magenta()))
        await game.update_board(channel)

    elif card_to_execute in ['Vả đơn', 'Vả đôi', 'Vả ba']:
        extra_turns = 1 if card_to_execute == 'Vả đơn' else (2 if card_to_execute == 'Vả đôi' else 3)
        passed_turns = game.turns_left
        game.current_turn = (game.current_turn + game.direction) % len(game.players)
        game.turns_left = passed_turns + extra_turns 
        next_player = game.players[game.current_turn]
        await channel.send(embed=create_card_embed(f"💥 {current_player.mention} dùng **{card_to_execute}**!\n➡️ Ép {next_player.mention} chịu {passed_turns} lượt cũ + {extra_turns} lượt mới.", actual_card_name, discord.Color.red()))
        await game.update_board(channel)

    elif card_to_execute == 'Tráo bài (Shuffle)':
        game.is_danger_100 = False 
        random.shuffle(game.deck)
        await channel.send(embed=create_card_embed(f"🔀 Nọc đã được xáo trộn bởi {current_player.mention}!", actual_card_name))
        await game.update_board(channel)

    elif card_to_execute == 'Chống xào bài':
        game.is_danger_100 = True 
        normal_cards = [c for c in game.deck if 'Mèo Nổ' not in c]
        bombs = [c for c in game.deck if 'Mèo Nổ' in c]
        game.deck = bombs + normal_cards 
        game.can_shuffle = False 
        await channel.send(embed=create_card_embed(f"🚷 {current_player.mention} dùng **Chống xào bài**!", actual_card_name, discord.Color.dark_red()))
        await game.update_board(channel)

    elif card_to_execute == 'Kháng xào bài':
        game.can_shuffle = False
        await channel.send(embed=create_card_embed(f"🔒 {current_player.mention} dùng **Kháng xào bài**!", actual_card_name, discord.Color.dark_grey()))

    elif card_to_execute == 'Nhìn trộm (See the future)':
        top_3 = game.deck[:3]
        await channel.send(embed=create_card_embed(f"👁️ {current_player.mention} đang **Nhìn trộm** 3 lá bài đầu nọc...", actual_card_name, discord.Color.purple()))
        try: await current_player.send(f"🔮 **3 lá trên cùng:** {', '.join(top_3)}")
        except: pass

    elif card_to_execute == 'Bom Nguyên Tử (Atomic Bomb)':
        game.is_danger_100 = True 
        normal_kittens = [c for c in game.deck if c == 'Mèo Nổ (Exploding Kitten)']
        game.deck = [c for c in game.deck if c != 'Mèo Nổ (Exploding Kitten)']
        random.shuffle(game.deck)
        game.deck = normal_kittens + game.deck
        await channel.send(embed=create_card_embed(f"☢️ **BOM NGUYÊN TỬ KÍCH HOẠT!**", actual_card_name, discord.Color.gold()))
        is_next = game.advance_turn()
        if is_next: await game.update_board(channel)

    elif card_to_execute == 'Hủy bài (Discard)':
        if target not in game.players: return
        target_hand = game.hands[target]
        dropped = random.sample(target_hand, min(2, len(target_hand)))
        for d in dropped: target_hand.remove(d)
        await channel.send(embed=create_card_embed(f"🗑️ {current_player.mention} đã dùng **Hủy bài** ném đi {len(dropped)} lá ngẫu nhiên của {target.mention}!", actual_card_name))

    elif card_to_execute == 'Đổi chiều (Reverse)':
        game.direction *= -1 
        await channel.send(embed=create_card_embed(f"🔄 {current_player.mention} đã dùng **Đổi chiều** vòng chơi!", actual_card_name))
        is_next = game.advance_turn()
        if is_next: await game.update_board(channel)

    elif card_to_execute == 'Rút từ đáy (Draw bottom)':
        drawn_card = game.deck.pop(-1)
        await channel.send(embed=create_card_embed(f"👇 {current_player.mention} đã lén **Rút một lá từ dưới đáy nọc**!", actual_card_name))
        if 'Mèo Nổ' in drawn_card: 
            if drawn_card == 'Mèo Nổ (Exploding Kitten)' and 'Mèo sọc (Streaking Kitten)' in game.hands[current_player]:
                game.hands[current_player].append(drawn_card)
                try: await current_player.send("🤫 Rút đáy trúng Mèo Nổ, nhưng nhờ **Mèo sọc**, bạn đã ôm gọn bom!")
                except: pass
            else:
                await game.handle_bomb_explosion(channel, current_player, drawn_card)
        else:
            game.hands[current_player].append(drawn_card)
            try: await current_player.send(f"📥 Bạn rút từ đáy được: **{drawn_card}**")
            except: pass
        is_next = game.advance_turn()
        if current_player in game.players and is_next: await game.update_board(channel)

    elif card_to_execute == 'Cướp bài (Steal)':
        if target not in game.players or target == current_player or not game.hands[target]: return await channel.send("❌ Mục tiêu không hợp lệ!")
        stolen_card = random.choice(game.hands[target])
        game.hands[target].remove(stolen_card)
        
        if stolen_card == 'Mèo sọc (Streaking Kitten)' and 'Mèo Nổ (Exploding Kitten)' in game.hands[target]:
            await channel.send(embed=create_card_embed(f"⚠️ {target.mention} bị cướp mất **Mèo sọc** nên quả Mèo Nổ kích hoạt!", 'Mèo Nổ (Exploding Kitten)', discord.Color.red()))
            game.hands[target].remove('Mèo Nổ (Exploding Kitten)')
            await game.handle_bomb_explosion(channel, target, 'Mèo Nổ (Exploding Kitten)')
        if stolen_card == 'Mèo Nổ (Exploding Kitten)' and 'Mèo sọc (Streaking Kitten)' not in game.hands[current_player]:
            await channel.send(embed=create_card_embed(f"💥 {current_player.mention} lỡ tay cướp trúng **Mèo Nổ**!", 'Mèo Nổ (Exploding Kitten)', discord.Color.red()))
            await game.handle_bomb_explosion(channel, current_player, 'Mèo Nổ (Exploding Kitten)')
        else:
            game.hands[current_player].append(stolen_card)
            try: await current_player.send(f"🤫 Bạn đã cướp được lá: **{stolen_card}**")
            except: pass
        await channel.send(embed=create_card_embed(f"🥷 {current_player.mention} đã dùng **Cướp bài** lấy 1 lá của {target.mention}!", actual_card_name))

    elif card_to_execute == 'Sưu tầm rác (Garbage Collection)':
        await channel.send(embed=create_card_embed(f"🗑️ {current_player.mention} đã dùng **Sưu tầm rác**!", actual_card_name, discord.Color.green()))
        
        async def ask_player(p):
            if not game.hands[p]: return None
            unique_hand = list(Counter(game.hands[p]).keys())
            msg_text = "🗑️ **SƯU TẦM RÁC:** Chọn 1 lá bài để ném vào nọc (nhập số):\n"
            for i, c in enumerate(unique_hand): msg_text += f"{i+1}. {c}\n"
            
            try: await p.send(msg_text)
            except: return p, random.choice(game.hands[p])
            
            def check_gc(m): return m.author == p and m.channel.type == discord.ChannelType.private and m.content.isdigit() and 1 <= int(m.content) <= len(unique_hand)
            
            try:
                msg = await bot.wait_for('message', check=check_gc, timeout=60.0)
                return p, unique_hand[int(msg.content) - 1]
            except asyncio.TimeoutError:
                return p, random.choice(game.hands[p])

        tasks = [ask_player(p) for p in game.players if game.hands[p]]
        results = await asyncio.gather(*tasks)
        
        for p, card in results:
            if card:
                game.hands[p].remove(card)
                game.deck.append(card)
                try: await p.send(f"✅ Bạn đã vứt lá **{card}** vào nọc.")
                except: pass

        random.shuffle(game.deck)
        game.is_danger_100 = False 
        await channel.send("♻️ Đã thu gom bài từ mọi người. Nọc đã được xào trộn!")
        await game.update_board(channel)

    elif card_to_execute == 'Tìm kiếm (Search)':
        cards_to_look = min(5, len(game.deck))
        if cards_to_look == 0: return await channel.send("❌ Nọc hết bài!")
        
        top_cards = [game.deck.pop(0) for _ in range(cards_to_look)]
        msg_text = f"🔍 **TÌM KIẾM:** Chọn 1 lá bài lấy lên tay (nhập số từ 1 đến {cards_to_look}):\n"
        for i, c in enumerate(top_cards): msg_text += f"{i+1}. {c}\n"
        
        try: await current_player.send(msg_text)
        except:
            game.deck.extend(top_cards)
            return await channel.send(f"⚠️ {current_player.mention}, hãy mở DM!")
        
        def check_search(m):
            return m.author == current_player and m.channel.type == discord.ChannelType.private and m.content.isdigit() and 1 <= int(m.content) <= cards_to_look

        try:
            msg = await bot.wait_for('message', check=check_search, timeout=60.0)
            chosen_card = top_cards.pop(int(msg.content) - 1)
            
            if 'Mèo Nổ' in chosen_card:
                if chosen_card == 'Mèo Nổ (Exploding Kitten)' and 'Mèo sọc (Streaking Kitten)' in game.hands[current_player]:
                    game.hands[current_player].append(chosen_card)
                    await current_player.send("🤫 Tìm kiếm trúng Mèo Nổ, nhưng nhờ **Mèo sọc**, bạn đã ôm gọn bom!")
                else:
                    await game.handle_bomb_explosion(channel, current_player, chosen_card, from_search=True, top_5_deck=top_cards)
            else:
                game.hands[current_player].append(chosen_card)
                await current_player.send(f"✅ Bạn đã lấy lá: **{chosen_card}**")
                
            game.deck.extend(top_cards)
            random.shuffle(game.deck)
            game.is_danger_100 = False 
            await channel.send(f"🔀 {current_player.mention} đã chọn xong.")
        except asyncio.TimeoutError:
            game.deck.extend(top_cards)
            random.shuffle(game.deck)
        
        await game.update_board(channel)

    elif card_to_execute == 'Biến đổi tương lai (Alter)':
        cards_to_look = min(3, len(game.deck))
        if cards_to_look == 0: return await channel.send("❌ Nọc hết bài!")
        
        top_cards = [game.deck.pop(0) for _ in range(cards_to_look)]
        msg_text = f"🔮 **BIẾN ĐỔI TƯƠNG LAI:** {cards_to_look} lá trên cùng:\n"
        for i, c in enumerate(top_cards): msg_text += f"{i+1}. {c}\n"
        
        try: await current_player.send(msg_text)
        except:
            top_cards.reverse()
            for c in top_cards: game.deck.insert(0, c)
            return await channel.send("⚠️ Vui lòng mở DM!")

        def check_alter(m):
            if m.author != current_player or m.channel.type != discord.ChannelType.private: return False
            parts = m.content.split()
            return len(parts) == cards_to_look and sorted([int(p) for p in parts]) == list(range(1, cards_to_look + 1))

        try:
            msg = await bot.wait_for('message', check=check_alter, timeout=60.0)
            new_order = [int(p) - 1 for p in msg.content.split()]
            reordered_cards = [top_cards[i] for i in new_order]
            reordered_cards.reverse()
            for c in reordered_cards: game.deck.insert(0, c)
            await current_player.send("✅ Đã thay đổi thứ tự thành công!")
        except asyncio.TimeoutError:
            top_cards.reverse()
            for c in top_cards: game.deck.insert(0, c)

    elif card_to_execute == 'Xin xỏ (Favor)':
        if target not in game.players or target == current_player or not game.hands[target]:
            return await channel.send("❌ Mục tiêu không hợp lệ!")
        
        unique_target_hand = list(Counter(game.hands[target]).keys())
        msg_text = f"🎁 {current_player.name} xin bạn 1 lá. Chọn 1 lá (nhập số):\n"
        for i, c in enumerate(unique_target_hand): msg_text += f"{i+1}. {c}\n"
            
        try: await target.send(msg_text)
        except: return await channel.send("⚠️ Mục tiêu không mở DM!")

        def check_favor(m):
            return m.author == target and m.channel.type == discord.ChannelType.private and m.content.isdigit() and 1 <= int(m.content) <= len(unique_target_hand)

        try:
            msg = await bot.wait_for('message', check=check_favor, timeout=60.0)
            card_to_give = unique_target_hand[int(msg.content) - 1]
        except asyncio.TimeoutError:
            card_to_give = random.choice(game.hands[target])
            
        game.hands[target].remove(card_to_give)
        game.hands[current_player].append(card_to_give)
        try:
            await target.send(f"✅ Đã đưa lá **{card_to_give}**.")
            await current_player.send(f"🎁 Nhận được lá: **{card_to_give}**")
        except: pass
        await channel.send(f"🤝 {target.mention} đã đưa 1 lá bài cho {current_player.mention}!")


# --- LỆNH KHỞI ĐỘNG ---
@bot.command(name='meo')
async def start_lobby(ctx):
    channel_id = ctx.channel.id
    if channel_id not in games: games[channel_id] = ExplodingKittensGame()
    game = games[channel_id]
    
    if game.is_started: return await ctx.send("🚫 Trò chơi đang diễn ra ở kênh này rồi!")
    
    await ctx.send("🎮 **Phòng chờ Mèo Nổ!**", view=LobbyView(game))

# SỬA ĐOẠN NÀY: Dùng os.getenv để lấy token an toàn
import os
TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)
