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
rest_collection = cluster.zxc.rest  # Одна коллекция для всех групп

role_id = config['rest_role']

class Rest(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.green, label = 'Принять', custom_id = 'rest_action_accept', emoji = f'<:zxc3:1009168371213926452>'))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label = 'Отклонить', custom_id = 'rest_action_cancel', emoji = f'<:zxc2:1009168373936050206>'))

class RestYes(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.green, label = 'Принято', custom_id = 'rest_action_accept', emoji = f'<:zxc3:1009168371213926452>', disabled = True))

class RestNo(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label = 'Отклонено', custom_id = 'rest_action_accept', emoji = f'<:zxc3:1009168371213926452>', disabled = True))

class RestCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        custom_id = inter.component.custom_id

        if custom_id.startswith("rest"):
            embed = disnake.Embed(color=3092790)
            embed.set_author(name=f"Взять/Снять отпуск | {inter.guild.name}", icon_url=inter.guild.icon.url)
            embed.set_thumbnail(url=inter.author.display_avatar.url)

            if not custom_id == "rest_action_accept" or custom_id == "rest_action_cancel":
                if inter.message.content != inter.author.mention:
                    embed.description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**'
                    return await inter.send(ephemeral=True, embed=embed)

            # Получаем группу пользователя
            db_target = cluster.zxc.target.find_one({'_id': str(inter.author.id)})
            group_choice = db_target['group']

            # Проверяем, есть ли уже документ пользователя в коллекции
            user_rest_doc = rest_collection.find_one({
                'user_id': str(inter.author.id), 
                'group': group_choice
            })

            if custom_id == 'rest_action':
                # Если уже активен, предлагаем снять отпуск
                if user_rest_doc and user_rest_doc.get('rest') == 'Активен':
                    await inter.response.send_modal(
                        title="Снять отпуск",
                        custom_id="unrest",
                        components=[
                            disnake.ui.TextInput(
                                label="Причина", 
                                placeholder="Например: Освободился пораньше", 
                                custom_id="Причина отпуска",
                                style=disnake.TextInputStyle.short, 
                                max_length=50
                            )
                        ]
                    )
                    modal_inter: disnake.ModalInteraction = await self.bot.wait_for(
                        "modal_submit", 
                        check=lambda i: i.custom_id == "unrest" and i.author.id == inter.author.id
                    )

                    await inter.author.remove_roles(inter.guild.get_role(role_id))

                    reason = list(modal_inter.text_values.values())[0]

                    # Удаляем документ пользователя, отпуск снимается досрочно
                    rest_collection.delete_one({
                        'user_id': str(inter.author.id), 
                        'group': group_choice
                    })

                    embed.description = f'{inter.author.mention}, **Вы** успешно отменили отпуск **досрочно**'
                    await modal_inter.send(embed=embed, ephemeral=True)

                    embed.description = (
                        f"{inter.author.mention} | {inter.author.name} | **ID:** {inter.author.id} `снял отпуск досрочно`"
                    )
                    embed.add_field(name='> ・Причина', value=f"```diff\n- {reason}```")
                    return await self.bot.get_channel(config['rest_log']).send(embed=embed)

                # Если отпуск не активен – берём отпуск:
                await inter.response.send_modal(
                    title="Взять отпуск",
                    custom_id="rest",
                    components=[
                        disnake.ui.TextInput(
                            label="Причина", 
                            placeholder="Например: Уезжаю в другой город", 
                            custom_id="Причина отпуска",
                            style=disnake.TextInputStyle.short, 
                            max_length=50
                        ),
                        disnake.ui.TextInput(
                            label="🕖 Время отпуска", 
                            placeholder="Например: 1д или 1d", 
                            custom_id="Время отпуска",
                            style=disnake.TextInputStyle.short,
                            min_length=1, 
                            max_length=3
                        )
                    ]
                )
                modal_inter: disnake.ModalInteraction = await self.bot.wait_for(
                    "modal_submit", 
                    check=lambda i: i.custom_id == "rest" and i.author.id == inter.author.id
                )

                values = list(modal_inter.text_values.values())
                reason, time_str = values[0], values[1]

                # Преобразуем время (например, "1д" или "1d") в целое число дней
                if time_str[-1] in ['д', 'd']:
                    time_days = int(time_str[:-1])
                else:
                    time_days = int(time_str)

                # Считаем время окончания отпуска
                expires_at = datetime.now() + timedelta(days=time_days)

                # Отправляем заявку в админ-канал с кнопками для подтверждения/отклонения
                embed.description = f'### {inter.author.mention}, хочет взять отпуск'
                embed.add_field(name="Время", value=f"```{time_days} дней```")
                embed.add_field(name="Причина", value=f"```{reason}```")
                msg = await self.bot.get_channel(config['rest_channel']).send(embed=embed, view=Rest())

                # Сохраняем заявку с полями группы и пользователя
                rest_collection.insert_one({
                    "_id": str(msg.id),  # ID сообщения для связи с заявкой
                    "user_id": str(inter.author.id),
                    "group": group_choice,
                    "time": time_days,
                    "reason": reason,
                    "expires_at": expires_at,
                    "rest": "Заявка",  # Статус заявки
                    "created_at": datetime.now()
                })

                embed = disnake.Embed(
                    description=f"{inter.author.mention}, **Вы** успешно **отправили** заявку на **взятие отпуска**", 
                    color=3092790
                )
                embed.set_author(name=f"Отпуск | {inter.guild.name}", icon_url=inter.guild.icon.url)
                embed.add_field(name=f'> {files.find_one({"_id": "online"})["emoji_take"]} Время', value=f"```yaml\n{time_days} дней```")
                embed.set_thumbnail(url=inter.author.display_avatar.url)
                return await modal_inter.send(embed=embed, ephemeral=True)

            if custom_id == "rest_action_accept":
                # Обработка подтверждения заявки админом
                doc = rest_collection.find_one({'_id': str(inter.message.id)})
                if not doc:
                    return await inter.response.send_message("Запись не найдена или уже устарела.", ephemeral=True)

                user_id = doc['user_id']
                group = doc['group']
                time_days = doc['time']
                expires_at = doc['expires_at']

                # Обновляем статус отпуска на активен
                rest_collection.update_one(
                    {'_id': str(inter.message.id)}, 
                    {'$set': {
                        'rest': 'Активен',
                        'approved_by': str(inter.author.id),
                        'approved_at': datetime.now()
                    }}
                )

                # Создаем отдельную запись для активного отпуска пользователя
                new_date = datetime.now().replace(microsecond=0) + timedelta(days=time_days)
                try:
                    rest_collection.insert_one({
                        "_id": f"{user_id}_{group}",  # Уникальный ID для активного отпуска
                        "user_id": user_id,
                        "group": group,
                        "rest": "Активен",
                        "time": time_days,
                        "days": new_date,
                        "expires_at": expires_at,
                        "approved_by": str(inter.author.id),
                        "approved_at": datetime.now()
                    })
                except:
                    return await inter.send(content = f"{inter.author.mention}, **У этого** пользователя уже есть активный **отпуск!**", ephemeral = True)

                # Обновляем счетчик отпусков
                cluster.zxc.rest_count.update_one(
                    {"_id": user_id},
                    {"$push": {"data": f"<t:{int(new_date.timestamp())}:F>"}},
                    upsert=True
                )

                guild = self.bot.get_guild(config['server_id'])
                member = disnake.utils.get(guild.members, id=int(user_id))

                if member:
                    await member.add_roles(guild.get_role(role_id))

                    try:
                        embed.description = f"{member.mention}, {inter.author.mention} `одобрил вам отпуск`"
                        embed.add_field(name=f'> {files.find_one({"_id": "online"})["emoji_take"]} Время', value=f"```yaml\n{time_days} дней```")
                        await member.send(embed=embed)
                    except:
                        pass
                
                await inter.response.edit_message(content=f"{inter.author.mention} одобрил отпуск {member.mention}", view=RestYes())
                
                embed.description = f"{inter.author.mention} `одобрил отпуск` {member.mention}"
                return await self.bot.get_channel(config['rest_log']).send(embed=embed)

            if custom_id == "rest_action_cancel":
                doc = rest_collection.find_one({'_id': str(inter.message.id)})
                if doc:
                    user_id = doc['user_id']
                    time_days = doc['time']
                    
                    guild = self.bot.get_guild(config['server_id'])
                    member = disnake.utils.get(guild.members, id=int(user_id))
                    
                    # Удаляем заявку из коллекции
                    rest_collection.delete_one({'_id': str(inter.message.id)})
                    
                    if member:
                        try:
                            embed.description = f"{member.mention}, {inter.author.mention} `отклонил вам отпуск`"
                            embed.add_field(name=f'> {files.find_one({"_id": "online"})["emoji_take"]} Время', value=f"```yaml\n{time_days} дней```")
                            await member.send(embed=embed)
                        except:
                            pass

                    await inter.response.edit_message(
                        content=f"{inter.author.mention} отклонил отпуск {member.mention}", 
                        view=RestNo()
                    )


def setup(bot: commands.Bot):
    bot.add_cog(RestCog(bot))