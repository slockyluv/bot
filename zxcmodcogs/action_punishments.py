import pymongo
import disnake
import datetime
import json
import requests
import os
import asyncio
import random
from disnake.ext import commands
from disnake.enums import ButtonStyle, TextInputStyle
from datetime import datetime, timedelta
from statistics import mean
from PIL import Image, ImageDraw, ImageFont
import re

# Загрузка конфигураций и подключение к БД
with open('configs/zxc.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
with open('configs/zxc_tokens.json', 'r', encoding='utf-8') as f:
    config1 = json.load(f)
cluster = pymongo.MongoClient(config1['mongodb'])
db = cluster.zxc
files = cluster.zxc.files_moderation
ban_limits_collection = cluster.zxc.ban_limits


administrator = config['administrator']
master = config['master']
security = config['security']
curator = config['curator']
moderator = config['moderator']
closer = config['closer']
helper = config['helper']
tribunemod = config['tribunemod']
eventer = config['eventer']
creative = config['creative']
support = config['support']
own_roles = config['own_roles']
control = config['control']

EXCLUDED_ROLES = {1384954166689923172, 999609135396032534, 1390137707014918299, 1383126511758082198, 1383126511762145330}

BAN_LIMIT_PER_DAY = config.get('ban_limit_per_day', 3)
BAN_LIMITED_CUSTOM_IDS = {
    'ban_vidat': 'обычный бан',
    'ban_event_vidat': 'ивент бан',
    'ban_close_vidat': 'клоз бан',
    'creative_ban_vidat': 'креатив бан'
}
LOG_RELEASE_CONFIG = {
    'text_mute': {
        'label': 'Снять текстовый мут',
        'style': ButtonStyle.green,
        'role_id': config['tmute'],
        'title': 'Текстовый мут',
        'success_text': 'снял текстовый мут'
    },
    'voice_mute': {
        'label': 'Снять голосовой мут',
        'style': ButtonStyle.green,
        'role_id': config['vmute'],
        'title': 'Голосовой мут',
        'success_text': 'снял голосовой мут'
    },
    'ban': {
        'label': 'Разбанить',
        'style': ButtonStyle.red,
        'role_id': config['ban'],
        'title': 'Бан',
        'success_text': 'разбанил пользователя'
    },
    'event_ban': {
        'label': 'Снять ивент бан',
        'style': ButtonStyle.red,
        'role_id': config['event_ban'],
        'title': 'Ивент бан',
        'success_text': 'снял ивент бан'
    },
    'close_ban': {
        'label': 'Снять клоз бан',
        'style': ButtonStyle.red,
        'role_id': config['close_ban'],
        'title': 'Клоз бан',
        'success_text': 'снял клоз бан'
    },
    'creative_ban': {
        'label': 'Снять креатив бан',
        'style': ButtonStyle.red,
        'role_id': config['creative_ban'],
        'title': 'Креатив бан',
        'success_text': 'снял креатив бан'
    }
}



def get_effective_top_role(member):
    filtered_roles = [role for role in member.roles if role.id not in EXCLUDED_ROLES]
    if not filtered_roles:
        return member.guild.default_role
    return max(filtered_roles, key=lambda role: role.position)

def draw_text_with_offset(im, text, x, y, font_size, color=(255,255,255)):
    draw = ImageDraw.Draw(im)
    
    font = ImageFont.truetype("fonts/Gordita_bold.ttf", size=font_size)

    bbox = draw.textbbox((x, y), text, font=font)
    text_width = bbox[2] - bbox[0]
    x -= text_width // 2
    draw.text((x, y), text, font=font, fill=color)

class LogActionView(disnake.ui.View):
    def __init__(self, member_id: int, action_key: str):
        super().__init__(timeout=None)
        cfg = LOG_RELEASE_CONFIG.get(action_key)
        if not cfg:
            return
        self.add_item(
            disnake.ui.Button(
                style=cfg['style'],
                label=cfg['label'],
                custom_id=f"log_action:{action_key}:{member_id}"
            )
        )

def enforce_daily_ban_limit(moderator_id: int, target_id: int, ban_label: str, reason: str, guild_id: int):
    """Track issued bans per moderator and prevent exceeding the daily limit."""
    today = datetime.utcnow().date().isoformat()
    doc = ban_limits_collection.find_one({"_id": str(moderator_id)})

    if not doc or doc.get("date") != today:
        ban_limits_collection.update_one(
            {"_id": str(moderator_id)},
            {"$set": {"date": today, "count": 0}},
            upsert=True
        )
        current_count = 0
    else:
        current_count = doc.get("count", 0)

    if current_count >= BAN_LIMIT_PER_DAY:
        return False, current_count

    record = {
        "target_id": str(target_id),
        "target_guild": str(guild_id),
        "ban_type": ban_label,
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat()
    }

    ban_limits_collection.update_one(
        {"_id": str(moderator_id)},
        {
            "$inc": {"count": 1},
            "$set": {"date": today},
            "$push": {
                "history": {
                    "$each": [record],
                    "$slice": -25
                }
            }
        }
    )

    return True, current_count + 1

class ActionStaffWarns(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Выдать выговор', custom_id = 'give_warn_staff_action', emoji = f'{files.find_one({"_id": "action_plus"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Список выговоров', custom_id = 'warns_staff_list', emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Снять выговор', custom_id = 'snyat_warn_staff_action', emoji = f'{files.find_one({"_id": "action_minus"})["emoji_take"]}', row=1))

        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row=2))

class ActionMuteBan(disnake.ui.View):
    def __init__(self): 
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Выдать бан', custom_id="give_ban_action", emoji = f'{files.find_one({"_id": "action_plus"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Снять бан', custom_id="snyat_ban_action", emoji = f'{files.find_one({"_id": "action_minus"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))

        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row=2))

class ActionEventBan(disnake.ui.View):
    def __init__(self): 
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Выдать бан', custom_id="ban_event_vidat", emoji = f'{files.find_one({"_id": "action_plus"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Снять бан', custom_id="ban_event_snyat", emoji = f'{files.find_one({"_id": "action_minus"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))

        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row=2))
class ActionCloseBan(disnake.ui.View):
    def __init__(self): 
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Выдать бан', custom_id="ban_close_vidat", emoji = f'{files.find_one({"_id": "action_plus"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Снять бан', custom_id="ban_close_snyat", emoji = f'{files.find_one({"_id": "action_minus"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))

        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row=2))
        
class ActionCreativeBan(disnake.ui.View):
    def __init__(self): 
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Выдать креатив бан', custom_id="creative_ban_give_action", emoji = f'{files.find_one({"_id": "action_plus"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Снять креатив бан', custom_id="creative_ban_snyat_action", emoji = f'{files.find_one({"_id": "action_minus"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))

        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row=2))

class ActionWarns(disnake.ui.View):
    def __init__(self): 
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Выдать варн', custom_id="give_warn_action", emoji = f'{files.find_one({"_id": "action_plus"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Снять варн', custom_id="snyat_warn_action", emoji = f'{files.find_one({"_id": "action_minus"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))

        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row=2))

class ActionMuteView(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style=ButtonStyle.secondary, label='Текстовый мут', custom_id="textmute_action", emoji=f'{files.find_one({"_id": "action_mute"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style=ButtonStyle.secondary, label='Голосовой мут', custom_id="voicemute_action", emoji=f'{files.find_one({"_id": "action_support"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))

        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row=2))

class ActionMuteChoice(disnake.ui.View):
    def __init__(self, bot, member):
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        if db.action.count_documents({"_id": str(member.id)}) == 0:
            mute_button = disnake.ui.Button(style=ButtonStyle.secondary, label='Снять мут', custom_id="snyat_mute_action", emoji=f'{files.find_one({"_id": "action_minus"})["emoji_take"]}', disabled=True, row=1)
        else:
            mute_button = disnake.ui.Button(style=ButtonStyle.secondary, label='Снять мут', custom_id ="snyat_mute_action", emoji=f'{files.find_one({"_id": "action_minus"})["emoji_take"]}', row=1)
        self.add_item(disnake.ui.Button(style=ButtonStyle.secondary, label='Выдать мут', custom_id="give_mute_action", emoji=f'{files.find_one({"_id": "action_plus"})["emoji_take"]}', row=1))
        self.add_item(mute_button)
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))

        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row=2))

class PunishmentsCogs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def handle_log_action_button(self, inter):
        await inter.response.defer(ephemeral=True)
        parts = inter.component.custom_id.split(":")
        if len(parts) < 3:
            return await inter.followup.send("Некорректная кнопка.", ephemeral=True)

        action_key = parts[1]
        member_id = int(parts[2])

        cfg = LOG_RELEASE_CONFIG.get(action_key)
        if not cfg:
            return await inter.followup.send("Не удалось определить тип наказания.", ephemeral=True)

        role = inter.guild.get_role(cfg['role_id'])
        member = inter.guild.get_member(member_id)

        if member:
            highest_role_user1 = get_effective_top_role(inter.author)
            highest_role_user2 = get_effective_top_role(member)
            if highest_role_user1.position < highest_role_user2.position:
                return await inter.followup.send(
                    f"Роль пользователя {member.mention} выше, чем роль пользователя {inter.author.mention}.",
                    ephemeral=True
                )

        if not role:
            return await inter.followup.send("Не найдена роль для снятия наказания.", ephemeral=True)

        if not member:
            return await inter.followup.send("Пользователь не найден на сервере.", ephemeral=True)

        try:
            await member.remove_roles(role, reason=f"Log release button by {inter.author}")
            cluster.zxc.action.delete_one({'_id': str(member_id)})
        except Exception as e:
            print(e)
            return await inter.followup.send("Не удалось снять наказание. Проверьте журнал ошибок.", ephemeral=True)

        release_embed = disnake.Embed(
            color=3092790,
            description=f"{inter.author.mention} {cfg['success_text']} у {member.mention}."
        )
        release_embed.set_author(name=f"Снятие | {cfg['title']}", icon_url=inter.guild.icon.url)
        release_embed.add_field(name="> Снял наказание", value=f"{inter.author.mention} | **ID:** {inter.author.id}", inline=False)
        release_embed.add_field(name="> Пользователь", value=f"{member.mention} | **ID:** {member.id}", inline=False)

        if inter.message.embeds:
            for field in inter.message.embeds[0].fields:
                release_embed.add_field(name=field.name, value=field.value, inline=field.inline)

        try:
            view = disnake.ui.View.from_message(inter.message)
            for child in view.children:
                child.disabled = True
            await inter.message.edit(view=view)
        except Exception as e:
            print(e)

        await inter.channel.send(embed=release_embed)
        await inter.followup.send("Наказание успешно снято.", ephemeral=True)

    @commands.Cog.listener()
    async def on_button_click(self, inter):
        custom_id = inter.component.custom_id

        if custom_id.startswith("log_action:"):
            await self.handle_log_action_button(inter)
            return

        now = datetime.now()
        day = f"{now.strftime('%A')}, {now.strftime('%B')} {now.day}"
        time = f"{now.strftime('%H:%M')}"
        print(custom_id[-5:])
        if "warn" in custom_id:
            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(title = f'Наказания | {inter.guild.name}', description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.send(ephemeral = True, embed=embed)

            пользователь = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))

            if custom_id == 'warn_action':
                im = Image.open(f'action_zxc/warn.png')

                draw_text_with_offset(im, str(day), 710, 76, font_size=32)
                draw_text_with_offset(im, str(time), 708, 120, font_size=96)

                width = 110
                height = 110
                avatar_x = 137
                avatar_y = 139

                Image.open(requests.get(пользователь.display_avatar.url, stream = True).raw).resize((width, height)).save('avatars/avatar_profile_zxc.png')
                mask_im = Image.new("L", Image.open("avatars/avatar_profile_zxc.png").size)
                ImageDraw.Draw(mask_im).ellipse((0, 0, width, height), fill = 255)
                im.paste(Image.open('avatars/avatar_profile_zxc.png'), (avatar_x, avatar_y), mask_im)

                пользователь_name = f"{пользователь.name[:13]}" if len(пользователь.name) > 13 else f"{пользователь.name}"
                draw_text_with_offset(im, пользователь_name, 412, 194.26, font_size=32)

                im.save(f'out/warn_{inter.author.id}.png')

                await inter.response.edit_message(attachments = None, file = disnake.File(f'out/warn_{inter.author.id}.png'), view = ActionWarns())

            if custom_id == 'staff_warns_action':
                im = Image.open(f'action_zxc/staff_warn.png')

                draw_text_with_offset(im, str(day), 710, 76, font_size=32)
                draw_text_with_offset(im, str(time), 708, 120, font_size=96)

                width = 110
                height = 110
                avatar_x = 137
                avatar_y = 139

                Image.open(requests.get(пользователь.display_avatar.url, stream = True).raw).resize((width, height)).save('avatars/avatar_profile_zxc.png')
                mask_im = Image.new("L", Image.open("avatars/avatar_profile_zxc.png").size)
                ImageDraw.Draw(mask_im).ellipse((0, 0, width, height), fill = 255)
                im.paste(Image.open('avatars/avatar_profile_zxc.png'), (avatar_x, avatar_y), mask_im)

                пользователь_name = f"{пользователь.name[:13]}" if len(пользователь.name) > 13 else f"{пользователь.name}"
                draw_text_with_offset(im, пользователь_name, 412, 194.26, font_size=32)

                im.save(f'out/staff_warn{inter.author.id}.png')

                await inter.response.edit_message(attachments = None, file = disnake.File(f'out/staff_warn{inter.author.id}.png'), view = ActionStaffWarns())

            if custom_id == "give_warn_staff_action":
                await inter.response.send_modal(title = "Выдать выговор", custom_id = "give_staff_warn_action", components = [
                    disnake.ui.TextInput(label="Причина",placeholder="Например: Плохо работал",custom_id = "Причина выговора",style=disnake.TextInputStyle.short, max_length=50)])
            if custom_id == "snyat_warn_staff_action":
                await inter.response.send_modal(title = "Снять выговор", custom_id = "snyat_staff_warn_action", components = [
                    disnake.ui.TextInput(label="Причина",placeholder="Например: Плохо работал",custom_id = "Причина выговора",style=disnake.TextInputStyle.short, max_length=50)])

            if custom_id == "warns_staff_list":
                db_target = cluster.zxc.target.find_one({'_id': str(inter.author.id)})
                group_choice = db_target['group']

                # Получаем данные пользователя
                user_doc = cluster.zxc.staff_warns.find_one({'_id': str(пользователь.id)})

                if not user_doc or group_choice not in user_doc.get("groups", {}):
                    # Инициализируем если нет данных
                    cluster.zxc.staff_warns.update_one(
                        {"_id": str(пользователь.id)},
                        {"$set": {f"groups.{group_choice}": {"warn_count": 0, "warns": []}}},
                        upsert=True
                    )
                    staff_warns = []
                else:
                    staff_warns = user_doc["groups"][group_choice].get("warns", [])

                embed = disnake.Embed(color=3092790)
                embed.set_author(name=f"История выговоров {пользователь} | {inter.guild.name}", icon_url=inter.guild.icon.url)
                embed.set_thumbnail(url=пользователь.display_avatar.url)
                if staff_warns == []:
                    embed.description = f"{пользователь.mention}, у **{пользователь.mention}** нету **выговоров** на ветке **{group_choice}**"
                    return await inter.send(embed=embed, ephemeral=True)

                embed.description = f"{''.join(staff_warns)}"
                embed.set_footer(text=f"Всего выговоров на ветке {group_choice}: {len(staff_warns)}")
                await inter.send(embed=embed, ephemeral=True)

            if custom_id == "give_warn_action":
                await inter.response.send_modal(title = "Выдать варн",custom_id = "warn_vidat",components=[
                    disnake.ui.TextInput(label="Причина варна",placeholder="Например: Оскорбление", custom_id = "Причина варна",style=disnake.TextInputStyle.short, max_length=50), 
                    disnake.ui.TextInput(label="🕖 Время варна",placeholder="Например: 10m или 10m",custom_id = "🕖 Время варна", style=disnake.TextInputStyle.short,min_length=1,max_length=4)])
            if custom_id == "snyat_warn_action":
                await inter.response.send_modal(title = "Снять варн",custom_id = "warn_snyat",components=[
                    disnake.ui.TextInput(label="Причина предупреждения",placeholder="Например: ошибка", custom_id = "Причина варн",style=disnake.TextInputStyle.short,max_length=50)])

        if "mute" in custom_id:
            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790)
                embed.set_author(name = "Мут", icon_url = inter.guild.icon.url)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.send(ephemeral = True, embed=embed)
            
            пользователь = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))
                
            if custom_id == "snyat_mute_action":
                await inter.response.send_modal(title = "Размут",custom_id = "mute_snyat", components=[
                    disnake.ui.TextInput(label="Причина", placeholder="Например: ошибка",custom_id = "Причина размута",style=disnake.TextInputStyle.short,max_length=50),
                    disnake.ui.TextInput(label="Выбор мута:", placeholder="Например: 1 - Текстовый, 2 - Голосовой",custom_id = "Выбор мута:",style=disnake.TextInputStyle.short,max_length=1)])
            
            if custom_id == 'mute_action':
                im = Image.open(f'action_zxc/mute.png')

                draw_text_with_offset(im, str(day), 710, 76, font_size=32)
                draw_text_with_offset(im, str(time), 708, 120, font_size=96)

                width = 110
                height = 110
                avatar_x = 137
                avatar_y = 139

                Image.open(requests.get(пользователь.display_avatar.url, stream = True).raw).resize((width, height)).save('avatars/avatar_profile_zxc.png')
                mask_im = Image.new("L", Image.open("avatars/avatar_profile_zxc.png").size)
                ImageDraw.Draw(mask_im).ellipse((0, 0, width, height), fill = 255)
                im.paste(Image.open('avatars/avatar_profile_zxc.png'), (avatar_x, avatar_y), mask_im)

                пользователь_name = f"{пользователь.name[:13]}" if len(пользователь.name) > 13 else f"{пользователь.name}"
                draw_text_with_offset(im, пользователь_name, 412, 194.26, font_size=32)

                im.save(f'out/mute{inter.author.id}.png')

                await inter.response.edit_message(attachments = None, file = disnake.File(f'out/mute{inter.author.id}.png'), view = ActionMuteChoice(self.bot, пользователь))

            if custom_id == "give_mute_action":
                im = Image.open(f'action_zxc/mute_choice.png')

                draw_text_with_offset(im, str(day), 710, 76, font_size=32)
                draw_text_with_offset(im, str(time), 708, 120, font_size=96)

                width = 110
                height = 110
                avatar_x = 137
                avatar_y = 139

                Image.open(requests.get(пользователь.display_avatar.url, stream = True).raw).resize((width, height)).save('avatars/avatar_profile_zxc.png')
                mask_im = Image.new("L", Image.open("avatars/avatar_profile_zxc.png").size)
                ImageDraw.Draw(mask_im).ellipse((0, 0, width, height), fill = 255)
                im.paste(Image.open('avatars/avatar_profile_zxc.png'), (avatar_x, avatar_y), mask_im)

                пользователь_name = f"{пользователь.name[:13]}" if len(пользователь.name) > 13 else f"{пользователь.name}"
                draw_text_with_offset(im, пользователь_name, 412, 194.26, font_size=32)

                im.save(f'out/mute_choice{inter.author.id}.png')

                await inter.response.edit_message(attachments = None, file = disnake.File(f'out/mute_choice{inter.author.id}.png'), view = ActionMuteView())
        
            if inter.component.custom_id == 'textmute_action':
                await inter.response.send_modal(title="Текстовый мут", custom_id = "text_mute_vidat", components=[
                    disnake.ui.TextInput(label="Причина", placeholder="Например: Оскорбление", custom_id = "Причина текстового мута",style=disnake.TextInputStyle.short,max_length=50,),
                    disnake.ui.TextInput(label="🕖 Время текстового мута",placeholder="Например: 10m или 10m",custom_id = "🕖 Время текстового мута",style=disnake.TextInputStyle.short,min_length=1,max_length=3)])

            if inter.component.custom_id == 'voicemute_action':
                await inter.response.send_modal(title = "Голосовой мут", custom_id = "voice_mute_vidat", components=[
                    disnake.ui.TextInput(label="Причина",placeholder="Например: Оскорбление",custom_id = "Причина текстового мута",style=disnake.TextInputStyle.short,max_length=50,),
                    disnake.ui.TextInput(label="🕖 Время голосового мута",placeholder="Например: 10m или 10m",custom_id = "🕖 Время голосового мута",style=disnake.TextInputStyle.short,min_length=1,max_length=3)])

        if "ban" in custom_id:
            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790)
                embed.set_author(name = "Бан", icon_url = inter.guild.icon.url)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.send(ephemeral = True, embed=embed)
            
            пользователь = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))

            if custom_id == 'ban_action':
                im = Image.open(f'action_zxc/ban.png')

                draw_text_with_offset(im, str(day), 710, 76, font_size=32)
                draw_text_with_offset(im, str(time), 708, 120, font_size=96)

                width = 110
                height = 110
                avatar_x = 137
                avatar_y = 139

                Image.open(requests.get(пользователь.display_avatar.url, stream = True).raw).resize((width, height)).save('avatars/avatar_profile_zxc.png')
                mask_im = Image.new("L", Image.open("avatars/avatar_profile_zxc.png").size)
                ImageDraw.Draw(mask_im).ellipse((0, 0, width, height), fill = 255)
                im.paste(Image.open('avatars/avatar_profile_zxc.png'), (avatar_x, avatar_y), mask_im)

                пользователь_name = f"{пользователь.name[:13]}" if len(пользователь.name) > 13 else f"{пользователь.name}"
                draw_text_with_offset(im, пользователь_name, 412, 194.26, font_size=32)

                im.save(f'out/ban{inter.author.id}.png')

                await inter.response.edit_message(attachments = None, file = disnake.File(f'out/ban{inter.author.id}.png'), view = ActionMuteBan())

            if custom_id == 'give_ban_action':
                await inter.response.send_modal(title = "Бан", custom_id = "ban_vidat",components=[
                    disnake.ui.TextInput(label="Причина",placeholder="Например: Оскорбление",custom_id = "Причина бана",style=disnake.TextInputStyle.short,max_length=50,),
                    disnake.ui.TextInput(label="🕖 Время бана",placeholder="Например: 10m или 10m",custom_id = "🕖 Время бана", style=disnake.TextInputStyle.short,min_length=1,max_length=4)])

            if custom_id == 'snyat_ban_action':
                await inter.response.send_modal(title = "Разбан",custom_id = "ban_snyat",components=[
                    disnake.ui.TextInput(label="Причина",placeholder="Например: ошибка",custom_id = "Причина снятия",style=disnake.TextInputStyle.short,max_length=50)])
                
        if "creative_ban" in custom_id:
            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790)
                embed.set_author(name = "Бан", icon_url = inter.guild.icon.url)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.send(ephemeral = True, embed=embed)
            
            пользователь = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))

            if custom_id == 'creative_ban_action':
                im = Image.open(f'action_zxc/ban.png')

                draw_text_with_offset(im, str(day), 710, 76, font_size=32)
                draw_text_with_offset(im, str(time), 708, 120, font_size=96)

                width = 110
                height = 110
                avatar_x = 137
                avatar_y = 139

                Image.open(requests.get(пользователь.display_avatar.url, stream = True).raw).resize((width, height)).save('avatars/avatar_profile_zxc.png')
                mask_im = Image.new("L", Image.open("avatars/avatar_profile_zxc.png").size)
                ImageDraw.Draw(mask_im).ellipse((0, 0, width, height), fill = 255)
                im.paste(Image.open('avatars/avatar_profile_zxc.png'), (avatar_x, avatar_y), mask_im)

                пользователь_name = f"{пользователь.name[:13]}" if len(пользователь.name) > 13 else f"{пользователь.name}"
                draw_text_with_offset(im, пользователь_name, 412, 194.26, font_size=32)

                im.save(f'out/ban{inter.author.id}.png')

                await inter.response.edit_message(attachments = None, file = disnake.File(f'out/ban{inter.author.id}.png'), view = ActionCreativeBan())

            if custom_id == 'creative_ban_give_action':
                await inter.response.send_modal(title = "Креатив бан", custom_id = "creative_ban_vidat",components=[
                    disnake.ui.TextInput(label="Причина",placeholder="Например: Оскорбление",custom_id = "Причина бана",style=disnake.TextInputStyle.short,max_length=50,),
                    disnake.ui.TextInput(label="🕖 Время бана",placeholder="Например: 10m или 10m",custom_id = "🕖 Время бана", style=disnake.TextInputStyle.short,min_length=1,max_length=4)])

            if custom_id == 'creative_ban_snyat_action':
                await inter.response.send_modal(title = "Разбан",custom_id = "creative_ban_snyat",components=[
                    disnake.ui.TextInput(label="Причина",placeholder="Например: ошибка",custom_id = "Причина снятия",style=disnake.TextInputStyle.short,max_length=50)])
                
        if "ban_event" in custom_id:
            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790)
                embed.set_author(name = "Бан", icon_url = inter.guild.icon.url)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.send(ephemeral = True, embed=embed)
            
            пользователь = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))

            if custom_id == 'ban_event_action':
                im = Image.open(f'action_zxc/ban.png')

                draw_text_with_offset(im, str(day), 710, 76, font_size=32)
                draw_text_with_offset(im, str(time), 708, 120, font_size=96)

                width = 110
                height = 110
                avatar_x = 137
                avatar_y = 139

                Image.open(requests.get(пользователь.display_avatar.url, stream = True).raw).resize((width, height)).save('avatars/avatar_profile_zxc.png')
                mask_im = Image.new("L", Image.open("avatars/avatar_profile_zxc.png").size)
                ImageDraw.Draw(mask_im).ellipse((0, 0, width, height), fill = 255)
                im.paste(Image.open('avatars/avatar_profile_zxc.png'), (avatar_x, avatar_y), mask_im)

                пользователь_name = f"{пользователь.name[:13]}" if len(пользователь.name) > 13 else f"{пользователь.name}"
                draw_text_with_offset(im, пользователь_name, 412, 194.26, font_size=32)

                im.save(f'out/ban{inter.author.id}.png')

                await inter.response.edit_message(attachments = None, file = disnake.File(f'out/ban{inter.author.id}.png'), view = ActionEventBan())

            if custom_id == 'ban_event_vidat':
                await inter.response.send_modal(title = "Ивент бан", custom_id = "ban_event_vidat",components=[
                    disnake.ui.TextInput(label="Причина",placeholder="Например: Оскорбление",custom_id = "Причина ивент бана",style=disnake.TextInputStyle.short,max_length=50,),
                    disnake.ui.TextInput(label="🕖 Время ивент бана",placeholder="Например: 10m или 10m",custom_id = "🕖 Время ивент бана", style=disnake.TextInputStyle.short,min_length=1,max_length=4)])

            if custom_id == 'ban_event_snyat':
                await inter.response.send_modal(title = "Ивент разбан",custom_id = "ban_event_snyat",components=[
                    disnake.ui.TextInput(label="Причина",placeholder="Например: ошибка",custom_id = "Причина снятия",style=disnake.TextInputStyle.short,max_length=50)])
                
        if "ban_close" in custom_id:
            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790)
                embed.set_author(name = "Бан", icon_url = inter.guild.icon.url)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.send(ephemeral = True, embed=embed)
            
            пользователь = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))

            if custom_id == 'ban_close_action':

                im = Image.open(f'action_zxc/ban.png')

                draw_text_with_offset(im, str(day), 710, 76, font_size=32)
                draw_text_with_offset(im, str(time), 708, 120, font_size=96)

                width = 110
                height = 110
                avatar_x = 137
                avatar_y = 139

                Image.open(requests.get(пользователь.display_avatar.url, stream = True).raw).resize((width, height)).save('avatars/avatar_profile_zxc.png')
                mask_im = Image.new("L", Image.open("avatars/avatar_profile_zxc.png").size)
                ImageDraw.Draw(mask_im).ellipse((0, 0, width, height), fill = 255)
                im.paste(Image.open('avatars/avatar_profile_zxc.png'), (avatar_x, avatar_y), mask_im)

                пользователь_name = f"{пользователь.name[:13]}" if len(пользователь.name) > 13 else f"{пользователь.name}"
                draw_text_with_offset(im, пользователь_name, 412, 194.26, font_size=32)

                im.save(f'out/ban{inter.author.id}.png')

                await inter.response.edit_message(attachments = None, file = disnake.File(f'out/ban{inter.author.id}.png'), view = ActionCloseBan())

            if custom_id == 'ban_close_vidat':
                await inter.response.send_modal(title = "Клоз бан", custom_id = "ban_close_vidat",components=[
                    disnake.ui.TextInput(label="Причина",placeholder="Например: Оскорбление",custom_id = "Причина клоз бана",style=disnake.TextInputStyle.short,max_length=50,),
                    disnake.ui.TextInput(label="🕖 Время клоз бана",placeholder="Например: 10m или 10m",custom_id = "🕖 Время клоз бана", style=disnake.TextInputStyle.short,min_length=1,max_length=4)])

            if custom_id == 'ban_close_snyat':
                await inter.response.send_modal(title = "Клоз разбан",custom_id = "ban_close_snyat",components=[
                    disnake.ui.TextInput(label="Причина",placeholder="Например: ошибка",custom_id = "Причина снятия",style=disnake.TextInputStyle.short,max_length=50)])

    @commands.Cog.listener()
    async def on_modal_submit(self, inter):
        custom_id = inter.custom_id

        if "staff_warn" in custom_id:
            member = disnake.utils.get(inter.guild.members, id=int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))

            for key, value in inter.text_values.items():
                reason = value

            db_target = cluster.zxc.target.find_one({'_id': str(inter.author.id)})
            group_choice = db_target['group']

            # Инициализируем документ пользователя если его нет
            if cluster.zxc.staff_warns.count_documents({"_id": str(member.id)}) == 0:
                cluster.zxc.staff_warns.insert_one({
                    "_id": str(member.id), 
                    "groups": {}
                })

            # Инициализируем группу если её нет
            user_doc = cluster.zxc.staff_warns.find_one({"_id": str(member.id)})
            if group_choice not in user_doc.get("groups", {}):
                cluster.zxc.staff_warns.update_one(
                    {"_id": str(member.id)},
                    {"$set": {f"groups.{group_choice}": {"warn_count": 0, "warns": []}}}
                )

            if custom_id == 'snyat_staff_warn_action':
                highest_role_user1 = get_effective_top_role(inter.author)
                highest_role_user2 = get_effective_top_role(member)

                if highest_role_user1.position < highest_role_user2.position:
                    return await inter.send(f"Роль пользователя {member.mention} выше, чем роль пользователя {inter.author.mention}.", ephemeral=True)
                
                # Получаем данные группы
                group_data = cluster.zxc.staff_warns.find_one({"_id": str(member.id)})["groups"].get(group_choice, {"warns": []})
                staff_warns = group_data.get("warns", [])

                if len(staff_warns) < 1:
                    embed = disnake.Embed(
                        title='Снятие выговора',
                        description=f'{inter.author.mention}, **У** этого пользователя нет **выговоров!** на ветке {group_choice}',
                        color=disnake.Color.red()
                    )
                    embed.set_footer(text=inter.author, icon_url=inter.author.display_avatar.url)
                    return await inter.send(embed=embed, ephemeral=True)
                else:
                    # Уменьшаем счетчик и удаляем последний выговор
                    cluster.zxc.staff_warns.update_one(
                        {"_id": str(member.id)},
                        {
                            "$inc": {f"groups.{group_choice}.warn_count": -1},
                            "$pop": {f"groups.{group_choice}.warns": 1}  # Удаляем последний элемент
                        }
                    )

                    last_warn = staff_warns[-1]  # Берем последний элемент для сообщения
                    embed = disnake.Embed(
                        title='Снятие выговора',
                        description=f'**Вы** успешно сняли **выговор** {member.mention} по причине {last_warn} на ветке {group_choice}',
                        color=3092790
                    )
                    embed.set_thumbnail(url=inter.author.display_avatar.url)
                    return await inter.send(embed=embed, ephemeral=True)

            if custom_id == 'give_staff_warn_action':
                highest_role_user1 = get_effective_top_role(inter.author)
                highest_role_user2 = get_effective_top_role(member)

                if highest_role_user1.position < highest_role_user2.position:
                    return await inter.send(f"Роль пользователя {member.mention} выше, чем роль пользователя {inter.author.mention}.", ephemeral=True)

                # Получаем текущее количество выговоров
                current_warn_count = cluster.zxc.staff_warns.find_one({"_id": str(member.id)})["groups"][group_choice]["warn_count"]
                new_warn_number = current_warn_count + 1

                # Добавляем выговор
                cluster.zxc.staff_warns.update_one(
                    {"_id": str(member.id)},
                    {
                        "$push": {f"groups.{group_choice}.warns": f"**{new_warn_number})** {reason}\n"},
                        "$inc": {f"groups.{group_choice}.warn_count": 1}
                    }
                )

                # Проверяем количество выговоров после добавления
                updated_warn_count = new_warn_number

                if updated_warn_count >= 3:
                    embed = disnake.Embed(
                        description=f'{member.mention}, **Вы** были сняты с **ролей**, так как вы получили **3 выговора** на ветке {group_choice}',
                        color=3092790
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.set_author(name=f"Выговор на ветке {group_choice}", icon_url=inter.guild.icon.url)
                    embed.add_field(name=f"> Управляющий", value=f"{inter.author.mention} | **ID:** {inter.author.id}")
                    await member.send(embed=embed)

                    try:
                        await member.remove_roles(disnake.utils.get(inter.guild.roles, id=config[group_choice]))
                        await member.remove_roles(config['staff_role'])
                    except:
                        pass
                    
                    embed = disnake.Embed(
                        description=f'{inter.author.mention}, **Вы** успешно выдали **последний** выговор, {member.mention} был снят со **всех ролей** на ветке {group_choice}',
                        color=3092790
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.set_author(name=f"Выговор на ветке {group_choice}", icon_url=inter.guild.icon.url)
                    return await inter.send(embed=embed, ephemeral=True)

                embed = disnake.Embed(
                    description=f'{member.mention}, **Вы** успешно выдали **выговор** {member.mention} по причине {reason} на ветке {group_choice}',
                    color=3092790
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_author(name=f"Выговор на ветке {group_choice}", icon_url=inter.guild.icon.url)
                await inter.send(embed=embed, ephemeral=True)

                # Отправляем уведомление пользователю
                try:
                    embed = disnake.Embed(
                        description=f'{member.mention}, **Вам** выдали **выговор** по причине {reason} на ветке {group_choice}',
                        color=3092790
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.set_author(name=f"Выговор на ветке {group_choice}", icon_url=inter.guild.icon.url)
                    embed.add_field(name=f"> Управляющий", value=f"{inter.author.mention} | **ID:** {inter.author.id}")
                    await member.send(embed=embed)
                except:
                    pass
                
                # Отправляем в лог канал
                embed = disnake.Embed(color=3092790)
                embed.set_author(name=f"Выговор на ветке {group_choice}", icon_url=inter.guild.icon.url)
                embed.add_field(name=f"> Управляющий", value=f"{inter.author.mention} | **ID:** {inter.author.id}")
                embed.add_field(name=f"> Пользователь", value=f"{member.mention} | **ID:** {member.id}")
                embed.add_field(name=f"> Причина", value=f"```yaml\n{reason}```")

                # Отправляем уведомление в соответствующий канал
                if inter.guild.get_role(support) in member.roles:
                    await self.bot.get_channel(1183884244922159134).send(content=f"<@&{config['support_admin']}>", embed=embed)
                elif inter.guild.get_role(moderator) in member.roles:
                    await self.bot.get_channel(1183884244922159134).send(content=f"<@&{config['moderator_admin']}>", embed=embed)
                elif inter.guild.get_role(tribunemod) in member.roles:
                    await self.bot.get_channel(1183884244922159134).send(content=f"<@&{config['tribunemod_admin']}>", embed=embed)
                elif inter.guild.get_role(eventer) in member.roles:
                    await self.bot.get_channel(1183884244922159134).send(content=f"<@&{config['event_admin']}>", embed=embed)
                elif inter.guild.get_role(closer) in member.roles:
                    await self.bot.get_channel(1183884244922159134).send(content=f"<@&{config['close_admin']}>", embed=embed)
                else:
                    await self.bot.get_channel(1183884244922159134).send(embed=embed)

        if custom_id[-5:] == 'snyat':
            emb = disnake.Embed(color = 3092790)
            emb.set_author(name = "Снять наказание", icon_url = inter.guild.icon.url)
            emb.set_thumbnail(url = inter.author.display_avatar.url)

            for key, value in inter.text_values.items():
                reason = value

            пользователь = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))

            embed = disnake.Embed(color = 3092790)
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            embed.set_author(name = "Снять наказание", icon_url = inter.guild.icon.url)
            embed.add_field(name = f"> Пользователь", value = f"{пользователь.mention} | **ID:** {пользователь.id}")
            embed.add_field(name = f"> Модератор", value = f"{inter.author.mention} | **ID:** {inter.author.id}")
            embed.add_field(name = f"> Причина", value = f"```yaml\n{reason}```")

            if custom_id == 'mute_snyat':
                channel_id = 1413214490455048252

                id = 0
                for key, value in inter.text_values.items():
                    if id == 0:
                        reason = value
                    if id == 1:
                        mute_choice = value
                    id += 1

                embed.title = "Снять мут"
                emb.description = f"{inter.author.mention}, **Вы** успешно сняли мут {пользователь.mention}"
        
                role = inter.guild.get_role(config['tmute'])
                role1 = inter.guild.get_role(config['vmute'])
                
                if int(mute_choice) == 1:
                    await пользователь.remove_roles(role)
                else:
                    await пользователь.remove_roles(role1)

                try: 
                    await пользователь.move_to(пользователь.voice.channel)
                except: 
                    pass
                
                cluster.zxc.action.delete_one({'_id': str(пользователь.id)})

            if custom_id == 'ban_snyat':
                channel_id = 1413214508071125002

                embed.set_author(name = "Снять бан", icon_url = inter.guild.icon.url)
                emb.description = f"{inter.author.mention}, **Вы** успешно сняли бан {пользователь.mention}" 

                role = disnake.utils.get(inter.guild.roles, id = config['ban'])
                await пользователь.remove_roles(role)

                # await пользователь.add_roles(inter.guild.get_role(1328044273765187666))

                cluster.zxc.action.delete_one({'_id': str(пользователь.id)})
                
            if custom_id == 'creative_ban_snyat':
                channel_id = 1413215555011346622

                embed.set_author(name = "Снять бан", icon_url = inter.guild.icon.url)
                emb.description = f"{inter.author.mention}, **Вы** успешно сняли бан {пользователь.mention}" 

                role = disnake.utils.get(inter.guild.roles, id = config['creative_ban'])
                await пользователь.remove_roles(role)

                # await пользователь.add_roles(inter.guild.get_role(1328044273765187666))

                cluster.zxc.action.delete_one({'_id': str(пользователь.id)})
                
            if custom_id == 'ban_event_snyat':
                channel_id = 1413215476753895567

                embed.set_author(name = "Снять ивент бан", icon_url = inter.guild.icon.url)
                emb.description = f"{inter.author.mention}, **Вы** успешно сняли ивент бан {пользователь.mention}" 

                role = disnake.utils.get(inter.guild.roles, id = config['event_ban'])
                await пользователь.remove_roles(role)

                # await пользователь.add_roles(inter.guild.get_role(1328044273765187666))

                cluster.zxc.action.delete_one({'_id': str(пользователь.id)})

            if custom_id == 'ban_close_snyat':
                channel_id = 1421189874198904892

                embed.set_author(name = "Снять клоз бан", icon_url = inter.guild.icon.url)
                emb.description = f"{inter.author.mention}, **Вы** успешно сняли клоз бан {пользователь.mention}" 

                role = disnake.utils.get(inter.guild.roles, id = config['close_ban'])
                await пользователь.remove_roles(role)

                # await пользователь.add_roles(inter.guild.get_role(1328044273765187666))

                cluster.zxc.action.delete_one({'_id': str(пользователь.id)})

            if custom_id == 'warn_snyat':
                channel_id = 1413214714858573956

                embed.set_author(name = "Снять варн", icon_url = inter.guild.icon.url)
                emb.description = f"{inter.author.mention}, **Вы** успешно сняли варн {пользователь.mention}" 

            if custom_id == 'otpysk_snyat':
                channel_id = 1406315258062045215

                emb = disnake.Embed(color = 3092790)
                emb.set_author(name = "Снять отпуск", icon_url = inter.guild.icon.url)
                emb.description = f"{inter.author.mention}, **Вы** успешно сняли отпуск {пользователь.mention}" 

            await self.bot.get_channel(channel_id).send(embed=embed)
            
            await inter.send(embed = emb, ephemeral = True)

        if custom_id[-5:] == 'vidat':
            if not inter.message.content == inter.author.mention:
                embed.description = f"{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**"
                return await inter.send(ephemeral = True, embed=embed)

            id = 0
            for key, value in inter.text_values.items():
                if id == 0:
                    reason = value
                else:
                    time = value
                id += 1

            member = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))

            highest_role_user1 = get_effective_top_role(inter.author)
            highest_role_user2 = get_effective_top_role(member)

            if highest_role_user1.position < highest_role_user2.position:
                return await inter.send(f"Роль пользователя {member.mention} выше, чем роль пользователя {inter.author.mention}.", ephemeral=True)

            if custom_id in BAN_LIMITED_CUSTOM_IDS:
                can_issue_ban, issued_today = enforce_daily_ban_limit(
                    inter.author.id,
                    member.id,
                    BAN_LIMITED_CUSTOM_IDS[custom_id],
                    reason,
                    inter.guild.id
                )
                if not can_issue_ban:
                    limit_embed = disnake.Embed(
                        description=(
                            f"{inter.author.mention}, вы уже выдали **{issued_today}** бан(ов) сегодня.\n"
                            f"Лимит на сутки — **{BAN_LIMIT_PER_DAY}**. Дождитесь следующего дня, чтобы выдать новый бан."
                        ),
                        color=disnake.Color.red()
                    )
                    limit_embed.set_footer(text="Счётчик обнуляется ежедневно в 00:00 (UTC)")
                    return await inter.send(embed=limit_embed, ephemeral=True)

            if cluster.zxc.history_punishment.count_documents({"_id": str(member.id)}) == 0: 
                cluster.zxc.history_punishment.insert_one({"_id": str(member.id), "warns": 0, "mutes": 0, "bans": 0, "eventban": 0})

            if cluster.zxc.history_add.count_documents({"_id": str(member.id)}) == 0: 
                cluster.zxc.history_add.insert_one({"_id": str(member.id), "tip_data": [], "punishment": [], "moderator": []})

            if cluster.zxc.balls.count_documents({"_id": str(inter.author.id)}) == 0: 
                cluster.zxc.balls.insert_one({"_id": str(inter.author.id), "balls": 0, "warns": 0, "mutes": 0, "bans": 0})
            
            try:
                if time[-1] == 'м':
                    num = 'минут'
                    time1 = int(time[:-1]) * 60
                    new_date = datetime.now().replace(microsecond=0) + timedelta(seconds=time1)
                elif time[-1] == 'ч':
                    num = 'часов'
                    time1 = int(time[:-1]) * 60 * 60
                    new_date = datetime.now().replace(microsecond=0) + timedelta(seconds=time1)
                elif time[-1] == 'д':
                    num = 'дней'
                    time1 = int(time[:-1]) * 60 * 60 * 24
                    new_date = datetime.now().replace(microsecond=0) + timedelta(seconds=time1)
                elif time[-1] == 'm':
                    num = 'минут'
                    time1 = int(time[:-1]) * 60
                    new_date = datetime.now().replace(microsecond=0) + timedelta(seconds=time1)
                elif time[-1] == 'h':
                    num = 'часов'
                    time1 = int(time[:-1]) * 60 * 60
                    new_date = datetime.now().replace(microsecond=0) + timedelta(seconds=time1)
                elif time[-1] == 'd':
                    num = 'дней'
                    time1 = int(time[:-1]) * 60 * 60 * 24
                    new_date = datetime.now().replace(microsecond=0) + timedelta(seconds=time1)
            except Exception as e:
                print(e)

            emb = disnake.Embed(color = 3092790).set_thumbnail(url = inter.author.display_avatar.url)

            embed = disnake.Embed(color = 3092790).set_thumbnail(url = inter.author.display_avatar.url)
            embed.add_field(name='> ・Причина', value = f'```yaml\n{reason}```', inline = False)
            try:
                embed.add_field(name='> ・Время', value = f'```yaml\n{time[:-1]} {num}```')
            except:
                pass
            embed.set_footer(text = f'Выполнил(а) команду {inter.author}', icon_url = inter.author.display_avatar.url)

            general = len(cluster.zxc.history_add.find_one({'_id': str(member.id)})['tip_data']) + 1

            input = datetime.now()
            data = int(input.timestamp())
            try:
                cluster.zxc.history_add.update_one({"_id": str(member.id)}, {"$push": {"punishment": f"{reason} <:online:1109846973378470050> {time[:-1]} {num}"}})
                cluster.zxc.history_add.update_one({"_id": str(member.id)}, {"$push": {"moderator": f"{inter.author.id}"}})
            except:
                embed.description = f"**{inter.author.mention}** Введите время в формате **30d,30h,30m** а не как вы ввели: __**{time}**__"
                return await inter.send(embed=embed, ephemeral = True)

            def update_stat(filter_dict):
                try:
                    cluster.zxc.online_stats.update_one(
                        filter_dict,
                        {"$inc": {"duration": 1}},  # увеличиваем счётчик на 1
                        upsert=True
                    )
                except Exception as e:
                    print("Error updating stat:", e)

            # Предполагаем, что day_start определён следующим образом:
            now = datetime.utcnow()
            day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

            time_punishment = f"{time[:-1]} {num}"
            current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            log_action_key = None

            if custom_id == 'text_mute_vidat':
                channel_id = 1413214490455048252

                punishment = 'Текстовый мут'
                log_action_key = 'text_mute'

                update_stat({"user_id": str(inter.author.id), "category": "mutes", "period": "day", "date": day_start})
                cluster.zxc.balls.update_one({"_id": str(inter.author.id)}, {"$inc": {"mutes": 2}})
                
                # Добавляем подробную запись в историю наказаний через $push
                cluster.zxc.history_punishment.update_one(
                    {"_id": str(member.id)},
                    {"$push": {"punishments": {
                        "punishment": punishment,
                        "reason": reason,
                        "time_punishment": time_punishment,
                        "date": current_date,
                        "moderator": str(inter.author.id)
                    }}},
                    upsert=True
                )
                
                cluster.zxc.history_add.update_one(
                    {"_id": str(member.id)},
                    {"$push": {"tip_data": f"#{general} <:mute:1109833278376120383> <t:{data}:F>"}}
                )
                role_id = config['tmute']

                desc = f'{inter.author.mention}, **Вы** успешно **замутили**\n{member.mention}!'
                embed.set_author(name=punishment, icon_url=inter.guild.icon.url)
                emb.set_author(name=punishment, icon_url=inter.guild.icon.url)
                cluster.zxc.action.update_one(
                    {'_id': str(member.id)},
                    {'$set': {'time': new_date, 'role': role_id, 'reason': reason, 'type': punishment}},
                    upsert=True
                )
            
            elif custom_id == 'voice_mute_vidat':
                channel_id = 1413214490455048252

                punishment = "Голосовой мут"
                log_action_key = 'voice_mute'

                update_stat({"user_id": str(inter.author.id), "category": "mutes", "period": "day", "date": day_start})
                cluster.zxc.balls.update_one({"_id": str(inter.author.id)}, {"$inc": {"mutes": 2}})
                
                cluster.zxc.history_punishment.update_one(
                    {"_id": str(member.id)},
                    {"$push": {"punishments": {
                        "punishment": punishment,
                        "reason": reason,
                        "time_punishment": time_punishment,
                        "date": current_date,
                        "moderator": str(inter.author.id)
                    }}},
                    upsert=True
                )
                
                cluster.zxc.history_add.update_one(
                    {"_id": str(member.id)},
                    {"$push": {"tip_data": f"#{general} <:mute:1109833278376120383> <t:{data}:F>"}}
                )
                role_id = config['vmute']

                desc = f'{inter.author.mention}, **Вы** успешно **замутили**\n{member.mention}!'
                embed.set_author(name=punishment, icon_url=inter.guild.icon.url)
                emb.set_author(name=punishment, icon_url=inter.guild.icon.url)
                
                try:
                    await member.move_to(None)
                except Exception as e:
                    print(e)

                cluster.zxc.action.update_one(
                    {'_id': str(member.id)},
                    {'$set': {'time': new_date, 'role': role_id, 'reason': reason, 'type': punishment}},
                    upsert=True
                )
            
            elif custom_id == 'ban_vidat':
                channel_id = 1413214508071125002

                punishment = "Бан"
                log_action_key = 'ban'

                update_stat({"user_id": str(inter.author.id), "category": "bans", "period": "day", "date": day_start})
                cluster.zxc.balls.update_one({"_id": str(inter.author.id)}, {"$inc": {"bans": 3}})
                
                cluster.zxc.history_punishment.update_one(
                    {"_id": str(member.id)},
                    {"$push": {"punishments": {
                        "punishment": punishment,
                        "reason": reason,
                        "date": current_date,
                        "time_punishment": time_punishment,
                        "moderator": str(inter.author.id)
                    }}},
                    upsert=True
                )
                
                cluster.zxc.history_add.update_one(
                    {"_id": str(member.id)},
                    {"$push": {"tip_data": f"#{general} <:unavailable:1109833288945782854> <t:{data}:F>"}}
                )
                role_id = config['ban']
                await member.move_to(None)

                desc = f'{inter.author.mention}, **Вы** успешно выдали **{punishment}**\n{member.mention}!'
                embed.set_author(name=punishment, icon_url=inter.guild.icon.url)
                emb.set_author(name=punishment, icon_url=inter.guild.icon.url)
                cluster.zxc.action.update_one(
                    {'_id': str(member.id)},
                    {'$set': {'time': new_date, 'role': role_id, 'type': punishment}},
                    upsert=True
                )
                await member.remove_roles(disnake.utils.get(inter.guild.roles, id=config['female']))
                await member.remove_roles(disnake.utils.get(inter.guild.roles, id=config['male']))

            elif custom_id == 'ban_event_vidat':
                channel_id = 1413215476753895567

                punishment = "Ивент Бан"
                log_action_key = 'event_ban'

                update_stat({"user_id": str(inter.author.id), "category": "event_bans", "period": "day", "date": day_start})
                cluster.zxc.balls.update_one({"_id": str(inter.author.id)}, {"$inc": {"bans": 5}})
                
                cluster.zxc.history_punishment.update_one(
                    {"_id": str(member.id)},
                    {"$push": {"punishments": {
                        "punishment": punishment,
                        "reason": reason,
                        "date": current_date,
                        "time_punishment": time_punishment,
                        "moderator": str(inter.author.id)
                    }}},
                    upsert=True
                )
                
                cluster.zxc.history_add.update_one(
                    {"_id": str(member.id)},
                    {"$push": {"tip_data": f"#{general} <:unavailable:1109833288945782854> <t:{data}:F>"}}
                )
                role_id = config['event_ban']
                await member.move_to(None)

                desc = f'{inter.author.mention}, **Вы** успешно выдали **{punishment}**\n{member.mention}!'
                embed.set_author(name=punishment, icon_url=inter.guild.icon.url)
                emb.set_author(name=punishment, icon_url=inter.guild.icon.url)
                cluster.zxc.action.update_one(
                    {'_id': str(member.id)},
                    {'$set': {'time': new_date, 'role': role_id, 'type': punishment}},
                    upsert=True
                )

            elif custom_id == 'ban_close_vidat':
                channel_id = 1421189874198904892

                punishment = "Клоз Бан"
                log_action_key = 'close_ban'

                update_stat({"user_id": str(inter.author.id), "category": "close_bans", "period": "day", "date": day_start})
                cluster.zxc.balls.update_one({"_id": str(inter.author.id)}, {"$inc": {"bans": 5}})
                
                cluster.zxc.history_punishment.update_one(
                    {"_id": str(member.id)},
                    {"$push": {"punishments": {
                        "punishment": punishment,
                        "reason": reason,
                        "date": current_date,
                        "time_punishment": time_punishment,
                        "moderator": str(inter.author.id)
                    }}},
                    upsert=True
                )
                
                cluster.zxc.history_add.update_one(
                    {"_id": str(member.id)},
                    {"$push": {"tip_data": f"#{general} <:unavailable:1109833288945782854> <t:{data}:F>"}}
                )
                role_id = config['close_ban']
                await member.move_to(None)

                desc = f'{inter.author.mention}, **Вы** успешно выдали **{punishment}**\n{member.mention}!'
                embed.set_author(name=punishment, icon_url=inter.guild.icon.url)
                emb.set_author(name=punishment, icon_url=inter.guild.icon.url)
                cluster.zxc.action.update_one(
                    {'_id': str(member.id)},
                    {'$set': {'time': new_date, 'role': role_id, 'type': punishment}},
                    upsert=True
                )
                
            elif custom_id == 'creative_ban_vidat':
                channel_id = 1413215555011346622

                punishment = "Креатив Бан"
                log_action_key = 'creative_ban'

                update_stat({"user_id": str(inter.author.id), "category": "bans", "period": "day", "date": day_start})
                cluster.zxc.balls.update_one({"_id": str(inter.author.id)}, {"$inc": {"bans": 5}})
                
                cluster.zxc.history_punishment.update_one(
                    {"_id": str(member.id)},
                    {"$push": {"punishments": {
                        "punishment": punishment,
                        "reason": reason,
                        "date": current_date,
                        "time_punishment": time_punishment,
                        "moderator": str(inter.author.id)
                    }}},
                    upsert=True
                )
                
                cluster.zxc.history_add.update_one(
                    {"_id": str(member.id)},
                    {"$push": {"tip_data": f"#{general} <:unavailable:1109833288945782854> <t:{data}:F>"}}
                )
                role_id = config['creative_ban']
                await member.move_to(None)

                desc = f'{inter.author.mention}, **Вы** успешно выдали **{punishment}**\n{member.mention}!'
                embed.set_author(name=punishment, icon_url=inter.guild.icon.url)
                emb.set_author(name=punishment, icon_url=inter.guild.icon.url)
                cluster.zxc.action.update_one(
                    {'_id': str(member.id)},
                    {'$set': {'time': new_date, 'role': role_id, 'type': punishment}},
                    upsert=True
                )
            
            elif custom_id == 'warn_vidat':
                channel_id = 1413214714858573956

                punishment = "Варн"

                update_stat({"user_id": str(inter.author.id), "category": "warns", "period": "day", "date": day_start})
                cluster.zxc.balls.update_one({"_id": str(inter.author.id)}, {"$inc": {"warns": 1}})


                cluster.zxc.history_punishment.update_one(
                    {"_id": str(member.id)},
                    {"$push": {"punishments": {
                        "punishment": punishment,
                        "reason": reason,
                        "date": current_date,
                        "time_punishment": time_punishment,
                        "moderator": str(inter.author.id)
                    }}},
                    upsert=True
                )

                cluster.zxc.history_punishment.update_one(
                    {"_id": str(member.id)},
                    {"$inc": {"warns": 1}},
                    upsert=True
                )

                cluster.zxc.history_add.update_one(
                    {"_id": str(member.id)},
                    {"$push": {"tip_data": f"#{general} <:warn:1109833262001561680> <t:{data}:F>"}}
                )

                desc = f'{inter.author.mention}, **Вы** успешно выдали **{punishment}** \n{member.mention}!'
                embed.set_author(name=punishment, icon_url=inter.guild.icon.url)
                emb.set_author(name=punishment, icon_url=inter.guild.icon.url)
                # Дополнительная логика для варнов
                if cluster.zxc.action_warns.count_documents({"_id": str(member.id)}) == 0:
                    cluster.zxc.action_warns.update_one({'_id': str(member.id)}, {'$set': {"warns": []}}, upsert=True)
                if cluster.zxc.history_punishment.find_one({'_id': str(member.id)})['warns'] == 1:
                    cluster.zxc.action_warns.update_one({'_id': str(member.id)}, {'$set': {"warns": []}}, upsert=True)
                if cluster.zxc.history_punishment.find_one({'_id': str(member.id)})['warns'] == 2:
                    cluster.zxc.action_warns.update_one({'_id': str(member.id)}, {'$push': {"warns": f"Перевел | `{datetime.now().strftime('%d.%m.%Y')}`"}}, upsert=True)
                if cluster.zxc.history_punishment.find_one({'_id': str(member.id)})['warns'] == 3:
                    cluster.zxc.action_warns.update_one({'_id': str(member.id)}, {'$set': {"warns": []}}, upsert=True)
                    role_id = config['ban']
                    punishment = "Бан (3 варна)"
                    await member.move_to(None)
                    await member.remove_roles(disnake.utils.get(inter.guild.roles, id=config['male']))
                    await member.remove_roles(disnake.utils.get(inter.guild.roles, id=config['female']))
                cluster.zxc.action_warns.update_one(
                    {"_id": str(member.id)},
                    {"$push": {"tip_data": f"Перевел | `{datetime.now().strftime('%d.%m.%Y')}`"}},
                    upsert=True
                )

            embed.description = desc
            await inter.send(embed=embed, ephemeral = True)

            try:
                embed = disnake.Embed(
                    color=disnake.Color.red(),
                    description=f'Привет {member.mention}, **Вы** получили **{punishment}** на сервере {inter.guild.name}!\n> ・Модератор {inter.author.mention} \n> ・Время {time[:-1]} {num}\n> ・Причина: **{reason}**'
                )
                embed.set_thumbnail(url=inter.guild.icon.url)
                embed.set_author(name=punishment)
                await member.send(embed=embed)
            except:
                pass

            try:
                role_get = disnake.utils.get(inter.guild.roles, id=int(role_id))
                await member.add_roles(role_get)
            except:
                pass

            embed.description = ""
            embed.add_field(name='> ・Модератор', value=f'{inter.author.mention}', inline=False)
            embed.add_field(name='> ・Нарушитель', value=f'{member.mention}', inline=False)
            embed.add_field(name='> ・Причина', value=f'```{reason}```', inline=False)
            embed.add_field(name='> ・Время', value=f'```{time[:-1]} {num}```', inline=False)
            log_view = LogActionView(member.id, log_action_key) if log_action_key else None
            await self.bot.get_channel(channel_id).send(embed=embed, view=log_view)

def setup(bot: commands.Bot):
    bot.add_cog(PunishmentsCogs(bot))
