import disnake
from disnake.ext import commands
from disnake.enums import ButtonStyle

def get_members_embed(role: disnake.Role, members_in_voice: list, members_not_in_voice: list, room: disnake.VoiceChannel = None) -> disnake.Embed:
    description = f"Роль: {role.mention}\n"
    if room:
        description += f"Комната: {room.mention}\n"
    
    total_members = len(members_in_voice) + len(members_not_in_voice)
    description += f"\n**Всего**: {total_members} участников\n"
    
    if room:
        description += f"**В войсе**: {len(members_in_voice)} участников\n"
        description += f"**Не в войсе**: {len(members_not_in_voice)} участников\n\n"
    else:
        description += "\n"
    
    # Показываем первые 25 участников в войсе и первые 25 не в войсе
    start = 0
    end = min(25, len(members_in_voice))
    page_members_in_voice = members_in_voice[start:end]
    
    end_not_voice = min(25, len(members_not_in_voice))
    page_members_not_in_voice = members_not_in_voice[start:end_not_voice]
    
    if room and members_in_voice:
        description += "**🔊 В войсе:**\n"
        description += "".join(page_members_in_voice)
        description += "\n"
    
    if room and members_not_in_voice:
        description += "**🔇 Не в войсе:**\n"
        description += "".join(page_members_not_in_voice)
    elif not room:
        # Если комната не указана, показываем всех участников как раньше
        all_members = members_in_voice + members_not_in_voice
        page_members = all_members[start:min(50, len(all_members))]
        description += "".join(page_members)
    
    embed = disnake.Embed(
        title=f"Участники роли {role.name}",
        description=description,
        color=role.color
    )
    
    if room:
        total_pages_voice = (len(members_in_voice) - 1) // 25 + 1 if members_in_voice else 1
        total_pages_not_voice = (len(members_not_in_voice) - 1) // 25 + 1 if members_not_in_voice else 1
        total_pages = max(total_pages_voice, total_pages_not_voice)
    else:
        total_pages = (total_members - 1) // 50 + 1
    
    if total_pages > 1:
        embed.set_footer(text=f"Страница 1 из {total_pages}")
    
    return embed

class MembersPaginationView(disnake.ui.View):
    def __init__(self, members_in_voice: list, members_not_in_voice: list, category: str, role: disnake.Role, room: disnake.VoiceChannel = None, page: int = 0):
        super().__init__(timeout=180)
        self.members_in_voice = members_in_voice
        self.members_not_in_voice = members_not_in_voice
        self.category = category
        self.page = page
        self.role = role
        self.room = room

    def get_page_embed(self) -> disnake.Embed:
        if self.room:
            # При выборе комнаты показываем по 25 участников каждой категории
            start_voice = self.page * 25
            end_voice = start_voice + 25
            page_members_in_voice = self.members_in_voice[start_voice:end_voice]
            
            start_not_voice = self.page * 25
            end_not_voice = start_not_voice + 25
            page_members_not_in_voice = self.members_not_in_voice[start_not_voice:end_not_voice]
            
            description = f"Роль: {self.role.mention}\n"
            description += f"Комната: {self.room.mention}\n"
            
            total_members = len(self.members_in_voice) + len(self.members_not_in_voice)
            description += f"\n**Всего**: {total_members} участников\n"
            description += f"**В войсе**: {len(self.members_in_voice)} участников\n"
            description += f"**Не в войсе**: {len(self.members_not_in_voice)} участников\n\n"
            
            if page_members_in_voice:
                description += "**🔊 В войсе:**\n"
                description += "".join(page_members_in_voice)
                description += "\n"
            
            if page_members_not_in_voice:
                description += "**🔇 Не в войсе:**\n"
                description += "".join(page_members_not_in_voice)
                
            total_pages_voice = (len(self.members_in_voice) - 1) // 25 + 1 if self.members_in_voice else 1
            total_pages_not_voice = (len(self.members_not_in_voice) - 1) // 25 + 1 if self.members_not_in_voice else 1
            total_pages = max(total_pages_voice, total_pages_not_voice)
        else:
            # Без комнаты показываем как раньше
            all_members = self.members_in_voice + self.members_not_in_voice
            start = self.page * 50
            end = start + 50
            page_members = all_members[start:end]
            
            description = f"Роль: {self.role.mention}\n"
            description += f"\n**Всего**: {len(all_members)} участников\n\n"
            description += "".join(page_members)
            
            total_pages = (len(all_members) - 1) // 50 + 1
        
        embed = disnake.Embed(
            title=f"Участники роли {self.role.name}",
            description=description,
            color=self.role.color
        )
        embed.set_footer(text=f"Страница {self.page + 1} из {total_pages}")
        return embed

    @disnake.ui.button(label="Предыдущая", style=ButtonStyle.primary, custom_id="prev_page")
    async def prev_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        pass

    @disnake.ui.button(label="Следующая", style=ButtonStyle.primary, custom_id="next_page")
    async def next_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        pass

