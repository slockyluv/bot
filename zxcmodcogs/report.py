import disnake
import pymongo
import json
from disnake.ext import commands
from disnake.enums import ButtonStyle

with open('configs/zxc.json', 'r') as f:
    config = json.load(f)

with open('configs/zxc_tokens.json', 'r') as f:
    config1 = json.load(f)

cluster = pymongo.MongoClient(config1['mongodb'])

db = cluster.zxc.target
files = cluster.zxc.files_moderation
report_meta = cluster.zxc.report_meta

class BallReportDisabled(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Вы успешно оставили отзыв', custom_id = 'ball_report', row = 0, disabled=True))

class BallReport(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, label = 'Оставить отзыв', custom_id = 'ball_report', row = 0))

class ReportView(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.green, label = 'Принять', custom_id = 'accept_report', row = 0))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, label = 'Отклонить', custom_id = 'decline_report', row = 0))

class ReportMenu(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, emoji = f'{files.find_one({"_id": "one"})["emoji_take"]}', custom_id = 'accept_one', row = 0))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, emoji = f'{files.find_one({"_id": "two"})["emoji_take"]}', custom_id = 'accept_two', row = 0))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', custom_id = 'close_report', row = 0))

class PrefixReportView(disnake.ui.View):
    def __init__(self, author: disnake.Member, target: disnake.Member):
        super().__init__(timeout = 300)
        self.author_id = author.id
        self.target = target

    @disnake.ui.button(label = 'Указать причину жалобы', style = ButtonStyle.secondary)
    async def open_reason_modal(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.author.id != self.author_id:
            await inter.response.send_message('Вы не можете использовать эту форму.', ephemeral = True)
            return

        await inter.response.send_modal(
            title = f"Жалоба на {self.target.name}",
            custom_id = f"prefix_report:{self.author_id}:{self.target.id}",
            components = [
                disnake.ui.TextInput(
                    label = f"Причина жалобы на {self.target.name}",
                    custom_id = "report_reason",
                    style = disnake.TextInputStyle.paragraph,
                    max_length = 500,
                )
            ],
        )

class report_cog(commands.Cog):
    def __init__(self, bot: commands.Bot(intents=disnake.Intents.all(), command_prefix = "report!")): # type: ignore
        self.bot = bot

    def _build_report_embed(self, author: disnake.Member, target: disnake.Member, reason: str) -> disnake.Embed:
        embed = disnake.Embed(title = "Репорт", color = 3092790)
        embed.set_thumbnail(url = author.display_avatar.url)
        channel = author.voice.channel if author.voice and author.voice.channel else None
        channel_member = target.voice.channel if target.voice and target.voice.channel else None

        embed.add_field(
            name = "Пользователь",
            value = author.mention + (f"\n{channel}" if channel else ""),
            inline = True,
        )
        embed.add_field(
            name = "Обвиняемый",
            value = target.mention + (f"\n{channel_member}" if channel_member else ""),
            inline = True,
        )
        embed.add_field(name = "Причина", value = f"```{reason}```", inline = False)
        return embed

    async def _send_report(self, author: disnake.Member, target: disnake.Member, reason: str) -> disnake.Message:
        embed = self._build_report_embed(author, target, reason)
        msg = await self.bot.get_channel(config['report_channel_id']).send(content=f"<@&{config['moderator']}>", embed=embed, view = ReportView())

        db.update_one({'_id': str(msg.id)}, {'$set': {'user': author.id}}, upsert = True)
        db.update_one({'_id': str(msg.id)}, {'$set': {'target': target.id}}, upsert = True)
        return msg

    @commands.slash_command(description = 'Отправить жалобу')
    async def report(self, inter, пользователь: disnake.Member):
        await inter.response.send_modal(title=f"Жалоба на {пользователь.name}", custom_id = "report", components=[
            disnake.ui.TextInput(label=f"Причина жалобы на {пользователь.name}", custom_id = f"Причина жалобы на {пользователь.name}", style=disnake.TextInputStyle.paragraph, max_length=500)])
        modal_inter: disnake.ModalInteraction = await self.bot.wait_for("modal_submit",check=lambda i: i.custom_id == "report" and i.author.id == inter.author.id)
        
        
        await modal_inter.response.defer(ephemeral=True)

        for key, value in modal_inter.text_values.items():
            reason = value

        msg = await self._send_report(inter.author, пользователь, reason)

        embed = disnake.Embed(color = 3092790, description=f"{inter.author.mention}, Вы **успешно** отправили **жалобу** на {пользователь.mention}")
        embed.set_author(name = f"Пожаловаться на нарушителя | {inter.guild.name}", icon_url = inter.guild.icon.url)
        embed.set_thumbnail(url = inter.author.display_avatar.url)
        return await modal_inter.edit_original_response(embed=embed)

    @commands.command(name="report", description = 'Отправить жалобу')
    async def report_prefix(self, ctx, пользователь: disnake.Member | None = None):
        if пользователь is None:
            embed = disnake.Embed(
                color = 3092790,
                description = f"{ctx.author.mention}, укажите пользователя для жалобы после команды.",
            )
            await ctx.send(embed = embed)
            return

        embed = disnake.Embed(
            color = 3092790,
            description = (
                f"{ctx.author.mention}, нажмите кнопку ниже, чтобы указать причину жалобы "
                f"на {пользователь.mention}."
            ),
        )
        embed.set_author(
            name = f"Пожаловаться на нарушителя | {ctx.guild.name if ctx.guild else 'Сервер'}",
            icon_url = ctx.guild.icon.url if ctx.guild and ctx.guild.icon else disnake.Embed.Empty,
        )
        embed.set_thumbnail(url = ctx.author.display_avatar.url)

        await ctx.send(embed = embed, view = PrefixReportView(ctx.author, пользователь))
    
    @commands.Cog.listener()
    async def on_modal_submit(self, inter):
        custom_id = inter.custom_id
        if custom_id == 'review_report':
            await inter.response.edit_message(view = BallReportDisabled())
            for key, value in inter.text_values.items():
                review = value
                
            guild = self.bot.get_guild(config["server_id"])
            moder = disnake.utils.get(guild.members, id = db.find_one({'_id': str(inter.message.id)})['moderator'])
            embed = disnake.Embed(color = 3092790, title = "Moderation Logs", description=f"```{review}```")
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            embed.add_field(name = "Оставил отзыв", value = f"{inter.author.mention}", inline = True)
            embed.add_field(name = "Модератор", value = f"{moder.mention}", inline = True)
            await self.bot.get_channel(config['report_reviews']).send(embed=embed)

        if custom_id.startswith('prefix_report:'):
            await inter.response.defer(ephemeral=True)
            _, author_id, target_id = custom_id.split(':')

            if inter.author.id != int(author_id):
                await inter.edit_original_response(content = 'Вы не можете отправить эту жалобу.')
                return

            target = disnake.utils.get(inter.guild.members, id = int(target_id)) if inter.guild else None

            if target is None:
                await inter.edit_original_response(content = 'Указанный пользователь не найден на сервере.')
                return

            for value in inter.text_values.values():
                reason = value

            await self._send_report(inter.author, target, reason)

            embed = disnake.Embed(color = 3092790, description=f"{inter.author.mention}, Вы **успешно** отправили **жалобу** на {target.mention}")
            embed.set_author(name = f"Пожаловаться на нарушителя | {inter.guild.name if inter.guild else 'Сервер'}", icon_url = inter.guild.icon.url if inter.guild and inter.guild.icon else disnake.Embed.Empty)
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            await inter.edit_original_response(embed=embed)
        
    @commands.Cog.listener()
    async def on_button_click(self, inter):
        custom_id = inter.component.custom_id

        if custom_id == 'ball_report':
            await inter.response.send_modal(title=f"Отзыв", custom_id = "review_report", components=[
                disnake.ui.TextInput(label=f"Текст", custom_id = f"Текст", style=disnake.TextInputStyle.paragraph, max_length=500)])

        if custom_id[-6:] == 'report':
            if not inter.response.is_done():
                await inter.response.defer()

            if custom_id == 'accept_report':
                counter_doc = report_meta.find_one({'_id': 'report_counter'})
                number = 1

                if counter_doc and 'value' in counter_doc:
                    number = counter_doc['value'] + 1

                report_meta.update_one({'_id': 'report_counter'}, {'$set': {'value': number}}, upsert = True)

                embed = inter.message.embeds[0]
                embed.set_footer(text=f"Принял репорт {number} - {inter.author}", icon_url=inter.author.display_avatar.url)
                await inter.message.edit(embed=embed, components = [])

                thread = await inter.message.create_thread(name = f"Жалоба {number}")

                user = disnake.utils.get(inter.guild.members, id = db.find_one({'_id': str(inter.message.id)})['user'])
                target = disnake.utils.get(inter.guild.members, id = db.find_one({'_id': str(inter.message.id)})['target'])

                for member in (user, target, inter.author):
                    try:
                        await thread.add_user(member)
                    except:
                        pass

                try:
                    embed = disnake.Embed(title = "Moderation Logs", color = 3092790, description=f"{user.mention}, Ваша **жалоба** на {target.mention} была **Принята** модератором, в скором Времени с вами свяжутся")
                    embed.set_thumbnail(url = user.display_avatar.url)
                    embed.add_field(name = "Модератор", value = f"> {inter.author.mention}")
                    embed.set_footer(text = f"Сервер {inter.guild.name}", icon_url = inter.guild.icon.url)
                    msg = await user.send(embed=embed)
                except:
                    pass

                one = files.find_one({"_id": "one"})["emoji_take"]
                two = files.find_one({"_id": "two"})["emoji_take"]
                basket = files.find_one({"_id": "action_basket"})["emoji_take"]
                embed = disnake.Embed(
                    title = f"Управление жалобой {number}",
                    description=(
                        f"* {one} - завершить в пользу {user.mention}\n"
                        f"* {two} - завершить в пользу {target.mention}\n"
                        f"* {basket} Закрыть жалобу"
                    ),
                    color = 3092790
                )
                embed.set_footer(text = f"Модератор - {inter.author}", icon_url = inter.author.display_avatar.url)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                msg = await thread.send(inter.author.mention, embed=embed, view = ReportMenu())

                db.update_one({'_id': str(msg.id)}, {'$set': {'user': user.id}}, upsert = True)
                db.update_one({'_id': str(msg.id)}, {'$set': {'target': target.id}}, upsert = True)
                db.update_one({'_id': str(msg.id)}, {'$set': {'report_message_id': str(inter.message.id)}}, upsert = True)

            if custom_id == 'decline_report':
                embed = inter.message.embeds[0]
                embed.set_footer(text=f"Отклонил репорт - {inter.author}", icon_url=inter.author.display_avatar.url)
                await self._update_report_status(int(inter.message.id), "Отклонено")
                await inter.message.edit(embed=embed, components = [])

        if custom_id == 'accept_one':

            if not inter.response.is_done():
                await inter.response.defer()

            user = disnake.utils.get(inter.guild.members, id = db.find_one({'_id': str(inter.message.id)})['user'])
            target = disnake.utils.get(inter.guild.members, id = db.find_one({'_id': str(inter.message.id)})['target'])
            report_doc = db.find_one({'_id': str(inter.message.id)})
            report_message_id = report_doc.get('report_message_id') if report_doc else None
            await inter.message.edit(components = [])
            try:
                embed = disnake.Embed(title = "Moderation Logs", color = 3092790, description=f"{user.mention}, **Разбор** Вашей жалобы **был** завершен в вашу пользу.\nОставьте **отзыв** модератору, который **занимался** Вашей **жалобой**")
                embed.set_thumbnail(url = user.display_avatar.url)
                embed.add_field(name = "Модератор", value = f"> {inter.author.mention}")
                embed.set_footer(text = f"Сервер {inter.guild.name}", icon_url = inter.guild.icon.url)
                msg = await user.send(embed=embed, view = BallReport())
                db.update_one({'_id': str(msg.id)}, {'$set': {'moderator': int(inter.author.id)}}, upsert = True)
            except:
                pass

            if report_message_id:
                await self._update_report_status(int(report_message_id), "Одобрено")

        if custom_id == 'accept_two':

            if not inter.response.is_done():
                await inter.response.defer()

            user = disnake.utils.get(inter.guild.members, id = db.find_one({'_id': str(inter.message.id)})['user'])
            target = disnake.utils.get(inter.guild.members, id = db.find_one({'_id': str(inter.message.id)})['target'])
            report_doc = db.find_one({'_id': str(inter.message.id)})
            report_message_id = report_doc.get('report_message_id') if report_doc else None
            await inter.message.edit(components = [])
            try:
                embed = disnake.Embed(title = "Moderation Logs", color = 3092790, description=f"{user.mention}, **Разбор** Вашей жалобы **был** завершен в вашу пользу.\nОставьте **отзыв** модератору, который **занимался** Вашей **жалобой**")
                embed.set_thumbnail(url = user.display_avatar.url)
                embed.add_field(name = "Модератор", value = f"> {inter.author.mention}")
                embed.set_footer(text = f"Сервер {inter.guild.name}", icon_url = inter.guild.icon.url)
                msg = await target.send(embed=embed, view = BallReport())
                db.update_one({'_id': str(msg.id)}, {'$set': {'moderator': int(inter.author.id)}}, upsert = True)
            except:
                pass

            if report_message_id:
                await self._update_report_status(int(report_message_id), "Отклонено")

        if custom_id == 'close_report':
            if not inter.response.is_done():
                await inter.response.defer()
            await inter.message.edit(components = [])
                
def setup(bot):
    bot.add_cog(report_cog(bot))