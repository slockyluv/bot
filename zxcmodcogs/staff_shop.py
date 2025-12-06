import pymongo
import disnake
import json
from disnake.ext import commands
from disnake.utils import get
from disnake.enums import ButtonStyle, TextInputStyle
from collections import OrderedDict

with open('configs/zxc.json', 'r') as f:
    config = json.load(f)

with open('configs/zxc_tokens.json', 'r') as f:
    config1 = json.load(f)

cluster = pymongo.MongoClient(config1['mongodb'])

files = cluster.zxc.files_moderation

rolebutton = {}
roleyes = {}
currentShopTopPage = {}
hour = 60 * 60
shop = {}

administrator = config['administrator']
curator = config['curator']
moderator = config['moderator']
support = config['support']
staff_role = config['staff_role']
own_roles = config['own_roles']
master = config['master']
closer = config['closer']
eventer = config['eventer']
creative = config['creative']
tribunemod = config['tribunemod']

class AcceptOtherShop(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, custom_id="shop_other_accept", emoji=f"{files.find_one({'_id': 'accept'})['emoji_take']}"))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, custom_id="shop_back", emoji=f"{files.find_one({'_id': 'decline'})['emoji_take']}"))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, custom_id="exit_action", emoji=f'{files.find_one({"_id": "basket"})["emoji_take"]}'))

class ShopBack(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, custom_id="shop_back", emoji=f"{files.find_one({'_id': 'back'})['emoji_take']}"))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, custom_id="exit_action", emoji=f'{files.find_one({"_id": "basket"})["emoji_take"]}', row = 0))

class ShopOther(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label = "⠀", custom_id="shop_other_buy1", emoji=f"{files.find_one({'_id': 'one'})['emoji_take']}", row = 0))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label = "⠀", custom_id="shop_other_buy2", emoji=f"{files.find_one({'_id': 'two'})['emoji_take']}", row = 0))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label = "⠀", custom_id="shop_other_buy3", emoji=f"{files.find_one({'_id': 'three'})['emoji_take']}", row = 0))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label = "⠀", custom_id="shop_other_buy4", emoji=f"{files.find_one({'_id': 'four'})['emoji_take']}", row = 0))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label = "⠀", custom_id="shop_other_buy5", emoji=f"{files.find_one({'_id': 'five'})['emoji_take']}", row = 1))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label = "⠀", custom_id="shop_other_buy6", emoji=f"{files.find_one({'_id': 'six'})['emoji_take']}", row = 1))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label = "⠀", custom_id="shop_other_buy7", emoji=f"{files.find_one({'_id': 'seven'})['emoji_take']}", row = 1))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label = "⠀", custom_id="shop_other_buy8", emoji=f"{files.find_one({'_id': 'eight'})['emoji_take']}", row = 1))
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, custom_id="exit_action", emoji=f'{files.find_one({"_id": "basket"})["emoji_take"]}', row = 1))

