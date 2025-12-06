import disnake
import datetime
import json
import pymongo
import asyncio
import time
from disnake.ext import commands, tasks
from disnake.enums import ButtonStyle, TextInputStyle

with open('configs/zxc.json', 'r') as f:
    config = json.load(f)

with open('configs/zxc_tokens.json', 'r') as f:
    config1 = json.load(f)

cluster = pymongo.MongoClient(config1['mongodb'])

files = cluster.zxc.files_moderation

support = config['support']
verify = {}

class UserView(disnake.ui.View):
    def __init__(self, author):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Запрос на выдачу', custom_id = 'give_key', emoji = f'{files.find_one({"_id": "verify"})["emoji_take"]}'))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Запрос на снятие', custom_id = 'snyat_key', emoji = f'{files.find_one({"_id": "minus"})["emoji_take"]}'))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Список ключей', custom_id = 'list_key', emoji = f'{files.find_one({"_id": "minus"})["emoji_take"]}'))

class Key(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Отказать', custom_id = 'decline_key', emoji = f'{files.find_one({"_id": "decline"})["emoji_take"]}'))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Разрешить', custom_id = 'accept_key', emoji = f'{files.find_one({"_id": "accept"})["emoji_take"]}'))

class SnyatKey(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Отказать', custom_id = 'decline_snyat_key', emoji = f'{files.find_one({"_id": "decline"})["emoji_take"]}'))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Разрешить', custom_id = 'accept_snyat_key', emoji = f'{files.find_one({"_id": "accept"})["emoji_take"]}'))

class BlacklistView(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label = 'Выдать ЧС ключа', custom_id = 'add_blacklist_key', emoji = '🚫'))
        self.add_item(disnake.ui.Button(style = ButtonStyle.green, label = 'Снять ЧС ключа', custom_id = 'remove_blacklist_key', emoji = '✅'))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Посмотреть всех в ЧС', custom_id = 'view_blacklist_key', emoji = '📋'))

def time_end_form(seconds):
    h = seconds // 3600
    m = (seconds - h * 3600) // 60
    s = seconds % 60
    if h < 10: h = f"0{h}"
    if m < 10: m = f"0{m}"
    if s < 10: s = f"0{s}"
    return f"{h} : {m} : {s}"
    
async def task1(self, seconds, user, msg):
    for i in range(seconds + 4):
        try:
            embed = disnake.Embed(description=f"{user.mention}, для того, чтобы **отметиться** нажми на кнопку **ниже**.", color=3092790)
            embed.set_thumbnail(url = user.display_avatar.url)
            embed.set_author(name = f"Анти Афк")
            embed.set_footer(text = f"Осталось времени на ответ: {time_end_form(seconds)}")
            await msg.edit(embed=embed, view = PtOtmet())

            await asyncio.sleep(5)

            seconds -= 5

            if seconds < -1:
                cluster.zxc.pt.delete_one({'_id': str(user.id)})
                try:
                    await user.move_to(None)
                except:
                    pass

                return await self.bot.get_channel(config['pt_channel']).send(f"{user.mention}, **Вы** не успели ответить на **Анти-Афк**, ваш ПТ было автоматически **закончено.**")
        except:
            return


class PtOtmet(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label = 'Отметиться', custom_id = 'pt_otmet', emoji = f"{files.find_one({'_id': 'events'})['emoji_take']}"))

class Spanel(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label = 'Запланировать ПТ', custom_id = 'pt_start', emoji = f'{files.find_one({"_id": "events"})["emoji_take"]}'))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label = 'Отменить ПТ', custom_id = 'pt_cancel', emoji = f'{files.find_one({"_id": "basket"})["emoji_take"]}'))

