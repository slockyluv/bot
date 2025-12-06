import pymongo
import disnake
import datetime
import json
import requests
import os
import asyncio
import random
from disnake.ext import commands
from typing import Optional
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

files = db.files_moderation

mod_currentPage = {}
mod_items_per_page = 10
mod_selectedPeriod = {}
mod_customPeriod = {}

mod_agg_mapping = {
    "top_staff_verify": {
        "match": {"category": "give_verify"},
        "group_field": "user_id",
        "emoji": f'{files.find_one({"_id": "verify"})["emoji_take"]}'
    },
    "top_staff_voice": {
        "match": {"category": "global"},
        "group_field": "user_id",
        "emoji": f'{files.find_one({"_id": "clock"})["emoji_take"]}'
    },
    "top_staff_support": {
        "match": {"category": "verify"},
        "group_field": "user_id",
        "emoji": f'{files.find_one({"_id": "clock"})["emoji_take"]}'
    },
    "top_staff_message": {
        "match": {"category": "message"},
        "group_field": "user_id",
        "emoji": f'{files.find_one({"_id": "message"})["emoji_take"]}'
    },
    "top_staff_balls": {
        "match": {"category": "balls"},
        "group_field": "user_id",
        "emoji": f'{files.find_one({"_id": "point"})["emoji_take"]}'
    },
    "top_staff_mutes": {
        "match": {"category": "mutes"},
        "group_field": "user_id",
        "emoji": f'{files.find_one({"_id": "micoff"})["emoji_take"]}'
    },
    "top_staff_bans": {
        "match": {"category": "bans"},
        "group_field": "user_id",
        "emoji": f'{files.find_one({"_id": "ban"})["emoji_take"]}'
    },
    "top_staff_warn": {
        "match": {"category": "warns"},
        "group_field": "user_id",
        "emoji": f'{files.find_one({"_id": "warn"})["emoji_take"]}'
    },
    "top_staff_warn_staff": {
        "match": {"category": "staff_warn"},
        "group_field": "user_id",
        "emoji": f'{files.find_one({"_id": "list"})["emoji_take"]}'
    },
    "top_mod_creative": {
        "match": {"category": "creative"},
        "group_field": "user_id",
        "emoji": f'{files.find_one({"_id": "creative"})["emoji_take"]}'
    },
    "top_mod_closer": {
        "match": {"category": "closer"},
        "group_field": "user_id",
        "emoji": f'{files.find_one({"_id": "closes"})["emoji_take"]}'
    },
    "top_mod_eventer": {
        "match": {"category": "eventer"},
        "group_field": "user_id",
        "emoji": f'{files.find_one({"_id": "event"})["emoji_take"]}'
    },
    "top_mod_events": {
        "match": {"category": "events"},
        "group_field": "user_id",
        "emoji": f'{files.find_one({"_id": "event"})["emoji_take"]}'
    },
    "top_mod_staff": {
        "match": {"category": "staff"},
        "group_field": "user_id",
        "emoji": f'{files.find_one({"_id": "moder"})["emoji_take"]}'
    },
    "top_mod_moderation": {
        "match": {"category": "staff"},
        "group_field": "user_id",
        "emoji": f'{files.find_one({"_id": "moder"})["emoji_take"]}'
    },
    "top_mod_helper": {
        "match": {"category": "staff"},
        "group_field": "user_id",
        "emoji": f'{files.find_one({"_id": "moder"})["emoji_take"]}'
    },
    "top_mod_tribune": {
        "match": {"category": "tribune"},
        "group_field": "user_id",
        "emoji": f'{files.find_one({"_id": "tribune"})["emoji_take"]}'
    }
}

