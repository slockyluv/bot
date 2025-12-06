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

class report_cog(commands.Cog):
    def __init__(self, bot: commands.Bot(intents=disnake.Intents.all(), command_prefix = "report!")): # type: ignore
        self.bot = bot

    @commands.slash_command(description = 'Отправить жалобу')
    async def report(self, inter, пользователь: disnake.Member):
        await inter.response.send_modal(title=f"Жалоба на {пользователь.name}", custom_id = "report", components=[
            disnake.ui.TextInput(label=f"Причина жалобы на {пользователь.name}", custom_id = f"Причина жалобы на {пользователь.name}", style=disnake.TextInputStyle.paragraph, max_length=500)])
        modal_inter: disnake.ModalInteraction = await self.bot.wait_for("modal_submit",check=lambda i: i.custom_id == "report" and i.author.id == inter.author.id)
        
        await modal_inter.response.defer(ephemeral=True)

        for key, value in modal_inter.text_values.items():
            reason = value

        embed = disnake.Embed(title = "Репорт", color = 3092790)
        embed.set_thumbnail(url = inter.author.display_avatar.url)
        channel = inter.author.voice.channel if inter.author.voice and inter.author.voice.channel else None
        channel_member = пользователь.voice.channel if пользователь.voice and пользователь.voice.channel else None

        embed.add_field(
            name = "Пользователь",
            value = f"{inter.author.mention}{f'\n{channel}' if channel else ''}",
            inline = True,
        )
        embed.add_field(
            name = "Обвиняемый",
            value = f"{пользователь.mention}{f'\n{channel_member}' if channel_member else ''}",
            inline = True,
        )
        embed.add_field(name = "Причина", value = f"```{reason}```", inline = False)
        msg = await self.bot.get_channel(config['report_channel_id']).send(content=f"<@&{config['moderator']}>", embed=embed, view = ReportView())
        
        db.update_one({'_id': str(msg.id)}, {'$set': {'user': inter.author.id}}, upsert = True)
        db.update_one({'_id': str(msg.id)}, {'$set': {'target': пользователь.id}}, upsert = True)

        embed = disnake.Embed(color = 3092790, description=f"{inter.author.mention}, Вы **успешно** отправили **жалобу** на {пользователь.mention}")
        embed.set_author(name = f"Пожаловаться на нарушителя | {inter.guild.name}", icon_url = inter.guild.icon.url)
        embed.set_thumbnail(url = inter.author.display_avatar.url)
        return await modal_inter.edit_original_response(embed=embed)
    
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

            if custom_id == 'decline_report':
                embed = inter.message.embeds[0]
                embed.set_footer(text=f"Отклонил репорт - {inter.author}", icon_url=inter.author.display_avatar.url)
                await inter.message.edit(embed=embed, components = [])

        if custom_id == 'accept_one':

            if not inter.response.is_done():
                await inter.response.defer()

            user = disnake.utils.get(inter.guild.members, id = db.find_one({'_id': str(inter.message.id)})['user'])
            target = disnake.utils.get(inter.guild.members, id = db.find_one({'_id': str(inter.message.id)})['target'])
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

        if custom_id == 'accept_two':

            if not inter.response.is_done():
                await inter.response.defer()

            user = disnake.utils.get(inter.guild.members, id = db.find_one({'_id': str(inter.message.id)})['user'])
            target = disnake.utils.get(inter.guild.members, id = db.find_one({'_id': str(inter.message.id)})['target'])
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

        if custom_id == 'close_report':
            if not inter.response.is_done():
                await inter.response.defer()
            await inter.message.edit(components = [])
                
def setup(bot):
    bot.add_cog(report_cog(bot))