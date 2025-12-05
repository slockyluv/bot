import pymongo
import disnake
import json
import requests
import os
from disnake.ext import commands
from disnake.enums import ButtonStyle
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

with open('configs/zxc.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
with open('configs/zxc_tokens.json', 'r', encoding='utf-8') as f:
    config1 = json.load(f)

cluster = pymongo.MongoClient(config1['mongodb'])
db = cluster.zxc
files = cluster.zxc.files_moderation

EXCLUDED_ROLES = {1384954166689923172, 999609135396032534, 1390137707014918299, 1383126511758082198, 1383126511762145330}

master_role = config['master']
curator_role = config['curator']
security_role = config['security']
staff_role = config['staff_role']
administrator = config['administrator']

branch_keys = ['creative', 'support', 'moderator', 'tribunemod', 'mafiamod', 'contentmaker', 'eventsmod', 'closemod', 'clanmod']

def get_effective_top_role(member):
    filtered_roles = [role for role in member.roles if role.id not in EXCLUDED_ROLES]
    if not filtered_roles:
        return member.guild.default_role
    return max(filtered_roles, key=lambda role: role.position)

def get_user_admin_branch(member):
    author_roles = {r.id for r in member.roles}
    admin_roles = {
        'closemod': config.get('closemod_admin'),
        'eventsmod': config.get('eventmod_admin') or config.get('eventsmod_admin'),
        'support': config.get('support_admin'),
        'moderator': config.get('moderator_admin'),
        'tribunemod': config.get('tribunemod_admin'),
        'creative': config.get('creative_admin'),
        'contentmaker': config.get('contentmaker_admin'),
        'mafiamod': config.get('mafiamod_admin'),
        'helper': config.get('helper_admin'),
        'clanmod': config.get('clan_staff_role')
    }
    for branch, admin_role_id in admin_roles.items():
        if admin_role_id and admin_role_id in author_roles:
            return branch
    return None

def get_user_branches(member):
    member_roles = {r.id for r in member.roles}
    user_branches = []

    for branch in branch_keys:
        role_id = config.get(branch)
        if role_id and role_id in member_roles:
            user_branches.append(branch)
    return user_branches

def get_user_permission_level(member):
    member_roles = {r.id for r in member.roles}
    
    if administrator in member_roles:
        return 5
    elif security_role in member_roles:
        return 4
    elif curator_role in member_roles:
        return 3
    elif master_role in member_roles:
        return 2
    elif get_user_admin_branch(member):
        return 1
    else:
        return 0

def draw_text_with_offset(im, text, x, y, font_size, color=(255,255,255)):
    draw = ImageDraw.Draw(im)
    
    font = ImageFont.truetype("fonts/Gordita_bold.ttf", size=font_size)

    bbox = draw.textbbox((x, y), text, font=font)
    text_width = bbox[2] - bbox[0]
    x -= text_width // 2
    draw.text((x, y), text, font=font, fill=color)

class EditRoleView(disnake.ui.View):
    def __init__(self, branch_label, permissions):
        super().__init__()
        
        self.add_item(disnake.ui.Button(style=ButtonStyle.blurple, label='Assistant', custom_id='security_action', row=1, disabled=(permissions < 5), emoji=f'{files.find_one({"_id":"action_up"})["emoji_take"]}'))
        self.add_item(disnake.ui.Button(style=ButtonStyle.blurple, label='Curator', custom_id='curator_action', row=1, disabled=(permissions <= 3), emoji=f'{files.find_one({"_id":"action_up"})["emoji_take"]}'))
        self.add_item(disnake.ui.Button(style=ButtonStyle.blurple, label='Master', custom_id='master_action', row=1, disabled=(permissions <= 2), emoji=f'{files.find_one({"_id":"action_up"})["emoji_take"]}'))
        self.add_item(disnake.ui.Button(style=ButtonStyle.blurple, label=branch_label, custom_id='branch_action', row=1, disabled=(permissions < 1), emoji=f'{files.find_one({"_id":"action_up"})["emoji_take"]}'))
        self.add_item(disnake.ui.Button(style=ButtonStyle.red, label='Снять с ролей', custom_id='remove_roles_action', row=1, emoji=f'{files.find_one({"_id":"action_down"})["emoji_take"]}'))
        self.add_item(disnake.ui.Button(style=ButtonStyle.gray, label='Меню', custom_id='back_action', row=2, emoji=f'{files.find_one({"_id":"action_menu"})["emoji_take"]}'))
        self.add_item(disnake.ui.Button(style=ButtonStyle.red, label='Выход', custom_id='exit_action', row=2, emoji=f'{files.find_one({"_id":"action_basket"})["emoji_take"]}'))

class EditRoleCogs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _get_target_member_and_group(self, inter: disnake.MessageInteraction):
        db_target = cluster.zxc.target.find_one({'_id': str(inter.author.id)})
        if not db_target:
            await inter.send("Ошибка: цель не найдена в базе.", ephemeral=True)
            return None, None
        member = disnake.utils.get(self.bot.get_guild(config['server_id']).members, id=int(db_target['member']))
        if member is None:
            await inter.send("Ошибка: участник не найден на сервере.", ephemeral=True)
            return None, None
        return member, db_target.get('group')

    def _author_is_branch_admin_for(self, author: disnake.Member, group_choice: str):
        admin_branch = get_user_admin_branch(author)
        return admin_branch is not None and admin_branch == group_choice

    def _member_has_branch(self, member: disnake.Member, group_choice: str):
        role_id = config.get(group_choice)
        return role_id in {r.id for r in member.roles}

    def _member_has_other_branches(self, member: disnake.Member, excluded_role_id: int):
        for branch in branch_keys:
            r_id = config.get(branch)
            if r_id and r_id != excluded_role_id and r_id in {r.id for r in member.roles}:
                return True
        return False

    def _can_assign_rank(self, author: disnake.Member, rank_role_id: int):
        author_permission = get_user_permission_level(author)
        
        if author_permission >= 5:
            return True
        
        if rank_role_id == security_role:
            return author_permission > 4  # Только Administrator может выдавать Security
        elif rank_role_id == curator_role:
            return author_permission > 3  # Security и выше могут выдавать Curator
        elif rank_role_id == master_role:
            return author_permission > 2  # Curator и выше могут выдавать Master
        
        return False

    def _can_remove_rank(self, author: disnake.Member, target_member: disnake.Member):
        author_permission = get_user_permission_level(author)
        target_permission = get_user_permission_level(target_member)
        
        if author_permission >= 5:
            return True
        
        return author_permission > target_permission

    async def _assign_rank(self, inter: disnake.MessageInteraction, member: disnake.Member, group_choice: str, rank_role_id: int):
        author_permission = get_user_permission_level(inter.author)
        
        if author_permission < 5 and not self._author_is_branch_admin_for(inter.author, group_choice):
            return await inter.send(f"Вы не являетесь администратором ветки **{group_choice}**.", ephemeral=True)

        if not self._can_assign_rank(inter.author, rank_role_id):
            rank_name = {security_role: "Security", curator_role: "Curator", master_role: "Master"}.get(rank_role_id, "Role")
            return await inter.send(f"У вас недостаточно прав для назначения роли **{rank_name}**.", ephemeral=True)

        if not self._can_remove_rank(inter.author, member):
            return await inter.send(f"У вас недостаточно прав для изменения ролей этого участника.", ephemeral=True)
        print(group_choice)
        group_role_id = config.get(group_choice)
        if not group_role_id:
            return await inter.send("Ошибка конфигурации: роль ветки не найдена.", ephemeral=True)

        if group_role_id not in {r.id for r in member.roles}:
            return await inter.send("Невозможно выдать статус: участник не состоит на выбранной ветке.", ephemeral=True)

        roles_to_remove = {master_role, curator_role, security_role} - {rank_role_id}
        admin_role_id = config.get(f'{group_choice}_admin')
        
        try:
            await member.remove_roles(*[disnake.Object(id=r) for r in roles_to_remove if r])
            await member.add_roles(disnake.Object(id=rank_role_id))
            if admin_role_id:
                await member.add_roles(disnake.Object(id=admin_role_id))
        except Exception as e:
            return await inter.send(f"Ошибка при назначении роли: {e}", ephemeral=True)

        rank_name = {security_role: "Security", curator_role: "Curator", master_role: "Master"}.get(rank_role_id, "Role")
        embed = disnake.Embed(color=3092790, description=f"{inter.author.mention}, вы успешно выдали **{rank_name}** участнику {member.mention} на ветке **{group_choice}**.")
        embed.set_author(name=f"Выдано {rank_name} | {inter.guild.name}", icon_url=inter.guild.icon.url)
        embed.set_thumbnail(url=member.display_avatar.url)
        await inter.send(embed=embed, ephemeral=True)
        
        # Отправка сообщения участнику
        try:
            await member.send(embed=embed)
        except:
            pass
        
        # Логирование действия
        try:
            log_embed = disnake.Embed(color=3092790)
            log_embed.add_field(name="> Администратор:", value=f"{inter.author.mention}")
            log_embed.add_field(name="> Пользователь:", value=f"{member.mention}")
            log_embed.set_author(name=f"Повышен до {rank_name} | {inter.guild.name}", icon_url=inter.guild.icon.url)
            log_embed.set_thumbnail(url=member.display_avatar.url)
            
            log_channel = self.bot.get_channel(config.get('rang_mod_log'))
            if log_channel and admin_role_id:
                await log_channel.send(content=f"<@&{admin_role_id}>", embed=log_embed)
        except Exception as e:
            print(f"Ошибка отправки лога: {e}")

    async def _assign_branch(self, inter: disnake.MessageInteraction, member: disnake.Member, group_choice: str):
        author_permission = get_user_permission_level(inter.author)
        
        if author_permission < 5 and not self._author_is_branch_admin_for(inter.author, group_choice):
            return await inter.send(f"Вы не являетесь администратором ветки **{group_choice}**.", ephemeral=True)

        group_role_id = config.get(group_choice)
        if group_role_id and group_role_id in {r.id for r in member.roles}:
            if not self._can_remove_rank(inter.author, member):
                return await inter.send(f"У вас недостаточно прав для снятия ветки с этого участника.", ephemeral=True)

        if not group_role_id:
            return await inter.send("Ошибка конфигурации: роль ветки не найдена.", ephemeral=True)

        current_ids = {r.id for r in member.roles}
        admin_role_id = config.get(f'{group_choice}_admin')
        
        try:
            if group_role_id in current_ids:
                await member.remove_roles(disnake.Object(id=group_role_id))
                if not self._member_has_other_branches(member, group_role_id):
                    await member.remove_roles(disnake.Object(id=staff_role))
                await inter.send(f"{inter.author.mention}, роль ветки **{group_choice}** удалена у {member.mention}.", ephemeral=True)
                
                # Логирование удаления ветки
                try:
                    log_embed = disnake.Embed(color=0xff0000)  # Красный цвет для удаления
                    log_embed.add_field(name="> Администратор:", value=f"{inter.author.mention}")
                    log_embed.add_field(name="> Пользователь:", value=f"{member.mention}")
                    log_embed.set_author(name=f"Снята ветка {group_choice.capitalize()} | {inter.guild.name}", icon_url=inter.guild.icon.url)
                    log_embed.set_thumbnail(url=member.display_avatar.url)
                    
                    log_channel = self.bot.get_channel(config.get('rang_mod_log'))
                    if log_channel and admin_role_id:
                        await log_channel.send(content=f"<@&{admin_role_id}>", embed=log_embed)
                except Exception as e:
                    print(f"Ошибка отправки лога: {e}")
                    
            else:
                await member.add_roles(disnake.Object(id=group_role_id))
                await member.add_roles(disnake.Object(id=staff_role))
                await inter.send(f"{inter.author.mention}, роль ветки **{group_choice}** выдана {member.mention}.", ephemeral=True)
                
                # Логирование выдачи ветки
                try:
                    log_embed = disnake.Embed(color=0x00ff00)  # Зеленый цвет для выдачи
                    log_embed.add_field(name="> Администратор:", value=f"{inter.author.mention}")
                    log_embed.add_field(name="> Пользователь:", value=f"{member.mention}")
                    log_embed.set_author(name=f"Выдана ветка {group_choice.capitalize()} | {inter.guild.name}", icon_url=inter.guild.icon.url)
                    log_embed.set_thumbnail(url=member.display_avatar.url)
                    
                    log_channel = self.bot.get_channel(config.get('rang_mod_log'))
                    if log_channel and admin_role_id:
                        await log_channel.send(content=f"<@&{admin_role_id}>", embed=log_embed)
                except Exception as e:
                    print(f"Ошибка отправки лога: {e}")
                    
        except Exception as e:
            await inter.send(f"Ошибка при изменении ролей: {e}", ephemeral=True)

    async def _remove_roles_safe(self, inter: disnake.MessageInteraction, member: disnake.Member, group_choice: str):
        author_permission = get_user_permission_level(inter.author)
        target_permission = get_user_permission_level(member)
        
        # Основная проверка: автор может снимать роли только с участников НИЖЕ своего ранга
        if author_permission <= target_permission:
            return await inter.send(f"У вас недостаточно прав для снятия ролей с этого участника. Вы можете снимать роли только с участников ниже вашего ранга.", ephemeral=True)
        
        # Дополнительная проверка для администраторов веток
        if author_permission < 5:  # Если не Administrator
            admin_branch = get_user_admin_branch(inter.author)
            if not admin_branch or admin_branch != group_choice:
                return await inter.send(f"Вы можете управлять только своей веткой. Требуемая ветка: **{admin_branch or 'нет'}**. Текущая: **{group_choice}**.", ephemeral=True)

        group_role_id = config.get(group_choice)
        admin_role_id = config.get(f'{group_choice}_admin')
        member_role_ids = {r.id for r in member.roles}
        roles_to_remove = []
        removed_roles_names = []
        
        # Снятие роли ветки
        if group_role_id and group_role_id in member_role_ids:
            roles_to_remove.append(disnake.Object(id=group_role_id))
            removed_roles_names.append(f"ветка {group_choice.capitalize()}")
        
        # Снятие staff роли если нет других веток
        if not self._member_has_other_branches(member, group_role_id):
            roles_to_remove.append(disnake.Object(id=staff_role))
            removed_roles_names.append("Staff")
        
        # Проверка наличия админ роли ветки для снятия рангов
        has_admin_role = admin_role_id and admin_role_id in member_role_ids
        
        # Снятие рангов на основе прав автора (только если у участника есть админ роль ветки)
        if has_admin_role:
            if author_permission >= 5:  # Administrator может снимать все роли
                if security_role in member_role_ids:
                    roles_to_remove.append(disnake.Object(id=security_role))
                    removed_roles_names.append("Security")
                if curator_role in member_role_ids:
                    roles_to_remove.append(disnake.Object(id=curator_role))
                    removed_roles_names.append("Curator")
                if master_role in member_role_ids:
                    roles_to_remove.append(disnake.Object(id=master_role))
                    removed_roles_names.append("Master")
            elif author_permission == 4:  # Security может снимать Curator и Master
                if curator_role in member_role_ids:
                    roles_to_remove.append(disnake.Object(id=curator_role))
                    removed_roles_names.append("Curator")
                if master_role in member_role_ids:
                    roles_to_remove.append(disnake.Object(id=master_role))
                    removed_roles_names.append("Master")
            elif author_permission == 3:  # Curator может снимать только Master
                if master_role in member_role_ids:
                    roles_to_remove.append(disnake.Object(id=master_role))
                    removed_roles_names.append("Master")
            # Если author_permission == 2 (Master) или меньше, то ранговые роли не снимаются
        
        # Снятие админ роли ветки
        if has_admin_role:
            roles_to_remove.append(disnake.Object(id=admin_role_id))
            removed_roles_names.append(f"администратор {group_choice.capitalize()}")
        
        try:
            if roles_to_remove:
                await member.remove_roles(*roles_to_remove)
            await inter.send(f"{inter.author.mention}, роли участника {member.mention} были обновлены.", ephemeral=True)
            
            # Логирование снятия ролей
            if removed_roles_names:
                try:
                    log_embed = disnake.Embed(color=0xff4500)  # Оранжевый цвет для снятия ролей
                    log_embed.add_field(name="> Администратор:", value=f"{inter.author.mention}")
                    log_embed.add_field(name="> Пользователь:", value=f"{member.mention}")
                    log_embed.add_field(name="> Сняты роли:", value=", ".join(removed_roles_names), inline=False)
                    log_embed.set_author(name=f"Сняты роли | {inter.guild.name}", icon_url=inter.guild.icon.url)
                    log_embed.set_thumbnail(url=member.display_avatar.url)
                    
                    log_channel = self.bot.get_channel(config.get('rang_mod_log'))
                    if log_channel and admin_role_id:
                        await log_channel.send(content=f"<@&{admin_role_id}>", embed=log_embed)
                except Exception as e:
                    print(f"Ошибка отправки лога: {e}")
                    
        except Exception as e:
            await inter.send(f"Ошибка при снятии ролей: {e}", ephemeral=True)

    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        custom_id = inter.component.custom_id

        if custom_id.endswith("edit_action"):
            if inter.message.content != inter.author.mention:
                embed = disnake.Embed(description=f'{inter.author.mention}, **Вы** не можете использовать **чужие кнопки!**', color=3092790)
                embed.set_author(name="Изменить роли", icon_url=inter.guild.icon.url)
                embed.set_thumbnail(url=inter.author.display_avatar.url)
                return await inter.send(ephemeral=True, embed=embed)

            member, group_choice = await self._get_target_member_and_group(inter)
            if member is None or group_choice is None:
                return

            await inter.response.defer()
            now = datetime.now()
            day = f"{now.strftime('%A')}, {now.strftime('%B')} {now.day}"
            time_str = now.strftime('%H:%M')
            im = Image.open("action_zxc/edit_role.png")
            draw_text_with_offset(im, day, 710, 76, font_size=32)
            draw_text_with_offset(im, time_str, 708, 120, font_size=96)
            width, height = 110, 110
            avatar_x, avatar_y = 137, 139
            avatar_response = requests.get(member.display_avatar.url, stream=True)
            Image.open(avatar_response.raw).resize((width, height)).save('avatars/avatar_profile_zxc.png')
            mask_im = Image.new("L", (width, height))
            ImageDraw.Draw(mask_im).ellipse((0, 0, width, height), fill=255)
            im.paste(Image.open('avatars/avatar_profile_zxc.png'), (avatar_x, avatar_y), mask_im)
            пользователь_name = member.name[:13] if len(member.name) > 13 else member.name
            draw_text_with_offset(im, пользователь_name, 412, 194.26, font_size=32)
            im.save(f'out/edit_role_{inter.author.id}.png')
            
            user_permissions = get_user_permission_level(inter.author)
            await inter.message.edit(attachments=None, file=disnake.File(f"out/edit_role_{inter.author.id}.png"), view=EditRoleView(branch_label=group_choice.capitalize(), permissions=user_permissions))
            return

        if custom_id in ("security_action", "curator_action", "master_action", "branch_action", "remove_roles_action"):
            await inter.response.defer()
            
            member, group_choice = await self._get_target_member_and_group(inter)
            if member is None or group_choice is None:
                return

            author_permission = get_user_permission_level(inter.author)
            
            if author_permission < 5 and not self._author_is_branch_admin_for(inter.author, group_choice):
                return await inter.send(f"Вы можете управлять только своей веткой. Требуемая ветка: **{get_user_admin_branch(inter.author) or 'нет'}**. Текущая: **{group_choice}**.", ephemeral=True)

            if custom_id == "security_action":
                return await self._assign_rank(inter, member, group_choice, security_role)
            if custom_id == "curator_action":
                return await self._assign_rank(inter, member, group_choice, curator_role)
            if custom_id == "master_action":
                return await self._assign_rank(inter, member, group_choice, master_role)
            if custom_id == "branch_action":
                return await self._assign_branch(inter, member, group_choice)
            if custom_id == "remove_roles_action":
                return await self._remove_roles_safe(inter, member, group_choice)

def setup(bot: commands.Bot):
    bot.add_cog(EditRoleCogs(bot))