class PtStartDropdown(disnake.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="Выберите пт",
            custom_id = 'choice_pt',
            options = [
                disnake.SelectOption(label="00:00-02:00", value = 'pt_00:00-02:00', description="Взять пт", emoji=f'{files.find_one({"_id": "edit"})["emoji_take"]}'),
                disnake.SelectOption(label="02:00-04:00", value = 'pt_02:00-04:00', description="Взять пт", emoji=f'{files.find_one({"_id": "edit"})["emoji_take"]}'),
                disnake.SelectOption(label="04:00-06:00", value = 'pt_04:00-06:00', description="Взять пт", emoji=f'{files.find_one({"_id": "edit"})["emoji_take"]}'),
                disnake.SelectOption(label="06:00-08:00", value = 'pt_06:00-08:00', description="Взять пт", emoji=f'{files.find_one({"_id": "edit"})["emoji_take"]}'),
                disnake.SelectOption(label="08:00-10:00", value = 'pt_08:00-10:00', description="Взять пт", emoji=f'{files.find_one({"_id": "edit"})["emoji_take"]}'),
                disnake.SelectOption(label="10:00-12:00", value = 'pt_10:00-12:00', description="Взять пт", emoji=f'{files.find_one({"_id": "edit"})["emoji_take"]}'),
                disnake.SelectOption(label="12:00-14:00", value = 'pt_12:00-14:00', description="Взять пт", emoji=f'{files.find_one({"_id": "edit"})["emoji_take"]}'),
                disnake.SelectOption(label="14:00-16:00", value = 'pt_14:00-16:00', description="Взять пт", emoji=f'{files.find_one({"_id": "edit"})["emoji_take"]}'),
                disnake.SelectOption(label="16:00-18:00", value = 'pt_16:00-18:00', description="Взять пт", emoji=f'{files.find_one({"_id": "edit"})["emoji_take"]}'),
                disnake.SelectOption(label="18:00-20:00", value = 'pt_18:00-20:00', description="Взять пт", emoji=f'{files.find_one({"_id": "edit"})["emoji_take"]}'),
                disnake.SelectOption(label="20:00-22:00", value = 'pt_20:00-22:00', description="Взять пт", emoji=f'{files.find_one({"_id": "edit"})["emoji_take"]}'),
                disnake.SelectOption(label="22:00-00:00", value = 'pt_22:00-00:00', description="Взять пт", emoji=f'{files.find_one({"_id": "edit"})["emoji_take"]}'),
            ],
        )

class Spanel(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.blurple, label = 'Запланировать ПТ', custom_id = 'pt_start', emoji = f'{files.find_one({"_id": "events"})["emoji_take"]}'))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label = 'Отменить ПТ', custom_id = 'pt_cancel', emoji = f'{files.find_one({"_id": "basket"})["emoji_take"]}'))

