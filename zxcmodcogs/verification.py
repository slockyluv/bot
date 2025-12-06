import pymongo
import disnake
import datetime
import json
import time
from disnake.ext import commands
from disnake.enums import ButtonStyle, TextInputStyle

with open('configs/zxc.json', 'r') as f:
    config = json.load(f)

with open('configs/zxc_tokens.json', 'r') as f:
    config1 = json.load(f)

cluster = pymongo.MongoClient(config1['mongodb'])

files = cluster.zxc.files_moderation

min = 60
hour = 60 * 60
day = 60 * 60 * 24

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
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = disnake.ButtonStyle.secondary, label = "Подать аппеляцию", url = "https://discord.com/channels/1007716878577315880/1328053143396941896"))

class Comment(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Оставить отзыв', custom_id = 'comment_verify', emoji = f'{files.find_one({"_id": "star"})["emoji_take"]}'))

class TakeNoVerifyDropdown(disnake.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="Выберите причину",
            options = [
                disnake.SelectOption(label="Неадекват", value = 'neadkvat_noverif', description=""),
                disnake.SelectOption(label="Меньше 13 лет", value = 'menshe_noverif', description=""),
                disnake.SelectOption(label="Не работает микрофон", value = 'voice_noverif', description=""),
                disnake.SelectOption(label="Неординарная причина", value = 'svast_noverif', description=""),
                    
            ],
        )

class TakeNoVerify(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(TakeNoVerifyDropdown())
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Назад', custom_id = 'back_verification', emoji = f'{files.find_one({"_id": "back"})["emoji_take"]}'))

class BackVerify(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Назад', custom_id = 'back_verification', emoji = f'{files.find_one({"_id": "back"})["emoji_take"]}'))

class VerificationView(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Мужская роль', custom_id = 'male_verify', emoji = f'{files.find_one({"_id": "male"})["emoji_take"]}'))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Женская роль', custom_id = 'female_verify', emoji = f'{files.find_one({"_id": "female"})["emoji_take"]}'))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Назад', custom_id = 'back_verification', emoji = f'{files.find_one({"_id": "back"})["emoji_take"]}'))

class TwinkView(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Добавить', custom_id = 'add_twink', emoji = f'{files.find_one({"_id": "plus"})["emoji_take"]}'))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Удалить', custom_id = 'delete_twink', emoji = f'{files.find_one({"_id": "minus"})["emoji_take"]}'))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Назад', custom_id = 'back_verification', emoji = f'{files.find_one({"_id": "back"})["emoji_take"]}'))

class GiveNoVerify(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Назад', custom_id = 'back_verification', emoji = f'{files.find_one({"_id": "back"})["emoji_take"]}'))

class GiveVerify(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Изменить выбор', custom_id = 'verify_main', emoji = f'{files.find_one({"_id": "verify"})["emoji_take"]}'))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Назад', custom_id = 'back_verification', emoji = f'{files.find_one({"_id": "back"})["emoji_take"]}'))

class VerifyView(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Верифицировать', custom_id = "verify_main", emoji = f'{files.find_one({"_id": "verify"})["emoji_take"]}'))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Недопуск', custom_id = "choice_nedopysk", emoji = f'{files.find_one({"_id": "ban"})["emoji_take"]}'))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Твинки', custom_id = "twink_main", emoji = f'{files.find_one({"_id": "more"})["emoji_take"]}'))

class ChoiceNedopysk(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Выдать недопуск', custom_id = "vidat_nedopysk", emoji = f'{files.find_one({"_id": "verify"})["emoji_take"]}'))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Снять недопуск', custom_id = "snyat_nedopysk", emoji = f'{files.find_one({"_id": "ban"})["emoji_take"]}'))

class VerifyNews(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Сделать оповещение', custom_id = "verify_news", emoji = f'{files.find_one({"_id": "verify"})["emoji_take"]}'))

class GhettoView(disnake.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="Выберите оценку",
            options = [
                disnake.SelectOption(label="Войс", value = 'voice_log_mod', description="Выход-заход в войс", emoji = f'{files.find_one({"_id": "edit"})["emoji_take"]}'),
                disnake.SelectOption(label="Инвайты", value = 'invites_log_mod', description="Выход-заход на сервер", emoji = f'{files.find_one({"_id": "edit"})["emoji_take"]}'),
                disnake.SelectOption(label="Роли", value = 'roles_log', description="Выдача/снятие ролей", emoji = f'{files.find_one({"_id": "edit"})["emoji_take"]}'),
                disnake.SelectOption(label="Сообщения", value = 'message_log_mod', description="Сообщения", emoji = f'{files.find_one({"_id": "edit"})["emoji_take"]}'),
                disnake.SelectOption(label="Верификация", value = 'verification_log_mod', description="Верификация", emoji = f'{files.find_one({"_id": "edit"})["emoji_take"]}'),
            ],
        )

class Trafic(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Ссылка приглашение', custom_id = "https_verify"))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Поисковик', custom_id = "search_verify"))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Мониторинг', custom_id = "monitoring_verify"))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='С другого сервера', custom_id = "another_verify"))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Реклама', custom_id = "ad_verify"))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Ютуб/тик-ток', custom_id = "youtube_verify"))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Не указывать', custom_id = "not_verify"))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label='Назад', custom_id = "back_verification"))