def get_mod_top_data(category, period_selection, group_field, author_id=None):
    now = datetime.utcnow()
    
    def day_bounds(dt):
        s = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        e = s + timedelta(days=1)
        return s, e

    # Базовый match для всех запросов
    base_match = {"category": category}
    
    if period_selection == "День":
        start, end = day_bounds(now)
        # Убираем фильтр по period, добавляем только фильтр по дате
        base_match.update({"date": {"$gte": start, "$lt": end}})
        
    elif period_selection == "Неделя":
        start = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        base_match.update({"date": {"$gte": start, "$lt": end}})
        
    elif period_selection == "Месяц":
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if month_start.month == 12:
            next_month = month_start.replace(year=month_start.year+1, month=1)
        else:
            next_month = month_start.replace(month=month_start.month+1)
        base_match.update({"date": {"$gte": month_start, "$lt": next_month}})
        
    elif period_selection == "Всё время":
        # Оставляем только фильтр по категории
        pass
        
    elif period_selection == "Свой период":
        if not author_id or str(author_id) not in mod_customPeriod:
            return []
        start_date, end_date = mod_customPeriod[str(author_id)]
        start = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = end_date.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        base_match.update({"date": {"$gte": start, "$lt": end}})
    else:
        return []

    # Добавляем фильтр для валидных user_id (исключаем null и пустые строки)
    base_match[group_field] = {"$ne": None, "$ne": ""}

    pipeline = [
        {"$match": base_match},
        {"$group": {
            "_id": f"${group_field}", 
            "total": {"$sum": "$duration"}
        }},
        {"$sort": {"total": -1}},
        # Добавляем лимит для производительности
        {"$limit": 1000}
    ]
    
    # Для отладки - выведите pipeline в лог
    print(f"Pipeline for {category}, {period_selection}: {pipeline}")
    
    try:
        results = list(db.online_stats.aggregate(pipeline))
        # Фильтруем результаты от невалидных user_id
        valid_results = []
        for res in results:
            user_id = res["_id"]
            if user_id and str(user_id).isdigit():
                valid_results.append((user_id, res["total"]))
        
        return valid_results
    except Exception as e:
        print(f"Error in aggregation: {e}")
        return []



