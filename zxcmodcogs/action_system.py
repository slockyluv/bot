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
database = cluster.zxc
files = cluster.zxc.files_moderation

class DataBaseDeleteDropdown(disnake.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="Выберите коллекцию",
            options = [
                disnake.SelectOption(label="Личная комната", value = 'room_delete_action', description="Удалить личную комнату", emoji = f'{files.find_one({"_id": "database"})["emoji_take"]}'),
                disnake.SelectOption(label="Лав рума", value = 'love_room_action', description="Удалить лав руму", emoji = f'{files.find_one({"_id": "database"})["emoji_take"]}'),
                disnake.SelectOption(label="История наказаний", value = 'delete_history_mod', description = "Удалить историю наказаний пользователя", emoji = f'{files.find_one({"_id": "database"})["emoji_take"]}'),
                disnake.SelectOption(label="История браков", value = 'delete_history_marry', description = "Удалить историю браков пользователя", emoji = f'{files.find_one({"_id": "database"})["emoji_take"]}'),
                disnake.SelectOption(label="История переводов", value = 'delete_history_transfer', description = "Удалить историю переводов пользователя", emoji = f'{files.find_one({"_id": "database"})["emoji_take"]}'),
            ],
        )
        
class DataBaseDelete(disnake.ui.View):
    def __init__(self): 
        super().__init__()
        self.add_item(DataBaseDeleteDropdown())

class DataBaseAction(disnake.ui.View):
    def __init__(self): 
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Выдача', custom_id = 'give_db', emoji = f'{files.find_one({"_id": "plus"})["emoji_take"]}', row = 0))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Аннулирование', custom_id = 'delete_db', emoji = f'{files.find_one({"_id": "minus"})["emoji_take"]}', row = 0))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Продление', custom_id = 'expand_db', emoji = f'{files.find_one({"_id": "clock"})["emoji_take"]}', row = 0))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Очистка лишних данных', custom_id = 'clear_db', emoji = f'{files.find_one({"_id": "basket"})["emoji_take"]}', row=1, disabled = True))

class SystemAction(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style=ButtonStyle.secondary, label='Зарплата', custom_id='salary_action', emoji=f'{files.find_one({"_id": "take"})["emoji_take"]}', row = 0))
        self.add_item(disnake.ui.Button(style=ButtonStyle.secondary, label='База данных', custom_id='database_action', emoji=f'{files.find_one({"_id": "basket"})["emoji_take"]}', row = 0))

