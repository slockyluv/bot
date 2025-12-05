import json
import re
from difflib import get_close_matches

import disnake
from disnake.ext import commands
import pymongo
from translate import Translator

def translate_text(text: str, target_language: str = "ru") -> str:
    try:
        return Translator(to_lang=target_language).translate(text)
    except:
        return text

def remove_special_characters(name: str) -> str:
    return re.sub(r'[^\w\s]', '', name).strip()

def paginate_text(text: str, max_length: int = 4000) -> list[str]:
    lines = text.split("\n")
    pages = []
    current = ""
    for line in lines:
        if len(current) + len(line) + 1 > max_length:
            pages.append(current)
            current = line
        else:
            current = (current + "\n" + line) if current else line
    if current:
        pages.append(current)
    return pages

class ConfigView(disnake.ui.View):
    def __init__(self, embeds: list[disnake.Embed], found: dict, missing: dict, author_id: int):
        super().__init__(timeout=None)
        self.embeds = embeds
        self.found = found    # {"roles": {...}, "channels": {...}, "categories": {...}, "logs": {...}}
        self.missing = missing
        self.author_id = author_id
        self.current = 0

        # Кнопки подтверждения и создания
        buttons = [
            ("roles_accept",      "Подтвердить изменения ролей"),
            ("channels_accept",   "Подтвердить изменения каналов"),
            ("categories_accept", "Подтвердить изменения категорий"),
            ("logs_accept",       "Подтвердить изменения логов"),
            ("roles_create",      "Создать недостающие роли"),
            ("channels_create",   "Создать недостающие каналы"),
            ("categories_create", "Создать недостающие категории"),
            ("logs_create",       "Создать недостающие логи"),
            ("manual_id",         "Добавить вручную ID"),
            ("check_config",      "Проверить значения конфига"),
        ]
        for cid, label in buttons:
            self.add_item(disnake.ui.Button(
                style=disnake.ButtonStyle.secondary,
                label=label,
                custom_id=cid
            ))

        # Навигация страниц
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.primary, label="◀️", custom_id="prev"))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.primary, label="▶️", custom_id="next"))

