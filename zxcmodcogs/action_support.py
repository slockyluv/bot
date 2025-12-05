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

def update_stat(filter_dict):
    try:
        cluster.zxc.online_stats.update_one(
            filter_dict,
            {"$inc": {"duration": 1}},  # здесь можно увеличить счётчик на 1
            upsert=True
        )
    except Exception as e:
        print("Error updating verify stat:", e)

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

class Comment(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Оставить отзыв', custom_id = 'comment_verify', emoji = f'{files.find_one({"_id": "star"})["emoji_take"]}'))

class SupportCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        custom_id = inter.component.custom_id

        if custom_id.endswith("support"):
            member = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))

            if custom_id == "verify_support":
                now = datetime.now()
                day = f"{now.strftime('%A')}, {now.strftime('%B')} {now.day}"
                time = f"{now.strftime('%H:%M')}"

                im = Image.open(f"action_zxc/verification.png")

                draw_text_with_offset(im, str(day), 710, 76, font_size=32)
                draw_text_with_offset(im, str(time), 708, 120, font_size=96)

                width = 110
                height = 110
                avatar_x = 137
                avatar_y = 139

                Image.open(requests.get(member.display_avatar.url, stream = True).raw).resize((width, height)).save('avatars/avatar_profile_zxc.png')
                mask_im = Image.new("L", Image.open("avatars/avatar_profile_zxc.png").size)
                ImageDraw.Draw(mask_im).ellipse((0, 0, width, height), fill = 255)
                im.paste(Image.open('avatars/avatar_profile_zxc.png'), (avatar_x, avatar_y), mask_im)

                пользователь_name = f"{member.name[:13]}" if len(member.name) > 13 else f"{member.name}"
                draw_text_with_offset(im, пользователь_name, 412, 194.26, font_size=32)

                im.save(f'out/edit_role_{inter.author.id}.png')

                return await inter.response.edit_message(
                    attachments = None,
                    file=disnake.File(f"out/edit_role_{inter.author.id}.png"),
                    view=Verification()
                )
            
            if custom_id == "twink_support":
                now = datetime.now()
                day = f"{now.strftime('%A')}, {now.strftime('%B')} {now.day}"
                time = f"{now.strftime('%H:%M')}"

                im = Image.open(f"action_zxc/verification.png")

                draw_text_with_offset(im, str(day), 710, 76, font_size=32)
                draw_text_with_offset(im, str(time), 708, 120, font_size=96)

                width = 110
                height = 110
                avatar_x = 137
                avatar_y = 139

                Image.open(requests.get(member.display_avatar.url, stream = True).raw).resize((width, height)).save('avatars/avatar_profile_zxc.png')
                mask_im = Image.new("L", Image.open("avatars/avatar_profile_zxc.png").size)
                ImageDraw.Draw(mask_im).ellipse((0, 0, width, height), fill = 255)
                im.paste(Image.open('avatars/avatar_profile_zxc.png'), (avatar_x, avatar_y), mask_im)

                # Получаем данные из коллекции twink по _id участника
                db_entry = cluster.zxc.twink.find_one({"_id": str(member.id)})

                if db_entry is None or not db_entry.get("twink"):
                    twink_list = []  # Если записи нет, или список пустой
                else:
                    twink_list = db_entry["twink"]

                coordinates = [
                    {
                        "name_x": 300, "name_y": 407,
                        "id_x": 523, "id_y": 407,
                        "avatar_x": 117, "avatar_y": 350,
                        "avatar_w": 70, "avatar_h": 70
                    },
                    {
                        "name_x": 954, "name_y": 407,
                        "id_x": 1177, "id_y": 407,
                        "avatar_x": 771, "avatar_y": 350,
                        "avatar_w": 70, "avatar_h": 70
                    },
                    {
                        "name_x": 300, "name_y": 571,
                        "id_x": 523, "id_y": 571,
                        "avatar_x": 117, "avatar_y": 514,
                        "avatar_w": 70, "avatar_h": 70
                    },
                    {
                        "name_x": 954, "name_y": 571,
                        "id_x": 1177, "id_y": 571,
                        "avatar_x": 771, "avatar_y": 514,
                        "avatar_w": 70, "avatar_h": 70
                    }
                ]

                # Проходим по первым 4 твинкам
                for i, twink_str in enumerate(twink_list[:4]):
                    # Предполагаем, что строка имеет формат "<@123456789>\n"
                    twink_id = int(twink_str.strip().replace("<@", "").replace(">", ""))
                    twink_member = disnake.utils.get(inter.guild.members, id=twink_id)
                    if not twink_member:
                        continue  # Если участник не найден, пропускаем
                    
                    coords = coordinates[i]

                    # Загружаем аватар и изменяем размер по заданным координатам
                    response = requests.get(twink_member.display_avatar.url, stream=True)
                    avatar_img = Image.open(response.raw).resize((coords["avatar_w"], coords["avatar_h"]))

                    # Создаем круглую маску для аватара
                    mask_im = Image.new("L", (coords["avatar_w"], coords["avatar_h"]))
                    ImageDraw.Draw(mask_im).ellipse((0, 0, coords["avatar_w"], coords["avatar_h"]), fill=255)

                    # Вставляем аватар на основное изображение (im)
                    im.paste(avatar_img, (coords["avatar_x"], coords["avatar_y"]), mask_im)

                    # Получаем имя участника и обрезаем, если оно длинное
                    twink_name = twink_member.name if len(twink_member.name) <= 13 else twink_member.name[:13]
                    draw_text_with_offset(im, twink_name, coords["name_x"], coords["name_y"], font_size=25)

                    # Рисуем ID участника
                    draw_text_with_offset(im, str(twink_member.id), coords["id_x"], coords["id_y"], font_size=25)

                пользователь_name = f"{member.name[:13]}" if len(member.name) > 13 else f"{member.name}"
                draw_text_with_offset(im, пользователь_name, 412, 194.26, font_size=32)

                im.save(f'out/twink_sup_{inter.author.id}.png')

                return await inter.response.edit_message(
                    attachments = None,
                    file=disnake.File(f"out/twink_sup_{inter.author.id}.png"),
                    view=Twink()
                )
            
            if custom_id == "info_support":
                pass
            if custom_id == "nedopysk_support":
                now = datetime.now()
                day = f"{now.strftime('%A')}, {now.strftime('%B')} {now.day}"
                time = f"{now.strftime('%H:%M')}"

                im = Image.open(f"action_zxc/nedopysk.png")

                draw_text_with_offset(im, str(day), 710, 76, font_size=32)
                draw_text_with_offset(im, str(time), 708, 120, font_size=96)

                width = 110
                height = 110
                avatar_x = 137
                avatar_y = 139

                Image.open(requests.get(member.display_avatar.url, stream = True).raw).resize((width, height)).save('avatars/avatar_profile_zxc.png')
                mask_im = Image.new("L", Image.open("avatars/avatar_profile_zxc.png").size)
                ImageDraw.Draw(mask_im).ellipse((0, 0, width, height), fill = 255)
                im.paste(Image.open('avatars/avatar_profile_zxc.png'), (avatar_x, avatar_y), mask_im)

                пользователь_name = f"{member.name[:13]}" if len(member.name) > 13 else f"{member.name}"
                draw_text_with_offset(im, пользователь_name, 412, 194.26, font_size=32)

                im.save(f'out/edit_role_{inter.author.id}.png')

                return await inter.response.edit_message(
                    attachments = None,
                    file=disnake.File(f"out/edit_role_{inter.author.id}.png"),
                    view=Nedopysk()
                )

            if custom_id.endswith("verify_support"):
                await inter.response.defer()

                embed = disnake.Embed(color = 3092790)
                embed.set_author(name = f"Верификация | {inter.guild.name}", icon_url = inter.guild.icon.url)

                пользователь = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))

                if custom_id == "male_verify_support":
                    gender = 'Мужская'
                    embed = disnake.Embed(color=disnake.Color.blue())
                    await пользователь.add_roles(disnake.utils.get(inter.guild.roles, id=config['male']))
                    await пользователь.remove_roles(disnake.utils.get(inter.guild.roles, id=config['unverify']))
                elif custom_id == "female_verify_support":
                    gender = "Женская"
                    embed = disnake.Embed(color=disnake.Color.purple())
                    await пользователь.add_roles(inter.guild.get_role(config['female']))
                    await пользователь.remove_roles(inter.guild.get_role(config['unverify']))
                else:
                    gender = "Не указан"  # Если custom_id не совпадает, подставляем значение по умолчанию
                    embed = disnake.Embed(color=disnake.Color.default())

                if cluster.zxc.balls.count_documents({"_id": str(inter.author.id)}) == 0:
                    cluster.zxc.balls.insert_one({"_id": str(inter.author.id), "balls": 0})

                now = datetime.utcnow()
                day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

                update_stat({"user_id": str(inter.author.id), "category": "give_verify", "period": "day", "date": day_start})

                cluster.zxc.balls.update_one({"_id": str(inter.author.id)}, {"$inc": {"balls": +1}})

                embed.add_field(name="Пользователь:", value=f"> {пользователь.mention} | {пользователь}", inline=False)
                embed.add_field(name="Саппорт:", value=f"> {inter.author.mention} | {inter.author}", inline=False)
                embed.add_field(name="Гендер:", value=f"> {gender} гендер", inline=False)
                embed.set_image(url = "https://i.ibb.co/fkPw2Lf/bg23232.png")
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                embed.set_author(name = f"Верификация | {inter.guild.name}", icon_url = inter.guild.icon.url)
                await inter.message.edit(embed=embed, view = GiveVerify())

                await self.bot.get_channel(config['reviews_channel']).send(embed=embed) # Логи

                try:
                    embed = disnake.Embed(description = f'{пользователь.mention}, Вас **верифицировал** {inter.author.mention}, можете оставить отзыв, **нажав** на кнопку **ниже**', timestamp = datetime.utcnow(), color = 3092790)
                    embed.set_author(name = f"Добро пожаловать на {inter.guild}", icon_url = inter.guild.icon.url)
                    embed.set_thumbnail(url = пользователь.display_avatar.url)
                    msg = await пользователь.send(embed=embed, view = Comment())

                    cluster.zxc.target.update_one({'_id': str(пользователь.id)}, {'$set': {'member': inter.author.id}}, upsert = True)

                    await msg.pin()
                except:
                    pass

            if custom_id.endswith("twink_support"):
                if custom_id == "add_twink_support":
                    return await inter.response.send_modal(title=f"Добавить твинк", custom_id = "add_twink_support", components=[
                        disnake.ui.TextInput(label="Айди пользователя", custom_id = "Айди пользователя", style=disnake.TextInputStyle.short, max_length=40)])
                if custom_id == "remove_twink_support":
                    return await inter.response.send_modal(title=f"Удалить твинк", custom_id = "remove_twink_support", components=[
                        disnake.ui.TextInput(label="Айди пользователя", custom_id = "Айди пользователя", style=disnake.TextInputStyle.short, max_length=40)])
            
    @commands.Cog.listener()
    async def on_modal_submit(self, inter):
        custom_id = inter.custom_id

        if custom_id == "comment_verify":
            pass

        if custom_id.endswith("twink_support"):
            member = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))

            embed = disnake.Embed(color = 3092790, timestamp = datetime.utcnow())
            embed.set_thumbnail(url = inter.author.display_avatar.url).set_author(name = f"Твинки | {member.name}", icon_url = inter.guild.icon.url)
            embed.set_footer(text = f"Запросил(а) {inter.author}", icon_url = inter.author.display_avatar.url)

            for key, value in inter.text_values.items():
                twink = value

            if custom_id == 'add_twink_support':
                cluster.zxc.twink.update_one({"_id": str(member.id)}, {"$push": {"twink": f"<@{twink}>\n"}})
                embed.description = f"{inter.author.mention}, **Вы** успешно **добавили** твинк <@{twink}> пользователю {member.mention}"

                main = disnake.utils.get(inter.guild.members, id = int(twink))
                for role in main.roles:
                    if role.id in config['ban']:
                        embed.description = f"У **пользователя** {member.mention}, на **основном** аккаунте {main.mention}, **обнаружены нарушения**, верификация **невозможна**!"
                        break
                    
            elif custom_id == 'remove_twink_support':
                cluster.zxc.twink.update_one({'_id': str(member.id)}, {'$pull': {'twink': f"<@{twink}>\n"}}, upsert = True)
                embed.description = f"{inter.author.mention}, **Вы** успешно **удалили** твинк <@{twink}> пользователю {member.mention}"

            return await inter.send(embed=embed, ephemeral = True)

    @commands.Cog.listener()
    async def on_dropdown(self, inter):
        custom_id = inter.values[0]

        if custom_id.endswith("nedopysk_support"):
            embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790, timestamp = datetime.utcnow())
            embed.set_author(name = f"Недопуск | {inter.guild.name}", icon_url = inter.guild.icon.url)
            embed.set_thumbnail(url = inter.author.display_avatar.url)

            if not inter.message.content == inter.author.mention:
                embed.description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**'
                return await inter.send(ephemeral = True, embed=embed)
            
            пользователь = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))
            await пользователь.add_roles(disnake.utils.get(inter.guild.roles, id = int(config['nedopysk'])))

            пользователь = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))
            await пользователь.remove_roles(disnake.utils.get(inter.guild.roles, id = int(config['unverify'])))

            cluster.zxc.unverify.update_one({'_id': str(пользователь.id)}, {'$set': {'unverify': 1}}, upsert = True)

            if custom_id ==  'neadkvat_nedopysk_support':
                reason = "Неадекват"
                new_date = datetime.now().replace(microsecond=0) + timedelta(days=14)
            if custom_id ==  'menshe_nedopysk_support':
                reason = "Меньше 13 лет"
                new_date = datetime.now().replace(microsecond=0) + timedelta(days=365)
            if custom_id == "no_microphone_nedopysk_support":
                reason = "Без микрофона"
                new_date = datetime.now().replace(microsecond=0) + timedelta(days=7)
            if custom_id == "swastika_nedopysk_support":
                reason = "Свастика"
                new_date = datetime.now().replace(microsecond=0) + timedelta(days=7)
            if custom_id == "nick_nedopysk_support":
                reason = "Ник"
                new_date = datetime.now().replace(microsecond=0) + timedelta(days=7)
            if custom_id == "numbers_nedopysk_support":
                reason = "Цифры"
                new_date = datetime.now().replace(microsecond=0) + timedelta(days=7)
            if custom_id == "avatrka_nedopysk_support":
                reason = "Аватарка"
                new_date = datetime.now().replace(microsecond=0) + timedelta(days=7)
            if custom_id == "obxod_nedopysk_support":
                reason = "Обход"
                new_date = datetime.now().replace(microsecond=0) + timedelta(days=1000)
            if custom_id == "reload_nedopysk_support":
                reason = "Перезаходы"
                new_date = datetime.now().replace(microsecond=0) + timedelta(days=14)

            cluster.zxc.noverify.update_one({'_id': str(пользователь.id)}, {'$set': {'time': new_date}}, upsert = True)

            try:
                embed.description = f"{пользователь.mention}, **Вам** выдали недопуск до **{new_date}** по причине"
                embed.add_field(name='> ・Причина', value = f'```{reason}```', inline = False)
                embed.add_field(name='> ・Модератор', value = f'{inter.author.mention}', inline = False)
                await пользователь.send(embed=embed, view = Invitelink(inter.guild.id))
            except:
                pass

            embed.description = f'{inter.author.mention}, вы успешно выдали недопуск пользователю {пользователь.mention} на **{new_date}**'
            await inter.send(embed=embed, ephemeral = True)

            embed.description = ""
            embed.add_field(name='> ・Нарушитель', value = f'{пользователь.mention}', inline = False)
            await self.bot.get_channel(config['mod_log']).send(embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(SupportCog(bot))