class PtStart(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(PtStartDropdown())

class KeyCogs(commands.Cog):
    def __init__(self, bot: commands.Bot(intents = disnake.Intents.all(), command_prefix = 'pt!')): # type: ignore
        self.bot = bot

    @commands.slash_command(description = 'Панель для мастера ключей')
    async def keys(self, inter, пользователь: disnake.Member):
        for role in inter.author.roles:
            if role.id in config['own_roles'] or role.id == config['support']:
                if cluster.zxc.verify_traphic.count_documents({"_id": str(inter.author.id)}) == 0:
                    cluster.zxc.verify_traphic.insert_one({"_id": str(inter.author.id), "key_give": 0, "key_users": []})

                output = пользователь.joined_at.timetuple()
                output = time.mktime(пользователь.joined_at.timetuple())
                output = str(output)
                output = output[:-2]
                joined = output

                verify[inter.author.id] = пользователь.id

                cluster.zxc.target.update_one({'_id': str(inter.author.id)}, {'$set': {'user': пользователь.id}}, upsert = True)

                embed = disnake.Embed(color = 3092790).set_author(name = f"Управление пользователем {пользователь}", icon_url = пользователь.display_avatar.url)
                embed.set_author(name = f"Панель верификации | {inter.guild.name}", icon_url = inter.guild.icon.url)
                embed.add_field(name = f"> Пользователь", value = f"**{пользователь.mention} | ID: {пользователь.id}**")
                embed.add_field(name = f"> Присоединился", value = f'<t:{joined}:R>')
                embed.set_image(url = "https://media.discordapp.net/attachments/1147909757068398622/1150819629132943451/3306a8965de5bba20ec812862409ff6e.gif")
                return await inter.send(inter.author.mention, embed=embed, view = UserView(inter.author))

        embed = disnake.Embed(description = f'{inter.author.mention}, У **Вас** нет на это **разрешения**!', timestamp = datetime.datetime.utcnow(), color = 3092790)
        embed.set_thumbnail(url = inter.author.display_avatar.url)
        embed.set_author(name = inter.author, icon_url = inter.author.avatar.url)
        await inter.send(embed=embed)

    @commands.slash_command(description = 'Чёрный список ключей')
    async def blacklist_keys(self, inter):
        # Проверка доступа
        has_permission = False
        for role in inter.author.roles:
            if (role.id == config.get('security') or 
                role.id == config.get('administrator') or 
                role.id in config.get('own_roles', [])):
                has_permission = True
                break
        
        if not has_permission:
            embed = disnake.Embed(description = f'{inter.author.mention}, У **Вас** нет на это **разрешения**!', timestamp = datetime.datetime.utcnow(), color = 3092790)
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            embed.set_author(name = inter.author, icon_url = inter.author.avatar.url)
            return await inter.send(embed=embed)

        embed = disnake.Embed(color = 3092790)
        embed.set_author(name = f"Чёрный список ключей | {inter.guild.name}", icon_url = inter.guild.icon.url)
        embed.add_field(name = "📋 Управление", value = "Выберите действие с помощью кнопок ниже")
        embed.set_image(url = "https://media.discordapp.net/attachments/1147909757068398622/1150819629132943451/3306a8965de5bba20ec812862409ff6e.gif")
        
        await inter.send(embed=embed, view=BlacklistView())

    @commands.Cog.listener()
    async def on_button_click(self, inter):
        custom_id = inter.component.custom_id

        # Обработка кнопок чёрного списка
        if custom_id == "add_blacklist_key":
            return await inter.response.send_modal(
                title="Добавить в ЧС ключей",
                custom_id="add_blacklist_key_modal",
                components=[
                    disnake.ui.TextInput(
                        label="ID пользователя",
                        custom_id="user_id",
                        style=disnake.TextInputStyle.short,
                        placeholder="Введите ID пользователя",
                        max_length=20
                    ),
                    disnake.ui.TextInput(
                        label="Причина",
                        custom_id="reason",
                        style=disnake.TextInputStyle.short,
                        placeholder="Причина добавления в ЧС",
                        max_length=100
                    )
                ]
            )

        if custom_id == "remove_blacklist_key":
            return await inter.response.send_modal(
                title="Убрать из ЧС ключей",
                custom_id="remove_blacklist_key_modal",
                components=[
                    disnake.ui.TextInput(
                        label="ID пользователя",
                        custom_id="user_id",
                        style=disnake.TextInputStyle.short,
                        placeholder="Введите ID пользователя",
                        max_length=20
                    )
                ]
            )

        if custom_id == "view_blacklist_key":
            # Получаем всех пользователей в ЧС
            blacklist_users = list(cluster.zxc.keys_blacklist.find({}))
            
            if not blacklist_users:
                embed = disnake.Embed(
                    description="📋 Чёрный список ключей пуст",
                    color=3092790
                )
                embed.set_author(name=f"ЧС ключей | {inter.guild.name}", icon_url=inter.guild.icon.url)
                return await inter.send(embed=embed, ephemeral=True)

            embed = disnake.Embed(color=3092790)
            embed.set_author(name=f"ЧС ключей | {inter.guild.name}", icon_url=inter.guild.icon.url)
            
            blacklist_text = ""
            for user_data in blacklist_users:
                user_id = user_data['_id']
                reason = user_data.get('reason', 'Не указана')
                added_by = user_data.get('added_by', 'Неизвестно')
                timestamp = user_data.get('timestamp', 'Неизвестно')
                
                blacklist_text += f"<@{user_id}> (ID: {user_id})\n"
                blacklist_text += f"├ Причина: {reason}\n"
                blacklist_text += f"├ Добавил: <@{added_by}>\n"
                blacklist_text += f"└ Время: <t:{timestamp}:R>\n\n"

            if len(blacklist_text) > 4000:
                blacklist_text = blacklist_text[:4000] + "..."

            embed.add_field(name="🚫 Пользователи в ЧС", value=blacklist_text or "Пусто", inline=False)
            
            return await inter.send(embed=embed, ephemeral=True)

        if custom_id.endswith("key"):
            if custom_id == "list_key":
                key_give = cluster.zxc.verify_traphic.find_one({'_id': str(inter.author.id)})['key_give']
                key_users = cluster.zxc.verify_traphic.find_one({'_id': str(inter.author.id)})['key_users']
                mentions = "\n".join([f"<@{uid}>" for uid in key_users]) if key_users else "Пусто"

                embed = disnake.Embed(color = 3092790)
                embed.add_field(name = f"Выдано ключей:", value = f"```{key_give}```", inline = True)
                embed.add_field(name = f"Кому выдано:", value = mentions, inline = True)
                embed.set_author(name = f"Мастер ключей | {inter.guild.name}", icon_url = inter.guild.icon.url)
                return await inter.send(embed = embed, ephemeral = True)
            
            if custom_id == "snyat_key":
                return await inter.response.send_modal(title=f"Мастер ключей", custom_id = "snyat_key", components=[
                    disnake.ui.TextInput(label="Причина", custom_id = "Причина", style=disnake.TextInputStyle.short, max_length=40)])
                
            if custom_id == "give_key":
                return await inter.response.send_modal(title=f"Мастер ключей", custom_id = "give_key", components=[
                    disnake.ui.TextInput(label="Причина", custom_id = "Причина", style=disnake.TextInputStyle.short, max_length=40)])

            embed = disnake.Embed(color = 3092790)
            embed.set_author(name = f"Ключ | {inter.guild.name}", icon_url = inter.guild.icon.url)

            пользователь = disnake.utils.get(inter.guild.members, id = int(cluster.zxc.target.find_one({'_id': str(inter.message.id)})['user']))

            await inter.response.defer()

            for role in inter.author.roles:
                if role.id == config['curator'] or role.id == config['administrator'] or role.id in config['own_roles'] or config['security'] == role.id:
                    if custom_id == "accept_key":
                        await inter.message.edit(f"Принято пользователем {inter.author.mention}", components = [])
                        await пользователь.add_roles(disnake.utils.get(inter.guild.roles, id = config['key_role']))
                    if custom_id == "decline_key":
                        await inter.message.edit(f"Отказано пользователем {inter.author.mention}", components = [])
                    if custom_id == "accept_snyat_key":
                        await inter.message.edit(f"Принято пользователем {inter.author.mention}", components = [])
                        await пользователь.remove_roles(disnake.utils.get(inter.guild.roles, id = config['key_role']))
                    if custom_id == "decline_snyat_key":
                        await inter.message.edit(f"Отказано пользователем {inter.author.mention}", components = [])
                        

    @commands.Cog.listener()
    async def on_modal_submit(self, inter):
        custom_id = inter.custom_id

        if custom_id == "give_key":
            member = disnake.utils.get(inter.guild.members, id = int(verify[inter.author.id]))

            # Проверка на ЧС
            is_blacklisted = cluster.zxc.keys_blacklist.find_one({'_id': str(member.id)})
            if is_blacklisted:
                embed = disnake.Embed(
                    description=f'❌ {member.mention} находится в **чёрном списке** ключей!\n\n'
                               f'**Причина:** {is_blacklisted.get("reason", "Не указана")}\n'
                               f'**Добавил:** <@{is_blacklisted.get("added_by", "Неизвестно")}>\n'
                               f'**Время:** <t:{is_blacklisted.get("timestamp", "Неизвестно")}:R>',
                    color=15158332,  # Красный цвет
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_author(name=f"Мастер ключей | {inter.guild.name}", icon_url=inter.guild.icon.url)
                embed.set_thumbnail(url=member.display_avatar.url)
                return await inter.response.edit_message(embed=embed, components=[])

            for key, value in inter.text_values.items():
                reason = value

            embed = disnake.Embed(color = 3092790, description = f'{inter.author.mention}, **заявка** успешно было **создана.**', timestamp = datetime.datetime.utcnow())
            embed.set_author(name = f"Мастер ключей | {inter.guild.name}", icon_url = inter.guild.icon.url)
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            await inter.response.edit_message(embed=embed, components = [])

            embed = disnake.Embed(color = 3092790, description = f'* Причина выдачи: **{reason}**', timestamp = datetime.datetime.utcnow())
            embed.set_author(name = f"Мастер ключей | {inter.guild.name}", icon_url = inter.guild.icon.url)
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            embed.add_field(name = f"> Создал заявку:", value=inter.author.mention)
            embed.add_field(name = f"> Для выдачи:", value=member.mention)
            msg = await self.bot.get_channel(config['key_channel']).send(content=f"<@&{config['support_admin']}>", embed=embed, view = Key())
            cluster.zxc.target.update_one({'_id': str(msg.id)}, {'$set': {'user': member.id}}, upsert = True)

            cluster.zxc.verify_traphic.update_one({'_id': str(inter.author.id)}, {'$push': {'key_users': member.id}})
            cluster.zxc.verify_traphic.update_one({"_id": str(inter.author.id)}, {"$inc": {"key_give": +1}})

        elif custom_id == "snyat_key":
            member = disnake.utils.get(inter.guild.members, id = int(verify[inter.author.id]))

            for key, value in inter.text_values.items():
                reason = value

            embed = disnake.Embed(color = 3092790, description = f'{inter.author.mention}, **заявка** успешно было **создана.**', timestamp = datetime.datetime.utcnow())
            embed.set_author(name = f"Выдача ключа | {inter.guild.name}", icon_url = inter.guild.icon.url)
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            await inter.response.edit_message(embed=embed, components = [])

            embed = disnake.Embed(color = 3092790, description = f'* Причина снятия: **{reason}**', timestamp = datetime.datetime.utcnow())
            embed.set_author(name = f"Снятие ключа | {inter.guild.name}", icon_url = inter.guild.icon.url)
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            embed.add_field(name = f"> Создал заявку:", value=inter.author.mention)
            embed.add_field(name = f"> Для снятия ключа:", value=member.mention)
            msg = await self.bot.get_channel(config['key_channel']).send(content=f"<@&{config['support_admin']}>", embed=embed, view = SnyatKey())
            cluster.zxc.target.update_one({'_id': str(msg.id)}, {'$set': {'user': member.id}}, upsert = True)

        # Обработка модальных окон для ЧС
        elif custom_id == "add_blacklist_key_modal":
            user_id = None
            reason = None
            
            for key, value in inter.text_values.items():
                if key == "user_id":
                    user_id = value.strip()
                elif key == "reason":
                    reason = value.strip()

            # Проверка валидности ID
            try:
                user_id = int(user_id)
            except ValueError:
                embed = disnake.Embed(
                    description="❌ Неверный формат ID пользователя!",
                    color=15158332
                )
                return await inter.response.edit_message(embed=embed, components=[])

            # Проверка, не находится ли уже в ЧС
            if cluster.zxc.keys_blacklist.find_one({'_id': str(user_id)}):
                embed = disnake.Embed(
                    description="❌ Пользователь уже находится в чёрном списке!",
                    color=15158332
                )
                return await inter.response.edit_message(embed=embed, components=[])

            # Добавление в ЧС
            timestamp = int(time.time())
            cluster.zxc.keys_blacklist.insert_one({
                '_id': str(user_id),
                'reason': reason,
                'added_by': str(inter.author.id),
                'timestamp': timestamp
            })

            embed = disnake.Embed(
                description=f"✅ Пользователь <@{user_id}> успешно добавлен в чёрный список ключей!\n\n"
                           f"**Причина:** {reason}\n"
                           f"**Добавил:** {inter.author.mention}",
                color=3092790,
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_author(name=f"ЧС ключей | {inter.guild.name}", icon_url=inter.guild.icon.url)
            
            await inter.response.edit_message(embed=embed, components=[])

        elif custom_id == "remove_blacklist_key_modal":
            user_id = inter.text_values.get("user_id", "").strip()

            # Проверка валидности ID
            try:
                user_id = int(user_id)
            except ValueError:
                embed = disnake.Embed(
                    description="❌ Неверный формат ID пользователя!",
                    color=15158332
                )
                return await inter.response.edit_message(embed=embed, components=[])

            # Проверка, находится ли в ЧС
            blacklist_entry = cluster.zxc.keys_blacklist.find_one({'_id': str(user_id)})
            if not blacklist_entry:
                embed = disnake.Embed(
                    description="❌ Пользователь не находится в чёрном списке!",
                    color=15158332
                )
                return await inter.response.edit_message(embed=embed, components=[])

            # Удаление из ЧС
            cluster.zxc.keys_blacklist.delete_one({'_id': str(user_id)})

            embed = disnake.Embed(
                description=f"✅ Пользователь <@{user_id}> успешно удалён из чёрного списка ключей!\n\n"
                           f"**Удалил:** {inter.author.mention}",
                color=3092790,
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_author(name=f"ЧС ключей | {inter.guild.name}", icon_url=inter.guild.icon.url)
            
            await inter.response.edit_message(embed=embed, components=[])

def setup(bot): 
    bot.add_cog(KeyCogs(bot))