async def build_mod_top_embed(
    category: str,
    author_id: int,
    page: int = 0,
    guild: Optional[disnake.Guild] = None
):
    mapping = mod_agg_mapping.get(category)
    if not mapping:
        embed = disnake.Embed(
            title="Ошибка",
            description="Неизвестная категория топа.",
            color=0xFF0000
        )
        return embed, 1

    period = mod_selectedPeriod.get(str(author_id), "Всё время")
    top_data = get_mod_top_data(
        mapping["match"]["category"],
        period,
        mapping["group_field"],
        author_id
    )

    totals = {}
    for uid, total in top_data:
        if uid is None:
            continue
        try:
            uid_int = int(uid)
        except Exception:
            continue
        totals[uid_int] = totals.get(uid_int, 0) + (total or 0)
    top_data = sorted(totals.items(), key=lambda x: x[1], reverse=True)

    if category == "top_mod_moderation" and guild is not None:
        role_id = int(config.get('moderator'))
        role = guild.get_role(role_id) if role_id else None
        print(role.id)
        if role:
            allowed_ids = {member.id for member in role.members}
            top_data = [(uid, total) for uid, total in top_data if uid in allowed_ids]

    if category == "top_mod_eventer" and guild is not None:
        role_id = config.get('eventer')
        role = guild.get_role(role_id) if role_id else None
        if role:
            allowed_ids = {member.id for member in role.members}
            top_data = [(uid, total) for uid, total in top_data if uid in allowed_ids]

    if category == "top_mod_helper" and guild is not None:
        role_id = config.get('helper')
        role = guild.get_role(role_id) if role_id else None
        if role:
            allowed_ids = {member.id for member in role.members}
            top_data = [(uid, total) for uid, total in top_data if uid in allowed_ids]

    if category == "top_staff_support" and guild is not None:
        role_id = config.get('support')
        role = guild.get_role(role_id) if role_id else None
        if role:
            allowed_ids = {member.id for member in role.members if not member.bot}
            existing_ids = {int(uid) for uid, _ in top_data if uid is not None}
            # вместо insert_one в базу — просто дополняем локально нулями
            for member in role.members:
                if member.bot:
                    continue
                if member.id not in existing_ids:
                    top_data.append((member.id, 0))
            # пересобираем totals как раньше
            totals = {}
            for uid, total in top_data:
                try:
                    uid_int = int(uid)
                except Exception:
                    continue
                totals[uid_int] = totals.get(uid_int, 0) + (total or 0)
            top_data = sorted(totals.items(), key=lambda x: x[1], reverse=True)
            top_data = [(uid, total) for uid, total in top_data if uid in allowed_ids]

    if not top_data:
        embed = disnake.Embed(
            title=f"Топ ({period})",
            description="Данные не найдены.",
            color=0x2ECC71
        )
        embed.set_footer(text="Обновлено: " + datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        return embed, 1

    total_sum = sum(value for _, value in top_data)
    if mapping["match"]["category"] in {
        "give_verify", "message", "balls", "mutes", "warns", "bans", "staff_warn", "events"
    }:
        total_display = str(total_sum)
    else:
        total_hours = total_sum // 3600
        total_minutes = (total_sum % 3600) // 60
        total_display = f"{total_hours}ч {total_minutes}м"

    embed = disnake.Embed(
        title=f"Топ ({period})",
        description=f"Общее количество: {mapping['emoji']} {total_display}\n\n",
        color=0x2ECC71
    )

    pages = [top_data[i:i + mod_items_per_page] for i in range(0, len(top_data), mod_items_per_page)]
    total_pages = max(1, len(pages))
    page = max(0, min(page, total_pages - 1))
    current = pages[page]

    for idx, (uid, value) in enumerate(current, start=1 + page * mod_items_per_page):
        if mapping["match"]["category"] in {
            "give_verify", "message", "balls", "mutes", "warns", "bans", "staff_warn", "events"
        }:
            display_value = value
        else:
            hours = value // 3600
            minutes = (value % 3600) // 60
            display_value = f"{hours}ч {minutes}м"
        embed.description += f"{idx}. <@{uid}> {mapping['emoji']} {display_value}\n"

    embed.set_footer(
        text=f"Страница {page + 1} из {total_pages}. Обновлено: " +
             datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    )
    return embed, total_pages

class ActionListTopDropdown(disnake.ui.Select):
    def __init__(self):
        options = [
            disnake.SelectOption(
                label="Верификация",
                value="top_staff_verify",
                description="Топ по верификации",
                emoji=f'{files.find_one({"_id": "verify"})["emoji_take"]}'
            ),
            disnake.SelectOption(
                label="Онлайн",
                value="top_staff_voice",
                description="Топ по войсу",
                emoji=f'{files.find_one({"_id": "clock"})["emoji_take"]}'
            ),
            disnake.SelectOption(
                label="Саппортский онлайн",
                value="top_staff_support",
                description="Топ по саппортскому онлайн",
                emoji=f'{files.find_one({"_id": "clock"})["emoji_take"]}'
            ),
            disnake.SelectOption(
                label="Сообщения",
                value="top_staff_message",
                description="Топ по сообщениям",
                emoji=f'{files.find_one({"_id": "message"})["emoji_take"]}'
            ),
            disnake.SelectOption(
                label="Баллы",
                value="top_staff_balls",
                description="Топ по баллам",
                emoji=f'{files.find_one({"_id": "point"})["emoji_take"]}'
            ),
            disnake.SelectOption(
                label="Муты",
                value="top_staff_mutes",
                description="Топ по выдаче мутов",
                emoji=f'{files.find_one({"_id": "micoff"})["emoji_take"]}'
            ),
            disnake.SelectOption(
                label="Баны",
                value="top_staff_bans",
                description="Топ по выдаче банов",
                emoji=f'{files.find_one({"_id": "ban"})["emoji_take"]}'
            ),
            disnake.SelectOption(
                label="Варны",
                value="top_staff_warn",
                description="Топ по выдаче варнов",
                emoji=f'{files.find_one({"_id": "warn"})["emoji_take"]}'
            ),
            disnake.SelectOption(
                label="Выговоры",
                value="top_staff_warn_staff",
                description="Топ по выговорам",
                emoji=f'{files.find_one({"_id": "list"})["emoji_take"]}'
            ),
            disnake.SelectOption(
                label="Креатив",
                value="top_mod_creative",
                description="Топ по креативу",
                emoji=f'{files.find_one({"_id": "creative"})["emoji_take"]}'
            ),
            disnake.SelectOption(
                label="Клозер",
                value="top_mod_closer",
                description="Топ по клозеру",
                emoji=f'{files.find_one({"_id": "closes"})["emoji_take"]}'
            ),
            disnake.SelectOption(
                label="Ивентер",
                value="top_mod_eventer",
                description="Топ по ивентерам",
                emoji=f'{files.find_one({"_id": "event"})["emoji_take"]}'
            ),
            disnake.SelectOption(
                label="Ивентер",
                value="top_mod_events",
                description="Топ по ивентам",
                emoji=f'{files.find_one({"_id": "event"})["emoji_take"]}'
            ),
            disnake.SelectOption(
                label="Стaфф",
                value="top_mod_staff",
                description="Топ по модер войсам",
                emoji=f'{files.find_one({"_id": "staff"})["emoji_take"]}'
            ),
            disnake.SelectOption(
                label="Модератор",
                value="top_mod_moderation",
                description="Топ по модераторам",
                emoji=f'{files.find_one({"_id": "staff"})["emoji_take"]}'
            ),
            disnake.SelectOption(
                label="Хелперы",
                value="top_mod_helper",
                description="Топ по хелперам",
                emoji=f'{files.find_one({"_id": "moder"})["emoji_take"]}'
            ),
            disnake.SelectOption(
                label="Трибун",
                value="top_mod_tribune",
                description="Топ по трибюну",
                emoji=f'{files.find_one({"_id": "tribune"})["emoji_take"]}'
            )
        ]
        super().__init__(placeholder="Выберите категорию топа", custom_id="top_staff", options=options)

    async def callback(self, inter: disnake.MessageInteraction):
        mod_currentPage[str(inter.author.id)] = 0
        category = self.values[0]
        embed, total_pages = await build_mod_top_embed(category, inter.author.id, 0, inter.guild)
        await inter.response.send_message(embed=embed, ephemeral=True, view=ModerationTopView(inter.author.id, category, total_pages))

class ActionListTop(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ActionListTopDropdown())

class ModerationTopView(disnake.ui.View):
    def __init__(self, author: int, category: str, total_pages: int):
        super().__init__()
        self.author = author
        self.category = category
        self.total_pages = total_pages
        self.add_item(ModPeriodSelectButton(author, category))
        self.add_item(ModRefreshButton(author, category))
    
    async def update_view(self, inter: disnake.MessageInteraction):
        current_page = mod_currentPage.get(str(self.author), 0)
        embed, total_pages = await build_mod_top_embed(self.category, self.author, current_page, inter.guild)
        self.total_pages = total_pages
        self.first_page.disabled = (current_page == 0)
        self.prev_page.disabled = (current_page == 0)
        self.next_page.disabled = (current_page >= total_pages - 1)
        self.last_page.disabled = (current_page >= total_pages - 1)
        await inter.response.edit_message(embed=embed, view=self)
    
    @disnake.ui.button(style=disnake.ButtonStyle.secondary, emoji="⏮", custom_id="mod_top_first_page")
    async def first_page(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        mod_currentPage[str(self.author)] = 0
        await self.update_view(inter)
    
    @disnake.ui.button(style=disnake.ButtonStyle.secondary, emoji="◀️", custom_id="mod_top_prev_page")
    async def prev_page(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        current = mod_currentPage.get(str(self.author), 0)
        if current > 0:
            mod_currentPage[str(self.author)] = current - 1
        await self.update_view(inter)
    
    @disnake.ui.button(style=disnake.ButtonStyle.red, emoji="❌", custom_id="mod_top_exit")
    async def exit_page(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.message.delete()
    
    @disnake.ui.button(style=disnake.ButtonStyle.secondary, emoji="▶️", custom_id="mod_top_next_page")
    async def next_page(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        current = mod_currentPage.get(str(self.author), 0)
        if current < self.total_pages - 1:
            mod_currentPage[str(self.author)] = current + 1
        await self.update_view(inter)
    
    @disnake.ui.button(style=disnake.ButtonStyle.secondary, emoji="⏭", custom_id="mod_top_last_page")
    async def last_page(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        mod_currentPage[str(self.author)] = self.total_pages - 1
        await self.update_view(inter)

class ModPeriodSelectButton(disnake.ui.Button):
    def __init__(self, author: int, category: str):
        super().__init__(style=disnake.ButtonStyle.primary, label="Выбрать период", custom_id="mod_period_select")
        self.author = author
        self.category = category
    
    async def callback(self, inter: disnake.MessageInteraction):
        view = disnake.ui.View()
        view.add_item(ModPeriodSelect(self.category, self.author))
        await inter.response.send_message("Выберите период:", view=view, ephemeral=True)

class ModPeriodSelect(disnake.ui.Select):
    def __init__(self, category: str, author: int):
        options = [
            disnake.SelectOption(label="День", value="День", description="Статистика за день"),
            disnake.SelectOption(label="Неделя", value="Неделя", description="Статистика за неделю"),
            disnake.SelectOption(label="Месяц", value="Месяц", description="Статистика за месяц"),
            disnake.SelectOption(label="Всё время", value="Всё время", description="Статистика за всё время"),
            disnake.SelectOption(label="Свой период", value="Свой период", description="Задайте собственный диапазон")
        ]
        super().__init__(placeholder="Выберите период", min_values=1, max_values=1, options=options)
        self.category = category
        self.author = author
    
    async def callback(self, inter: disnake.MessageInteraction):
        selected = self.values[0]
        if selected == "Свой период":
            await inter.response.send_modal(title="Выбрать свой период топа",custom_id="custom_period_modal",components=[
            disnake.ui.TextInput(
                label="Начало периода (YYYY-MM-DD)",
                custom_id="start_date",
                style=disnake.TextInputStyle.short,
                placeholder="Например, 2025-03-01"
            ),
            disnake.ui.TextInput(
                label="Конец периода (YYYY-MM-DD)",
                custom_id="end_date",
                style=disnake.TextInputStyle.short,
                placeholder="Например, 2025-03-10"
            ),
            ])
        else:
            mod_selectedPeriod[str(self.author)] = selected
            await inter.response.send_message(
                f"Период изменён на: **{selected}**\nНажмите **Обновить**, чтобы обновить топ.",
                ephemeral=True
            )

class ModRefreshButton(disnake.ui.Button):
    def __init__(self, author: int, category: str):
        super().__init__(style=disnake.ButtonStyle.secondary, label="Обновить", custom_id="mod_top_refresh", emoji="🔄")
        self.author = author
        self.category = category
    
    async def callback(self, inter: disnake.MessageInteraction):
        current_page = mod_currentPage.get(str(self.author), 0)
        embed, total_pages = await build_mod_top_embed(self.category, self.author, current_page, inter.guild)
        await inter.response.edit_message(embed=embed, view=ModerationTopView(self.author, self.category, total_pages))

class ModerationTopCogs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_dropdown(self, inter: disnake.MessageInteraction):
        if inter.data.get("custom_id") == "top_staff":
            category = inter.values[0]
            mod_currentPage[str(inter.author.id)] = 0
            embed, total_pages = await build_mod_top_embed(category, inter.author.id, 0, inter.guild)
            await inter.response.send_message(embed=embed, ephemeral=True, view=ModerationTopView(inter.author.id, category, total_pages))

    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        custom_id = inter.component.custom_id

        if custom_id == 'places_action':
            if inter.message.content != inter.author.mention:
                embed = disnake.Embed(
                    description=f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**',
                    color=3092790
                )
                embed.set_author(name=f"Стафф топы | {inter.guild.name}", icon_url=inter.guild.icon.url)
                embed.set_thumbnail(url=inter.author.display_avatar.url)
                return await inter.send(ephemeral=True, embed=embed)

            from bson import ObjectId
            
            # 1) Посмотреть сам документ (тот, что вы привели)
            doc = db.online_stats.find_one({"_id": ObjectId("68bf6e1dee3ba5f23537d0a4")})
            print("Документ:", doc)
            
            # 2) Посмотреть сейчас (UTC) и границы дня, которые использует функция
            now = datetime.utcnow()
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
            print("UTC now:", now, "start:", start, "end:", end)
            
            # 3) Счётчик совпадений за этот UTC-день для категории global
            cnt = db.online_stats.count_documents({"category": "global", "date": {"$gte": start, "$lt": end}})
            print("count_documents(category='global', date >= start < end):", cnt)
            
            # 4) Проверка, попадает ли конкретный документ в этот диапазон
            doc_matches = db.online_stats.count_documents({"_id": ObjectId("68bf6e1dee3ba5f23537d0a4"),
                                                            "date": {"$gte": start, "$lt": end}})
            print("Этот документ попадает в UTC-диапазон (0/1):", doc_matches)
            
            # 5) Альтернативно — если даты в базе хранятся в локальном (naive) времени:
            now_local = datetime.now()
            s_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
            e_local = s_local + timedelta(days=1)
            print("local now:", now_local, "local start:", s_local, "local end:", e_local)
            cnt_local = db.online_stats.count_documents({"category": "global", "date": {"$gte": s_local, "$lt": e_local}})
            print("count local:", cnt_local)


            embed = disnake.Embed(
                description=f'{inter.author.mention}, **Выберите** топ, который вы хотите посмотреть',
                color=3092790
            )
            embed.set_author(name=f"Стафф топы | {inter.guild.name}", icon_url=inter.guild.icon.url)
            embed.set_thumbnail(url=inter.author.display_avatar.url)
            await inter.send(embed=embed, view=ActionListTop(), ephemeral=True)
    
    @commands.Cog.listener()
    async def on_modal_submit(self, inter: disnake.ModalInteraction):
        if inter.custom_id != "custom_period_modal":
            return
        start_date_str = inter.text_values.get("start_date")
        end_date_str = inter.text_values.get("end_date")
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError:
            return await inter.response.send_message("Неверный формат дат. Используйте формат YYYY-MM-DD.", ephemeral=True)
        mod_customPeriod[str(inter.author.id)] = (start_date, end_date)
        mod_selectedPeriod[str(inter.author.id)] = "Свой период"
        await inter.response.send_message(
            f"Пользовательский период установлен: с {start_date_str} по {end_date_str}.\nНажмите **Обновить**, чтобы обновить топ.",
            ephemeral=True
        )

def setup(bot: commands.Bot):
    bot.add_cog(ModerationTopCogs(bot))