class DataBaseReset(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(DataBaseResetDropdown())

class DataBaseExpandDropdown(disnake.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="Выберите коллекцию",
            options = [
                disnake.SelectOption(label="Личную комнату", value = 'room_expand', description="Продлить личную комнату", emoji = f'{files.find_one({"_id": "database"})["emoji_take"]}'),
                disnake.SelectOption(label="Личную роль", value = 'role_expand', description="Продлить личную роль", emoji = f'{files.find_one({"_id": "database"})["emoji_take"]}'),
                disnake.SelectOption(label="Лав руму", value = 'love_room_expand', description="Продлить лав руму", emoji = f'{files.find_one({"_id": "database"})["emoji_take"]}'),
            ],
        )
        
class DataBaseExpand(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(DataBaseExpandDropdown())
        
class DataBaseGiveDropdown(disnake.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="Выберите коллекцию",
            options = [
                disnake.SelectOption(label="Онлайн", value = 'online_give', description="Выдать онлайн", emoji = f'{files.find_one({"_id": "database"})["emoji_take"]}'),
                disnake.SelectOption(label="Сообщения", value = 'message_give', description="Выдать сообщения", emoji = f'{files.find_one({"_id": "database"})["emoji_take"]}'),
                disnake.SelectOption(label="Уровень", value = 'level_give', description="Выдать уровень", emoji = f'{files.find_one({"_id": "database"})["emoji_take"]}'),
                disnake.SelectOption(label="Опыт", value = 'exp_give', description="Выдать опыт", emoji = f'{files.find_one({"_id": "database"})["emoji_take"]}'),
                disnake.SelectOption(label="Кейсы", value = 'case_give', description="Выдать кейс", emoji = f'{files.find_one({"_id": "database"})["emoji_take"]}'),
                disnake.SelectOption(label="Баллы", value = 'balls_give', description="Выдать баллы", emoji = f'{files.find_one({"_id": "database"})["emoji_take"]}'),
                disnake.SelectOption(label="Выдать лав руму", value = 'marry_give', description="Выдать без согласия другого пользователя", emoji = f'{files.find_one({"_id": "database"})["emoji_take"]}'),
            ],
        )
        
class DataBaseGive(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(DataBaseGiveDropdown())

class DataBaseDeleteDropdown(disnake.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="Выберите коллекцию",
            options = [
                disnake.SelectOption(label="Личная комната", value = 'room_delete_action', description="Удалить личную комнату", emoji = f'{files.find_one({"_id": "database"})["emoji_take"]}'),
                disnake.SelectOption(label="Лав рума", value = 'love_room_action', description="Удалить лав руму", emoji = f'{files.find_one({"_id": "database"})["emoji_take"]}'),
                disnake.SelectOption(label="История наказаний", value = 'delete_history_mod', description = "Удалить историю наказаний пользователя", emoji = f'{files.find_one({"_id": "database"})["emoji_take"]}'),
                disnake.SelectOption(label="История браков", value = 'delete_history_marry', description = "Удалить историю браков пользователя", emoji = f'{files.find_one({"_id": "database"})["emoji_take"]}'),
                disnake.SelectOption(label="История переводов", value = 'delete_history_transfer', description = "Удалить историю переводов пользователя", emoji = f'{files.find_one({"_id": "database"})["emoji_take"]}'),
            ],
        )
        
class DataBaseDelete(disnake.ui.View):
    def __init__(self): 
        super().__init__()
        self.add_item(DataBaseDeleteDropdown())

class SystemActionCogs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        custom_id = inter.component.custom_id

        if custom_id == 'system_action':
            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(title = 'Система', description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.send(ephemeral = True, embed=embed)
            
            embed = disnake.Embed(
                description = f'> {inter.author.mention}, **Выберите** действие с системой', 
                color = 3092790
            ).set_footer(text = 'Команда работает только для уполномоченных пользователей.', icon_url = "https://cdn.discordapp.com/emojis/1000345530670518322.webp?size=96&quality=lossless")
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            embed.set_author(name = f"Система на сервере {inter.guild.name}", icon_url = inter.guild.icon.url)
            await inter.send(embed=embed, content = inter.author.mention, view = SystemAction(), ephemeral=True)

        if custom_id.endswith("db"):
            пользователь = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))
            if custom_id.endswith("db"):
                if not inter.message.content == inter.author.mention:
                   embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790)
                   embed.set_thumbnail(url = inter.author.display_avatar.url)
                   embed.set_author(name = f"База данных на сервере {inter.guild.name}", icon_url = inter.guild.icon.url)
                   return await inter.send(ephemeral = True, embed=embed)

            if custom_id == "clear_db":
                economy_count = 0
                message_count = 0
                online_count = 0
                love_count = 0
                anti_crash_count = 0

                embed = disnake.Embed(description = f'### <a:waiting:1143927212291129374> Очищаю экономику', color = 3092790)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                embed.set_author(name = f"Очистка базы данных {inter.guild.name}", icon_url = inter.guild.icon.url)
                await inter.response.edit_message(embed=embed, components = [])

                for x in cluster.zxc.economy.find():
                    member = disnake.utils.get(inter.guild.members, id = int(x['_id']))
                    if member is None or cluster.zxc.economy.find_one({'_id': str(x['_id'])})['balance'] == 0:
                        cluster.zxc.economy.delete_one({'_id': str(x['_id'])})
                        economy_count += 1
                for x in cluster.zxc.donate.find():
                    member = disnake.utils.get(inter.guild.members, id = int(x['_id']))
                    if member is None or cluster.zxc.donate.find_one({'_id': str(x['_id'])})['donate_balance'] == 0:
                        cluster.zxc.donate.delete_one({'_id': str(x['_id'])})
                        economy_count += 1

                embed = disnake.Embed(description = f'### <a:waiting:1143927212291129374> Очищаю сообщения', color = 3092790)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                embed.set_author(name = f"Очистка базы данных | {inter.guild.name}", icon_url = inter.guild.icon.url)
                await inter.message.edit(embed=embed)

                for x in cluster.zxc.message.find():
                    member = disnake.utils.get(inter.guild.members, id = int(x['_id']))
                    if member is None or cluster.zxc.message.find_one({'_id': str(x['_id'])})['message_count'] == 0:
                        cluster.zxc.message.delete_one({'_id': str(x['_id'])})
                        message_count += 1
                for x in cluster.zxc.message_week.find():
                    member = disnake.utils.get(inter.guild.members, id = int(x['_id']))
                    if member is None or cluster.zxc.message_week.find_one({'_id': str(x['_id'])})['message_count'] == 0:
                        cluster.zxc.message_week.delete_one({'_id': str(x['_id'])})
                        message_count += 1
                for x in cluster.zxc.message_month.find():
                    member = disnake.utils.get(inter.guild.members, id = int(x['_id']))
                    if member is None or cluster.zxc.message_month.find_one({'_id': str(x['_id'])})['message_count'] == 0:
                        cluster.zxc.message_month.delete_one({'_id': str(x['_id'])})
                        message_count += 1

                embed = disnake.Embed(description = f'### <a:waiting:1143927212291129374> Очищаю онлайн', color = 3092790)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                embed.set_author(name = f"Очистка базы данных | {inter.guild.name}", icon_url = inter.guild.icon.url)
                await inter.message.edit(embed=embed)

                for x in cluster.zxc.online.find():
                    member = disnake.utils.get(inter.guild.members, id = int(x['_id']))
                    if member is None or cluster.zxc.online.find_one({'_id': str(x['_id'])})['online'] == 0:
                        cluster.zxc.online.delete_one({'_id': str(x['_id'])})
                        online_count += 0
                for x in cluster.zxc.day.find():
                    member = disnake.utils.get(inter.guild.members, id = int(x['_id']))
                    if member is None or cluster.zxc.day.find_one({'_id': str(x['_id'])})['day'] == 0:
                        cluster.zxc.day.delete_one({'_id': str(x['_id'])})
                        online_count += 1

                embed = disnake.Embed(description = f'### <a:waiting:1143927212291129374> Очищаю лав румы', color = 3092790)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                embed.set_author(name = f"Очистка базы данных | {inter.guild.name}", icon_url = inter.guild.icon.url)
                await inter.message.edit(embed=embed)

                for x in cluster.zxc.marry.find():
                    member = disnake.utils.get(inter.guild.members, id = int(x['_id']))
                    if member is None or cluster.zxc.marry.find_one({'_id': str(x['_id'])})['love'] == "Отсутствует":
                        cluster.zxc.marry.delete_one({'_id': str(x['_id'])})
                        love_count += 1

                for x in cluster.zxc.love_online.find():
                    member = disnake.utils.get(inter.guild.members, id = int(x['_id']))
                    if member is None or cluster.zxc.love_online.find_one({'_id': str(x['_id'])})['Love_online'] == 0:
                        cluster.zxc.love_online.delete_one({'_id': str(x['_id'])})
                        love_count += 1

                embed = disnake.Embed(description = f'### <a:waiting:1143927212291129374> Очищаю анти краш (запись ролей)', color = 3092790)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                embed.set_author(name = f"Очистка базы данных | {inter.guild.name}", icon_url = inter.guild.icon.url)
                await inter.message.edit(embed=embed)

                for x in cluster.zxc.backup.find():
                    cluster.zxc.backup.delete_one({'_id': str(x['_id'])})
                    anti_crash_count += 1

                embed = disnake.Embed(description = f'### <a:waiting:1143927212291129374> Успешно выполнена очистка лишних файлов в базе данных.\n\n* Было удалено:\n * **{economy_count} economy записей** \
                                      \n * **{message_count} msg записей**\n * **{online_count} online записей**\n * **{love_count} love записей**\n * **{anti_crash_count} anti_crash записей** \
                                      \n  * Всего: **{economy_count + message_count + online_count + love_count + anti_crash_count} записей**', color = 3092790)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                embed.set_author(name = f"Очистка базы данных | {inter.guild.name}", icon_url = inter.guild.icon.url)
                await inter.message.edit(embed=embed)

            if custom_id == 'delete_db':
                embed = disnake.Embed(description = f'> {inter.author.mention}, **Выберите** что вы хотите удалить пользователю {пользователь.mention}', color = 3092790)
                embed.set_footer(text = 'Команда работает только для уполномоченных пользователей.')
                embed.set_author(name = f"Удалить на сервере {inter.guild}", icon_url = inter.guild.icon.url)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                await inter.response.edit_message(embed=embed, view = DataBaseDelete())

            if custom_id == 'expand_db':
                embed = disnake.Embed(description = f'> {inter.author.mention}, **Выберите** что вы хотите продлить пользователю {пользователь.mention}', color = 3092790)
                embed.set_author(name = f"Продлить на сервере {inter.guild}", icon_url = inter.guild.icon.url)
                embed.set_footer(text = 'Команда работает только для уполномоченных пользователей.')
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                await inter.response.edit_message(embed=embed, view = DataBaseExpand())

            if custom_id == 'give_db':
                embed = disnake.Embed(description = f'> {inter.author.mention}, **Выберите** что вы хотите выдать пользователю {пользователь.mention}', color = 3092790)
                embed.set_author(name = f"Выдать на сервере {inter.guild}", icon_url = inter.guild.icon.url)
                embed.set_footer(text = 'Команда работает только для уполномоченных пользователей.')
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                await inter.response.edit_message(embed=embed, view = DataBaseGive())

        if custom_id == 'salary_action':
            await inter.response.send_modal(title = "Выдать зарплату", custom_id = "action_selery", components=[
                disnake.ui.TextInput(label = "Сумма", placeholder = "Например: 4000", custom_id = "Сумма", style = disnake.TextInputStyle.short, max_length = 20),
                disnake.ui.TextInput(label = "Айди роли", placeholder = "Например: 849353684249083914", custom_id = "Айди роли", style = disnake.TextInputStyle.short, max_length = 20),
                ])

        if custom_id == 'delete_bd':
            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(title = 'База Данных', description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.send(ephemeral = True, embed=embed)
            
            embed = disnake.Embed(title = 'Удалить', description = f'> {inter.author.mention}, **Выберите** коллекцию', color = 3092790)
            embed.set_footer(text = 'Команда работает только для уполномоченных пользователей.')
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            await inter.response.edit_message(embed=embed, view = DataBaseDelete())

        if custom_id == 'database_action':
            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(title = 'База Данных', description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.send(ephemeral = True, embed=embed)
            
            embed = disnake.Embed(
                description = f'> {inter.author.mention}, **Выберите** действие с базой данных', 
                color = 3092790
            ).set_footer(text = 'Команда работает только для уполномоченных пользователей.').set_thumbnail(url = inter.author.display_avatar.url)
            embed.set_author(name = f"База данных на сервере {inter.guild.name}", icon_url = inter.guild.icon.url)
            await inter.response.edit_message(embed=embed, view = DataBaseAction())

    @commands.Cog.listener()
    async def on_modal_submit(self, inter):
        custom_id = inter.custom_id

        if custom_id[:15] == 'staff_blacklist':
            embed = disnake.Embed(description="", color = 3092790)
            embed.set_author(name = f"ЧС Staff | {inter.guild.name}", icon_url = inter.guild.icon.url)
            embed.set_footer(text = f'Запросил(а) {inter.author}', icon_url = inter.author.display_avatar.url)
        
            for role in inter.author.roles:
                if int(role.id) in config['own_roles'] or int(role.id) == config['administrator']:
                    if custom_id == "staff_blacklist_add":
                        id = 0
                        for key, value in inter.text_values.items():
                            if id == 0:
                                reason = value
                            else:
                                member = disnake.utils.get(inter.guild.members, id = int(value))
                            id += 1
                    else:
                        for key, value in inter.text_values.items():
                            member = disnake.utils.get(inter.guild.members, id = int(value))

                    highest_role_user1 = inter.author.top_role
                    highest_role_user2 = member.top_role

                    if highest_role_user1 > highest_role_user2:
                        if custom_id == "staff_blacklist_add":
                            cluster.zxc.staff_blacklist.update_one({'_id': str(inter.guild.id)}, {'$push': {'members': member.id}}, upsert = True)

                            await member.remove_roles(disnake.utils.get(inter.guild.roles, id = config['curator']))
                            await member.remove_roles(disnake.utils.get(inter.guild.roles, id = config['moderator']))
                            await member.remove_roles(disnake.utils.get(inter.guild.roles, id = config['master']))
                            await member.remove_roles(disnake.utils.get(inter.guild.roles, id = config['support']))
                            await member.remove_roles(disnake.utils.get(inter.guild.roles, id = config['closer']))
                            await member.remove_roles(disnake.utils.get(inter.guild.roles, id = config['eventer']))
                            await member.remove_roles(disnake.utils.get(inter.guild.roles, id = config['creative']))
                            await member.remove_roles(disnake.utils.get(inter.guild.roles, id = config['tribunemod']))
                            await member.remove_roles(disnake.utils.get(inter.guild.roles, id = config['staff_role']))

                            embed.set_thumbnail(url = member.display_avatar.url)
                            embed.description = f"{inter.author.mention}, **Вы** успешно добавили в **ЧС** {member.mention}!"
                            embed.add_field(name = "Причина", value = f"```{reason}```")
                            await inter.send(embed=embed, ephemeral = True)

                            embed.set_thumbnail(url = member.display_avatar.url)
                            embed.description = f"> Причина: {reason}"
                            embed.add_field(name = "Добавил в ЧС:", value = inter.author.mention)
                            embed.description = f"Привет {member.mention}, **Вы **были добавлены в **ЧС Staff** на сервере **{inter.guild.name}**!"
                            await member.send(embed=embed)

                            embed.set_thumbnail(url = member.display_avatar.url)
                            embed.add_field(name = "Удалил из ЧС:", value = inter.author.mention)
                            embed.add_field(name = "Администратор", value = member.mention)
                            await self.bot.get_channel(config['staff_blacklist_channel']).send(embed=embed)

                        if custom_id == "staff_blacklist_delete":
                            for key, value in inter.text_values.items():
                                member = disnake.utils.get(inter.guild.members, id = int(value))

                            cluster.zxc.staff_blacklist.update_one({'_id': str(inter.guild.id)}, {'$pull': {'members': member.id}}, upsert = True)

                            embed.set_thumbnail(url = member.display_avatar.url)
                            embed.description = f"{inter.author.mention}, **Вы** успешно удалили из **ЧС** {member.mention}!"
                            embed.add_field(name = "Причина", value = f"```{reason}```")
                            await inter.send(embed=embed, ephemeral = True)

                            embed.set_thumbnail(url = member.display_avatar.url)
                            embed.add_field(name = "Удалил из ЧС:", value = inter.author.mention)
                            embed.description = f"Привет {member.mention}, **Вы **были удалены из **ЧС Staff** на сервере **{inter.guild.name}**!"
                            await member.send(embed=embed)

                            embed.set_thumbnail(url = member.display_avatar.url)
                            embed.add_field(name = "Удалил из ЧС:", value = inter.author.mention)
                            embed.add_field(name = "Администратор", value = member.mention)
                            await self.bot.get_channel(config['staff_blacklist_channel']).send(embed=embed)

                    elif highest_role_user1 < highest_role_user2:
                        return await inter.response.send_message(f"Роль пользователя {member.mention} выше, чем роль пользователя {inter.author.mention}.")
                    else:
                        return await inter.response.send_message(f"Роли пользователя {inter.author.metion} и пользователя {member.mention} равны по иерархии.")

            return await inter.response.send_message(f"Роль пользователя {member.mention} выше, чем роль пользователя {inter.author.mention}.")

        if custom_id[-6:] == "expand":
            for key, value in inter.text_values.items():
                days = value

            seconds_in_a_day = 24 * 60 * 60
            total_seconds = int(days) * int(seconds_in_a_day)

            member = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))

            embed = disnake.Embed(color = 3092790)
            embed.set_footer(text = f"Команда работает только для уполномоченных пользователей.")
            embed.set_thumbnail(url = inter.author.display_avatar.url)

            if custom_id == "room_expand":
                cluster.zxc.role_plata.update_one({"_id": str(пользователь.id)}, {"$inc": {"time": +int(total_seconds)}})

                embed.description = f"{inter.author.mention}, **Вы** успешно продлили руму {member.mention} на **{value}** дней"
                embed.set_author(name = f"Продлить личную комнату | {inter.guild.name}", icon_url = inter.guild.icon.url)

            if custom_id == "role_expand":
                id = 0
                for key, value in inter.text_values.items():
                    if id == 0:
                        id_role = value
                    else:
                        days = value
                    id += 1

                seconds_in_a_day = 24 * 60 * 60
                total_seconds = days * seconds_in_a_day

                cluster.zxc.role_plata.update_one({"_id": str(id_role)}, {"$inc": {"time": +int(total_seconds)}})

                embed.description=f"{inter.author.mention}, **Вы** успешно продлили роль {member.mention} на **{days}** дней"
                embed.set_author(name = f"Продлить личную роль | {inter.guild.name}", icon_url = inter.guild.icon.url)

            if custom_id == "love_room_expand":
                embed.description=f"{inter.author.mention}, **Вы** успешно продлили лав руму {member.mention} на **{value}** дней"
                embed.set_author(name = f"Продлить лав руму | {inter.guild.name}", icon_url = inter.guild.icon.url)

            await inter.send(ephemeral = True, embed=embed)

        if custom_id[-4:] == 'give':
            for key, value in inter.text_values.items():
                value = value

            member = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))
            embed = disnake.Embed(color = 3092790)
            embed.set_footer(text = f"Команда работает только для уполномоченных пользователей.")
            embed.set_thumbnail(url = inter.author.display_avatar.url)

            if custom_id == "online_give":
                cluster.zxc.online.update_one({"_id": str(member.id)}, {"$inc": {"online": +int(value)}})
                embed.description = f"{inter.author.mention}, **Вы** успешно выдали онлайн {member.mention} в размере **{value}** секунд"
                embed.set_author(name = f"Выдать онлайн | {inter.guild.name}", icon_url = inter.guild.icon.url)
            if custom_id == "message_give":
                cluster.zxc.message.update_one({"_id": str(member.id)}, {"$inc": {"message_count": +int(value)}})
                embed.description=f"{inter.author.mention}, **Вы** успешно выдали сообщения {member.mention} в размере **{value}**"
                embed.set_author(name = f"Выдать сообщения | {inter.guild.name}", icon_url = inter.guild.icon.url)
            if custom_id == "level_give":
                cluster.zxc.lvl.update_one({"_id": str(member.id)}, {"$inc": {"lvl": +int(value)}})
                embed.description=f"{inter.author.mention}, **Вы** успешно выдали уровень {member.mention} в размере **{value}**"
                embed.set_author(name = f"Выдать уровень | {inter.guild.name}", icon_url = inter.guild.icon.url)
            if custom_id == "exp_give":
                cluster.zxc.lvl.update_one({"_id": str(member.id)}, {"$inc": {"exp": +int(value)}})
                embed.description=f"{inter.author.mention}, **Вы** успешно выдали опыт {member.mention} в размере **{value}**"
                embed.set_author(name = f"Выдать опыт | {inter.guild.name}", icon_url = inter.guild.icon.url)
            if custom_id == "case_give":
                cluster.zxc.case.update_one({"_id": str(member.id)}, {"$inc": {"count": +int(value)}})
                embed.description=f"{inter.author.mention}, **Вы** успешно выдали кейсы {member.mention} в размере **{value}**"
                embed.set_author(name = f"Выдать кейсы | {inter.guild.name}", icon_url = inter.guild.icon.url)
            if custom_id == "balls_give":
                cluster.zxc.balls.update_one({"_id": str(member.id)}, {"$inc": {"balls": +int(value)}})
                embed.description=f"{inter.author.mention}, **Вы** успешно выдали баллы {member.mention} в размере **{value}**"
                embed.set_author(name = f"Выдать баллы | {inter.guild.name}", icon_url = inter.guild.icon.url)

            if custom_id == "marry_give":
                id = 0
                for key, value in inter.text_values.items():
                    if id == 0:
                        пользователь = disnake.utils.get(inter.guild.members, id = int(value))
                    else:
                        author = disnake.utils.get(inter.guild.members, id = int(value))
                    id += 1

                marry_collection = database.marry
                history_marry_collection = database.history_marry

                author_id = str(author.id)
                user_id = str(пользователь.id)

                if history_marry_collection.count_documents({"_id": author_id}) == 0:
                    history_marry_collection.insert_one({"_id": author_id, "tip_data": [], "user": [], "brakov": 0})

                if history_marry_collection.count_documents({"_id": user_id}) == 0:
                    history_marry_collection.insert_one({"_id": user_id, "tip_data": [], "user": [], "brakov": 0})

                history_marry_collection.update_one(
                    {"_id": author_id},
                    {"$push": {"tip_data": f"Заключил(а) | `{datetime.now().strftime('%d.%m.%Y')}`"}}
                )
                history_marry_collection.update_one({"_id": author_id}, {"$push": {"user": int(user_id)}})

                history_marry_collection.update_one(
                    {"_id": user_id},
                    {"$push": {"tip_data": f"Заключил(а) | `{datetime.now().strftime('%d.%m.%Y')}`"}}
                )
                history_marry_collection.update_one({"_id": user_id}, {"$push": {"user": int(author_id)}})

                history_marry_collection.update_one({"_id": user_id}, {"$inc": {"brakov": +1}})
                history_marry_collection.update_one({"_id": author_id}, {"$inc": {"brakov": +1}})

                marry_collection.update_one({'_id': author_id}, {'$set': {'love': str(user_id)}}, upsert=True)
                marry_collection.update_one({'_id': user_id}, {'$set': {'love': str(author_id)}}, upsert=True)
                marry_collection.update_one({'_id': author_id}, {'$set': {'Time': datetime.now().strftime("%d.%m.%Y")}}, upsert=True)
                marry_collection.update_one({'_id': user_id}, {'$set': {'Time': datetime.now().strftime("%d.%m.%Y")}}, upsert=True)
                marry_collection.update_one({'_id': author_id}, {'$set': {'Online': 'Offline'}}, upsert=True)
                marry_collection.update_one({'_id': user_id}, {'$set': {'Online': 'Offline'}}, upsert=True)
                marry_collection.update_one({'_id': author_id}, {'$set': {'balance': 0}}, upsert=True)
                marry_collection.update_one({'_id': user_id}, {'$set': {'balance': 0}}, upsert=True)
                database.love_online.update_one({'_id': author_id}, {'$set': {'Love_online': 0}}, upsert=True)
                database.love_online.update_one({'_id': user_id}, {'$set': {'Love_online': 0}}, upsert=True)

                new_date = datetime.now().replace(microsecond=0) + timedelta(days=30)

                cluster.zxc.love_plata.update_one({'_id': str(author_id)}, {'$set': {'time': new_date}}, upsert = True)
                cluster.zxc.love_plata.update_one({'_id': str(user_id)}, {'$set': {'time': new_date}}, upsert = True)

                cluster.zxc.love_plata.update_one({'_id': str(author_id)}, {'$set': {'notification': "No"}}, upsert = True)
                cluster.zxc.love_plata.update_one({'_id': str(user_id)}, {'$set': {'notification': "No"}}, upsert = True)

                database.economy.update_one({"_id": str(user_id)}, {"$inc": {"balance": -2500}})
                database.history.update_one({"_id": str(user_id)}, {"$inc": {"loverooms": +2500}})

                user_id = str(inter.author.id)
                current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                win_entry = {'amount': 2500, 'date': current_date, 'title': "Списание с баланса", "description": "Создание брака marry"}

                if cluster.zxc.transactions_minus.count_documents({"_id": user_id}) == 0:
                    cluster.zxc.transactions_minus.insert_one({"_id": user_id, "history": []})

                cluster.zxc.transactions_minus.update_one({'_id': user_id}, {'$push': {'history': win_entry}})

                await author.add_roles(disnake.utils.get(inter.guild.roles, id=config['love_role']))
                await пользователь.add_roles(disnake.utils.get(inter.guild.roles, id=config['love_role']))

                embed.description=f"{inter.author.mention}, **Вы** успешно поженили <@{author.id}> <@{пользователь.id}>"
                embed.set_author(name = f"Выдать лав руму | {inter.guild.name}", icon_url = inter.guild.icon.url)
                await inter.send(ephemeral = True, embed=embed)

            await inter.response.edit_message(embed = embed)

            embed.color = disnake.Color.orange()
            await self.bot.get_channel(1383529893026857153).send(embed = embed)

        if custom_id == 'action_selery':
            id = 0
            for key, value in inter.text_values.items():
                if id == 0:
                    salary = value
                else:
                    role = disnake.utils.get(inter.guild.roles, id = int(value))
                id += 1

            embed = disnake.Embed(title = f"Выдать зарплату роли {role.name}", color = 3092790)
            embed.description = f"<a:waiting:1143927212291129374> {inter.author.mention}, **Подождите немного**, идет обработка запроса."
            await inter.response.edit_message(embed=embed, components = [])
            
            for member in role.members:
                try:
                    cluster.zxc.economy.update_one({"_id": str(member.id)}, {"$inc": {"balance": +int(salary)}})
                except:
                    pass

            embed.description = f"{inter.author.mention}, **Вы** успешно выдали зарплату роли**{role.name}!**"
            await inter.send(embed=embed, ephemeral = True)

        if custom_id[-6:] == 'delete': # последние 6 символов
            embed = disnake.Embed(color = 3092790)
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            embed.set_author(name = "Удаление", icon_url = inter.guild.icon.url)

            if not inter.message.content == inter.author.mention:
                embed.description = f"{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**"
                return await inter.send(ephemeral = True, embed=embed)

            if custom_id == 'id_channel_delete':
                for key, value in inter.text_values.items():
                    id_channel = value

                room_role = cluster.zxc.room.find_one({'_id': str(id_channel)})['Role']
                await disnake.utils.get(inter.guild.roles, id = int(room_role)).delete()

                cluster.zxc.roomcheck.update_one({'_id': str(inter.author.id)}, {'$pull': {'room': int(id_channel)}}, upsert = True)
                await self.bot.get_channel(int(id_channel)).delete()

                cluster.zxc.room.delete_one({'_id': str(inter.author.id)})
                cluster.zxc.roomweek.delete_one({'_id': str(id_channel)})

                embed.description = f'{inter.author.mention}, **Вы** успешно **удалили комнату!**'
                return await inter.message.edit(embed=embed)
            
            if custom_id == 'id_love_room_delete':
                for key, value in inter.text_values.items():
                    id_member = value

                пользователь = disnake.utils.get(inter.guild.members, id = int(id_member))

                user_id = cluster.zxc.marry.find_one({'_id': str(пользователь.id)})['love']

                embed =  disnake.Embed(description = f'{пользователь.mention}, Вы успешно развели {пользователь.mention} и <@{user_id}>!', color = 3092790)
                embed.set_author(name = "Брак", icon_url = inter.guild.icon.url)
                embed.set_footer(text = inter.author,icon_url = inter.author.display_avatar.url)
                await inter.response.edit_message(attachments=None, embed=embed, files = [], components = [])

                if cluster.zxc.balance.count_documents({"_id": str(inter.author.id)}) == 0: 
                    cluster.zxc.balance.insert_one({"_id": str(inter.author.id), "balance": 0})
                if cluster.zxc.balance.count_documents({"_id": str(user_id)}) == 0:
                    cluster.zxc.balance.insert_one({"_id": str(user_id), "balance": 0})

                cluster.zxc.economy.update_one({"_id": str(inter.author.id)},{"$inc": {"balance": +int(cluster.zxc.balance.find_one({"_id": str(inter.author.id)})["balance"])}})
                cluster.zxc.economy.update_one({"_id": str(user_id)},{"$inc": {"balance": +int(cluster.zxc.balance.find_one({"_id": str(user_id)})["balance"])}})

                await inter.author.remove_roles(disnake.utils.get(inter.guild.roles, id = config['love_role']))

                cluster.zxc.marry.delete_one({'_id': str(inter.author.id)})
                cluster.zxc.marry.delete_one({'_id': str(user_id)})

            for key, value in inter.text_values.items():
                member = value

            if custom_id == 'id_history_mod_delete':
                cluster.zxc.history_punishment.delete_one({'_id': str(member)})

                embed.description = f"{inter.author}, **Вы** успешно удалили историю наказаний <@{member}>"

            if custom_id == 'id_history_marry_delete':
                cluster.zxc.history_marry.delete_one({'_id': str(member)})

                embed.description = f"{inter.author}, **Вы** успешно удалили историю браков <@{member}>"

            if custom_id == 'id_history_transfer_delete':
                cluster.zxc.history_transactions.delete_one({'_id': str(member)})

                embed.description = f"{inter.author}, **Вы** успешно удалили историю транзакций <@{member}>"

            return await inter.message.edit(embed=embed)

    @commands.Cog.listener()
    async def on_dropdown(self, inter):
        custom_id = inter.values[0]

        if custom_id == 'room_delete_action':
            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(title = 'Удалить личную комнату', description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.send(ephemeral = True, embed=embed)
            
            await inter.response.send_modal(title=f"Айди канала", custom_id = "id_channel_delete", components=[disnake.ui.TextInput(label="Айди", placeholder="Например: 849353684249083914",custom_id = "Айди", style=disnake.TextInputStyle.short, max_length=25)])
        
        if custom_id == 'love_room_action':
            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(title = 'Удалить лав руму', description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.send(ephemeral = True, embed=embed)
            
            await inter.response.send_modal(title=f"Айди пользователя", custom_id = "id_love_room_delete", components=[
                disnake.ui.TextInput(label="Айди", placeholder="Например: 849353684249083914",custom_id = "Айди", style=disnake.TextInputStyle.short, max_length=25)])

        if custom_id[-6:] == "expand":
            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790)
                embed.set_author(name = f"Продлить на сервере {inter.guild.name}", icon_url = inter.guild.icon.url)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.send(ephemeral = True, embed=embed)
            
            пользователь = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))

            if custom_id == "room_expand":
                await inter.response.send_modal(title=f"Продлить руму {пользователь}", custom_id = "room_expand", components=[
                disnake.ui.TextInput(label="Дней", placeholder="Например: 5",custom_id = "Дней", style=disnake.TextInputStyle.short, max_length=6)])
            if custom_id == "role_expand":
                await inter.response.send_modal(title=f"Продлить роль", custom_id = "role_expand", components=[
                disnake.ui.TextInput(label="Айди роли", placeholder="Например: 849353684249083914",custom_id = "Айди роли", style=disnake.TextInputStyle.short, max_length=25),
                disnake.ui.TextInput(label="Дней", placeholder="Например: 5",custom_id = "Дней", style=disnake.TextInputStyle.short, max_length=6)])
            if custom_id == "love_room_expand":
                await inter.response.send_modal(title=f"Продлить лав руму {пользователь}", custom_id = "love_room_expand", components=[
                disnake.ui.TextInput(label="Дней", placeholder="Например: 5",custom_id = "Дней", style=disnake.TextInputStyle.short, max_length=5)])

        if custom_id[-4:] == "give":
            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790)
                embed.set_author(name = f"Выдать на сервере {inter.guild.name}", icon_url = inter.guild.icon.url)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.send(ephemeral = True, embed=embed)
            
            пользователь = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))

            if custom_id == "online_give":
                await inter.response.send_modal(title=f"Выдать онлайн {пользователь}", custom_id = "online_give", components=[
                disnake.ui.TextInput(label="Количество секунд", placeholder="Например: 6000",custom_id = "Количество секунд", style=disnake.TextInputStyle.short, max_length=6)])
            if custom_id == "message_give":
                await inter.response.send_modal(title=f"Выдать сообщения {пользователь}", custom_id = "message_give", components=[
                disnake.ui.TextInput(label="Количество сообщений", placeholder="Например: 6000",custom_id = "Количество сообщений", style=disnake.TextInputStyle.short, max_length=6)])
            if custom_id == "level_give":
                await inter.response.send_modal(title=f"Выдать уровень {пользователь}", custom_id = "level_give", components=[
                disnake.ui.TextInput(label="Количество уровней", placeholder="Например: 5",custom_id = "Количество уровней", style=disnake.TextInputStyle.short, max_length=5)])
            if custom_id == "exp_give":
                await inter.response.send_modal(title=f"Выдать опыт {пользователь}", custom_id = "exp_give", components=[
                disnake.ui.TextInput(label="Количество опыта", placeholder="Например: 1000",custom_id = "Количество опыта", style=disnake.TextInputStyle.short, max_length=6)])
            if custom_id == "case_give":
                await inter.response.send_modal(title=f"Выдать кейсы {пользователь}", custom_id = "case_give", components=[
                disnake.ui.TextInput(label="Количество кейсов", placeholder="Например: 999",custom_id = "Количество кейсов", style=disnake.TextInputStyle.short, max_length=6)])
            if custom_id == "balls_give":
                await inter.response.send_modal(title=f"Выдать баллы {пользователь}", custom_id = "balls_give", components=[
                disnake.ui.TextInput(label="Количество баллов", placeholder="Например: 999",custom_id = "Количество баллов", style=disnake.TextInputStyle.short, max_length=6)])
            if custom_id == "marry_give":
                await inter.response.send_modal(title=f"Выдать лав руму", custom_id = "marry_give", components=[
                disnake.ui.TextInput(label="Первый пользователь", placeholder="Айди пользователя",custom_id = "Первый пользователь", style=disnake.TextInputStyle.short, max_length=25),
                disnake.ui.TextInput(label="Второй пользователь", placeholder="Айди пользователя",custom_id = "Второй пользователь", style=disnake.TextInputStyle.short, max_length=25),
                ])

        if custom_id[:14] == 'delete_history':
            embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**',color = 3092790)
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            embed.set_author(name = "История наказаний", icon_url = inter.guild.icon.url)
        
            if not inter.message.content == inter.author.mention:
                embed.description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**'
                return await inter.send(ephemeral = True, embed=embed)

            if custom_id == 'delete_history_mod':
                await inter.response.send_modal(title=f"Айди пользователя", custom_id = "id_history_mod_delete", components=[disnake.ui.TextInput(label="Айди", placeholder="Например: 849353684249083914",custom_id = "Айди", style=disnake.TextInputStyle.short, max_length=25)])

            if custom_id == 'delete_history_marry':
                await inter.response.send_modal(title=f"Айди пользователя", custom_id = "id_history_marry_delete", components = [disnake.ui.TextInput(label = "Айди", placeholder="Например: 849353684249083914",custom_id = "Айди", style=disnake.TextInputStyle.short, max_length=25)])

            if custom_id == 'delete_history_transfer':
                await inter.response.send_modal(title = f"Айди пользователя", custom_id = "id_history_transfer_delete", components = [disnake.ui.TextInput(label = "Айди", placeholder="Например: 849353684249083914",custom_id = "Айди", style=disnake.TextInputStyle.short, max_length=25)])  

def setup(bot: commands.Bot):
    bot.add_cog(SystemActionCogs(bot))