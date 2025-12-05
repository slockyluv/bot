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

with open('configs/zxc.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
with open('configs/zxc_tokens.json', 'r', encoding='utf-8') as f:
    config1 = json.load(f)

cluster = pymongo.MongoClient(config1['mongodb'])
db = cluster.zxc
files = cluster.zxc.files_moderation

def draw_text_with_offset(im, text, x, y, font_size, color=(255,255,255)):
    draw = ImageDraw.Draw(im)
    
    font = ImageFont.truetype("fonts/Gordita_bold.ttf", size=font_size)

    bbox = draw.textbbox((x, y), text, font=font)
    text_width = bbox[2] - bbox[0]
    x -= text_width // 2
    draw.text((x, y), text, font=font, fill=color)

class Invitelink(disnake.ui.View):
    def __init__(self, guild_id):
        super().__init__()
        channel_id = cluster.zxc.server_settings.find_one({"_id": str(guild_id)})["appeal_nedopysk_channel"]

        self.add_item(disnake.ui.Button(style = disnake.ButtonStyle.secondary, label = "Подать аппеляцию", url = f"https://discord.com/channels/{guild_id}/{channel_id}"))

class GiveVerify(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Изменить выбор', custom_id = 'verify_main', emoji = f'{files.find_one({"_id": "verify"})["emoji_take"]}'))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Назад', custom_id = 'back_verification', emoji = f'{files.find_one({"_id": "back"})["emoji_take"]}'))

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

class NedopyskDropdown(disnake.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="Выберите причину",
            options = [
                disnake.SelectOption(label="Неадекват", description="Выдать недопуск", value = 'neadkvat_nedopysk_support'),
                disnake.SelectOption(label="Меньше 13 лет", description="Выдать недопуск", value = 'menshe_nedopysk_support'),
                disnake.SelectOption(label="Без микрофона", description="Выдать недопуск", value = 'no_microphone_nedopysk_support'),
                disnake.SelectOption(label="Свастика", description="Выдать недопуск", value = 'swastika_nedopysk_support'),
                disnake.SelectOption(label="Ник", description="Выдать недопуск", value = 'nick_nedopysk_support'),
                disnake.SelectOption(label="Цифры", description="Выдать недопуск", value = 'numbers_nedopysk_support'),
                disnake.SelectOption(label="Аватарка", description="Выдать недопуск", value = 'avatrka_nedopysk_support'),
                disnake.SelectOption(label="Обход", description="Выдать недопуск", value = 'obxod_nedopysk_support'),
                disnake.SelectOption(label="Перезаходы", description="Выдать недопуск", value = 'reload_nedopysk_support'),
            ],
        )

class Nedopysk(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(NedopyskDropdown())

        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row=2))

