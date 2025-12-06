import pymongo
import disnake
import datetime
import json
import requests
import os
import asyncio
import random
from typing import Union
from disnake.ext import commands
from disnake.enums import ButtonStyle, TextInputStyle
from datetime import datetime, timedelta
from statistics import mean
from PIL import Image, ImageDraw, ImageFont
import re

with open('configs/zxc.json', 'r') as f:
    config = json.load(f)

with open('configs/zxc_tokens.json', 'r') as f:
    config1 = json.load(f)

cluster = pymongo.MongoClient(config1['mongodb'])

database = cluster.zxc
online_stats = database.online_stats
files = cluster.zxc.files_moderation

min = 60
hour = 60 * 60
day = 60 * 60 * 24

action_author = {}
msgidsupport = {}
currentStaffBlacklistPage = {}

staff_role = config['staff_role']
staff_admin = config['staff_admin']
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

mafiamod = config['mafiamod']
contentmaker = config['contentmaker']
clanmod = config['clan_staff_role']

class SupportVacation(disnake.ui.View):
    def __init__(self):
        super().__init__()
        # self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Верифицировать', custom_id = "verify_support", emoji = f'{files.find_one({"_id": "action_verify"})["emoji_take"]}', row = 0))
        # self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Твинки', custom_id="twink_support", emoji = f'{files.find_one({"_id": "action_twink"})["emoji_take"]}', row = 0))
        # self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Информация', custom_id="info_support", emoji = f'{files.find_one({"_id": "action_book"})["emoji_take"]}', row = 0))
        # self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Недопуск', custom_id = "nedopysk_support", emoji = f'{files.find_one({"_id": "action_nedopysk"})["emoji_take"]}', row = 0))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Изменить роли', custom_id = "edit_action", emoji = f'{files.find_one({"_id": "action_role"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Чс Ветки', custom_id = "blacklist_choice_action", emoji = f'{files.find_one({"_id": "action_blacklist"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row=2))

class ControlVacation(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row = 0))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Бан', custom_id = "ban_action", emoji = f'{files.find_one({"_id": "action_nedopysk"})["emoji_take"]}', row = 0))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Мут', custom_id = "mute_action", emoji = f'{files.find_one({"_id": "action_mute"})["emoji_take"]}', row = 0))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Варн', custom_id = "warn_action", emoji = f'{files.find_one({"_id": "action_warn"})["emoji_take"]}', row = 0))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row = 0))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Изменить роли', custom_id = "edit_action", emoji = f'{files.find_one({"_id": "action_role"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Чс Ветки', custom_id = "blacklist_choice_action", emoji = f'{files.find_one({"_id": "action_blacklist"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row=2))

class ModeratorVacation(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row = 0))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Бан', custom_id = "ban_action", emoji = f'{files.find_one({"_id": "action_nedopysk"})["emoji_take"]}', row = 0))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Мут', custom_id = "mute_action", emoji = f'{files.find_one({"_id": "action_mute"})["emoji_take"]}', row = 0))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Варн', custom_id = "warn_action", emoji = f'{files.find_one({"_id": "action_warn"})["emoji_take"]}', row = 0))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row = 0))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Изменить роли', custom_id = "edit_action", emoji = f'{files.find_one({"_id": "action_role"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Чс Ветки', custom_id = "blacklist_choice_action", emoji = f'{files.find_one({"_id": "action_blacklist"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row=2))