class verif(commands.Cog):
    def __init__(self, bot: commands.Bot(intents = disnake.Intents.all(), command_prefix = 'verify!')): # type: ignore
        self.bot = bot
    
    def convert_time_to_datetime(self, time_value):
        """Конвертирует время из разных форматов в datetime"""
        if time_value is None:
            return None
        
        # Если это уже datetime объект
        if isinstance(time_value, datetime.datetime):
            return time_value
        
        # Если это Unix timestamp (число)
        if isinstance(time_value, (int, float)):
            try:
                # Проверяем, это секунды или миллисекунды
                if time_value > 1e10:
                    return datetime.datetime.fromtimestamp(time_value / 1000)
                else:
                    return datetime.datetime.fromtimestamp(time_value)
            except:
                return None
        
        # Если это строка с Unix timestamp
        if isinstance(time_value, str):
            try:
                return datetime.datetime.fromtimestamp(int(time_value))
            except:
                pass
        
        # Если это MongoDB date (dict с ключом '$date')
        if isinstance(time_value, dict) and '$date' in time_value:
            try:
                date_str = time_value['$date']
                if isinstance(date_str, str):
                    # Формат ISO: "2025-09-14T11:55:34.000Z"
                    try:
                        # Пытаемся парсить с timezone
                        dt = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        # Конвертируем в timezone-naive (локальное время)
                        if dt.tzinfo:
                            dt = dt.astimezone().replace(tzinfo=None)
                        return dt
                    except:
                        # Если не получилось, пробуем без timezone
                        return datetime.datetime.fromisoformat(date_str.replace('Z', ''))
                elif isinstance(date_str, (int, float)):
                    # Unix timestamp в миллисекундах
                    return datetime.datetime.fromtimestamp(date_str / 1000)
            except:
                pass
        
        return None

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def asddasda(self, inter):
        await inter.message.delete()
        embed = disnake.Embed(
            color = 3092790,
            description = "<:to4kaaa:948159896979922966> Тогда проходи верификацию, что бы хорошо проводить своё время на нашем сервере!\n<:to4kaaa:948159896979922966> Перед тем как начать общение, \
            вам необходимо пройти верификацию на сервере, которая займёт у вас не более 2-ух минут!\n\n> ***Для прохождения верификации надо зайти в одну из прихожих***",
        ).set_image(url = 'https://media.discordapp.net/attachments/1090753034906251322/1130826108158349423/TxtBanner.png?width=1440&height=563')
        embed.set_author(name = "Привет! Хочешь получить доступ к серверу?", icon_url = inter.guild.icon.url)
        await inter.send(embed=embed, view = VerifyNews()) 

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def verify_embed(self, inter):
        await inter.message.delete()

        for member in inter.guild.members:
            try:
                await member.add_roles(disnake.utils.get(inter.guild.roles, id = 1198043093044310036))
            except:
                pass

    @commands.Cog.listener()
    async def on_dropdown(self, inter):
        custom_id = inter.values[0]

        if custom_id.endswith("noverif"):
            embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790, timestamp = datetime.datetime.utcnow())
            embed.set_author(name = f"Недопуск | {inter.guild.name}", icon_url = inter.guild.icon.url)
            embed.set_thumbnail(url = inter.author.display_avatar.url)

            if not inter.message.content == inter.author.mention:
                embed.description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**'
                return await inter.send(ephemeral = True, embed=embed)
            
            пользователь = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))
            await пользователь.add_roles(disnake.utils.get(inter.guild.roles, id = int(config['nedopysk'])))

            пользователь = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))
            await пользователь.remove_roles(disnake.utils.get(inter.guild.roles, id = int(config['unverify'])))
            
            if cluster.zxc.nedopysk.count_documents({"_id": str(inter.author.id)}) == 0:
                cluster.zxc.nedopysk.insert_one({"_id": str(inter.author.id), "nedopysk": 0})
                
            cluster.zxc.unverify.update_one({'_id': str(пользователь.id)}, {'$set': {'unverify': 1}}, upsert = True)
            cluster.zxc.nedopysk.update_one({'_id': str(inter.author.id)}, {'$set': {'nedopysk': 1}}, upsert = True)

            if custom_id ==  'neadkvat_noverif':
                reason = "Неадекват"
                new_date = datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(days=3)
            if custom_id ==  'menshe_noverif':
                reason = "Меньше 13 лет"
                new_date = datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(days=30)
            if custom_id == "voice_noverif":
                reason = "Без микрофона"
                new_date = datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(hours=2)
            if custom_id ==  'svast_noverif':
                reason = "Неординарная причина"
                new_date = datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(days=1)

            cluster.zxc.noverify.update_one({'_id': str(пользователь.id)}, {'$set': {'time': new_date}}, upsert = True)
            
            # Сохраняем недопуск в action для автоматического снятия
            cluster.zxc.action.update_one(
                {'_id': str(пользователь.id)},
                {'$set': {
                    'time': new_date,
                    'role': int(config['nedopysk']),
                    'reason': reason,
                    'type': 'Недопуск'
                }},
                upsert=True
            )
            print(f"[verification] ✅ Недопуск сохранен в action для пользователя {пользователь.id}, время окончания: {new_date}")

            try:
                embed.description = f"{пользователь.mention}, **Вам** выдали недопуск до **{new_date}** по причине"
                embed.add_field(name='> ・Причина', value = f'```{reason}```', inline = False)
                embed.add_field(name='> ・Модератор', value = f'{inter.author.mention}', inline = False)
                await пользователь.send(embed=embed, view = Invitelink())
            except:
                pass

            embed.description = f'{inter.author.mention}, вы успешно выдали недопуск пользователю {пользователь.mention} на **{new_date}**'
            await inter.response.edit_message(embed=embed, view = GiveNoVerify())

            embed.description = ""
            embed.add_field(name='> ・Нарушитель', value = f'{пользователь.mention}', inline = False)
            await self.bot.get_channel(config['mod_log']).send(embed=embed)

    @commands.Cog.listener()
    async def on_button_click(self, inter):
        custom_id = inter.component.custom_id
        
        if custom_id == "comment_verify":
            return await inter.response.send_modal(title=f"Доступ к проходной", custom_id = "comment_verify", components=[
                disnake.ui.TextInput(label="Оценка", placeholder = "Например: 1-5", custom_id = "Оценка", style=disnake.TextInputStyle.short, max_length=40),
                disnake.ui.TextInput(label="Комментарий", custom_id = "Комментарий", style=disnake.TextInputStyle.short, max_length=40)
                ])

        if custom_id == "verify_news":
            await inter.response.defer()
            await self.bot.get_channel(1187838794922213417).purge(limit = int(12))
            embed = disnake.Embed(description = f'<:to4kaaa:948159896979922966> Тогда проходи верификацию, что бы хорошо проводить своё время на нашем сервере!\n<:to4kaaa:948159896979922966> Перед тем как начать общение, вам необходимо пройти верификацию на сервере, которая займёт у вас не более 2-ух минут!\n\n> ***Для прохождения верификации надо зайти в одну из прихожих***\n> ***Зона верификации работает с 6:00 - 02:00 по московскому времени***', color = 3092790)
            embed.set_author(name = "Привет! Хочешь получить доступ к серверу?", icon_url = inter.guild.icon.url)
            embed.set_image(url = "https://media.discordapp.net/attachments/1090753034906251322/1130826108158349423/TxtBanner.png?width=1440&height=563")
            return await self.bot.get_channel(1187838794922213417).send(content = f"<@&{config['unverify']}>", embed=embed)

        if custom_id.endswith("verify"):
            await inter.response.defer()

            embed = disnake.Embed(color = 3092790)
            embed.set_author(name = f"Верификация | {inter.guild.name}", icon_url = inter.guild.icon.url)

            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.send(ephemeral = True, embed=embed)
            
            пользователь = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))

            fields = {
                "https_verify": "https",
                "search_verify": "search",
                "monitoring_verify": "monitoring",
                "another_verify": "another",
                "ad_verify": "ad",
                "youtube_verify": "youtube",
                "not_verify": "not"
            }
            
            if custom_id in fields:
                cluster.zxc.verify_traphic.update_one(
                    {"_id": str(inter.guild.id)},
                    {"$inc": {fields[custom_id]: 1}}
                )

                embed = disnake.Embed(color = 3092790, description = f"{inter.author.mention}, выберите **гендер** который будет **выдан** пользователю \
                                       {пользователь.mention}")
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                embed.set_author(name = f"Чтобы пропустить участника на сервер {inter.guild.name}", icon_url = inter.guild.icon.url)
                embed.set_image(url = "https://i.ibb.co/fkPw2Lf/bg23232.png")
                return await inter.message.edit(embed=embed, view = VerificationView())

            if custom_id == "male_verify":
                gender = 'Мужская'
                embed = disnake.Embed(color=disnake.Color.blue())
                await пользователь.add_roles(disnake.utils.get(inter.guild.roles, id=config['male']))
                await пользователь.remove_roles(inter.guild.get_role(config['female']))
                await пользователь.remove_roles(disnake.utils.get(inter.guild.roles, id=config['unverify']))
            elif custom_id == "female_verify":
                gender = "Женская"
                embed = disnake.Embed(color=disnake.Color.purple())
                await пользователь.add_roles(inter.guild.get_role(config['female']))
                await пользователь.remove_roles(inter.guild.get_role(config['unverify']))
                await пользователь.remove_roles(inter.guild.get_role(config['male']))
            
            if cluster.zxc.balls.count_documents({"_id": str(inter.author.id)}) == 0:
                cluster.zxc.balls.insert_one({"_id": str(inter.author.id), "balls": 0})
            if cluster.zxc.verify_count.count_documents({"_id": str(inter.author.id)}) == 0:
                cluster.zxc.verify_count.insert_one({"_id": str(inter.author.id), "verify_count": 0})
            
            now = datetime.datetime.utcnow()
            day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            
            update_stat({"user_id": str(inter.author.id), "category": "give_verify", "period": "day", "date": day_start})
            
            cluster.zxc.balls.update_one({"_id": str(inter.author.id)}, {"$inc": {"balls": +1}})
            
            cluster.zxc.verify_count.update_one({"_id": str(inter.author.id)}, {"$inc": {"verify_count": +1}})
            
            embed.add_field(name="Пользователь:", value=f"> {пользователь.mention} | {пользователь}", inline=False)
            embed.add_field(name="Саппорт:", value=f"> {inter.author.mention} | {inter.author}", inline=False)
            embed.add_field(name="Гендер:", value=f"> {gender} гендер", inline=False)
            embed.set_image(url = "https://i.ibb.co/fkPw2Lf/bg23232.png")
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            embed.set_author(name = f"Верификация | {inter.guild.name}", icon_url = inter.guild.icon.url)
            await inter.message.edit(embed=embed, view = GiveVerify())

            await self.bot.get_channel(config['log_verify']).send(embed=embed) # Логи
            
            try:
                await пользователь.edit(nick=None)
            except Exception as e:
                print(e)

            try:
                embed = disnake.Embed(description = f'{пользователь.mention}, Вас **верифицировал** {inter.author.mention}, можете оставить отзыв, **нажав** на кнопку **ниже**', timestamp = datetime.datetime.utcnow(), color = 3092790)
                embed.set_author(name = f"Добро пожаловать на {inter.guild}", icon_url = inter.guild.icon.url)
                embed.set_thumbnail(url = пользователь.display_avatar.url)
                msg = await пользователь.send(embed=embed, view = Comment())
                
                cluster.zxc.target.update_one({'_id': str(пользователь.id)}, {'$set': {'member': inter.author.id}}, upsert = True)

                await msg.pin()
            except:
                pass

        if inter.component.custom_id == 'verify_main':
            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                embed.set_author(name = f"Верификация | {inter.guild.name}", icon_url = inter.guild.icon.url)
                return await inter.send(ephemeral = True, embed=embed)
            
            await inter.response.defer()

            embed = disnake.Embed(color = 3092790)
            embed.set_author(name = f"Верификация | {inter.guild.name}", icon_url = inter.guild.icon.url)

            if cluster.zxc.verify_traphic.count_documents({"_id": str(inter.guild.id)}) == 0:
                cluster.zxc.verify_traphic.insert_one({"_id": str(inter.guild.id), "https": 0, "search": 0, "monitoring": 0, 'another': 0, "ad": 0, "youtube": 0, "not": 0})

            embed.description = f"{inter.author.mention}, **Выберите** кнопку ниже, для указания источника **трафика.**"
            return await inter.message.edit(embed = embed, view = Trafic())

        if custom_id[-5:] == "twink":
            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790)
                embed.set_author(name = "Твинки", icon_url = inter.guild.icon.url)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.send(ephemeral = True, embed=embed)

            if custom_id == 'add_twink':
                return await inter.response.send_modal(title=f"Добавить твинк", custom_id = "add_twink", components=[
                    disnake.ui.TextInput(label="Айди пользователя", custom_id = "Айди пользователя", style=disnake.TextInputStyle.short, max_length=40)])

            if custom_id == 'delete_twink':
                return await inter.response.send_modal(title=f"Удалить твинк", custom_id = "delete_twink", components=[
                    disnake.ui.TextInput(label="Айди пользователя", custom_id = "Айди пользователя", style=disnake.TextInputStyle.short, max_length=40)])

        if custom_id == 'twink_main':
            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790)
                embed.set_author(name = "Твинки", icon_url = inter.guild.icon.url)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.send(ephemeral = True, embed=embed)
            
            пользователь = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))
            
            if cluster.zxc.twink.count_documents({"_id": str(пользователь.id)}) == 0: 
                cluster.zxc.twink.insert_one({"_id": str(пользователь.id), "noverify": 0, "reason": 'Отсутствует', "twink": []})

            twink = cluster.zxc.twink.find_one({'_id': str(пользователь.id)})['twink']

            if twink == []:
                twink = 'Отсутствуют'
                twink_len = 0
            else:
                twink = f"{''.join(cluster.zxc.twink.find_one({'_id': str(пользователь.id)})['twink'])}"
                twink_len = len(cluster.zxc.twink.find_one({'_id': str(пользователь.id)})['twink'])

            embed = disnake.Embed(color = 3092790, description = twink)
            embed.set_author(name = f"Твинки {пользователь}", icon_url = inter.guild.icon.url)
            embed.set_thumbnail(url = пользователь.display_avatar.url)
            embed.set_footer(text = f"Всего твинков: {twink_len}")
            await inter.response.edit_message(embed=embed, view = TwinkView())

        if custom_id == 'back_verification':
            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790)
                embed.set_author(name = "Успешная верификация", icon_url = inter.guild.icon.url)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.send(ephemeral = True, embed=embed)
            
            пользователь = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))
            
            if cluster.zxc.noverify.count_documents({"_id": str(пользователь.id)}) == 0: 
                cluster.zxc.noverify.insert_one({"_id": str(пользователь.id), "noverify": 0, "reason": 'Отсутствует'})

            if cluster.zxc.member_join.count_documents({"_id": str(пользователь.id)}) == 0:
                cluster.zxc.member_join.insert_one({"_id": str(пользователь.id), "restart": 0})

            restart_main = cluster.zxc.member_join.find_one({'_id': str(пользователь.id)})['restart']

            device = None
            if пользователь.is_on_mobile() == True:
                device = "Телефон"
            else:
                device = "Компьютер"

            global time

            output = пользователь.joined_at.timetuple()
            output = time.mktime(пользователь.joined_at.timetuple())
            output = str(output)
            output = output[:-2]
            join = output

            input = пользователь.created_at.timetuple()
            input = time.mktime(пользователь.created_at.timetuple())
            input = str(input)
            input = input[:-2]
            created = input

            embed = disnake.Embed(color = 3092790)
            embed.set_author(name = f"Информация о {пользователь}", icon_url = inter.guild.icon.url)
            embed.add_field(name = f"Присоединился", value = f'<t:{join}:R>')
            embed.add_field(name = f"Создан аккаунт", value = f'<t:{created}>')
            embed.add_field(name = f"Устройство", value = f"{device}")
            embed.add_field(name = f"Недопущен", value = f"{cluster.zxc.noverify.find_one({'_id': str(пользователь.id)})['noverify']} раз(-и)")
            embed.add_field(name = f"Причина", value = f"{cluster.zxc.noverify.find_one({'_id': str(пользователь.id)})['reason']}")
            embed.add_field(name = f"Перезаход", value = f"{restart_main}")
            embed.set_image(url = f"https://cdn.discordapp.com/attachments/1409621739037786233/1409636444388982895/hgghffgh.png?ex=68ae19be&is=68acc83e&hm=af0e3ea4b37d81f90a9e73f6b410682cd9f1a694c746c8fb08ca86f27572f1d1&")
            await inter.response.edit_message(embed=embed, view = VerifyView())

        if inter.component.custom_id == 'choice_nedopysk':
            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790)
                embed.set_author(name = f"Недопуск | {inter.guild.name}", icon_url = inter.guild.icon.url)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.send(ephemeral = True, embed=embed)

            member = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))
            embed = disnake.Embed(color = 3092790, description = f'{inter.author.mention}, **выберите** действие над {member.mention}', timestamp = datetime.datetime.utcnow())
            embed.set_author(name = f"Не допуск | {inter.guild.name}", icon_url = inter.guild.icon.url)
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            return await inter.response.edit_message(embed=embed, view = ChoiceNedopysk())
        
        if inter.component.custom_id == 'vidat_nedopysk':
            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790)
                embed.set_author(name = f"Недопуск | {inter.guild.name}", icon_url = inter.guild.icon.url)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.send(ephemeral = True, embed=embed)
            
            try:
                member = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))
                embed = disnake.Embed(color = 3092790, description = f'{inter.author.mention}, **укажите причину** для выдачи недопуска пользователю {member.mention}', timestamp = datetime.datetime.utcnow())
                embed.set_author(name = f"Не допуск | {inter.guild.name}", icon_url = inter.guild.icon.url)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.response.edit_message(embed=embed, view = TakeNoVerify())
            except:
                embed = disnake.Embed(color = 3092790, description = f'{inter.author.mention}, **Пользователь вышел из сервера**.', timestamp = datetime.datetime.utcnow())
                embed.set_author(name = f"Не допуск | {inter.guild.name}", icon_url = inter.guild.icon.url)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.response.edit_message(embed=embed)
        
        if inter.component.custom_id == 'snyat_nedopysk':
            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color = 3092790)
                embed.set_author(name = f"Недопуск | {inter.guild.name}", icon_url = inter.guild.icon.url)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.send(ephemeral = True, embed=embed)

            member = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))

            role = disnake.utils.get(member.guild.roles, id = config['nedopysk'])
            role_unverify = disnake.utils.get(member.guild.roles, id = config['unverify'])

            await member.remove_roles(role)
            await member.add_roles(role_unverify)
            
            # Удаляем запись из action при ручном снятии недопуска
            cluster.zxc.action.delete_one({'_id': str(member.id)})
            print(f"[verification] ✅ Недопуск снят вручную для пользователя {member.id}, запись удалена из action")

            embed = disnake.Embed(color = 3092790, description = f'{inter.author.mention} **Вы** успешно **сняли недопуск** {member.mention}', timestamp = datetime.datetime.utcnow())
            embed.set_author(name = f"Не допуск | {inter.guild.name}", icon_url = inter.guild.icon.url)
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            return await inter.response.edit_message(embed=embed, view = BackVerify())

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            await member.edit(nick=f"🔴 {member.name}")
        except:
            pass
        
        await member.add_roles(disnake.utils.get(member.guild.roles, id = config['unverify']))

        try:
            role = disnake.utils.get(member.guild.roles, id = config['nedopysk'])
            aye = cluster.zxc.unverify.find_one({'_id': str(member.id)})['unverify']
            await member.add_roles(role)
            await member.remove_roles(disnake.utils.get(member.guild.roles, id = int(config['unverify'])))
        except:
            pass

        # Проверяем активные наказания
        try:
            result = cluster.zxc.action.find_one({'_id': str(member.id)})
            if not result:
                return
            
            punishment_type = result.get('type')
            time_value = result.get('time')
            role_id = result.get('role')
            
            if not punishment_type or not time_value:
                return
            
            # Конвертируем время окончания наказания
            end_time = self.convert_time_to_datetime(time_value)
            if not end_time:
                print(f"[verification] Не удалось конвертировать время для пользователя {member.id}")
                return
            
            # Проверяем, не истекло ли наказание
            end_time_naive = end_time.replace(tzinfo=None) if end_time.tzinfo else end_time
            now = datetime.datetime.now()
            if end_time_naive <= now:
                # Наказание истекло, не выдаем роль
                print(f"[verification] Наказание для пользователя {member.id} (тип: {punishment_type}) истекло, роль не выдана")
                return
            
            # Наказание активно - выдаем роль
            role = None
            role_id_int = None
            
            # Обрабатываем разные форматы role_id
            if isinstance(role_id, dict) and '$numberLong' in role_id:
                role_id_int = int(role_id['$numberLong'])
            elif isinstance(role_id, (str, int)):
                try:
                    role_id_int = int(role_id)
                except:
                    pass
            
            # Если role_id не найден, пытаемся использовать конфиг
            if not role_id_int:
                punishment_roles = {
                    'Бан': config.get('ban'),
                    'Ивент Бан': config.get('event_ban'),
                    'Клоз Бан': config.get('close_ban'),
                    'Креатив Бан': config.get('creative_ban'),
                    'Голосовой мут': config.get('vmute'),
                    'Текстовый мут': config.get('tmute'),
                    'Чилл Бан': config.get('chill_ban'),
                    'Недопуск': config.get('nedopysk')
                }
                role_id_int = punishment_roles.get(punishment_type)
                if role_id_int:
                    try:
                        role_id_int = int(role_id_int)
                    except:
                        role_id_int = None
            
            if role_id_int:
                role = disnake.utils.get(member.guild.roles, id=role_id_int)
            
            if role:
                try:
                    await member.add_roles(role)
                    print(f"[verification] ✅ Выдана роль наказания {role.name} (ID: {role.id}) пользователю {member.display_name} (ID: {member.id}), тип: {punishment_type}")
                    
                    # Для бана и недопуска убираем роль unverify
                    if punishment_type in ["Бан", "Ивент Бан", "Клоз Бан", "Креатив Бан", "Недопуск"]:
                        unverify_role = disnake.utils.get(member.guild.roles, id=config['unverify'])
                        if unverify_role:
                            try:
                                await member.remove_roles(unverify_role)
                            except:
                                pass
                except Exception as e:
                    print(f"[verification] ❌ Ошибка при выдаче роли наказания пользователю {member.id}: {e}")
            else:
                print(f"[verification] ⚠️ Роль для наказания не найдена: тип={punishment_type}, role_id={role_id}")
                
        except Exception as e:
            print(f"[verification] ❌ Ошибка при проверке наказаний для пользователя {member.id}: {e}")
            import traceback
            traceback.print_exc()

    @commands.Cog.listener()
    async def on_modal_submit(self, inter):
        custom_id = inter.custom_id

        if custom_id == "comment_verify":
            guild = self.bot.get_guild(config['server_id'])

            support = disnake.utils.get(guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))
            id = 0

            for key, value in inter.text_values.items():
                if id == 0:
                    stars = value
                else:
                    comment = value
                id += 1
            try:
                if int(stars) > 5 or int(stars) < 1:
                    embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** не можете поставить **меньше чем 1 звезду** или же **больше** чем **5 звезд.**', timestamp = datetime.datetime.utcnow(), color = disnake.Color.red())
                    embed.set_author(name = f"Отзыв {inter.author}", icon_url = inter.author.display_avatar.url)
                    embed.set_thumbnail(url = inter.author.display_avatar.url)
                    return await inter.response.send_message(embed=embed)
            except:
                embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** не можете **ввести** оценку **ниже 1** или **больше 5**', timestamp = datetime.datetime.utcnow(), color = disnake.Color.red())
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.author.send(embed=embed)
            
            await inter.response.edit_message(components = [])

            embed = disnake.Embed(description=f"Отзыв от {inter.author.mention}\n> {comment}",color = 3092790,timestamp = datetime.datetime.utcnow())
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            emoji = files.find_one({"_id": "star"})["emoji_take"]
            value = f"{emoji * int(stars)}"
            embed.add_field(name = f"Оценка", value = f"> {value}")
            embed.set_author(name = f"Отзыв Верификации {support}", icon_url = support.display_avatar.url)
            await self.bot.get_channel(config['reviews_channel']).send(content = support.mention, embed=embed)
            
            embed = disnake.Embed(description = f'{inter.author.mention}, Спасибо за оставленный **Вами** отзыв! Приятного **время провождения** на сервере.', timestamp = datetime.datetime.utcnow(), color = 3092790)
            embed.set_author(name = f"Отзыв {inter.author}", icon_url = inter.author.display_avatar.url)
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            await inter.author.send(embed=embed)

        if custom_id[-5:] == 'twink':
            member = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.author.id)})['member']))

            embed = disnake.Embed(color = 3092790,timestamp = datetime.datetime.utcnow())
            embed.set_thumbnail(url = inter.author.display_avatar.url).set_author(name = "Твинки", icon_url = inter.guild.icon.url)
            embed.set_footer(text = f"Запросил(а) {inter.author}", icon_url = inter.author.display_avatar.url)

            for key, value in inter.text_values.items():
                twink = value

            if custom_id == 'add_twink':
                cluster.zxc.twink.update_one({"_id": str(member.id)}, {"$push": {"twink": f"<@{twink}>\n"}})
                embed.description = f"{inter.author.mention}, **Вы** успешно **добавили** твинк <@{twink}> пользователю {member.mention}"

                main = disnake.utils.get(inter.guild.members, id = int(twink))
                for role in main.roles:
                    if role.id in config['ban']:
                        embed.description = f"У **пользователя** {member.mention}, на **основном** аккаунте {main.mention}, **обнаружены нарушения**, верификация **невозможна**!"
                        break
                    
            elif custom_id == 'delete_twink':
                cluster.zxc.twink.update_one({'_id': str(member.id)}, {'$pull': {'twink': f"<@{twink}>\n"}}, upsert = True)
                embed.description = f"{inter.author.mention}, **Вы** успешно **удалили** твинк <@{twink}> пользователю {member.mention}"

            return await inter.response.edit_message(embed=embed, view = GiveNoVerify())

    @commands.slash_command(description = 'Верифицировать пользователя')
    async def verify(self, inter, пользователь: disnake.Member):
        if пользователь == inter.author:
            embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** не можете верифицировать **себя!**', timestamp = datetime.datetime.utcnow(), color = 3092790)
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            embed.set_author(name = f"Верификация | {inter.guild.name}", icon_url = inter.guild.icon.url)
            return await inter.send(embed=embed, ephemeral = True)

        support = inter.guild.get_role(config['support'])
        
        for role_id in config['own_roles']:
            role = inter.guild.get_role(role_id)
            
            if role in inter.author.roles or support in inter.author.roles:
                if support in пользователь.roles:
                    embed = disnake.Embed(description = f'{inter.author.mention}, **Вы** не можете верифицировать **саппорта**', timestamp = datetime.datetime.utcnow(), color = 3092790)
                    embed.set_thumbnail(url = inter.author.display_avatar.url)
                    embed.set_author(name = f"Верификация | {inter.guild.name}", icon_url = inter.guild.icon.url)
                    return await inter.send(embed=embed, ephemeral = True)
                
                await inter.response.defer()

                cluster.zxc.target.update_one({'_id': str(inter.author.id)}, {'$set': {'member': пользователь.id}}, upsert = True)

                if cluster.zxc.noverify.count_documents({"_id": str(пользователь.id)}) == 0: 
                    cluster.zxc.noverify.insert_one({"_id": str(пользователь.id), "noverify": 0, "reason": 'Отсутствует'})

                if cluster.zxc.member_join.count_documents({"_id": str(пользователь.id)}) == 0:
                    cluster.zxc.member_join.insert_one({"_id": str(пользователь.id), "restart": 0})

                restart_main = cluster.zxc.member_join.find_one({'_id': str(пользователь.id)})['restart']

                device = None
                if пользователь.is_on_mobile() == True:
                    device = "Телефон"
                else:
                    device = "Компьютер"

                output = пользователь.joined_at.timetuple()
                output = time.mktime(пользователь.joined_at.timetuple())
                output = str(output)
                output = output[:-2]
                joined = output

                input = пользователь.created_at.timetuple()
                input = time.mktime(пользователь.created_at.timetuple())
                input = str(input)
                input = input[:-2]
                created = input

                embed = disnake.Embed(color = 3092790).set_author(name = f"Информация о {пользователь}", icon_url = пользователь.display_avatar.url)
                embed.add_field(name = f"> Присоединился", value = f'<t:{joined}:R>')
                embed.add_field(name = f"> Создан аккаунт", value = f'<t:{created}>')
                embed.add_field(name = f"> Устройство", value = f"{device}")
                embed.add_field(name = f"> Недопущен", value = f"{cluster.zxc.noverify.find_one({'_id': str(пользователь.id)})['noverify']} раз(-и)")
                embed.add_field(name = f"> Аватарка", value = f"[ссылка]({пользователь.display_avatar.url})")
                embed.add_field(name = f"> Перезаход", value = f"{restart_main}")
                embed.set_footer(text = f"Запросил(а) {inter.author}", icon_url = inter.author.display_avatar.url)
                embed.set_image(url = "https://cdn.discordapp.com/attachments/1409621739037786233/1409636444388982895/hgghffgh.png?ex=68ae19be&is=68acc83e&hm=af0e3ea4b37d81f90a9e73f6b410682cd9f1a694c746c8fb08ca86f27572f1d1&")
                return await inter.send(inter.author.mention, embed=embed, view = VerifyView())

        embed = disnake.Embed(description = f'{inter.author.mention}, У **Вас** нет на это **разрешения**!', timestamp = datetime.datetime.utcnow(), color = 3092790)
        embed.set_thumbnail(url = inter.author.display_avatar.url)
        embed.set_author(name = f"Верификация | {inter.guild.name}", icon_url = inter.guild.icon.url)
        await inter.send(embed=embed)

    @commands.slash_command(description = 'Мониторинг')
    async def monitoring(self, inter):
        support = inter.guild.get_role(config['support'])
        
        for role_id in config['own_roles']:
            role = inter.guild.get_role(role_id)
            
            if role in inter.author.roles or support in inter.author.roles:
                await inter.response.defer()

                traphic = cluster.zxc.verify_traphic
                invite = traphic.find_one({'_id': str(inter.guild.id)})['https']
                search = traphic.find_one({'_id': str(inter.guild.id)})['search']
                monitoring = traphic.find_one({'_id': str(inter.guild.id)})['monitoring']
                another = traphic.find_one({'_id': str(inter.guild.id)})['another']
                ad = traphic.find_one({'_id': str(inter.guild.id)})['ad']
                youtube = traphic.find_one({'_id': str(inter.guild.id)})['youtube']
                no_verify = traphic.find_one({'_id': str(inter.guild.id)})['not']
                all = int(invite) + int(search) + int(monitoring) + int(another) + int(ad) + int(youtube) + int(no_verify)
        
                embed = disnake.Embed(color = 3092790)
                embed.set_author(name = f"Мониторинг | {inter.guild.name}", icon_url = inter.guild.icon.url)
                embed.add_field(name = f"> Инвайт", value = f"{invite}")
                embed.add_field(name = f"> Поисковик", value = f"{search}")
                embed.add_field(name = f"> Мониторинг", value = f"{monitoring}")
                embed.add_field(name = f"> Другой сервер", value = f"{another}")
                embed.add_field(name = f"> Реклама", value = f"{ad}")
                embed.add_field(name = f"> Медиа", value = f"{youtube}")
                embed.add_field(name = f"> Не указано", value = f"{no_verify}")
                embed.add_field(name = f"> Верифицировно", value = f"{all}")
                embed.add_field(name = f"> Каллаборации", value = f"0")
                embed.set_image(url = "https://media.discordapp.net/attachments/1143970542576222268/1149704465818075156/53b4dba8c6642a0008f2a552b3bf0e53.jpg")
                return await inter.send(inter.author.mention, embed=embed)

        embed = disnake.Embed(description = f'{inter.author.mention}, У **Вас** нет на это **разрешения**!', timestamp = datetime.datetime.utcnow(), color = 3092790)
        embed.set_thumbnail(url = inter.author.display_avatar.url)
        embed.set_author(name = f"Верификация | {inter.guild.name}", icon_url = inter.guild.icon.url)
        await inter.send(embed=embed)

def setup(bot):
    bot.add_cog(verif(bot))