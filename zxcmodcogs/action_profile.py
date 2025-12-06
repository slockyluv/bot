import pymongo
import disnake
import datetime
import json
import requests
from disnake.ext import commands
from disnake.enums import ButtonStyle, TextInputStyle
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

with open('configs/zxc.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
with open('configs/zxc_tokens.json', 'r', encoding='utf-8') as f:
    config1 = json.load(f)

cluster = pymongo.MongoClient(config1['mongodb'])
db = cluster.zxc
database = cluster.zxc
files = cluster.zxc.files_moderation
online_stats = database.online_stats

# Новые коллекции для унифицированной системы
rest_collection = cluster.zxc.rest_requests  # Заявки на отпуск
staff_warns_collection = cluster.zxc.staff_warns  # Выговоры по группам

min = 60
hour = 60 * 60
day = 60 * 60 * 24

def format_duration(seconds: int) -> str:
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    parts = []
    if days > 0:
        parts.append(f"{days}д")
    if hours > 0:
        parts.append(f"{hours}ч")
    if minutes > 0:
        parts.append(f"{minutes}м")

    # если всё ноль — показать хотя бы секунды
    if not parts:
        parts.append(f"{seconds}с")

    return " ".join(parts)

def get_user_duration_for_period(user_id, category, period='Неделя', start=None, end=None):
    now = datetime.utcnow()
    m = {"$or": [{"user_id": str(user_id)}, {"user_id": user_id}]}
    if period == 'День':
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        pipeline = [
            {"$match": {**m, "category": category, "period": "day", "date": {"$gte": day_start, "$lt": day_end}}},
            {"$group": {"_id": None, "total": {"$sum": "$duration"}}}
        ]
    elif period == 'Неделя':
        week_start = (now - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        pipeline = [
            {"$match": {**m, "category": category, "period": "day", "date": {"$gte": week_start}}},
            {"$group": {"_id": None, "total": {"$sum": "$duration"}}}
        ]
    elif period == 'Месяц':
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        pipeline = [
            {"$match": {**m, "category": category, "period": "day", "date": {"$gte": month_start}}},
            {"$group": {"_id": None, "total": {"$sum": "$duration"}}}
        ]
    elif period == 'Всё время':
        pipeline = [
            {"$match": {**m, "category": category}},
            {"$group": {"_id": None, "total": {"$sum": "$duration"}}}
        ]
    elif period == 'Свой период':
        if not start or not end:
            return 0
        pipeline = [
            {"$match": {**m, "category": category, "period": "day", "date": {"$gte": start, "$lte": end}}},
            {"$group": {"_id": None, "total": {"$sum": "$duration"}}}
        ]
    else:
        return 0
    res = list(db.online_stats.aggregate(pipeline))
    return int(res[0]["total"]) if res else 0

def get_user_total_for_category(user_id, category):
    m = {"$or":[{"user_id": str(user_id)}, {"user_id": user_id}]}
    pipeline = [
        {"$match": {**m, "category": category}},
        {"$group": {"_id": None, "total": {"$sum": "$duration"}}}
    ]
    res = list(db.online_stats.aggregate(pipeline))
    return res[0]["total"] if res else 0

def get_user_day_duration(user_id, category, target_date=None):
    if target_date is None:
        target_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    day_start = target_date
    day_end = day_start + timedelta(days=1)
    m = {"$or":[{"user_id": str(user_id)}, {"user_id": user_id}]}
    docs = list(db.online_stats.find({
        **m,
        "category": category,
        "period": "day",
        "date": {"$gte": day_start, "$lt": day_end}
    }))
    total = sum(doc.get("duration", 0) for doc in docs)
    return total

def draw_text_with_offset(image, text, x, y, font_size, color=(255,255,255)):
    draw = ImageDraw.Draw(image)
    
    font = ImageFont.truetype("fonts/Gordita_bold.ttf", size=font_size)

    bbox = draw.textbbox((x, y), text, font=font)
    text_width = bbox[2] - bbox[0]
    x -= text_width // 2
    draw.text((x, y), text, font=font, fill=color)

async def build_profile_image(image, inter, category: str, author_id: int):
    period = mod_selectedPeriod.get(str(author_id), "Всё время")
    group_choice = cluster.zxc.action_set.find_one({"_id": str(author_id)})["group"]
    пользователь = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))

    result = database[f"balls"].find_one({'_id': str(пользователь.id)})

    if group_choice == "support":
        ImageDraw.Draw(image).text((868, 405), f"{sup['nedopysk']}", font = ImageFont.truetype("Gilroy-Bold.ttf", size=32), fill = (255, 255, 255))
        ImageDraw.Draw(image).text((868, 470), f"{verify['verify']}", font = ImageFont.truetype("Gilroy-Bold.ttf", size=32), fill = (255, 255, 255))

    if group_choice == "moderator":
        ImageDraw.Draw(image).text((868, 405), f"{result['mutes']}", font = ImageFont.truetype("Gilroy-Bold.ttf", size=32), fill = (255, 255, 255))
        ImageDraw.Draw(image).text((868, 470), f"{result['bans']}", font = ImageFont.truetype("Gilroy-Bold.ttf", size=32), fill = (255, 255, 255))
        ImageDraw.Draw(image).text((868, 533), f"{result['warns']}", font = ImageFont.truetype("Gilroy-Bold.ttf", size=32), fill = (255, 255, 255))
        ImageDraw.Draw(image).text((868, 596), f"0", font = ImageFont.truetype("Gilroy-Bold.ttf", size=32), fill = (255, 255, 255))

    hours = value // 3600
    minutes = (value % 3600) // 60

    staff_online = f"{hours}ч {minutes}м"
    staff_messages = count

    draw_text_with_offset(image, staff_online, 1209, 405, font_size=96)
    draw_text_with_offset(image, staff_messages, 1235, 470, font_size=96)

    return image