class CloseModVacation(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row = 0))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Бан', custom_id = "ban_close_action", emoji = f'{files.find_one({"_id": "action_nedopysk"})["emoji_take"]}', row = 0))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Варн', custom_id = "warn_action", emoji = f'{files.find_one({"_id": "action_warn"})["emoji_take"]}', row = 0))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row = 0))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Изменить роли', custom_id = "edit_action", emoji = f'{files.find_one({"_id": "action_role"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Чс Ветки', custom_id = "blacklist_choice_action", emoji = f'{files.find_one({"_id": "action_blacklist"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row=2))

class eventsmodVacation(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row = 0))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Бан', custom_id = "ban_event_action", emoji = f'{files.find_one({"_id": "action_nedopysk"})["emoji_take"]}', row = 0))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Варн', custom_id = "warn_action", emoji = f'{files.find_one({"_id": "action_warn"})["emoji_take"]}', row = 0))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row = 0))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Изменить роли', custom_id = "edit_action", emoji = f'{files.find_one({"_id": "action_role"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Чс Ветки', custom_id = "blacklist_choice_action", emoji = f'{files.find_one({"_id": "action_blacklist"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row=2))

class CreativeModVacation(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀", disabled=True, row = 0))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Креатив бан', custom_id = "creative_ban_action", emoji = f'{files.find_one({"_id": "action_nedopysk"})["emoji_take"]}', row = 0))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Творческие роли', custom_id = "edit_creative_action", emoji = f'{files.find_one({"_id": "action_role"})["emoji_take"]}', row = 0))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Варн', custom_id = "creative_warn_action", emoji = f'{files.find_one({"_id": "action_warn"})["emoji_take"]}', row = 0))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀", disabled=True, row = 0))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Изменить роли', custom_id = "edit_action", emoji = f'{files.find_one({"_id": "action_role"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Чс Ветки', custom_id = "blacklist_choice_action", emoji = f'{files.find_one({"_id": "action_blacklist"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row=2))

class TribuneModVacation(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Изменить роли', custom_id = "edit_action", emoji = f'{files.find_one({"_id": "action_role"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Чс Ветки', custom_id = "blacklist_choice_action", emoji = f'{files.find_one({"_id": "action_blacklist"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row=2))

class MafiaModVacation(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row = 0))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Бан', custom_id = "mafia_ban_action", emoji = f'{files.find_one({"_id": "action_nedopysk"})["emoji_take"]}', row = 0))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Варн', custom_id = "mafia_warn_action", emoji = f'{files.find_one({"_id": "action_warn"})["emoji_take"]}', row = 0))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row = 0))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Изменить роли', custom_id = "edit_action", emoji = f'{files.find_one({"_id": "action_role"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Чс Ветки', custom_id = "blacklist_choice_action", emoji = f'{files.find_one({"_id": "action_blacklist"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row=2))

class ContentMakerVacation(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Изменить роли', custom_id = "edit_action", emoji = f'{files.find_one({"_id": "action_role"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Чс Ветки', custom_id = "blacklist_choice_action", emoji = f'{files.find_one({"_id": "action_blacklist"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row=2))

class HelperVacation(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Изменить роли', custom_id = "edit_action", emoji = f'{files.find_one({"_id": "action_role"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Чс Ветки', custom_id = "blacklist_choice_action", emoji = f'{files.find_one({"_id": "action_blacklist"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row=2))

class clanmodVacation(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Изменить роли', custom_id = "edit_action", emoji = f'{files.find_one({"_id": "action_role"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Чс Ветки', custom_id = "blacklist_choice_action", emoji = f'{files.find_one({"_id": "action_blacklist"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row=2))

class ActionView(disnake.ui.View):
    def __init__(self, inter, member):
        super().__init__()
        checks = [
            {'roles': config['own_roles'] + [config['staff_admin'], staff_role], 'label': 'Магазин стаффа', 'custom_id': "shop_action", 'emoji': f'{files.find_one({"_id": "action_shop"})["emoji_take"]}', 'row': 0},
            {'roles': config['own_roles'] + [config['staff_admin'], staff_role], 'label': 'Топы стаффа', 'custom_id': "places_action", 'emoji': f'{files.find_one({"_id": "action_top"})["emoji_take"]}', 'row': 0},
            {'roles': config['own_roles'] + [config['staff_admin'], staff_admin, security, administrator, 1333831675133820979], 'label': 'ЧС стаффа', 'custom_id': "blacklist_action", 'emoji': f'{files.find_one({"_id": "action_book"})["emoji_take"]}', 'row': 0},
            {'roles': config['own_roles'] + [1347730584826413057, 1391177911809081405], 'label': 'Админ панель', 'custom_id': "system_action", 'emoji': f'{files.find_one({"_id": "action_system"})["emoji_take"]}', 'row': 0},
        ]

        roles_member = [role.id for role in member.roles]

        for check in checks:
            button = disnake.ui.Button(
                style=disnake.ButtonStyle.gray,
                label=check['label'],
                custom_id=check["custom_id"],
                emoji=check['emoji'],
                row=check['row'],
                disabled=not any(role_id in roles_member for role_id in check['roles'])
            )
            self.add_item(button)

        # Переносим SelectMenu вниз
        options = ActionViewChoice.get_options_static(inter, member)
        if options:
            self.add_item(ActionViewChoice(options))

class ActionViewChoice(disnake.ui.Select):
    def __init__(self, options):
        super().__init__(
            placeholder="Выберите вашу ветку",
            options=options
        )

    @staticmethod
    def get_options_static(inter, member):
        role_map = {
            support: ("Support", "support_vacation", "action_support"),
            control: ("Control", "control_vacation", "action_control"),
            moderator: ("Moderator", "moderator_vacation", "action_moderator"),
            closer: ("CloseMod", "closemod_vacation", "action_closemod"),
            eventer: ("EventsMod", "eventsmod_vacation", "action_eventsmod"),
            creative: ("CreativeMod", "creative_vacation", "action_creative"),
            tribunemod: ("TribuneMod", "tribunemod_vacation", "action_tribunemod"),
            mafiamod: ("MafiaMod", "mafiamod_vacation", "action_mafiamod"),
            helper: ("Helper", "helper_vacation", "action_helper"),
            contentmaker: ("ContentMaker", "contentmaker_vacation", "action_content"),
            clanmod: ("ClanMod", "clanmod_vacation", "action_content"),
        }

        own_roles = config['own_roles']
        options = []

        # Проверяем, есть ли у пользователя хотя бы одна роль из own_roles
        has_own_role = any(inter.guild.get_role(role_id) in member.roles for role_id in own_roles)

        for role, values in role_map.items():
            if has_own_role or inter.guild.get_role(role) in member.roles or inter.guild.get_role(config['staff_admin']) in member.roles or inter.author.id == 849353684249083914 or inter.author.id == 788353684660027392:
                if isinstance(values, list):
                    for label, value, emoji_id in values:
                        options.append(
                            disnake.SelectOption(
                                label=label,
                                value=value,
                                description=f"Выбрать: ветка {label.lower()}",
                                emoji=f'{files.find_one({"_id": emoji_id})["emoji_take"]}'
                            )
                        )
                else:
                    label, value, emoji_id = values
                    options.append(
                        disnake.SelectOption(
                            label=label,
                            value=value,
                            description=f"Выбрать: ветка {label.lower()}",
                            emoji=f'{files.find_one({"_id": emoji_id})["emoji_take"]}'
                        )
                    )

        return options

def draw_text_with_offset(im, text, x, y, font_size, color=(255,255,255)):
    draw = ImageDraw.Draw(im)
    
    font = ImageFont.truetype("fonts/Gordita_bold.ttf", size=font_size)

    bbox = draw.textbbox((x, y), text, font=font)
    text_width = bbox[2] - bbox[0]
    x -= text_width // 2
    draw.text((x, y), text, font=font, fill=color)

class action(commands.Cog):
    def __init__(self, bot: commands.Bot(intents = disnake.Intents.all(), command_prefix = 'test!')): # type: ignore
        self.bot = bot

    @commands.command(description = "")
    async def verify(self, inter):
        if str(inter.author.id) == str(config['author']):
            await inter.send("Начинаю выдачу")

            new_role = inter.guild.get_role(config['unverify'])
            man_gender = inter.guild.get_role(config['male'])

            # for member in inter.guild.members:
            #     if new_role in member.roles and member.status != disnake.Status.offline:
            #         await member.add_roles(man_gender)
            #         await member.remove_roles(new_role)

            for member in inter.guild.members:
                if new_role in member.roles:
                    try:
                        await member.add_roles(man_gender)
                        await member.remove_roles(new_role)
                    except:
                        pass
                    
    @commands.command(description = "")
    @commands.has_permissions(administrator = True)
    async def unverify(self, inter):
        await inter.send("Начинаю выдачу")

        new_role = inter.guild.get_role(int(config['unverify']))

        # for member in inter.guild.members:
        #     if new_role in member.roles and member.status != disnake.Status.offline:
        #         await member.add_roles(man_gender)
        #         await member.remove_roles(new_role)

        for member in inter.guild.members:
            try:
                await member.add_roles(new_role)
            except:
                pass

    async def handle_clear(self, ctx, количество: int = 10):
        try:
            amount = max(1, int(количество))
        except (TypeError, ValueError):
            error_embed = disnake.Embed(
                title="⚠️ Неверное количество сообщений",
                description="Укажите целое число больше нуля, чтобы очистить чат.",
                color=disnake.Color.red()
            )
            if isinstance(ctx, disnake.ApplicationCommandInteraction):
                if not ctx.response.is_done():
                    await ctx.response.send_message(embed=error_embed, ephemeral=True)
                else:
                    await ctx.edit_original_message(embed=error_embed)
            else:
                await ctx.send(embed=error_embed)
            return

        deleted_messages = await ctx.channel.purge(limit=amount)

        embed = disnake.Embed(
            title="🧹 Очистка чата",
            description=f"Удалено **{len(deleted_messages)}** сообщений в {ctx.channel.mention}.",
            color=disnake.Color.blurple(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Запрос", value=f"`{amount}` сообщений", inline=True)
        embed.add_field(name="Модератор", value=ctx.author.mention, inline=True)
        embed.set_footer(text="Бережём порядок", icon_url=ctx.author.display_avatar.url)

        if isinstance(ctx, disnake.ApplicationCommandInteraction):
            if not ctx.response.is_done():
                await ctx.response.defer(ephemeral=True)
            await ctx.edit_original_message(embed=embed)
        else:
            await ctx.send(embed=embed)

    @commands.command(name="clear", description='Очистить чат')
    @commands.has_permissions(administrator = True)
    async def clear_prefix(self, ctx, количество: int = 10):
        await self.handle_clear(ctx, количество)

    @commands.slash_command(description = 'Очистить чат')
    @commands.has_permissions(administrator = True)
    async def clear(self, inter, количество: int = 10):
        await self.handle_clear(inter, количество)

    async def handle_action(self, ctx, member: disnake.Member | None):
        if member is None or member == ctx.author:
            member = ctx.author

        allowed_roles = set(own_roles + [staff_admin, administrator, curator, master, moderator, support, closer, eventer, creative, security, control, tribunemod, helper, 1333831675133820979])
        author_role_ids = {role.id for role in ctx.author.roles}

        if isinstance(ctx, disnake.ApplicationCommandInteraction) and not ctx.response.is_done():
            await ctx.response.defer()

        if author_role_ids & allowed_roles:
            user_id_str = str(member.id)

            operations = [
                (database.event_balls, {"_id": user_id_str, "event_count": 0, "balls": 0}),
                (database.balls, {"_id": user_id_str, "balls": 0, "warns": 0, "mutes": 0, "bans": 0}),
                (database.online_verify, {"_id": user_id_str, "mod": 0}),
                (database.report, {"_id": user_id_str, "reports": 0}),
                (database.tickets, {"_id": user_id_str, "tickets": 0}),
                (database.creative, {"_id": user_id_str, "events": 0}),
                (cluster.zxc.economy, {"_id": user_id_str, "balance": 0}),
                (cluster.zxc.history_punishment, {"_id": user_id_str, "warns": 0, "mutes": 0, "bans": 0, "eventban": 0}),
                (cluster.zxc.rest, {"_id": user_id_str, "rest": 'Не активен'})
            ]

            for collection, default_doc in operations:
                collection.update_one({"_id": user_id_str}, {"$setOnInsert": default_doc}, upsert=True)

            cluster.zxc.target.update_one({'_id': str(ctx.author.id)}, {'$set': {'member': member.id}}, upsert=True)

            now = datetime.now()
            day = f"{now.strftime('%A')}, {now.strftime('%B')} {now.day}"
            time_str = f"{now.strftime('%H:%M')}"

            im = Image.open("action_zxc/main.png")
            draw_text_with_offset(im, day, 710, 76, font_size=32)
            draw_text_with_offset(im, time_str, 708, 120, font_size=96)

            width, height = 110, 110
            avatar_x, avatar_y = 137, 139

            avatar_url = member.display_avatar.url
            avatar_image = Image.open(requests.get(avatar_url, stream=True).raw).resize((width, height))
            avatar_image.save('avatars/avatar_profile_zxc.png')
            mask_im = Image.new("L", avatar_image.size)
            ImageDraw.Draw(mask_im).ellipse((0, 0, width, height), fill=255)
            im.paste(avatar_image, (avatar_x, avatar_y), mask_im)

            пользователь_name = member.name[:13] if len(member.name) > 13 else member.name
            draw_text_with_offset(im, пользователь_name, 412, 194.26, font_size=32)

            im.save(f'out/action_{ctx.author.id}.png')

            send_kwargs = {
                "content": ctx.author.mention,
                "file": disnake.File(f"out/action_{ctx.author.id}.png"),
                "view": ActionView(ctx, ctx.author)
            }

            if isinstance(ctx, disnake.ApplicationCommandInteraction):
                return await ctx.send(**send_kwargs)

            return await ctx.send(send_kwargs["content"], file=send_kwargs["file"], view=send_kwargs["view"])

        embed = disnake.Embed(
            description=f'{ctx.author.mention}, У **Вас** нет на это **разрешения**!',
            color=3092790
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.set_author(name=f"Взаимодействие с участником | {ctx.guild.name}", icon_url=ctx.guild.icon.url)

        if isinstance(ctx, disnake.ApplicationCommandInteraction):
            return await ctx.send(embed=embed)

        await ctx.send(embed=embed)

    @commands.command(description='Взаимодействие с участником')
    async def action(self, ctx, member: disnake.Member = None):
        await self.handle_action(ctx, member)

    @commands.slash_command(name="action", description='Взаимодействие с участником')
    async def action_slash(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member = None):
        await self.handle_action(inter, member)

    @commands.slash_command(description = 'Выдать предупреждение')
    @commands.has_any_role(1130553029184196628, 1150154871153111130, 1150055480450875412, 1150203323660640317, curator, moderator)
    async def pred(self, inter, пользователь: disnake.Member, причина):
        embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** успешно выдали {пользователь.mention} предупреждение на 24 часа!', color = 3092790)
        embed.set_author(name = "Выдать предупреждение", icon_url = inter.guild.icon.url)
        embed.set_thumbnail(url = inter.author.display_avatar.url)

        await inter.send(embed=embed)

        embed = disnake.Embed(color = disnake.Color.red())
        embed.set_author(name = "Выдача предупреждение", icon_url = inter.guild.icon.url)
        embed.set_thumbnail(url = пользователь.display_avatar.url)
        embed.add_field(name='> Модератор',value=f'{inter.author.mention} | {inter.author.name} | **ID:** {пользователь.id}', inline=False)
        embed.add_field(name='> Пользователь',value=f'{пользователь.mention} | {пользователь} | ID: **{пользователь.id}**', inline=False)
        await self.bot.get_channel(config['pred']).send(embed=embed)
        
        try:
            embed = disnake.Embed(description=f'Привет {пользователь.mention}, **Вы** получили **предупреждение** на сервере!\n> ・Модератор{inter.author.mention}\n> ・Время 24 часа\n> ・Причина: **{причина}**', color = disnake.Color.red())
            embed.set_thumbnail(url = inter.guild.icon.url)
            embed.set_author(name = 'Предупреждение')
            await пользователь.send(embed=embed)
        except:
            pass

        role_pred = disnake.utils.get(inter.guild.roles, id = 1203421998282440754)
        await пользователь.add_roles(role_pred)

        await asyncio.sleep(86400)

        try:
            embed = disnake.Embed(description=f'Привет {пользователь.mention}, **Ваше** предупреждение было закончено!', color = disnake.Color.red())
            embed.set_thumbnail(url = self.bot.get_guild(inter.guild.id).icon.url)
            embed.set_author(name = 'Предупреждение')
            await пользователь.send(embed=embed) 
        except:
            pass

        await пользователь.remove_roles(role_pred)

    @pred.error
    async def pred_error(self, inter, error):
        if isinstance(error, commands.MissingAnyRole):
            embed = disnake.Embed(description = f'{inter.author.mention}, У **Вас** нет на это **разрешения**!', color = 3092790)
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            embed.set_author(name = inter.author, icon_url = inter.author.avatar.url)
            await inter.send(embed=embed)
        else:
            print(error)

    @commands.slash_command(description = 'Снять предупреждение')
    @commands.has_any_role(1130553029184196628, 1150154871153111130, 1150055480450875412, 1150203323660640317, curator, moderator)
    async def unpred(self, inter, пользователь: disnake.Member):
        embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** успешно сняли {пользователь.mention} предупреждение!', color = 3092790)
        embed.set_author(name = "Снятие предупреждение", icon_url = inter.guild.icon.url)
        embed.set_thumbnail(url = inter.author.display_avatar.url)
        
        await inter.send(embed=embed)

        embed = disnake.Embed(color = 3092790)
        embed.set_author(name = "Снятие предупреждение", icon_url = inter.guild.icon.url)
        embed.set_thumbnail(url = пользователь.display_avatar.url)
        embed.add_field(name='> Модератор',value=f'{inter.author.mention} | {inter.author.name}', inline=False)
        embed.add_field(name='> Пользователь',value=f'{пользователь.mention} | {пользователь} | ID: **{пользователь.id}**', inline=False)
        await self.bot.get_channel(config['pred']).send(embed=embed)

        try: 
            embed = disnake.Embed(description=f'Привет {пользователь.mention}, **Ваше** предупреждение было закончено!', color = disnake.Color.red())
            embed.set_thumbnail(url = self.bot.get_guild(inter.guild.id).icon.url)
            embed.set_author(name = "Снятие предупреждение", icon_url = inter.guild.icon.url)
            await пользователь.send(embed=embed)
        except: 
            pass

        role_pred = disnake.utils.get(inter.guild.roles, id = 1203421998282440754)
        await пользователь.remove_roles(role_pred)
    
    @unpred.error
    async def unpred_error(self, inter, error):
        if isinstance(error, commands.MissingAnyRole):
            embed = disnake.Embed(description = f'{inter.author.mention}, У **Вас** нет на это **разрешения**!', color = 3092790)
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            embed.set_author(name = inter.author, icon_url = inter.author.avatar.url)
            await inter.send(embed=embed)
        else: 
            print(error)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if int(message.channel.id) in [1315722372439081031, 1188148632478826514]:
            staff_role = disnake.utils.get(message.guild.roles, id=int(config['staff_role']))
            if staff_role in message.author.roles:
                now = datetime.utcnow()
                day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                user_id = str(message.author.id)

                try:
                    # Обновление статистики сообщений за день
                    online_stats.update_one(
                        {"user_id": user_id, "category": "message", "period": "day", "date": day_start},
                        {"$inc": {"duration": 1}},
                        upsert=True
                    )
                except Exception as e:
                    print("Ошибка обновления статистики сообщений:", e)
        
    @commands.Cog.listener()
    async def on_button_click(self, inter):
        custom_id = inter.component.custom_id
        
        if custom_id == 'back_action':
            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790)
                embed.set_author(name = "Меню", icon_url = inter.guild.icon.url)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.send(ephemeral = True, embed=embed)
            
            await inter.response.defer()
    
            пользователь = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))

            # Список разрешённых ролей
            allowed_roles = set(own_roles + [staff_admin, administrator, curator, master, moderator, support, closer, eventer, creative, security, control, tribunemod, helper, 1333831675133820979])
            author_role_ids = {role.id for role in inter.author.roles}
    
            if author_role_ids & allowed_roles:
                user_id = str(inter.author.id)
    
                # Список операций: (коллекция, документ по умолчанию)
                operations = [
                    (database.event_balls, {"_id": user_id, "event_count": 0, "balls": 0}),
                    (database.balls, {"_id": user_id, "balls": 0, "warns": 0, "mutes": 0, "bans": 0}),
                    (database.report, {"_id": user_id, "reports": 0}),
                    (database.tickets, {"_id": user_id, "tickets": 0}),
                    (cluster.zxc.economy, {"_id": user_id, "balance": 0}),
                    (cluster.zxc.history_punishment, {"_id": user_id, "warns": 0, "mutes": 0, "bans": 0, "eventban": 0}),
                    (cluster.zxc.rest, {"_id": user_id, "rest": 'Не активен'})
                ]
    
                # Применение операции "upsert" для каждой коллекции
                for collection, default_doc in operations:
                    collection.update_one({"_id": user_id}, {"$setOnInsert": default_doc}, upsert=True)

                now = datetime.now()
                day = f"{now.strftime('%A')}, {now.strftime('%B')} {now.day}"
                time = f"{now.strftime('%H:%M')}"
    
                im = Image.open(f"action_zxc/main.png")
            
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

                im.save(f'out/action_{inter.author.id}.png')
    
                return await inter.message.edit(
                    attachments = None,
                    content = inter.author.mention, 
                    file=disnake.File(f"out/action_{inter.author.id}.png"), 
                    view=ActionView(inter, inter.author)
                )
        
        if custom_id == 'exit_action':
            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790)
                embed.set_author(name = "Отмена", icon_url = inter.guild.icon.url)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.send(ephemeral = True, embed=embed)

            await inter.message.delete()
    
    @commands.Cog.listener()
    async def on_dropdown(self, inter: disnake.MessageInteraction):
        custom_id = inter.values[0]

        now = datetime.now()
        day = f"{now.strftime('%A')}, {now.strftime('%B')} {now.day}"
        time = f"{now.strftime('%H:%M')}"

        # Defer immediately to avoid interaction expiration while images are generated
        if not inter.response.is_done():
            await inter.response.defer()

        if custom_id.endswith("vacation"):
            group_choice = custom_id.replace("_vacation", "")

            cluster.zxc.target.update_one({'_id': str(inter.author.id)}, {'$set': {'group': group_choice}}, upsert=True)

            im = Image.open(f"action_zxc/{group_choice}.png")

            if custom_id == "support_vacation":
                view = SupportVacation()
            if custom_id == "control_vacation":
                view = ControlVacation()
            if custom_id == "moderator_vacation":
                view = ModeratorVacation()
            if custom_id == "closemod_vacation":
                view = CloseModVacation()
            if custom_id == "eventsmod_vacation":
                view = eventsmodVacation()
            if custom_id == "creative_vacation":
                view = CreativeModVacation()
            if custom_id == "tribunemod_vacation":
                view = TribuneModVacation()
            if custom_id == "mafiamod_vacation":
                view = MafiaModVacation()
            if custom_id == "contentmaker_vacation":
                view = ContentMakerVacation()
            if custom_id == "helper_vacation":
                view = HelperVacation()
            if custom_id == "clanmod_vacation":
                view = clanmodVacation()

            draw_text_with_offset(im, str(day), 710, 76, font_size=32)
            draw_text_with_offset(im, str(time), 708, 120, font_size=96)

            im.save(f'out/action_{inter.author.id}.png')

            edit_kwargs = {
                "attachments": None,
                "file": disnake.File(f"out/action_{inter.author.id}.png"),
                "view": view,
            }

            if inter.response.is_done():
                await inter.edit_original_message(**edit_kwargs)
            else:
                await inter.response.edit_message(**edit_kwargs)

def setup(bot):
    bot.add_cog(action(bot))