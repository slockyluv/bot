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
from statistics import mean
from PIL import Image, ImageDraw, ImageFont
import re

with open('configs/zxc.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
with open('configs/zxc_tokens.json', 'r', encoding='utf-8') as f:
    config1 = json.load(f)
    
cluster = pymongo.MongoClient(config1['mongodb'])
db = cluster.zxc
files = cluster.zxc.files_moderation

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
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Выдать выговор', custom_id = 'give_warn_staff_action', emoji = f'{files.find_one({"_id": "action_plus"})["emoji_take"]}', row = 1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Список выговоров', custom_id = 'warns_staff_list', emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row = 1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Снять выговор', custom_id = 'snyat_warn_staff_action', emoji = f'{files.find_one({"_id": "action_minus"})["emoji_take"]}', row = 1))

        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row = 2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row = 2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row = 2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row = 2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row = 2))

class ActionMuteBan(disnake.ui.View):
    def __init__(self): 
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row = 1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Выдать бан', custom_id="give_ban_action", emoji = f'{files.find_one({"_id": "action_plus"})["emoji_take"]}', row = 1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Снять бан', custom_id="snyat_ban_action", emoji = f'{files.find_one({"_id": "action_minus"})["emoji_take"]}', row = 1))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row = 1))

        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row = 2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row = 2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row = 2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row = 2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row = 2))

class ActionEventBan(disnake.ui.View):
    def __init__(self): 
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row = 1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Выдать бан', custom_id="give_event_ban_action", emoji = f'{files.find_one({"_id": "action_plus"})["emoji_take"]}', row = 1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Снять бан', custom_id="snyat_event_ban_action", emoji = f'{files.find_one({"_id": "action_minus"})["emoji_take"]}', row = 1))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row = 1))

        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row = 2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row = 2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row = 2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row = 2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row = 2))

class ActionWarns(disnake.ui.View):
    def __init__(self): 
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row = 1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Выдать варн', custom_id="give_warn_action", emoji = f'{files.find_one({"_id": "action_plus"})["emoji_take"]}', row = 1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Снять варн', custom_id="snyat_warn_action", emoji = f'{files.find_one({"_id": "action_minus"})["emoji_take"]}', row = 1))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row = 1))

        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row = 2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row = 2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row = 2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row = 2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row = 2))

class ActionMuteView(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row = 1))
        self.add_item(disnake.ui.Button(style=ButtonStyle.secondary, label='Текстовый мут', custom_id="textmute_action", emoji=f'{files.find_one({"_id": "action_mute"})["emoji_take"]}', row = 1))
        self.add_item(disnake.ui.Button(style=ButtonStyle.secondary, label='Голосовой мут', custom_id="voicemute_action", emoji=f'{files.find_one({"_id": "action_support"})["emoji_take"]}', row = 1))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row = 1))

        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row = 2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row = 2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row = 2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row = 2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row = 2))

class ActionMuteChoice(disnake.ui.View):
    def __init__(self, bot, member):
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row = 1))
        if db.action.count_documents({"_id": str(member.id)}) == 0:
            mute_button = disnake.ui.Button(style=ButtonStyle.secondary, label='Снять мут', custom_id="snyat_mute_action", emoji=f'{files.find_one({"_id": "action_minus"})["emoji_take"]}', disabled=True, row = 1)
        else:
            mute_button = disnake.ui.Button(style=ButtonStyle.secondary, label='Снять мут', custom_id ="snyat_mute_action", emoji=f'{files.find_one({"_id": "action_minus"})["emoji_take"]}', row = 1)
        self.add_item(disnake.ui.Button(style=ButtonStyle.secondary, label='Выдать мут', custom_id="give_mute_action", emoji=f'{files.find_one({"_id": "action_plus"})["emoji_take"]}', row = 1))
        self.add_item(mute_button)
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row = 1))

        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row = 2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row = 2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row = 2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row = 2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row = 2))