def get_user_rest_status(user_id: str, group: str):
    """Получить статус отпуска пользователя для конкретной группы"""
    # Ищем активный отпуск с составным ID
    active_rest = rest_collection.find_one({"_id": f"{user_id}_{group}", "rest": "Активен"})
    
    if active_rest:
        return "Активен"
    else:
        return "Не активен"

def get_user_warns_count(user_id: str, group: str):
    """Получить количество выговоров пользователя для конкретной группы"""
    user_warns = staff_warns_collection.find_one({"_id": user_id})
    
    if not user_warns or group not in user_warns.get("groups", {}):
        return 0
    
    return user_warns["groups"][group].get("warn_count", 0)

def initialize_user_data(user_id: str, group: str):
    """Инициализация данных пользователя в новой системе"""
    # Инициализация выговоров
    staff_warns_collection.update_one(
        {"_id": user_id},
        {"$set": {f"groups.{group}": {"warn_count": 0, "warns": []}}},
        upsert=True
    )
    
    # Инициализация других коллекций при необходимости
    if cluster.zxc.verify_count.count_documents({"_id": user_id}) == 0:
        cluster.zxc.verify_count.insert_one({"_id": user_id, "verify_count": 0})
    
    if cluster.zxc.balls.count_documents({"_id": user_id}) == 0:
        cluster.zxc.balls.insert_one({"_id": user_id, "balls": 0, "mutes": 0, "bans": 0, "warns": 0})

class ProfileStaffView(disnake.ui.View):
    def __init__(self, inter, image, author: int, category: str):
        super().__init__()
        self.author = author
        self.category = category
    
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row=1))

class ModRefreshButton(disnake.ui.Button):
    def __init__(self, inter, image, author: int, category: str):
        super().__init__()
        self.author = author
        self.category = category
    
    async def callback(self, image, inter):
        if inter.author.id != self.author:
            return await inter.response.send_message("Вы не можете использовать эту кнопку.", ephemeral=True)
        embed = await build_profile_image(inter, image, self.category, self.author)
        await inter.response.edit_message(embed=embed, view=ProfileStaffView(inter, image, self.author, self.category))