class Twink(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Добавить', custom_id = 'add_twink_support', emoji = f'{files.find_one({"_id": "action_plus"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Удалить', custom_id = 'remove_twink_support', emoji = f'{files.find_one({"_id": "action_minus"})["emoji_take"]}', row=1))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", disabled=True, row=1))

        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row=2))
        
class EditRole(disnake.ui.View):
    def __init__(self, bot):
        super().__init__()
        self.add_item(EditRoleDropdown(bot))

        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выговоры', custom_id = "staff_warns_action", emoji = f'{files.find_one({"_id": "action_staff_warns"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Отпуск', custom_id = "rest_action", emoji = f'{files.find_one({"_id": "action_rest"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Профиль', custom_id = "profile_action", emoji = f'{files.find_one({"_id": "action_profile"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label='Меню', custom_id = "back_action", emoji = f'{files.find_one({"_id": "action_menu"})["emoji_take"]}', row=2))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label='Выход', custom_id = "exit_action", emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', row=2))

class Comment(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Оставить отзыв', custom_id = 'comment_verify', emoji = f'{files.find_one({"_id": "star"})["emoji_take"]}'))
        
class EditRoleDropdown(disnake.ui.Select):
    def __init__(self, bot):
        self.bot = bot

        options = []

        options.append(disnake.SelectOption(label=f"Караоке", value = f'edit_creative_1'))
        options.append(disnake.SelectOption(label=f"Даббер", value = f'edit_creative_2'))
        options.append(disnake.SelectOption(label=f"Лит клуб", value = f'edit_creative_3'))
        options.append(disnake.SelectOption(label=f"Киношка/Игровая", value = f'edit_creative_4'))
        options.append(disnake.SelectOption(label=f"Художник", value = f'edit_creative_5'))
        # options.append(disnake.SelectOption(label=f"Фулл", value = f'edit_creative_6'))
            
        super().__init__(
            placeholder="Выдать роль",
            options = options,
        )

class CreativeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        custom_id = inter.component.custom_id

        if custom_id.startswith("edit_creative"):
            if inter.message.content != inter.author.mention:
                embed = disnake.Embed(
                    description=f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**',
                    color=3092790
                )
                embed.set_author(name="Изменить роли", icon_url=inter.guild.icon.url)
                embed.set_thumbnail(url=inter.author.display_avatar.url)
                return await inter.send(ephemeral=True, embed=embed)

            db_target = cluster.zxc.target.find_one({'_id': str(inter.author.id)})
            member = disnake.utils.get(self.bot.get_guild(config['server_id']).members, id=int(db_target['member']))

            match custom_id:
                case "edit_creative_action":
                    await inter.response.defer()

                    now = datetime.now()
                    day = f"{now.strftime('%A')}, {now.strftime('%B')} {now.day}"
                    time_str = now.strftime('%H:%M')
                    im = Image.open("action_zxc/edit_creative_action.png")
                    draw_text_with_offset(im, day, 710, 76, font_size=32)
                    draw_text_with_offset(im, time_str, 708, 120, font_size=96)

                    width, height = 110, 110
                    avatar_x, avatar_y = 137, 139
                    avatar_response = requests.get(member.display_avatar.url, stream=True)
                    Image.open(avatar_response.raw).resize((width, height)).save('avatars/avatar_profile_zxc.png')

                    mask_im = Image.new("L", (width, height))
                    ImageDraw.Draw(mask_im).ellipse((0, 0, width, height), fill=255)
                    im.paste(Image.open('avatars/avatar_profile_zxc.png'), (avatar_x, avatar_y), mask_im)
                    пользователь_name = member.name[:13] if len(member.name) > 13 else member.name
                    draw_text_with_offset(im, пользователь_name, 412, 194.26, font_size=32)
                    im.save(f'out/edit_role_{inter.author.id}.png')
                    bot = self.bot
                    return await inter.message.edit(
                        attachments=None,
                        file=disnake.File(f"out/edit_role_{inter.author.id}.png"),
                        view=EditRole(bot)
                    )

    @commands.Cog.listener()
    async def on_dropdown(self, inter):
        custom_id = inter.values[0]
        
        if custom_id.startswith("edit_creative"):
            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(title = 'Изменить креатив роли', description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.send(ephemeral = True, embed=embed)

            db_target = cluster.zxc.target.find_one({'_id': str(inter.author.id)})
            member = disnake.utils.get(self.bot.get_guild(config['server_id']).members, id=int(db_target['member']))

            match custom_id:
                case "edit_creative_1":
                    role_id = 1077644286054637698 
                case "edit_creative_2":
                    role_id = 1208178195157876756
                case "edit_creative_3":
                    role_id = 1129915648156389466 
                case "edit_creative_4":
                    role_id = 1107257328803270728 
                case "edit_creative_5":
                    role_id = 1286997547017048155 
                case "edit_creative_6":
                    role_id = 1398729608366526607 

            role = inter.guild.get_role(role_id)
            if role in member.roles:
                await member.remove_roles(role)
            else:
                await member.add_roles(role)

            embed = disnake.Embed(color=3092790)
            embed.description = f"{inter.author.mention}, **Вы** успешно выдали роль <@&{role_id}> {member.mention}!"
            embed.set_author(name=f"Выдать творческую роль | {inter.guild.name}",
                                icon_url=inter.guild.icon.url)
            embed.set_thumbnail(url=member.display_avatar.url)
            await inter.send(embed=embed, ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(CreativeCog(bot))