class Verification(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Парень', custom_id = 'male_verify_support', emoji = f'{files.find_one({"_id": "action_man"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Девушка', custom_id = 'female_verify_support', emoji = f'{files.find_one({"_id": "action_girl"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row=2))

class UserCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        for folder in ["avatars", "out"]:
            os.makedirs(folder, exist_ok=True)

    @commands.user_command(name="Забанить")
    async def ban_action(self, inter: disnake.ApplicationCommandInteraction, пользователь: disnake.User):
        allowed_roles = set(own_roles + [staff_admin, administrator, curator, master, moderator, support, closer, eventer, creative, security, control, tribunemod, helper, 1393392040217153747])
        author_role_ids = {role.id for role in inter.author.roles}

        if author_role_ids & allowed_roles:
            cluster.zxc.target.update_one({'_id': str(inter.author.id)}, {'$set': {'member': пользователь.id}}, upsert=True)

            now = datetime.datetime.now()
            day = now.strftime('%d.%m.%Y')
            time_str = now.strftime('%H:%M')

            template_path = os.path.join("action_zxc", "ban.png")
            im = Image.open(template_path).convert("RGBA")

            draw_text_with_offset(im, day, 710, 76, font_size=32)
            draw_text_with_offset(im, time_str, 708, 120, font_size=96)

            width, height = 110, 110
            avatar_x, avatar_y = 137, 139

            avatar_url = пользователь.display_avatar.url
            response = requests.get(avatar_url, stream=True)
            avatar_im = Image.open(response.raw).convert("RGBA").resize((width, height))
            avatar_path = os.path.join("avatars", "avatar_profile_zxc.png")
            avatar_im.save(avatar_path)

            mask_im = Image.new("L", (width, height), 0)
            mask_draw = ImageDraw.Draw(mask_im)
            mask_draw.ellipse((0, 0, width, height), fill=255)

            im.paste(avatar_im, (avatar_x, avatar_y), mask_im)

            пользователь_name = пользователь.name if len(пользователь.name) <= 13 else пользователь.name[:13]
            draw_text_with_offset(im, пользователь_name, 412, 194.26, font_size=32)

            output_file = os.path.join("out", f"ban{inter.author.id}.png")
            im.save(output_file)

            return await self.bot.get_channel(1183881754776440903).send(
                content=inter.author.mention,
                file=disnake.File(output_file),
                view=ActionMuteBan()
            )

        embed = disnake.Embed(
            description=f'{inter.author.mention}, У **Вас** нет на это **разрешения**!',
            color=3092790
        )
        embed.set_thumbnail(url=inter.author.display_avatar.url)
        embed.set_author(name=f"Взаимодействие с участником | {inter.guild.name}", icon_url=inter.guild.icon.url)
        return await inter.response.send_message(embed=embed, ephemeral=True)

    @commands.user_command(name="Замьютить")
    async def mute_action(self, inter: disnake.ApplicationCommandInteraction, пользователь: disnake.User):
        allowed_roles = set(own_roles + [staff_admin, administrator, curator, master, moderator, support, closer, eventer, creative, security, control, tribunemod, helper, 1393392040217153747])
        author_role_ids = {role.id for role in inter.author.roles}

        if author_role_ids & allowed_roles:
            cluster.zxc.target.update_one({'_id': str(inter.author.id)}, {'$set': {'member': пользователь.id}}, upsert=True)

            now = datetime.datetime.now()
            day = now.strftime('%d.%m.%Y')
            time_str = now.strftime('%H:%M')

            template_path = os.path.join("action_zxc", "mute.png")
            im = Image.open(template_path).convert("RGBA")

            draw_text_with_offset(im, day, 710, 76, font_size=32)
            draw_text_with_offset(im, time_str, 708, 120, font_size=96)

            width, height = 110, 110
            avatar_x, avatar_y = 137, 139

            avatar_url = пользователь.display_avatar.url
            response = requests.get(avatar_url, stream=True)
            avatar_im = Image.open(response.raw).convert("RGBA").resize((width, height))
            avatar_path = os.path.join("avatars", "avatar_profile_zxc.png")
            avatar_im.save(avatar_path)

            mask_im = Image.new("L", (width, height), 0)
            mask_draw = ImageDraw.Draw(mask_im)
            mask_draw.ellipse((0, 0, width, height), fill=255)

            im.paste(avatar_im, (avatar_x, avatar_y), mask_im)

            пользователь_name = пользователь.name if len(пользователь.name) <= 13 else пользователь.name[:13]
            draw_text_with_offset(im, пользователь_name, 412, 194.26, font_size=32)

            output_file = os.path.join("out", f"mute{inter.author.id}.png")
            im.save(output_file)

            return await self.bot.get_channel(1183881754776440903).send(
                content=inter.author.mention,
                file=disnake.File(output_file),
                view=ActionMuteChoice(self.bot, пользователь)
            )

        embed = disnake.Embed(
            description=f'{inter.author.mention}, У **Вас** нет на это **разрешения**!',
            color=3092790
        )
        embed.set_thumbnail(url=inter.author.display_avatar.url)
        embed.set_author(name=f"Взаимодействие с участником | {inter.guild.name}", icon_url=inter.guild.icon.url)
        return await inter.response.send_message(embed=embed, ephemeral=True)

    @commands.user_command(name="Варн")
    async def warn_action(self, inter: disnake.ApplicationCommandInteraction, пользователь: disnake.User):
        allowed_roles = set(own_roles + [staff_admin, administrator, curator, master, moderator, support, closer, eventer, creative, security, control, tribunemod, helper, 1393392040217153747])
        author_role_ids = {role.id for role in inter.author.roles}

        if author_role_ids & allowed_roles:
            cluster.zxc.target.update_one({'_id': str(inter.author.id)}, {'$set': {'member': пользователь.id}}, upsert=True)

            now = datetime.datetime.now()
            day = now.strftime('%d.%m.%Y')
            time_str = now.strftime('%H:%M')

            template_path = os.path.join("action_zxc", "warn.png")
            im = Image.open(template_path).convert("RGBA")

            draw_text_with_offset(im, day, 710, 76, font_size=32)
            draw_text_with_offset(im, time_str, 708, 120, font_size=96)

            width, height = 110, 110
            avatar_x, avatar_y = 137, 139

            avatar_url = пользователь.display_avatar.url
            response = requests.get(avatar_url, stream=True)
            avatar_im = Image.open(response.raw).convert("RGBA").resize((width, height))
            avatar_path = os.path.join("avatars", "avatar_profile_zxc.png")
            avatar_im.save(avatar_path)

            mask_im = Image.new("L", (width, height), 0)
            mask_draw = ImageDraw.Draw(mask_im)
            mask_draw.ellipse((0, 0, width, height), fill=255)

            im.paste(avatar_im, (avatar_x, avatar_y), mask_im)

            пользователь_name = пользователь.name if len(пользователь.name) <= 13 else пользователь.name[:13]
            draw_text_with_offset(im, пользователь_name, 412, 194.26, font_size=32)

            output_file = os.path.join("out", f"warn_{inter.author.id}.png")
            im.save(output_file)

            return await self.bot.get_channel(1183881754776440903).send(
                content=inter.author.mention,
                file=disnake.File(output_file),
                view=ActionWarns()
            )

        embed = disnake.Embed(
            description=f'{inter.author.mention}, У **Вас** нет на это **разрешения**!',
            color=3092790
        )
        embed.set_thumbnail(url=inter.author.display_avatar.url)
        embed.set_author(name=f"Взаимодействие с участником | {inter.guild.name}", icon_url=inter.guild.icon.url)
        return await inter.response.send_message(embed=embed, ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(UserCommands(bot))