class ProfileCogs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_button_click(self, inter):
        custom_id = inter.component.custom_id

        if custom_id.endswith("profile_action"):
            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790)
                embed.set_author(name = "Профиль", icon_url = inter.guild.icon.url)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.send(ephemeral = True, embed=embed)

            if custom_id == "profile_action":
                db_target = cluster.zxc.target.find_one({'_id': str(inter.author.id)})
                пользователь = disnake.utils.get(self.bot.get_guild(config['server_id']).members, id=int(db_target['member']))

                group_choice = db_target['group']
                
                # Инициализация данных пользователя в новой системе
                initialize_user_data(str(пользователь.id), group_choice)

                now = datetime.now()
                day = f"{now.strftime('%A')}, {now.strftime('%B')} {now.day}"
                time_str = now.strftime('%H:%M')
                
                image = Image.open(f"action_zxc/{group_choice}_profile.png")
                draw_text_with_offset(image, day, 710, 76, font_size=32)
                draw_text_with_offset(image, time_str, 708, 120, font_size=96)
    
                width, height = 110, 110
                avatar_x, avatar_y = 137, 139
                avatar_response = requests.get(пользователь.display_avatar.url, stream=True)
                Image.open(avatar_response.raw).resize((width, height)).save('avatars/avatar_profile_zxc.png')
                
                mask_im = Image.new("L", (width, height))
                ImageDraw.Draw(mask_im).ellipse((0, 0, width, height), fill=255)
                image.paste(Image.open('avatars/avatar_profile_zxc.png'), (avatar_x, avatar_y), mask_im)
 
                пользователь_name = пользователь.name[:13] if len(пользователь.name) > 13 else пользователь.name
                draw_text_with_offset(image, пользователь_name, 413, 194.26, font_size=32)

                if cluster.zxc.backgrounds_profile.count_documents({"_id": str(пользователь.id)}) == 0:
                    cluster.zxc.backgrounds_profile.insert_one({"_id": str(пользователь.id), "choice_profile_moderation": 0, "choice_profile": 0, "choice_profile_mafia": 0})

                await inter.response.defer()

                choice_profile_image = cluster.zxc.backgrounds_profile.find_one({"_id": str(пользователь.id)})["choice_profile_moderation"] # Пока в разработке но пусть остается

                points = cluster.zxc.balls.find_one({"_id": str(пользователь.id)})['balls']
                draw_text_with_offset(image, str(points), 409, 172, font_size=20)

                # Новая система: получение статуса отпуска
                rest_status = get_user_rest_status(str(пользователь.id), group_choice)
                draw_text_with_offset(image, rest_status, 260, 488, font_size=32)
                
                # Новая система: получение количества выговоров
                warn_count = get_user_warns_count(str(пользователь.id), group_choice)
                draw_text_with_offset(image, str(warn_count), 260, 598, font_size=32)

                if group_choice == "support":
                    if cluster.zxc.nedopysk.count_documents({"_id": str(пользователь.id)}) == 0:
                        cluster.zxc.nedopysk.insert_one({"_id": str(пользователь.id), "nedopysk": 0})
                    
                    draw_text_with_offset(image, str(cluster.zxc.verify_count.find_one({"_id": str(пользователь.id)})["verify_count"]), 890, 410, font_size=32)
                    draw_text_with_offset(image, str(cluster.zxc.nedopysk.find_one({"_id": str(пользователь.id)})["nedopysk"]), 890, 477, font_size=32)
                    draw_text_with_offset(image, str("0$"), 260, 381, font_size=32)
                    draw_text_with_offset(image, str("0"), 1243, 540, font_size=32)
                    draw_text_with_offset(image, str("5/5"), 1243, 607, font_size=32)
                
                    user_id = str(пользователь.id)
                    messages = get_user_duration_for_period(user_id, "message", period='Неделя')
                    draw_text_with_offset(image, str(messages), 1250, 477, font_size=32)

                    user_id = str(пользователь.id)
                    week_seconds = get_user_duration_for_period(user_id, "verify", period='Неделя')
                    formatted_duration = format_duration(week_seconds)
                    draw_text_with_offset(image, formatted_duration, 1220, 412, font_size=32)

                if group_choice == "control" or group_choice == "moderator":
                    if cluster.zxc.nedopysk.count_documents({"_id": str(пользователь.id)}) == 0:
                        cluster.zxc.nedopysk.insert_one({"_id": str(пользователь.id), "nedopysk": 0})
                    
                    draw_text_with_offset(image, str(cluster.zxc.verify_count.find_one({"_id": str(пользователь.id)})["verify_count"]), 890, 410, font_size=32)
                    draw_text_with_offset(image, str(cluster.zxc.nedopysk.find_one({"_id": str(пользователь.id)})["nedopysk"]), 890, 477, font_size=32)
                    
                    pipeline = [
                        {
                            "$match": {
                                "user_id": пользователь.id,
                                "category": "message"
                            }
                        },
                        {
                            "$group": {
                                "_id": "$user_id",
                                "total_messages": {"$sum": "$duration"}
                            }
                        }
                    ]

                    result = list(online_stats.aggregate(pipeline))
                    total_messages = result[0]["total_messages"] if result else 0
                    draw_text_with_offset(image, str(total_messages), 1250, 477, font_size=32)
                    
                    user_stats = cluster.zxc.online_stats.find_one({
                        "_id": str(пользователь.id),
                        "category": "verify"
                    })

                    if user_stats and "period_stats" in user_stats:
                        total_duration = user_stats["period_stats"].get("Всё время", 0)
                        draw_text_with_offset(image, str(total_duration), 1220, 415, font_size=32)
                    else:
                        draw_text_with_offset(image, str(0), 1220, 412, font_size=32)

                # Остальные группы остаются без изменений
                if group_choice == "closemod":
                    pass
  
                if group_choice == "eventsmod":
                    doc = cluster.zxc.event_balls.find_one(
                        {"_id": str(пользователь.id)},
                        {"event_name": 1}
                    )

                    events_count = len(doc.get("event_name", [])) if doc else 0

                    pipeline = [
                        {"$match": {"_id": str(пользователь.id)}},
                        {"$unwind": {"path": "$event_name", "preserveNullAndEmptyArrays": True}},
                        {"$group": {"_id": "$event_name", "cnt": {"$sum": 1}}},
                        {"$sort": {"cnt": -1}},
                        {"$limit": 1}
                    ]
                    res = list(cluster.zxc.event_balls.aggregate(pipeline))

                    if res and res[0]["_id"] is not None:
                        most_common_event = res[0]["_id"]
                        most_common_count = res[0]["cnt"]
                    else:
                        most_common_event = "—"  # можно поставить прочерк или "нет"
                        most_common_count = 0

                    draw_text_with_offset(image, str(events_count), 1025, 410, font_size=32)
                    draw_text_with_offset(image, str(most_common_event), 1025, 475, font_size=32)
                    
                    draw_text_with_offset(image, str("0$"), 260, 381, font_size=32)
                    
                    user_id = str(пользователь.id)
                    messages = get_user_duration_for_period(user_id, "message", period='Неделя')
                    draw_text_with_offset(image, str(messages), 1025, 601, font_size=32)

                    user_id = str(пользователь.id)
                    week_seconds = get_user_duration_for_period(user_id, "eventer", period='Неделя')
                    formatted_duration = format_duration(week_seconds)
                    draw_text_with_offset(image, formatted_duration, 1025, 538, font_size=32)

                if group_choice == "creative":
                    pass

                if group_choice == "tribunemod":
                    pass

                if group_choice == "helper":
                    pass

                if group_choice == "contentmaker":
                    pass

                path = f"out/action_profile_{inter.author.id}.png"
                image.save(path)

                image = Image.open(path)

                return await inter.message.edit(attachments=None,file=disnake.File(path), view=ProfileStaffView(inter, image, inter.author.id, group_choice))

    @commands.Cog.listener()
    async def on_dropdown(self, inter: disnake.MessageInteraction):
        if inter.data.get("custom_id") == "profile_action":
            group_choice = cluster.zxc.action_set.find_one({"_id": str(inter.author.id)})["group"]

            image = Image.open(f"out/action_profile_{inter.author.id}.png")

            embed = await build_profile_image(inter, image, group_choice, inter.author.id, 0)
            await inter.response.send_message(embed=embed, ephemeral=True, view=ProfileStaffView(inter, image, inter.author.id, group_choice))

def setup(bot: commands.Bot):
    bot.add_cog(ProfileCogs(bot))