class inrole(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.user_data = {}

    @commands.slash_command(description='Список участников на роли')
    async def inrole(
        self, 
        inter: disnake.ApplicationCommandInteraction, 
        role: disnake.Role,
        room: disnake.VoiceChannel = None
    ):
        filtered_members = role.members
        
        if room:
            # Фильтруем участников только по роли, но разделяем их на тех кто в указанной комнате и кто нет
            members_in_voice = []
            members_not_in_voice = []
            
            for member in filtered_members:
                entry = f"{member.mention}\n"
                
                if member.voice and member.voice.channel == room:
                    members_in_voice.append(entry)
                else:
                    members_not_in_voice.append(entry)
        else:
            # Если комната не указана, разделяем на тех кто в любом войсе и кто не в войсе
            members_in_voice = []
            members_not_in_voice = []
            
            for member in filtered_members:
                if member.voice and member.voice.channel:
                    voice_channel = f"***{member.voice.channel.name}***"
                    entry = f"{member.mention} {voice_channel}\n"
                    members_in_voice.append(entry)
                else:
                    entry = f"{member.mention} Не в войсе\n"
                    members_not_in_voice.append(entry)

        self.user_data[inter.author.id] = {
            "role": role,
            "members_in_voice": members_in_voice,
            "members_not_in_voice": members_not_in_voice,
            "room": room
        }

        total_members = len(members_in_voice) + len(members_not_in_voice)
        
        if room:
            # При выборе комнаты проверяем нужна ли пагинация (более 25 в каждой категории)
            if len(members_in_voice) <= 25 and len(members_not_in_voice) <= 25:
                embed = get_members_embed(role, members_in_voice, members_not_in_voice, room)
                await inter.send(embed=embed)
            else:
                view = MembersPaginationView(members_in_voice, members_not_in_voice, "Участники", role, room)
                embed = view.get_page_embed()
                await inter.send(embed=embed, view=view)
        else:
            # Без комнаты проверяем общее количество (50 участников на страницу)
            if total_members <= 50:
                embed = get_members_embed(role, members_in_voice, members_not_in_voice, room)
                await inter.send(embed=embed)
            else:
                view = MembersPaginationView(members_in_voice, members_not_in_voice, "Участники", role, room)
                embed = view.get_page_embed()
                await inter.send(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        try:
            user_data = self.user_data[inter.author.id]
        except:
            pass

        if inter.component.custom_id == "prev_page":
            for component_row in inter.message.components:
                for component in component_row.children:
                    if hasattr(component, 'custom_id') and component.custom_id == "prev_page":
                        view = MembersPaginationView(
                            user_data["members_in_voice"], 
                            user_data["members_not_in_voice"], 
                            "Участники", 
                            user_data["role"], 
                            user_data.get("room")
                        )
                        if hasattr(inter.message, 'embeds') and inter.message.embeds:
                            current_page = 0
                            footer = inter.message.embeds[0].footer
                            if footer and "Страница" in str(footer.text):
                                try:
                                    current_page = int(str(footer.text).split()[1]) - 1
                                except:
                                    current_page = 0
                            
                            if current_page > 0:
                                view.page = current_page - 1
                                embed = view.get_page_embed()
                                await inter.response.edit_message(embed=embed, view=view)
                                return
                        await inter.response.defer()
                        return

        elif inter.component.custom_id == "next_page":
            for component_row in inter.message.components:
                for component in component_row.children:
                    if hasattr(component, 'custom_id') and component.custom_id == "next_page":
                        view = MembersPaginationView(
                            user_data["members_in_voice"], 
                            user_data["members_not_in_voice"], 
                            "Участники", 
                            user_data["role"], 
                            user_data.get("room")
                        )
                        if hasattr(inter.message, 'embeds') and inter.message.embeds:
                            current_page = 0
                            footer = inter.message.embeds[0].footer
                            if footer and "Страница" in str(footer.text):
                                try:
                                    current_page = int(str(footer.text).split()[1]) - 1
                                except:
                                    current_page = 0
                            
                            if user_data.get("room"):
                                # При выборе комнаты считаем максимальную страницу по 25 участников в каждой категории
                                total_pages_voice = (len(user_data["members_in_voice"]) - 1) // 25 + 1 if user_data["members_in_voice"] else 1
                                total_pages_not_voice = (len(user_data["members_not_in_voice"]) - 1) // 25 + 1 if user_data["members_not_in_voice"] else 1
                                max_page = max(total_pages_voice, total_pages_not_voice) - 1
                            else:
                                # Без комнаты считаем общее количество по 50 участников на страницу
                                total_members = len(user_data["members_in_voice"]) + len(user_data["members_not_in_voice"])
                                max_page = (total_members - 1) // 50
                            
                            if current_page < max_page:
                                view.page = current_page + 1
                                embed = view.get_page_embed()
                                await inter.response.edit_message(embed=embed, view=view)
                                return
                        await inter.response.defer()
                        return

    @commands.Cog.listener()
    async def on_dropdown(self, inter: disnake.MessageInteraction):
        pass

def setup(bot):
    bot.add_cog(inrole(bot))