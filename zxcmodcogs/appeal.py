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
from random import randint
from statistics import mean
from PIL import Image, ImageDraw, ImageFont
import re

with open('configs/zxc.json', 'r') as f:
    config = json.load(f)

with open('configs/zxc_tokens.json', 'r') as f:
    config1 = json.load(f)

cluster = pymongo.MongoClient(config1['mongodb'])
files = cluster.zxc.files_moderation

class AppealBtns(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="Снятие LocalBan", custom_id="unavailable_appeal", emoji=f'{files.find_one({"_id": "ban"})["emoji_take"]}'))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label = 'Правила', emoji = "📚", url = "https://discord.com/channels/1401585923032088576/1401585923032088576"))
        
class AppealBtns1(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="Снятие Не Допуск", custom_id="unverify_appeal", emoji = f'{files.find_one({"_id": "verify"})["emoji_take"]}'))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label = 'Правила', emoji = "📚", url = "https://discord.com/channels/1401585923032088576/1401585923032088576"))

class Appeal(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #@commands.slash_command(description="Вызвать команду аппеляции")
    #@commands.has_any_role(1158698008876159006)
    #async def appeal(self, inter):
    #    await inter.response.send_modal(title="Appeal", custom_id="appeal_appeal", components=[
    #        disnake.ui.TextInput(label="Причина вашего мута:", custom_id="Причина вашего мута:", style=disnake.TextInputStyle.short, max_length=100),
    #        disnake.ui.TextInput(label="Почему вы считаете что вы заслуживаете размут", custom_id="Почему вы считаете что вы заслуживаете размут", style=disnake.TextInputStyle.short, max_length=100),
    #        disnake.ui.TextInput(label="Что бы вы изменили в своем поведении?", custom_id="Что бы вы изменили в своем поведении?", style=disnake.TextInputStyle.short, max_length=100),
    #    ])
#
    #@appeal.error
    #async def appeal_error(self, inter, error):
    #    if isinstance(error, commands.MissingAnyRole):
    #        embed = disnake.Embed(title = "Ошибка", description=f"{inter.author.mention}, У **Вас** нету мута", color=3092790)
    #        embed.set_author(name = inter.author, icon_url = inter.author.display_avatar.url)
    #        embed.set_thumbnail(url = inter.author.display_avatar.url)
    #        await inter.send(embed=embed, ephemeral=True)
    #    else:
    #        raise error
    #    
    @commands.command(description="Вызвать команду аппеляции")
    @commands.has_permissions(administrator=True)
    async def appeal(self, inter):
        await inter.message.delete()

        embed1 = disnake.Embed(color=3092790)

        embed1.set_image(url = "https://cdn.discordapp.com/attachments/1328079062744301698/1328107237889146971/image.png?ex=67974c00&is=6795fa80&hm=fda59d2348be3069f1ef8a005efa1180bd0f17cd0b89b98e702528ebf058d9b0&")

        description = (
            f"# ПОЛУЧИЛ БАН? \n\n"
            f"*Если вы оказались в данном канале, то это означает, что Вы серьёзно нарушили правила сервера и получили за это бан.*\n\n"
            f"**Форма заполнения:**\n\n"
            f"<:to4kaa:947909744985800804> Дата получения бана и кто его выдал\n"
            f"<:to4kaa:947909744985800804> Причина бана, вы должны написать чёткий пункт правил\n"
            f"<:to4kaa:947909744985800804> Почему по вашему мнению, вас должны разбанить?\n\n"
            f"Всё это ты можешь описать в канале ⁠⁠<#1282408238955892827>\n\n"
            f"*Обратите внимание, что завки на обжалование бана рассматривает администратор с ролью <@&{config['moderator_admin']}>, "
            f"а заявки на обжалование недопуска рассматривает администратор с ролью <@&{config['support_admin']}>, не зависимо от ваших"
            f" пожеланий или требований.*\n"
            f"*Заявки, поданные со сторонних аккаунтов, рассматриваться не будут.*"
        )
        embed = disnake.Embed(color=3092790, description=description)
        embed.set_footer(text="Все заявки будут рассмотрены в течение 24 часов")
        embed.set_image(url = "https://cdn.discordapp.com/attachments/1068973656228757606/1141374896258175138/line.png?ex=67979534&is=679643b4&hm=4c13a7e04014dd57bbe2648c13096014c36f79b05bef0fc50d0a135394591a45&")
        await inter.send(embeds=[embed], view = AppealBtns())

        cluster.zxc.server_settings.update_one({'_id': str(inter.guild.id)}, {'$set': {'appeal_ban_channel': int(inter.channel.id)}}, upsert=True)

    @commands.command(description="Вызвать команду аппеляции")
    @commands.has_permissions(administrator=True)
    async def appeal1(self, inter):
        await inter.message.delete()

        embed1 = disnake.Embed(color=3092790)

        embed1.set_image(url = "https://cdn.discordapp.com/attachments/1328079062744301698/1328107237889146971/image.png?ex=67974c00&is=6795fa80&hm=fda59d2348be3069f1ef8a005efa1180bd0f17cd0b89b98e702528ebf058d9b0&")

        description = (
            f"# ПОЛУЧИЛ НЕДОПУСК? \n\n"
            f"*Если вы оказались в данном канале, то это означает, что Вы серьёзно нарушили правила сервера и получили за это бан.*\n\n  **Форма заполнения:**\n\n"
            f"<:to4kaa:947909744985800804> Дата получения бана и кто его выдал\n"
            f"<:to4kaa:947909744985800804> Причина бана, вы должны написать чёткий пункт правил\n"
            f"<:to4kaa:947909744985800804> Почему по вашему мнению, вас должны разбанить?\n\n"
            f"Всё это ты можешь описать в канале ⁠⁠<#1282408275089817821>\n\n"
            f"*Обратите внимание, что завки на обжалование бана рассматривает администратор с ролью <@&{config['moderator_admin']}>, "
            f"а заявки на обжалование недопуска рассматривает администратор с ролью <@&{config['support_admin']}>, не зависимо от ваших"
            f" пожеланий или требований.*\n"
            f"*Заявки, поданные со сторонних аккаунтов, рассматриваться не будут.*"
        )
        embed = disnake.Embed(color=3092790, description=description)
        embed.set_footer(text="Все заявки будут рассмотрены в течение 24 часов")
        embed.set_image(url = "https://cdn.discordapp.com/attachments/1068973656228757606/1141374896258175138/line.png?ex=67979534&is=679643b4&hm=4c13a7e04014dd57bbe2648c13096014c36f79b05bef0fc50d0a135394591a45&")
        await inter.send(embeds=[embed], view = AppealBtns1())

        cluster.zxc.server_settings.update_one({'_id': str(inter.guild.id)}, {'$set': {'appeal_nedopysk_channel': int(inter.channel.id)}}, upsert=True)
        
    @appeal.error
    async def appeal_error(self, inter, error):
        if isinstance(error, commands.MissingPermissions):
            embed = disnake.Embed(title = "Ошибка", description=f"{inter.author.mention}, У **Вас** нету прав", color=3092790)
            embed.set_author(name = inter.author, icon_url = inter.author.display_avatar.url)
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            await inter.send(embed=embed, ephemeral=True)
        else:
            raise error

    @commands.Cog.listener()
    async def on_button_click(self, inter):
        custom_id = inter.component.custom_id

        if custom_id.endswith("appeal"):
            if custom_id == "unavailable_appeal":
                await inter.response.send_modal(title="LocalBan Appeal", custom_id="unavailable_appeal", components=[
                    disnake.ui.TextInput(label="Причина вашего бана:", custom_id="Причина вашего бана:", style=disnake.TextInputStyle.paragraph, max_length=100),
                    disnake.ui.TextInput(label="Почему вы считаете что вы заслуживаете разбан", custom_id="Почему вы считаете что вы заслуживаете разбан", style=disnake.TextInputStyle.paragraph, max_length=100),
                    disnake.ui.TextInput(label="Что бы вы изменили в своем поведении?", custom_id="Что бы вы изменили в своем поведении?", style=disnake.TextInputStyle.paragraph, max_length=100),
                ])

            if custom_id == "unverify_appeal":
                await inter.response.send_modal(title="Не допуск Appeal", custom_id="unverify_appeal", components=[
                    disnake.ui.TextInput(label="Причина вашего не допуска:", custom_id="Причина вашего не допуска:", style=disnake.TextInputStyle.paragraph, max_length=100),
                    disnake.ui.TextInput(label="Почему вы считаете что вы заслуживаете снятие", custom_id="Почему вы считаете что вы заслуживаете снятие", style=disnake.TextInputStyle.paragraph, max_length=100),
                    disnake.ui.TextInput(label="Что бы вы изменили в своем поведении?", custom_id="Что бы вы изменили в своем поведении?", style=disnake.TextInputStyle.paragraph, max_length=100),
                ])

    @commands.Cog.listener()
    async def on_modal_submit(self, inter):
        custom_id = inter.custom_id

        if custom_id.endswith("appeal"):
            embed = disnake.Embed(color=3092790)
            embed.set_thumbnail(url=inter.author.display_avatar.url)
            embed.set_author(name=f"Appeal на сервере {inter.guild}", icon_url=inter.guild.icon.url)

            if custom_id == "unavailable_appeal":
                embed.description = f"Выбранная категория: **LocalBan**\n\n"
                channel_appeal = 1259842691307405334
            if custom_id == "unverify_appeal":
                embed.description = f"Выбранная категория: **Не допуск**\n\n"
                channel_appeal = 1259842730100527145
            
            if not cluster.zxc.appeal.count_documents({"_id": str(inter.author.id)}) == 0:
                data_delete = cluster.zxc.appeal.find_one({'_id': str(inter.author.id)})['time']
                remaining_minutes = (data_delete - datetime.now()).total_seconds() / 60
                if remaining_minutes > 0:
                    embed.description = f"{inter.author.mention}, **Вы** слишком часто подаете заявки на аппеляцию!"
                    return await inter.send(ephemeral = True, embed=embed)
                
            new_date = datetime.now().replace(microsecond=0) + timedelta(minutes=10)
            cluster.zxc.appeal.update_one({'_id': str(inter.author.id)}, {'$set': {'time': new_date}}, upsert = True)
            
            embed.set_footer(text=f"Подал заявку {inter.author} | ID: {inter.author.id}", icon_url=inter.author.display_avatar.url)
            for key, value in inter.text_values.items():
                embed.add_field(name=key.capitalize(), value=value, inline=False)
                
            reactions = ["✅", "❌"]
            msg = await self.bot.get_channel(channel_appeal).send(embed=embed)
            for i in reactions:
                await msg.add_reaction(i)

            cluster.zxc.appeal.update_one({"_id": str(msg.id)}, {"$set": {"msg_member": int(inter.author.id)}}, upsert=True)

            embed = disnake.Embed(description=f"{inter.author.mention}, Ваша апелляция была успешно принята на рассмотрение. Appeal ID: #{randint(0, 15)}", color=3092790)
            embed.set_author(name=f"Appeal на сервере {inter.guild}", icon_url=inter.guild.icon.url)
            embed.set_thumbnail(url=inter.author.display_avatar.url)
            await inter.send(ephemeral=True, embed=embed, components=[])

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        guild = self.bot.get_guild(payload.guild_id)
        reaction = disnake.utils.get(message.reactions, emoji=payload.emoji.name)

        if payload.channel_id == 1259842691307405334 and reaction.emoji == "✅" or payload.channel_id == 1259842730100527145 and reaction.emoji:
            interested_emojis = ["✅"]
            reaction_count = 0
            for reaction in message.reactions:
                if reaction.emoji in interested_emojis:
                    reaction_count += reaction.count
            if reaction_count > 1:
                await message.edit(content="# Аппеляция была принята")
                await message.clear_reactions()

                member = disnake.utils.get(guild.members, id=int(cluster.zxc.appeal.find_one({"_id": str(message.id)})["msg_member"]))

                await member.remove_roles(guild.get_role(config['unverify']))
                await member.add_roles(guild.get_role(config['male']))
           
                await member.remove_roles(guild.get_role(config['local_ban']))

                embed = disnake.Embed(description=f"{member.mention}, Аппеляция **была принята**, действия аппеляции **будут приняты** в ближайшее время.", color=disnake.Color.green())
                embed.set_author(name=f"Appeal | {member.guild}", icon_url=member.guild.icon.url)
                embed.set_thumbnail(url=member.display_avatar.url)
                await member.send(embed=embed)

            if payload.member.id == self.bot.user.id:
                return

        if payload.channel_id == 1259842691307405334 and reaction.emoji == "❌" or payload.channel_id == 1259842730100527145 and reaction.emoji == "❌":
            interested_emojis = ["❌"]
            reaction_count = 0

            for reaction in message.reactions:
                if reaction.emoji in interested_emojis:
                    reaction_count += reaction.count

            if reaction_count > 1:
                await message.edit(content="# Аппеляция была отклонена")
                await message.clear_reactions()

                member = disnake.utils.get(guild.members, id=int(cluster.zxc.appeal.find_one({"_id": str(message.id)})["msg_member"]))

                embed = disnake.Embed(description=f"{member.mention}, **Ваш** Appeal был **отклонен.**", color=disnake.Color.red())
                embed.set_author(name=f"Appeal | {member.guild}", icon_url=member.guild.icon.url)
                embed.set_thumbnail(url=member.display_avatar.url)
                await member.send(embed=embed)
            if payload.member.id == self.bot.user.id:
                return


def setup(bot):
    bot.add_cog(Appeal(bot))