class BotConfig(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config_path = "configs/zxc.json"
        with open(self.config_path, encoding="utf-8") as f:
            self.config = json.load(f)
        with open("configs/zxc_tokens.json", encoding="utf-8") as f:
            self.tokens = json.load(f)
        self.db = pymongo.MongoClient(self.tokens['mongodb'])
        self.active: dict[int, tuple[ConfigView, commands.Context]] = {}

    def fuzzy_search(self, items: list, terms: dict[str, list[str]]) -> tuple[dict[str, int], set[str]]:
        found: dict[str, int] = {}
        missing = set(terms.keys())
        for item in items:
            clean_name = remove_special_characters(item.name.lower())
            for key, variants in terms.items():
                if key not in missing:
                    continue
                for v in variants:
                    v0 = v.lower()
                    if clean_name.startswith(v0[0]):
                        cleaned_variants = [remove_special_characters(x.lower()) for x in variants]
                        if get_close_matches(clean_name, cleaned_variants, n=1, cutoff=0.8):
                            found[key] = item.id
                            missing.discard(key)
                            break
        return found, missing

    @commands.slash_command(name="init", description="Инструкция по инициализации бота zxcmod")
    async def init(self, inter: disnake.ApplicationCommandInteraction):
        """Показывает пошаговую инструкцию по инициализации бота"""
        embed = disnake.Embed(
            title="🚀 Инструкция по инициализации бота zxcmod",
            description="Пошаговое руководство по запуску бота",
            color=0x2ECC71
        )
        
        embed.add_field(
            name="📋 Шаг 1: Настройка загрузки эмоджи",
            value=(
                "**1.1. Изменение ID бота в emoji.py**\n"
                "• Откройте файл `zxcmod/zxcmodcogs/emoji.py`\n"
                "• Найдите строку `APPLICATION_ID = \"1405674113887895634\"` (строка 25)\n"
                "• Замените значение на ID вашего бота (Application ID можно найти в Discord Developer Portal)\n\n"
                "**1.2. Изменение цвета эмоджи (опционально)**\n"
                "• Запустите бота\n"
                "• Выполните команду: `!change_color #HEX_КОД_ЦВЕТА`\n"
                "• Например: `!change_color #FF5733`\n\n"
                "**1.3. Загрузка эмоджи в бота**\n"
                "• Убедитесь, что все файлы эмоджи находятся в папке `images_upload`\n"
                "• Выполните команду: `!upload_emojis`\n"
                "• Бот загрузит до 2000 эмоджи в приложение бота"
            ),
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Шаг 2: Настройка конфигурации",
            value=(
                "**2.1. Настройка configs/zxc_tokens.json**\n"
                "• Убедитесь, что указаны правильные значения:\n"
                "  - `mongodb` - строка подключения к MongoDB\n"
                "  - `moderation` - токен бота для модерации\n\n"
                "**2.2. Настройка configs/zxc.json**\n"
                "• Используйте команду `!config_set` для автоматической настройки\n"
                "• Или настройте вручную, изменив значения в файле"
            ),
            inline=False
        )
        
        embed.add_field(
            name="▶️ Шаг 3: Запуск бота",
            value=(
                "1. Убедитесь, что MongoDB запущена и доступна\n"
                "2. Запустите бота командой:\n"
                "   ```bash\n"
                "   python zxcmod.py\n"
                "   ```"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📝 Порядок действий (кратко)",
            value=(
                "1. ✅ Изменить `APPLICATION_ID` в `zxcmod/zxcmodcogs/emoji.py`\n"
                "2. ✅ (Опционально) Выполнить `!change_color #HEX` для изменения цвета\n"
                "3. ✅ Выполнить `!upload_emojis` для загрузки эмоджи\n"
                "4. ✅ Настроить `configs/zxc.json` (через `!config_set` или вручную)\n"
                "5. ✅ Запустить бота: `python zxcmod.py`"
            ),
            inline=False
        )
        
        embed.add_field(
            name="💡 Важные замечания",
            value=(
                "• Эмоджи загружаются в **приложение бота**, а не на сервер Discord\n"
                "• Это позволяет использовать до **2000 эмоджи** без ограничений сервера\n"
                "• Не нужно создавать сервера для хранения эмоджи\n"
                "• Все эмоджи будут доступны боту на всех серверах\n"
                "• Команды `!change_color` и `!upload_emojis` доступны только автору бота"
            ),
            inline=False
        )
        
        embed.set_footer(text="Подробная инструкция также доступна в файле INIT.md")
        
        await inter.response.send_message(embed=embed, ephemeral=True)

    @commands.command()
    async def config_set(self, ctx: commands.Context):
        # права
        if str(ctx.author.id) != str(self.config.get("author")):
            return await ctx.send("У вас нет прав для выполнения этой команды.")

        await ctx.message.delete()

        # Термины для поиска
        role_terms = {
            "love_role": ["любовная", "love", "Любовные"],
            "server_boost_role": ["бустер", "nitro boost", "boost"],
            "staff_role": ["стафф", "staff"],
            "old_server_role": ["старик", "old server"],
            "curator": ["curator", "куратор"],
            "administrator": ["administrator", "администратор"],
            "master": ["master", "мастер"],
            "moderator": ["moderator", "модератор"],
            "support": ["support", "саппорт"],
            "closer": ["closemod", "closer", "клозер"],
            "eventer": ["eventer", "eventsmod", "ивентер", "ивентёр"],
            "creative": ["creative", "креатив"],
            "tribunemod": ["трибунемод", "tribunемод"],
            "eventban_id": ["eventban", "event ban", "ивентбан"],
            "closeban_id": ["closeban", "close ban", "клоз бан"],
            "rest": ["отпуск", "rest"],
            "ban": ["бан", "ban", "localban", "local ban"],
            "tmute": ["tmute", "текстовый мут", "textmute", "text mute"],
            "vmute": ["vmute", "голосовой мут", "voice mute", "voicemute"],
            "sponsor": ["sponsor", "спонсор"],
            "nedopysk": ["недопуск", "nedopysk"],
            "unverify": ["unverify", ".unverify", "неверифирован", "новичок", "новоприбывший"],
            "verify": ["верификация", "verify"],
            "tribunemod_admin": ["трибунемод админ", "руководит трибунемодами"],
            "moderator_admin": ["модератор админ", "руководит модераторами"],
            "support_admin": ["саппорт админ", "руководит саппортами"],
            "staff_admin": ["staff админ", "руководит стаффом"],
            "creative_admin": ["creative админ", "руководит креативами"],
            "event_admin": ["event админ", "руководит ивентерами"],
            "closemod_admin": ["closer админ", "руководит клозерами"],
        }
        channel_terms = {
            "quarantine_channel": ["карантин", "anticrash", "quarantine"],
            "pred_channel": ["предупреждения", "преды", "pred"],
            "news_channel_id": ["события", "events", "мероприятия", "анонсы"],
            "dev_chat": ["dev", "developer"],
            "reviews_channel": ["отзывы", "reviews"],
            "ot4eti_channel": ["отчёты", "отчеты"],
        }
        category_terms = {
            "room_category": ["приватные", "room", "приватки", "privates"],
            "events_category": ["ивенты", "events", "мероприятия"],
            "moderation_category": ["модерация", "moder rooms", "модерируемые"],
            "pair_category": ["парные комнаты", "love rooms", "любовные комнаты"],
            "logs_category": ["логи", "logs", "LOGS"],
            "appilation": ["аппеляция", "апелляции"],
            "verify_rooms": ["верификация", "проходная"],
        }
        logs_terms = {
            "logs_roles": ["ролей", "roles"],
            "logs_messages": ["сообщений", "messages"],
            "logs_voice": ["войс", "voice"],
            "logs_bans": ["банов", "bans"],
            "logs_kicks": ["киков", "kicks"],
            "logs_timeouts": ["тайм-аут", "timeout"],
            "logs_server": ["сервер", "server"],
            "award_log": ["экономика", "economy"],
            "rest_log": ["отпуск", "rest"],
            "time_log": ["временные", "time"],
            "mod_log": ["модерация", "moderation"],
        }

        # Поиск
        found_roles, miss_roles = self.fuzzy_search(ctx.guild.roles, role_terms)
        found_ch,    miss_ch    = self.fuzzy_search(ctx.guild.text_channels + ctx.guild.voice_channels, channel_terms)
        found_cat,   miss_cat   = self.fuzzy_search(ctx.guild.categories, category_terms)

        found_logs: dict[str,int] = {}
        miss_logs = set(logs_terms.keys())
        if "logs_category" in found_cat:
            log_cat = ctx.guild.get_channel(found_cat["logs_category"])
            if log_cat and hasattr(log_cat, "channels"):
                found_logs, miss_logs = self.fuzzy_search(log_cat.channels, logs_terms)

        # Формируем описание
        desc = ""
        for k, i in found_roles.items():
            cfg = self.config.get(k, "—")
            desc += f"✅ {k}: <@&{i}> (текущая: <@&{cfg}>)\n"
        for k in miss_roles:
            cfg = self.config.get(k, "—")
            desc += f"❌ {k}: (текущая: <@&{cfg}>)\n"
        desc += "\n"
        for k, i in found_ch.items():
            cfg = self.config.get(k, "—")
            desc += f"✅ {k}: <#{i}> (текущая: <#{cfg}>)\n"
        for k in miss_ch:
            cfg = self.config.get(k, "—")
            desc += f"❌ {k}: (текущая: <#{cfg}>)\n"
        desc += "\n"
        for k, i in found_cat.items():
            chan = ctx.guild.get_channel(i)
            cfg = self.config.get(k, "—")
            desc += f"✅ {k}: {chan.name if chan else '—'} (текущая: <#{cfg}>)\n"
        for k in miss_cat:
            cfg = self.config.get(k, "—")
            desc += f"❌ {k}: (текущая: <#{cfg}>)\n"
        desc += "\n"
        for k, i in found_logs.items():
            cfg = self.config.get(k, "—")
            desc += f"✅ {k}: <#{i}> (текущая: <#{cfg}>)\n"
        for k in miss_logs:
            cfg = self.config.get(k, "—")
            desc += f"❌ {k}: (текущая: <#{cfg}>)\n"

        pages = paginate_text(desc, 2000)
        embeds = []
        for idx, page in enumerate(pages, 1):
            e = disnake.Embed(
                title=f"Конфиг | {ctx.guild.name}",
                description=page,
                color=0x2F3136
            )
            e.set_footer(text=f"Страница {idx}/{len(pages)}")
            embeds.append(e)

        view = ConfigView(
            embeds,
            {"roles": found_roles, "channels": found_ch, "categories": found_cat, "logs": found_logs},
            {"roles": miss_roles,    "channels": miss_ch,  "categories": miss_cat,  "logs": miss_logs},
            ctx.author.id
        )
        msg = await ctx.send(embed=embeds[0], view=view)
        self.active[msg.id] = (view, ctx)

    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id not in {
            "prev", "next",
            "roles_accept", "channels_accept", "categories_accept", "logs_accept",
            "roles_create", "channels_create", "categories_create", "logs_create",
            "manual_id", "check_config"
        }:
            return
    
        data = self.active.get(inter.message.id)
        if not data:
            return

        view, ctx = data
        cid = inter.component.custom_id

        # Навигация
        if cid == "prev":
            view.current = (view.current - 1) % len(view.embeds)
            return await inter.response.edit_message(embed=view.embeds[view.current], view=view)

        if cid == "next":
            view.current = (view.current + 1) % len(view.embeds)
            return await inter.response.edit_message(embed=view.embeds[view.current], view=view)

        found = view.found
        miss  = view.missing

        # Подтвердить
        if cid == "roles_accept":
            for k, v in found["roles"].items():
                self.config[k] = v
        if cid == "channels_accept":
            for k, v in found["channels"].items():
                self.config[k] = v
        if cid == "categories_accept":
            for k, v in found["categories"].items():
                self.config[k] = v
        if cid == "logs_accept":
            for k, v in found["logs"].items():
                self.config[k] = v

        # Создать недостающие роли
        if cid == "roles_create":
            for key in miss["roles"]:
                # переводим ключ в человекочитаемый текст
                name = translate_text(key.replace("_", " ").capitalize())
                new_role = await ctx.guild.create_role(name=name)
                self.config[key] = new_role.id
            await inter.response.send_message("Недостающие роли созданы.", ephemeral=True)

        # Создать недостающие каналы/категории/логи
        if cid == "channels_create":
            for key in miss["channels"]:
                ch = await ctx.guild.create_text_channel(key)
                self.config[key] = ch.id
            await inter.response.send_message("Недостающие каналы созданы.", ephemeral=True)

        if cid == "categories_create":
            for key in miss["categories"]:
                cat = await ctx.guild.create_category(key)
                self.config[key] = cat.id
            await inter.response.send_message("Недостающие категории созданы.", ephemeral=True)

        if cid == "logs_create":
            if "logs_category" not in found["categories"]:
                logs_cat = await ctx.guild.create_category("LOGS")
                self.config["logs_category"] = logs_cat.id
            else:
                logs_cat = ctx.guild.get_channel(found["categories"]["logs_category"])
            for key in miss["logs"]:
                if key == "logs_voice":
                    new = await ctx.guild.create_voice_channel(key, category=logs_cat)
                else:
                    new = await ctx.guild.create_text_channel(key, category=logs_cat)
                self.config[key] = new.id
            await inter.response.send_message("Недостающие лог-каналы созданы.", ephemeral=True)

        # Ручной ввод ID
        if cid == "manual_id":
            await inter.response.send_message("Введите ключ и ID через пробел:", ephemeral=True)
            msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author.id == inter.author.id,
                timeout=60
            )
            try:
                key, id_str = msg.content.split()
                self.config[key] = int(id_str)
                await inter.followup.send(f"Обновлено: `{key}` → `{id_str}`", ephemeral=True)
            except:
                await inter.followup.send("Неверный формат. Используйте: `ключ ID`", ephemeral=True)

        # Проверить значения конфига
        if cid == "check_config":
            lines = [f"**{k}**: {self.config.get(k, '—')}" for k in sorted(self.config.keys())]
            pages = paginate_text("\n".join(lines), 2000)
            embeds = []
            for idx, page in enumerate(pages, 1):
                e = disnake.Embed(
                    title="Проверка конфига",
                    description=page,
                    color=0x2F3136
                )
                e.set_footer(text=f"Страница {idx}/{len(pages)}")
                embeds.append(e)
            view.embeds = embeds
            view.current = 0
            return await inter.response.edit_message(embed=embeds[0], view=view)

        # Сохраняем изменения в конфиг
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

        # Подтверждение
        if cid not in ("roles_create", "channels_create", "categories_create", "logs_create"):
            await inter.response.send_message("Конфигурация обновлена.", ephemeral=True)

    def cog_unload(self):
        # Очищаем слушатели и память
        self.active.clear()

def setup(bot):
    bot.add_cog(BotConfig(bot))