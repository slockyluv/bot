import pymongo
import disnake
import datetime
import json
import asyncio
import random
from disnake.ext import commands
from disnake.enums import ButtonStyle, TextInputStyle
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import re

with open('configs/zxc.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
with open('configs/zxc_tokens.json', 'r', encoding='utf-8') as f:
    config1 = json.load(f)

cluster = pymongo.MongoClient(config1['mongodb'])
db = cluster.zxc
files = cluster.zxc.files_moderation

currentStaffBlacklistPage = {}

EXCLUDED_ROLES = {1384954166689923172, 999609135396032534, 1390137707014918299, 1383126511758082198, 1383126511762145330}

emoji_numbers = [
    "<:numberone:1328788490837692580>", "<:numbertwo:1328788502640328747>",
    "<:numberthree:1328788500765474869>", f"{files.find_one({'_id': 'four'})['emoji_take']}",
    f"{files.find_one({'_id': 'five'})['emoji_take']}", f"{files.find_one({'_id': 'six'})['emoji_take']}",
    f"{files.find_one({'_id': 'seven'})['emoji_take']}", f"{files.find_one({'_id': 'eight'})['emoji_take']}",
    f"{files.find_one({'_id': 'nine'})['emoji_take']}", f"{files.find_one({'_id': 'ten'})['emoji_take']}"
]

def get_effective_top_role(member):
    filtered_roles = [role for role in member.roles if role.id not in EXCLUDED_ROLES]
    if not filtered_roles:
        return member.guild.default_role
    return max(filtered_roles, key=lambda role: role.position)

class StaffBlackListMenu(disnake.ui.View):
    def __init__(self, author: int):
        super().__init__()

        if not str(author) in currentStaffBlacklistPage or currentStaffBlacklistPage[str(author)] == 0:
            self.add_item(disnake.ui.Button(
                style=disnake.ButtonStyle.secondary, 
                custom_id='staff_blacklist_first_page', 
                emoji=f"{files.find_one({'_id': 'double_left'})['emoji_take']}", 
                disabled=True
            ))
            self.add_item(disnake.ui.Button(
                style=disnake.ButtonStyle.secondary, 
                custom_id='staff_blacklist_prev_page', 
                emoji=f"{files.find_one({'_id': 'left'})['emoji_take']}", 
                disabled=True
            ))
        else:
            self.add_item(disnake.ui.Button(
                style=disnake.ButtonStyle.secondary, 
                custom_id='staff_blacklist_first_page', 
                emoji=f"{files.find_one({'_id': 'double_left'})['emoji_take']}"
            ))
            self.add_item(disnake.ui.Button(
                style=disnake.ButtonStyle.secondary, 
                custom_id='staff_blacklist_prev_page', 
                emoji=f"{files.find_one({'_id': 'left'})['emoji_take']}"
            ))
        self.add_item(disnake.ui.Button(
            style=disnake.ButtonStyle.red, 
            custom_id='exit_profile', 
            emoji=f"{files.find_one({'_id': 'basket'})['emoji_take']}"
        ))
        self.add_item(disnake.ui.Button(
            style=disnake.ButtonStyle.secondary, 
            custom_id='staff_blacklist_right_page', 
            emoji=f"{files.find_one({'_id': 'right'})['emoji_take']}"
        ))
        self.add_item(disnake.ui.Button(
            style=disnake.ButtonStyle.secondary, 
            custom_id='staff_blacklist_last_page', 
            emoji=f"{files.find_one({'_id': 'double_right'})['emoji_take']}"
        ))
        self.add_item(disnake.ui.Button(
            style=disnake.ButtonStyle.blurple, 
            label='Меню', 
            custom_id='staff_blacklist_menu', 
            emoji=f"{files.find_one({'_id': 'menu'})['emoji_take']}"
        ))

class StaffBlackList(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(
            style=disnake.ButtonStyle.secondary, 
            label='Добавить', 
            custom_id='staff_blacklist_add', 
            emoji='<:plus:1135581260950020177>'
        ))
        self.add_item(disnake.ui.Button(
            style=disnake.ButtonStyle.secondary, 
            label='Удалить', 
            custom_id='staff_blacklist_delete', 
            emoji='<:minus:1135581689536594050>'
        ))
        self.add_item(disnake.ui.Button(
            style=disnake.ButtonStyle.secondary, 
            label='Список ЧС', 
            custom_id='staff_blacklist', 
            emoji='<:list_fail:1096087494036029460>'
        ))
        self.add_item(disnake.ui.Button(
            style=disnake.ButtonStyle.secondary, 
            label='⠀⠀⠀⠀⠀⠀⠀⠀⠀', 
            custom_id='asfsaf', 
            row=1, 
            disabled=True
        ))
        self.add_item(disnake.ui.Button(
            style=disnake.ButtonStyle.secondary, 
            label='⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀', 
            custom_id='agsdfgf', 
            row=1, 
            disabled=True
        ))

class StaffChoiceBlackListMenu(disnake.ui.View):
    def __init__(self, author: int):
        super().__init__()
        # Кнопки навигации формируются одинаково для обоих вариантов (глобального и группового)
        if not str(author) in currentStaffBlacklistPage or currentStaffBlacklistPage[str(author)] == 0:
            self.add_item(disnake.ui.Button(
                style=disnake.ButtonStyle.secondary, 
                custom_id='staff_choice_blacklist_first_page', 
                emoji=f"{files.find_one({'_id': 'double_left'})['emoji_take']}", 
                disabled=True
            ))
            self.add_item(disnake.ui.Button(
                style=disnake.ButtonStyle.secondary, 
                custom_id='staff_choice_blacklist_prev_page', 
                emoji=f"{files.find_one({'_id': 'left'})['emoji_take']}", 
                disabled=True
            ))
        else:
            self.add_item(disnake.ui.Button(
                style=disnake.ButtonStyle.secondary, 
                custom_id='staff_choice_blacklist_first_page', 
                emoji=f"{files.find_one({'_id': 'double_left'})['emoji_take']}"
            ))
            self.add_item(disnake.ui.Button(
                style=disnake.ButtonStyle.secondary, 
                custom_id='staff_choice_blacklist_prev_page', 
                emoji=f"{files.find_one({'_id': 'left'})['emoji_take']}"
            ))
        self.add_item(disnake.ui.Button(
            style=disnake.ButtonStyle.red, 
            custom_id='exit_profile', 
            emoji=f"{files.find_one({'_id': 'basket'})['emoji_take']}"
        ))
        self.add_item(disnake.ui.Button(
            style=disnake.ButtonStyle.secondary, 
            custom_id='staff_choice_blacklist_right_page', 
            emoji=f"{files.find_one({'_id': 'right'})['emoji_take']}"
        ))
        self.add_item(disnake.ui.Button(
            style=disnake.ButtonStyle.secondary, 
            custom_id='staff_choice_blacklist_last_page', 
            emoji=f"{files.find_one({'_id': 'double_right'})['emoji_take']}"
        ))
        self.add_item(disnake.ui.Button(
            style=disnake.ButtonStyle.blurple, 
            label='Меню', 
            custom_id='staff_choice_blacklist_menu', 
            emoji=f"{files.find_one({'_id': 'menu'})['emoji_take']}"
        ))

class StaffChoiceBlackList(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(
            style=disnake.ButtonStyle.secondary, 
            label='Добавить', 
            custom_id='staff_choice_blacklist_add', 
            emoji='<:plus:1135581260950020177>'
        ))
        self.add_item(disnake.ui.Button(
            style=disnake.ButtonStyle.secondary, 
            label='Удалить', 
            custom_id='staff_choice_blacklist_delete', 
            emoji='<:minus:1135581689536594050>'
        ))
        self.add_item(disnake.ui.Button(
            style=disnake.ButtonStyle.secondary, 
            label='Список ЧС', 
            custom_id='staff_choice_blacklist', 
            emoji='<:list_fail:1096087494036029460>'
        ))
        self.add_item(disnake.ui.Button(
            style=disnake.ButtonStyle.secondary, 
            label='⠀⠀⠀⠀⠀⠀⠀⠀⠀', 
            custom_id='asfsaf', 
            row=1, 
            disabled=True
        ))
        self.add_item(disnake.ui.Button(
            style=disnake.ButtonStyle.secondary, 
            label='⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀', 
            custom_id='agsdfgf', 
            row=1, 
            disabled=True
        ))

class BlacklistCogs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        custom_id = inter.component.custom_id

        # Глобальный ЧС (staff_blacklist)
        if custom_id == "blacklist_action":
            embed = disnake.Embed(
                description=f'### {inter.author.mention}, **Выберите** действие, нажав на одну из кнопок ниже',
                color=3092790
            )
            embed.set_author(name="ЧС участников состава", icon_url=inter.guild.icon.url)
            embed.set_thumbnail(url=inter.author.display_avatar.url)
            return await inter.send(content=inter.author.mention, embed=embed, ephemeral=True, view=StaffBlackList())

        # Групповой ЧС: новый custom_id для выбора группы
        if custom_id == "blacklist_choice_action":
            # Получаем group_choice из базы (предполагается, что такой документ уже существует)
            db_target = cluster.zxc.target.find_one({'_id': str(inter.author.id)})
            if not db_target or 'group' not in db_target:
                return await inter.send("Ваша группа не указана в базе данных.", ephemeral=True)
            group_choice = db_target['group']
            blacklist_collection_name = f"blacklist_{group_choice}"
            # Если для данного сервера ещё нет документа в коллекции группы, создаём его
            if cluster.zxc[blacklist_collection_name].count_documents({"_id": str(inter.guild.id)}) == 0:
                cluster.zxc[blacklist_collection_name].insert_one({"_id": str(inter.guild.id), "members": []})
            
            embed = disnake.Embed(
                description=f'### {inter.author.mention}, **Выберите** действие для ЧС группы **{group_choice}**, нажав на одну из кнопок ниже',
                color=3092790
            )
            embed.set_author(name="ЧС группы", icon_url=inter.guild.icon.url)
            embed.set_thumbnail(url=inter.author.display_avatar.url)
            return await inter.send(content=inter.author.mention, embed=embed, ephemeral=True, view=StaffChoiceBlackList())

        # Обработка кнопок для глобального ЧС (custom_id начинается с "staff_blacklist")
        if custom_id.startswith('staff_blacklist'):
            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(
                    description=f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**',
                    color=3092790
                )
                embed.set_author(name=f"ЧС Staff {inter.guild.name}", icon_url=inter.guild.icon.url)
                embed.set_thumbnail(url=inter.author.display_avatar.url)
                return await inter.send(ephemeral=True, embed=embed)

            embed = disnake.Embed(color=3092790)
            embed.set_author(name="ЧС Staff", icon_url=inter.guild.icon.url)
            embed.set_thumbnail(url=inter.author.display_avatar.url)
            embed.set_footer(text=f'Запросил(а) {inter.author}', icon_url=inter.author.display_avatar.url)

            if cluster.zxc.staff_blacklist.count_documents({"_id": str(inter.guild.id)}) == 0:
                cluster.zxc.staff_blacklist.insert_one({"_id": str(inter.guild.id), "members": []})

            # Кнопка "Меню" для возврата в основное меню ЧС
            if custom_id == "staff_blacklist_menu":
                embed = disnake.Embed(
                    description=f'### {inter.author.mention}, **Выберите** действие, нажав на одну из кнопок ниже',
                    color=3092790
                )
                embed.set_author(name="ЧС участников состава", icon_url=inter.guild.icon.url)
                embed.set_thumbnail(url=inter.author.display_avatar.url)
                return await inter.response.edit_message(embed=embed, view=StaffBlackList())

            if custom_id == "staff_blacklist_add":
                return await inter.response.send_modal(
                    title="Добавить в ЧС стаффа",
                    custom_id="staff_blacklist_add",
                    components=[
                        disnake.ui.TextInput(
                            label="Причина",
                            placeholder="Например: Угроза доксом",
                            custom_id="Причина",
                            style=disnake.TextInputStyle.short,
                            max_length=20
                        ),
                        disnake.ui.TextInput(
                            label="Айди участника",
                            placeholder="Например: 849353684249083914",
                            custom_id="Айди участника",
                            style=disnake.TextInputStyle.short,
                            max_length=20
                        )
                    ]
                )

            if custom_id == "staff_blacklist_delete":
                return await inter.response.send_modal(
                    title="Удалить из ЧС стаффа",
                    custom_id="staff_blacklist_delete",
                    components=[
                        disnake.ui.TextInput(
                            label="Айди участника",
                            placeholder="Например: 849353684249083914",
                            custom_id="Айди участника",
                            style=disnake.TextInputStyle.short,
                            max_length=20
                        )
                    ]
                )

            await inter.response.defer()

            # Формирование списка участников ЧС (глобального)
            idd = 1
            members = cluster.zxc.staff_blacklist.find_one({'_id': str(inter.guild.id)})['members']
            description = f'### Всего участников в ЧС стаффа: {len(members)}\n\n'
            membersID = []
            items_per_page = 10
            for member_id in members:
                membersID.append(member_id)
            pages = [membersID[i:i + items_per_page] for i in range(0, len(membersID), items_per_page)]
            if not str(inter.author.id) in currentStaffBlacklistPage:
                currentStaffBlacklistPage[str(inter.author.id)] = 0
            for member_id in pages[currentStaffBlacklistPage[str(inter.author.id)]]:
                if idd >= len(emoji_numbers):
                    break
                description += f"**{emoji_numbers[idd]} — <@{member_id}>**\n\n"
                idd += 1

            embed.description = description
            return await inter.send(content=inter.author.mention, embed=embed, view=StaffBlackListMenu(inter.author.id), ephemeral=True)

        # Обработка кнопок для ЧС группы
        if custom_id.startswith('staff_choice_blacklist'):
            # Получаем group_choice и соответствующую коллекцию
            db_target = cluster.zxc.target.find_one({'_id': str(inter.author.id)})
            if not db_target or 'group' not in db_target:
                return await inter.send("Ваша группа не указана в базе данных.", ephemeral=True)
            group_choice = db_target['group']
            blacklist_collection_name = f"blacklist_{group_choice}"
            # Если для данного сервера ещё нет документа в коллекции группы, создаём его
            if cluster.zxc[blacklist_collection_name].count_documents({"_id": str(inter.guild.id)}) == 0:
                cluster.zxc[blacklist_collection_name].insert_one({"_id": str(inter.guild.id), "members": []})

            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(
                    description=f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**',
                    color=3092790
                )
                embed.set_author(name=f"ЧС группы {group_choice}", icon_url=inter.guild.icon.url)
                embed.set_thumbnail(url=inter.author.display_avatar.url)
                return await inter.send(ephemeral=True, embed=embed)

            embed = disnake.Embed(color=3092790)
            embed.set_author(name=f"ЧС группы {group_choice}", icon_url=inter.guild.icon.url)
            embed.set_thumbnail(url=inter.author.display_avatar.url)
            embed.set_footer(text=f'Запросил(а) {inter.author}', icon_url=inter.author.display_avatar.url)

            # Кнопка "Меню" для группового ЧС
            if custom_id == "staff_choice_blacklist_menu":
                embed = disnake.Embed(
                    description=f'### {inter.author.mention}, **Выберите** действие, нажав на одну из кнопок ниже',
                    color=3092790
                )
                embed.set_author(name=f"ЧС группы {group_choice}", icon_url=inter.guild.icon.url)
                embed.set_thumbnail(url=inter.author.display_avatar.url)
                return await inter.response.edit_message(embed=embed, view=StaffChoiceBlackList())

            if custom_id == "staff_choice_blacklist_add":
                return await inter.response.send_modal(
                    title=f"Добавить в ЧС группы {group_choice}",
                    custom_id="staff_choice_blacklist_add",
                    components=[
                        disnake.ui.TextInput(
                            label="Причина",
                            placeholder="Например: Нарушение правил",
                            custom_id="Причина",
                            style=disnake.TextInputStyle.short,
                            max_length=20
                        ),
                        disnake.ui.TextInput(
                            label="Айди участника",
                            placeholder="Например: 849353684249083914",
                            custom_id="Айди участника",
                            style=disnake.TextInputStyle.short,
                            max_length=20
                        )
                    ]
                )

            if custom_id == "staff_choice_blacklist_delete":
                return await inter.response.send_modal(
                    title=f"Удалить из ЧС группы {group_choice}",
                    custom_id="staff_choice_blacklist_delete",
                    components=[
                        disnake.ui.TextInput(
                            label="Айди участника",
                            placeholder="Например: 849353684249083914",
                            custom_id="Айди участника",
                            style=disnake.TextInputStyle.short,
                            max_length=20
                        )
                    ]
                )

            await inter.response.defer()

            # Формирование списка участников группового ЧС
            idd = 1
            members = cluster.zxc[blacklist_collection_name].find_one({'_id': str(inter.guild.id)})['members']
            description = f'### Всего участников в ЧС группы {group_choice}: {len(members)}\n\n'
            membersID = []
            items_per_page = 10
            for member_id in members:
                membersID.append(member_id)
            pages = [membersID[i:i + items_per_page] for i in range(0, len(membersID), items_per_page)]
            if not str(inter.author.id) in currentStaffBlacklistPage:
                currentStaffBlacklistPage[str(inter.author.id)] = 0

            for member_id in pages[currentStaffBlacklistPage[str(inter.author.id)]]:
                if idd >= len(emoji_numbers):
                    break
                description += f"**{emoji_numbers[idd]} — <@{member_id}>**\n\n"
                idd += 1

            embed.description = description
            return await inter.send(content=inter.author.mention, embed=embed, view=StaffChoiceBlackList(), ephemeral=True)

    @commands.Cog.listener()
    async def on_modal_submit(self, inter):
        custom_id = inter.custom_id

        if custom_id.startswith("staff_blacklist"):
            await inter.response.defer()

            embed = disnake.Embed(description="", color=3092790)
            embed.set_author(name=f"ЧС Staff | {inter.guild.name}", icon_url=inter.guild.icon.url)
            embed.set_footer(text=f'Запросил(а) {inter.author}', icon_url=inter.author.display_avatar.url)

            # Проверяем, что пользователь имеет необходимые роли
            for role in inter.author.roles:
                if int(role.id) in config['own_roles'] or int(role.id) == config['administrator']:
                    if custom_id == "staff_blacklist_add":
                        id = 0
                        for key, value in inter.text_values.items():
                            if id == 0:
                                reason = value
                            else:
                                member = disnake.utils.get(inter.guild.members, id=int(value))
                            id += 1
                    else:
                        for key, value in inter.text_values.items():
                            member = disnake.utils.get(inter.guild.members, id=int(value))

                    author_top_role = get_effective_top_role(inter.author)
                    member_top_role = get_effective_top_role(member)
                    
                    if author_top_role.position < member_top_role.position:
                        return await inter.send(
                            "Ваша роль ниже, вы не можете изменять роли этого участника.",
                            ephemeral=True
                        )

                    if custom_id == "staff_blacklist_add":
                        cluster.zxc.staff_blacklist.update_one(
                            {'_id': str(inter.guild.id)},
                            {'$push': {'members': member.id}},
                            upsert=True
                        )

                        await member.remove_roles(disnake.utils.get(inter.guild.roles, id=config['curator']))
                        await member.remove_roles(disnake.utils.get(inter.guild.roles, id=config['moderator']))
                        await member.remove_roles(disnake.utils.get(inter.guild.roles, id=config['master']))
                        await member.remove_roles(disnake.utils.get(inter.guild.roles, id=config['support']))
                        await member.remove_roles(disnake.utils.get(inter.guild.roles, id=config['closer']))
                        await member.remove_roles(disnake.utils.get(inter.guild.roles, id=config['eventer']))
                        await member.remove_roles(disnake.utils.get(inter.guild.roles, id=config['creative']))
                        await member.remove_roles(disnake.utils.get(inter.guild.roles, id=config['tribunemod']))
                        await member.remove_roles(disnake.utils.get(inter.guild.roles, id=config['staff_role']))

                        embed.set_thumbnail(url=member.display_avatar.url)
                        embed.description = f"{inter.author.mention}, **Вы** успешно добавили в **ЧС** {member.mention}!"
                        embed.add_field(name="Причина", value=f"```{reason}```")
                        await inter.send(embed=embed)

                        embed.set_thumbnail(url=member.display_avatar.url)
                        embed.description = f"> Причина: {reason}"
                        embed.add_field(name="Добавил в ЧС:", value=inter.author.mention)
                        embed.description = f"Привет {member.mention}, **Вы** были добавлены в **ЧС Staff** на сервере **{inter.guild.name}**!"
                        await member.send(embed=embed)

                        embed.set_thumbnail(url=member.display_avatar.url)
                        embed.add_field(name="Удалил из ЧС:", value=inter.author.mention)
                        embed.add_field(name="Администратор", value=member.mention)
                        return await self.bot.get_channel(config['staff_blacklist_channel']).send(embed=embed)

                    if custom_id == "staff_blacklist_delete":
                        for key, value in inter.text_values.items():
                            member = disnake.utils.get(inter.guild.members, id=int(value))

                        cluster.zxc.staff_blacklist.update_one(
                            {'_id': str(inter.guild.id)},
                            {'$pull': {'members': member.id}},
                            upsert=True
                        )

                        embed.set_thumbnail(url=member.display_avatar.url)
                        embed.description = f"{inter.author.mention}, **Вы** успешно удалили из **ЧС** {member.mention}!"
                        await inter.send(embed=embed)

                        embed.set_thumbnail(url=member.display_avatar.url)
                        embed.add_field(name="Удалил из ЧС:", value=inter.author.mention)
                        embed.description = f"Привет {member.mention}, **Вы** были удалены из **ЧС Staff** на сервере **{inter.guild.name}**!"
                        await member.send(embed=embed)

                        embed.set_thumbnail(url=member.display_avatar.url)
                        embed.add_field(name="Удалил из ЧС:", value=inter.author.mention)
                        embed.add_field(name="Администратор", value=member.mention)
                        return await self.bot.get_channel(config['staff_blacklist_channel']).send(embed=embed)

            return await inter.send(f"Роль пользователя {member.mention} выше, чем роль пользователя {inter.author.mention}.")

        # Обработка модальных окон для группового ЧС
        if custom_id.startswith("staff_choice_blacklist"):
            await inter.response.defer()

            # Получаем группу и коллекцию для группового ЧС
            db_target = cluster.zxc.target.find_one({'_id': str(inter.author.id)})
            if not db_target or 'group' not in db_target:
                return await inter.send("Ваша группа не указана в базе данных.", ephemeral=True)
            group_choice = db_target['group']
            blacklist_collection_name = f"blacklist_{group_choice}"

            embed = disnake.Embed(description="", color=3092790)
            embed.set_author(name=f"ЧС группы {group_choice} | {inter.guild.name}", icon_url=inter.guild.icon.url)
            embed.set_footer(text=f'Запросил(а) {inter.author}', icon_url=inter.author.display_avatar.url)

            for role in inter.author.roles:
                if int(role.id) in config['own_roles'] or int(role.id) == config['administrator']:
                    if custom_id == "staff_choice_blacklist_add":
                        id = 0
                        for key, value in inter.text_values.items():
                            if id == 0:
                                reason = value
                            else:
                                member = disnake.utils.get(inter.guild.members, id=int(value))
                            id += 1
                    else:
                        for key, value in inter.text_values.items():
                            member = disnake.utils.get(inter.guild.members, id=int(value))

                    author_top_role = get_effective_top_role(inter.author)
                    member_top_role = get_effective_top_role(member)
                    
                    if author_top_role.position < member_top_role.position:
                        return await inter.send(
                            "Ваша роль ниже, вы не можете изменять роли этого участника.",
                            ephemeral=True
                        )

                    if custom_id == "staff_choice_blacklist_add":
                        cluster.zxc[blacklist_collection_name].update_one(
                            {'_id': str(inter.guild.id)},
                            {'$push': {'members': member.id}},
                            upsert=True
                        )

                        await member.remove_roles(disnake.utils.get(inter.guild.roles, id=config['curator']))
                        await member.remove_roles(disnake.utils.get(inter.guild.roles, id=config['moderator']))
                        await member.remove_roles(disnake.utils.get(inter.guild.roles, id=config['master']))
                        await member.remove_roles(disnake.utils.get(inter.guild.roles, id=config['support']))
                        await member.remove_roles(disnake.utils.get(inter.guild.roles, id=config['closer']))
                        await member.remove_roles(disnake.utils.get(inter.guild.roles, id=config['eventer']))
                        await member.remove_roles(disnake.utils.get(inter.guild.roles, id=config['creative']))
                        await member.remove_roles(disnake.utils.get(inter.guild.roles, id=config['tribunemod']))
                        await member.remove_roles(disnake.utils.get(inter.guild.roles, id=config['staff_role']))

                        embed.set_thumbnail(url=member.display_avatar.url)
                        embed.description = f"{inter.author.mention}, **Вы** успешно добавили в **ЧС группы** {group_choice} {member.mention}!"
                        embed.add_field(name="Причина", value=f"```{reason}```")
                        await inter.send(embed=embed, ephemeral=True)

                        embed.set_thumbnail(url=member.display_avatar.url)
                        embed.description = f"> Причина: {reason}"
                        embed.add_field(name="Добавил в ЧС:", value=inter.author.mention)
                        embed.description = f"Привет {member.mention}, **Вы** были добавлены в **ЧС группы** {group_choice} на сервере **{inter.guild.name}**!"
                        await member.send(embed=embed)

                        embed.set_thumbnail(url=member.display_avatar.url)
                        embed.add_field(name="Удалил из ЧС:", value=inter.author.mention)
                        embed.add_field(name="Администратор", value=member.mention)
                        return await self.bot.get_channel(config['staff_blacklist_channel']).send(embed=embed)

                    if custom_id == "staff_choice_blacklist_delete":
                        for key, value in inter.text_values.items():
                            member = disnake.utils.get(inter.guild.members, id=int(value))

                        cluster.zxc[blacklist_collection_name].update_one(
                            {'_id': str(inter.guild.id)},
                            {'$pull': {'members': member.id}},
                            upsert=True
                        )

                        embed.set_thumbnail(url=member.display_avatar.url)
                        embed.description = f"{inter.author.mention}, **Вы** успешно удалили из **ЧС группы** {group_choice} {member.mention}!"
                        await inter.send(embed=embed, ephemeral=True)

                        embed.set_thumbnail(url=member.display_avatar.url)
                        embed.add_field(name="Удалил из ЧС:", value=inter.author.mention)
                        embed.description = f"Привет {member.mention}, **Вы** были удалены из **ЧС группы** {group_choice} на сервере **{inter.guild.name}**!"
                        await member.send(embed=embed)

                        embed.set_thumbnail(url=member.display_avatar.url)
                        embed.add_field(name="Удалил из ЧС:", value=inter.author.mention)
                        embed.add_field(name="Администратор", value=member.mention)
                        return await self.bot.get_channel(config['staff_blacklist_channel']).send(embed=embed)

            return await inter.send(f"У вас недостаточно прав чтобы кидать кого-то в ЧС стаффа", ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(BlacklistCogs(bot))