class StaffShop(commands.Cog):
    def __init__(self, bot: commands.Bot(intents=disnake.Intents.all(), command_prefix = "!")): # type: ignore
        self.bot = bot

    @commands.slash_command(description="Магазин для стаффа")
    async def staff_shop(self, inter):
        for role in inter.author.roles:
            if role.id in own_roles or role.id in [administrator, curator, master, moderator, support, closer, eventer, creative, tribunemod, staff_role]:
                if cluster.zxc.balls.count_documents({"_id": str(inter.author.id)}) == 0: 
                    cluster.zxc.balls.insert_one({"_id": str(inter.author.id), "balls": 0})

                balls = cluster.zxc.balls.find_one({"_id": str(inter.author.id)})["balls"]

                embed = disnake.Embed(color=3092790, description="")
                embed.set_thumbnail(url=inter.author.display_avatar.url)
                embed.set_author(name="Staff Shop", icon_url=inter.guild.icon.url)
                embed.add_field(name = f'{files.find_one({"_id": "one"})["emoji_take"]} Дискорд нитро месяц', value = '**Цена:** 600 баллов', inline = False)
                embed.add_field(name = f'{files.find_one({"_id": "two"})["emoji_take"]} Тг прем месяц', value = '**Цена:** 500 баллов', inline = False)
                embed.add_field(name = f'{files.find_one({"_id": "three"})["emoji_take"]} Дискорд нитро Год', value = '**Цена:** 1800 баллов', inline = False)
                embed.add_field(name = f'{files.find_one({"_id": "four"})["emoji_take"]} Тг прем год', value = '**Цена:** 1500 баллов', inline = False)
                
                embed.add_field(name = f'{files.find_one({"_id": "five"})["emoji_take"]} Украшение аватарки', value = '**Цена:** 500 баллов', inline = False)
                embed.add_field(name = f'{files.find_one({"_id": "six"})["emoji_take"]} Украшение профиля', value = '**Цена:** 600 баллов', inline = False)
                embed.add_field(name = f'{files.find_one({"_id": "seven"})["emoji_take"]} Снятия выговора', value = '**Цена:** 100 баллов', inline = False)
                embed.set_footer(text = f"У вас баллов: {balls}")
                return await inter.send(inter.author.mention, embed=embed, view = ShopOther())
            
        embed = disnake.Embed(description = f'{inter.author.mention}, У **Вас** нет на это **разрешения**!', color = 3092790)
        embed.set_thumbnail(url = inter.author.display_avatar.url)
        embed.set_author(name = inter.author, icon_url = inter.author.avatar.url)
        await inter.send(embed=embed)

    @commands.Cog.listener()
    async def on_button_click(self, inter):
        custom_id = inter.component.custom_id

        if custom_id[:4] == "shop":
            if not inter.message.content == inter.author.mention:
                embed = disnake.Embed(description=f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color=3092790)
                embed.set_author(name="Staff Shop", icon_url=inter.guild.icon.url)
                embed.set_thumbnail(url=inter.author.display_avatar.url)
                return await inter.send(ephemeral=True, embed=embed)
            
            embed = disnake.Embed(color=3092790, description="")
            embed.set_thumbnail(url=inter.author.display_avatar.url)
            embed.set_author(name="Staff Shop", icon_url=inter.guild.icon.url)

            balls = cluster.zxc.balls.find_one({"_id": str(inter.author.id)})["balls"]

            if custom_id == "shop_action":
                embed.add_field(name = f'{files.find_one({"_id": "one"})["emoji_take"]} Дискорд нитро месяц', value = '**Цена:** 600 баллов', inline = False)
                embed.add_field(name = f'{files.find_one({"_id": "two"})["emoji_take"]} Тг прем месяц', value = '**Цена:** 500 баллов', inline = False)
                embed.add_field(name = f'{files.find_one({"_id": "three"})["emoji_take"]} Дискорд нитро Год', value = '**Цена:** 1800 баллов', inline = False)
                embed.add_field(name = f'{files.find_one({"_id": "four"})["emoji_take"]} Тг прем год', value = '**Цена:** 1500 баллов', inline = False)
                
                embed.add_field(name = f'{files.find_one({"_id": "five"})["emoji_take"]} Украшение аватарки', value = '**Цена:** 500 баллов', inline = False)
                embed.add_field(name = f'{files.find_one({"_id": "six"})["emoji_take"]} Украшение профиля', value = '**Цена:** 600 баллов', inline = False)
                embed.add_field(name = f'{files.find_one({"_id": "seven"})["emoji_take"]} Снятия выговора', value = '**Цена:** 100 баллов', inline = False)
                return await inter.send(content = inter.author.mention, embed=embed, view = ShopOther(), ephemeral = True)

            if custom_id == "shop_back":
                embed.add_field(name = f'{files.find_one({"_id": "one"})["emoji_take"]} Дискорд нитро месяц', value = '**Цена:** 600 баллов', inline = False)
                embed.add_field(name = f'{files.find_one({"_id": "two"})["emoji_take"]} Тг прем месяц', value = '**Цена:** 500 баллов', inline = False)
                embed.add_field(name = f'{files.find_one({"_id": "three"})["emoji_take"]} Дискорд нитро Год', value = '**Цена:** 1800 баллов', inline = False)
                embed.add_field(name = f'{files.find_one({"_id": "four"})["emoji_take"]} Тг прем год', value = '**Цена:** 1500 баллов', inline = False)
                
                embed.add_field(name = f'{files.find_one({"_id": "five"})["emoji_take"]} Украшение аватарки', value = '**Цена:** 500 баллов', inline = False)
                embed.add_field(name = f'{files.find_one({"_id": "six"})["emoji_take"]} Украшение профиля', value = '**Цена:** 600 баллов', inline = False)
                embed.add_field(name = f'{files.find_one({"_id": "seven"})["emoji_take"]} Снятия выговора', value = '**Цена:** 100 баллов', inline = False)
                return await inter.response.edit_message(content = inter.author.mention, embed=embed, view = ShopOther())
            
            elif custom_id == "shop_exit":
                return await inter.message.delete()
            elif custom_id.startswith("shop_other"):
                if custom_id == "shop_other_accept":
                    price = roleyes[inter.author.id]['price']
                    description = roleyes[inter.author.id]['description']

                    if int(price) > int(balls):
                        embed.description = f'{inter.author.mention}, У **Вас** на балансе **недостаточно средств** для совершения этой **операции**.'
                        return await inter.send(embed=embed)

                    if description == "Купить отпуск":
                        channel = self.bot.get_channel(config['chat'])
                        await channel.set_permissions(inter.author, attach_files=True)
                    if description == "Кастомный стафф профиль":
                        if cluster.zxc.backgrounds_profile.count_documents({"_id": str(inter.author.id)}) == 0:
                            cluster.zxc.backgrounds_profile.insert_one({"_id": str(inter.author.id), "choice_profile_moderation": 0, "choice_profile": 0, "choice_profile_mafia": 0})

                        embed = disnake.Embed(description = f"{inter.author.mention}, **Отправьте** фото в этот канал для того чтобы **поставить** в **профиле** модерации **фон**", color = 3092790)
                        embed.set_thumbnail(url = inter.author.display_avatar.url)
                        embed.set_author(name = f"Добавить/Изменить фон профиля: Модерация | {inter.guild.name}", icon_url = inter.guild.icon.url)
                        await inter.response.edit_message(embed=embed, components = [])

                        def check(m):
                            return m.author.id == inter.author.id
                        try: 
                            image = await self.bot.wait_for("message", check = check)
                        except TimeoutError:
                            return

                        for attach in image.attachments:
                            await attach.save(f"profile_moderation_background/{inter.author.id}.png")

                        cluster.zxc.backgrounds_profile.update_one({'_id': str(inter.author.id)}, {'$set': {f"choice_profile_moderation": 1}}, upsert = True)

                        embed = disnake.Embed(description = f"{inter.author.mention}, **Вы** успешно поставили фон **профиля**", color = 3092790)
                        embed.set_thumbnail(url = inter.author.display_avatar.url)
                        embed.set_author(name = f"Добавить/Изменить фон профиля: Модерация | {inter.guild.name}", icon_url = inter.guild.icon.url)
                        return await inter.message.edit(embed=embed)
                    if description == "Освобождение от нормы на неделю":
                        cluster.zxc.history_punishment.delete_one({'_id': str(inter.author.id)})
                    if description == "Снятие выговора":
                        ...
                    if description == "Нитро фулл":
                        ...

                    point_emoji = files.find_one({'_id': 'point'})['emoji_take']
                    embed.description = (
                        f"{inter.author.mention}, **Вы успешно**, приобрели **{description}** "
                        f"за **{price}** {point_emoji}"
                    )
                    return await inter.response.edit_message(embed=embed, components = [])
                else:
                    id_mapping = {
                        "shop_other_buy1": {"price": 600, "description": "Дискорд нитро месяц"},
                        "shop_other_buy2": {"price": 500, "description": "Тг прем месяц"},
                        "shop_other_buy3": {"price": 1800, "description": "Дискорд нитро Год"},
                        "shop_other_buy4": {"price": 1500, "description": "Тг прем год"},
                        "shop_other_buy5": {"price": 500, "description": "Украшение аватарки"},
                        "shop_other_buy6": {"price": 600, "description": "Украшение профиля"},
                        "shop_other_buy7": {"price": 100, "description": "Снятия выговора"},
                    }
                    price = id_mapping[custom_id]['price']
                    description = id_mapping[custom_id]['description']
                    roleyes[inter.author.id] = {"price": price, "description": description}

                    point_emoji = files.find_one({'_id': 'point'})['emoji_take']
                    accept_emoji = files.find_one({'_id': 'accept'})['emoji_take']
                    decline_emoji = files.find_one({'_id': 'decline'})['emoji_take']
                    embed.description = (
                        f"{inter.author.mention}, **Вы уверены**, что Вы хотите купить **{description}** "
                        f"за **{price}** {point_emoji}?\n"
                        f"Для **согласия** нажмите на {accept_emoji}, для **отказа** на {decline_emoji}"
                    )
                    return await inter.response.edit_message(embed=embed, view = AcceptOtherShop())

def setup(bot):
    bot.add_cog(StaffShop(bot))