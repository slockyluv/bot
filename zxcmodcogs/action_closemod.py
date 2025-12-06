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

def draw_text_with_offset(im, text, x, y, font_size, color=(255,255,255)):
    draw = ImageDraw.Draw(im)
    
    font = ImageFont.truetype("fonts/Gordita_bold.ttf", size=font_size)

    bbox = draw.textbbox((x, y), text, font=font)
    text_width = bbox[2] - bbox[0]
    x -= text_width // 2
    draw.text((x, y), text, font=font, fill=color)

class ActionStaffWarns(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Выдать выговор', custom_id = 'give_warn_staff_action', emoji = f'{files.find_one({"_id": "action_plus"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Список выговоров', custom_id = 'warns_staff_list', emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Снять выговор', custom_id = 'snyat_warn_staff_action', emoji = f'{files.find_one({"_id": "action_minus"})["emoji_take"]}', row=1))

        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row=2))
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
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Выдать бан', custom_id="give_event_ban_action", emoji = f'{files.find_one({"_id": "action_plus"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Снять бан', custom_id="snyat_event_ban_action", emoji = f'{files.find_one({"_id": "action_minus"})["emoji_take"]}', row=1))
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

class CloseMod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot



def setup(bot: commands.Bot):
    bot.add_cog(CloseMod(bot))