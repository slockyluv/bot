import disnake
import pymongo
import json
from random import randint
from disnake.ext import commands
from disnake.enums import ButtonStyle, TextInputStyle

with open('configs/zxc.json', 'r') as f:
    config = json.load(f)

with open('configs/zxc_tokens.json', 'r') as f:
    config1 = json.load(f)

cluster = pymongo.MongoClient(config1['mongodb'])

db = cluster.zxc.target
files = cluster.zxc.files_moderation

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
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, emoji = f'{files.find_one({"_id": "one"})["emoji_take"]}', custom_id = 'move_one_report', row = 0))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, emoji = f'{files.find_one({"_id": "two"})["emoji_take"]}', custom_id = 'move_two_report', row = 0))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, emoji = f'{files.find_one({"_id": "three"})["emoji_take"]}', custom_id = 'accept_one', row = 0))
        self.add_item(disnake.ui.Button(style = ButtonStyle.secondary, emoji = f'{files.find_one({"_id": "four"})["emoji_take"]}', custom_id = 'accept_two', row = 0))
        self.add_item(disnake.ui.Button(style = ButtonStyle.red, emoji = f'{files.find_one({"_id": "action_basket"})["emoji_take"]}', custom_id = 'close_report', row = 0))

class report_cog(commands.Cog):
    def __init__(self, bot: commands.Bot(intents=disnake.Intents.all(), command_prefix = "report!")): # type: ignore
        self.bot = bot

    @commands.slash_command(description = 'Отправить жалобу')
    async def report(self, inter, пользователь: disnake.Member):
        await inter.response.send_modal(title=f"Жалоба на {пользователь.name}", custom_id = "report", components=[
            disnake.ui.TextInput(label=f"Причина жалобы на {пользователь.name}", custom_id = f"Причина жалобы на {пользователь.name}", style=disnake.TextInputStyle.paragraph, max_length=500)])
        modal_inter: disnake.ModalInteraction = await self.bot.wait_for("modal_submit",check=lambda i: i.custom_id == "report" and i.author.id == inter.author.id)
        
        for key, value in modal_inter.text_values.items():
            reason = value

        embed = disnake.Embed(title = "Репорт", color = 3092790)
        embed.set_thumbnail(url = inter.author.display_avatar.url)
        channel = "Отсутствует"
        channel_member = "Отсутствует"

        if inter.author.voice and inter.author.voice.channel:
            channel = inter.author.voice.channel
        if пользователь.voice and пользователь.voice.channel:
            channel_member = пользователь.voice.channel

        embed.add_field(name = "Пользователь", value = f"{inter.author.mention}\n{inter.author.id}\n{channel}", inline = True)
        embed.add_field(name = "Обвиняемый", value = f"{пользователь.mention}\n{пользователь.id}\n{channel_member}", inline = True)
        embed.add_field(name = "Причина", value = f"```{reason}```", inline = False)
        msg = await self.bot.get_channel(config['report_channel_id']).send(content=f"<@&{config['moderator']}>", embed=embed, view = ReportView())
        
        db.update_one({'_id': str(msg.id)}, {'$set': {'user': inter.author.id}}, upsert = True)
        db.update_one({'_id': str(msg.id)}, {'$set': {'target': пользователь.id}}, upsert = True)

        embed = disnake.Embed(color = 3092790, description=f"{inter.author.mention}, Вы **успешно** отправили **жалобу** на {пользователь.mention}")
        embed.set_author(name = f"Пожаловаться на нарушителя | {inter.guild.name}", icon_url = inter.guild.icon.url)
        embed.set_thumbnail(url = inter.author.display_avatar.url)
        return await modal_inter.response.send_message(embed=embed)
    
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
            embed.add_field(name = "Оставил отзыв", value = f"{inter.author.mention}\n{inter.author.id}", inline = True)
            embed.add_field(name = "Модератор", value = f"{moder.mention}\n{moder.id}", inline = True)
            await self.bot.get_channel(config['report_reviews']).send(embed=embed)
        
    @commands.Cog.listener()
    async def on_button_click(self, inter):
        custom_id = inter.component.custom_id

        if custom_id == 'ball_report':
            await inter.response.send_modal(title=f"Отзыв", custom_id = "review_report", components=[
                disnake.ui.TextInput(label=f"Текст", custom_id = f"Текст", style=disnake.TextInputStyle.paragraph, max_length=500)])

        if custom_id[-6:] == 'report':
            if custom_id == 'accept_report':
                number = randint(1000, 9999)

                embed = inter.message.embeds[0]
                embed.set_footer(text=f"Принял репорт {number} - {inter.author} / id - {inter.author.id}", icon_url=inter.author.display_avatar.url)
                await inter.message.edit(embed=embed, components = [])

                category = disnake.utils.get(inter.guild.categories, id = config['report_category_id'])
                report_channel_text = await inter.guild.create_text_channel(name = f"💬・Жалоба {number}", category = category)
                report_channel_voice = await inter.guild.create_voice_channel(name = f"🚫・Жалоба {number}", category = category)

                user = disnake.utils.get(inter.guild.members, id = db.find_one({'_id': str(inter.message.id)})['user'])
                target = disnake.utils.get(inter.guild.members, id = db.find_one({'_id': str(inter.message.id)})['target'])

                try:
                    embed = disnake.Embed(title = "Moderation Logs", color = 3092790, description=f"{user.mention}, Ваша **жалоба** на {target.mention} была **Принята** модератором, в скором Времени с вами свяжутся")
                    embed.set_thumbnail(url = user.display_avatar.url)
                    embed.add_field(name = "Модератор", value = f"> {inter.author.mention}\n> {inter.author.id}")
                    embed.set_footer(text = f"Сервер {inter.guild.name}", icon_url = inter.guild.icon.url)
                    msg = await user.send(embed=embed)
                except:
                    pass

                embed = disnake.Embed(title = f"Управление жалобой {number}", description=f"* {files.find_one({"_id": "one"})["emoji_take"]} - переместить {user.mention}\n* {files.find_one({"_id": "two"})["emoji_take"]} переместить {target.mention}\n* {files.find_one({"_id": "three"})["emoji_take"]} - завершить в пользу {user.mention}\n* {files.find_one({"_id": "four"})["emoji_take"]} - завершить в пользу {target.mention}\n* {files.find_one({"_id": "action_basket"})["emoji_take"]} Закрыть тикет", color = 3092790)
                embed.set_footer(text = f"Модератор - {inter.author} / id - {inter.author.id}", icon_url = inter.author.display_avatar.url)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                msg = await report_channel_text.send(inter.author.mention, embed=embed, view = ReportMenu())

                db.update_one({'_id': str(msg.id)}, {'$set': {'text_channel': report_channel_text.id}}, upsert = True)
                db.update_one({'_id': str(msg.id)}, {'$set': {'channel': report_channel_voice.id}}, upsert = True)
                db.update_one({'_id': str(msg.id)}, {'$set': {'user': user.id}}, upsert = True)
                db.update_one({'_id': str(msg.id)}, {'$set': {'target': target.id}}, upsert = True)
                
            if custom_id == 'decline_report':
                embed = inter.message.embeds[0]
                embed.set_footer(text=f"Отклонил репорт - {inter.author} / id - {inter.author.id}", icon_url=inter.author.display_avatar.url)
                await inter.message.edit(embed=embed, components = [])

            if custom_id == 'move_one_report':
                await inter.response.defer()
                report_channel_voice = db.find_one({'_id': str(inter.message.id)})['channel']
                user = disnake.utils.get(inter.guild.members, id = db.find_one({'_id': str(inter.message.id)})['user'])
                try:
                    await user.move_to(self.bot.get_channel(report_channel_voice))
                except:
                    embed = disnake.Embed(title="Репорт", color = 3092790, description = f"{inter.author.mention}, **{user.mention}** находится не в голосовом канале")
                    embed.set_thumbnail(url = inter.author.display_avatar.url)
                    await inter.send(embed=embed)

            if custom_id == 'move_two_report':
                await inter.response.defer()
                report_channel_voice = db.find_one({'_id': str(inter.message.id)})['channel']
                target = disnake.utils.get(inter.guild.members, id = db.find_one({'_id': str(inter.message.id)})['target'])
                try:
                    await target.move_to(self.bot.get_channel(report_channel_voice))
                except:
                    embed = disnake.Embed(title="Репорт", color = 3092790, description = f"{inter.author.mention}, **{target.mention}** находится не в голосовом канале")
                    embed.set_thumbnail(url = inter.author.display_avatar.url)
                    await inter.send(embed=embed)

        if custom_id == 'accept_one':

            user = disnake.utils.get(inter.guild.members, id = db.find_one({'_id': str(inter.message.id)})['user'])
            target = disnake.utils.get(inter.guild.members, id = db.find_one({'_id': str(inter.message.id)})['target'])
            await inter.message.edit(components = [])
            try:
                embed = disnake.Embed(title = "Moderation Logs", color = 3092790, description=f"{user.mention}, **Разбор** Вашей жалобы **был** завершен в вашу пользу.\nОставьте **отзыв** модератору, который **занимался** Вашей **жалобой**")
                embed.set_thumbnail(url = user.display_avatar.url)
                embed.add_field(name = "Модератор", value = f"> {inter.author.mention}\n> {inter.author.id}")
                embed.set_footer(text = f"Сервер {inter.guild.name}", icon_url = inter.guild.icon.url)
                msg = await user.send(embed=embed, view = BallReport())
                db.update_one({'_id': str(msg.id)}, {'$set': {'moderator': int(inter.author.id)}}, upsert = True)
            except:
                pass

            report_channel_voice = self.bot.get_channel(db.find_one({'_id': str(inter.message.id)})['channel'])
            report_channel_text = self.bot.get_channel(db.find_one({'_id': str(inter.message.id)})['text_channel'])
            await report_channel_text.delete()
            await report_channel_voice.delete()

        if custom_id == 'accept_two':

            user = disnake.utils.get(inter.guild.members, id = db.find_one({'_id': str(inter.message.id)})['user'])
            target = disnake.utils.get(inter.guild.members, id = db.find_one({'_id': str(inter.message.id)})['target'])
            await inter.message.edit(components = [])
            try:
                embed = disnake.Embed(title = "Moderation Logs", color = 3092790, description=f"{user.mention}, **Разбор** Вашей жалобы **был** завершен в вашу пользу.\nОставьте **отзыв** модератору, который **занимался** Вашей **жалобой**")
                embed.set_thumbnail(url = user.display_avatar.url)
                embed.add_field(name = "Модератор", value = f"> {inter.author.mention}\n> {inter.author.id}")
                embed.set_footer(text = f"Сервер {inter.guild.name}", icon_url = inter.guild.icon.url)
                msg = await target.send(embed=embed, view = BallReport())
                db.update_one({'_id': str(msg.id)}, {'$set': {'moderator': int(inter.author.id)}}, upsert = True)
            except:
                pass

            report_channel_voice = self.bot.get_channel(db.find_one({'_id': str(inter.message.id)})['channel'])
            report_channel_text = self.bot.get_channel(db.find_one({'_id': str(inter.message.id)})['text_channel'])
            await report_channel_text.delete()
            await report_channel_voice.delete()

        if custom_id == 'close_report':
            await inter.message.edit(components = [])

            report_channel_voice = self.bot.get_channel(db.find_one({'_id': str(inter.message.id)})['channel'])
            report_channel_text = self.bot.get_channel(db.find_one({'_id': str(inter.message.id)})['text_channel'])
            await report_channel_text.delete()
            await report_channel_voice.delete()
                
def setup(bot): 
    bot.add_cog(report_cog(bot))