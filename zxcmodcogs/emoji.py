import pymongo
import disnake
import json
import os
import asyncio
import random
import math
import requests
import base64
import re
from pathlib import Path
from disnake.ext import commands
from disnake.enums import ButtonStyle, TextInputStyle
from PIL import Image

with open('configs/zxc_tokens.json', 'r') as f:
    config1 = json.load(f)

token = config1['moderation']
cluster = pymongo.MongoClient(config1['mongodb'])
database_name = "zxc"
collection_name = "files_moderation"

BOT_TOKEN = config1['moderation']
APPLICATION_ID = "1408012503669145642"
EMOJI_FOLDER = "images_upload"
DELAY_SECONDS = 0

def change_image_color(input_image_path, output_image_path, new_color_hex):
    try:
        original_image = Image.open(input_image_path).convert("RGBA")
        width, height = original_image.size

        new_color_rgb = tuple(int(new_color_hex[i:i+2], 16) for i in (1, 3, 5))

        new_image_data = []
        for pixel in original_image.getdata():
            if pixel[:3] == (0, 0, 0):
                new_image_data.append((0, 0, 0, 0))
            else:
                new_image_data.append(new_color_rgb + (pixel[3],))

        new_image = Image.new("RGBA", (width, height))
        new_image.putdata(new_image_data)

        new_image.save(output_image_path)
    except Exception as e:
        print(e)

def batch_change_color(input_folder, output_folder, new_color_hex):
    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for filename in os.listdir(input_folder):
            if filename.endswith((".png", ".jpg", ".jpeg")):
                input_path = os.path.join(input_folder, filename)
                output_path = os.path.join(output_folder, filename)
                change_image_color(input_path, output_path, new_color_hex)
    except Exception as e:
        print(e)

def clean_name(filename):
    name = Path(filename).stem
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    name = re.sub(r'_+', '_', name)
    name = name.strip('_')
    if len(name) > 32:
        name = name[:32]
    if not name:
        name = f"emoji_{hash(filename) % 10000}"
    return name.lower()

def check_emoji_exists(emoji_name):
    collection = cluster[database_name][collection_name]
    existing = collection.find_one({'_id': str(emoji_name)})
    return existing is not None

def save_emoji_to_db(emoji_name, emoji_id):
    try:
        collection = cluster[database_name][collection_name]
        collection.update_one(
            {'_id': str(emoji_name)},
            {'$set': {
                "emoji_take": f"<:{emoji_name}:{emoji_id}>",
                "emoji_id": str(emoji_id)
            }},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"Database error: {e}")
        return False

def upload_emoji_to_discord(file_path, emoji_name):
    url = f"https://proxy.discord-bot.net/api/v10/applications/{APPLICATION_ID}/emojis"
    
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    with open(file_path, 'rb') as f:
        image_data = f.read()
    
    image_b64 = base64.b64encode(image_data).decode('utf-8')
    
    file_ext = file_path.suffix.lower()
    if file_ext == '.png':
        mime_type = 'image/png'
    elif file_ext in ['.jpg', '.jpeg']:
        mime_type = 'image/jpeg'
    elif file_ext == '.gif':
        mime_type = 'image/gif'
    elif file_ext == '.webp':
        mime_type = 'image/webp'
    else:
        return False, "Unsupported format", None
    
    data = {
        "name": emoji_name,
        "image": f"data:{mime_type};base64,{image_b64}"
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 201:
        emoji_data = response.json()
        emoji_id = emoji_data.get('id')
        return True, "Success", emoji_id
    elif response.status_code == 429:
        retry_after = response.json().get('retry_after', 60)
        return False, f"Rate limited, wait {retry_after}s", None
    else:
        return False, f"Error {response.status_code}: {response.text}", None

class emojicog(commands.Cog):
    def __init__(self, bot: commands.Bot(intents = disnake.Intents.all(), command_prefix="!")):
        self.bot = bot

    @commands.command()
    async def change_color(self, inter, new_color: str):
        if inter.author.id == 685920167871512818:
            await inter.message.delete()

            embed = disnake.Embed(color = 3092790)
            embed.set_author(name = "Перекрашивание эмоджи", icon_url = inter.guild.icon.url)
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            embed.description = f'### Перекрашиваю эмоджи в цвет {new_color}'
            await inter.send(embed = embed)

            input_folder = f"images_upload"
            output_folder = f"images_upload"
            batch_change_color(input_folder, output_folder, new_color)
            embed.description = f"{inter.author.mention}, **Все** эмоджи были успешно перекрашены в цвет {new_color}."
            await inter.send(embed = embed)

    @commands.command()
    async def upload_emojis(self, inter):
        if inter.author.id == 685920167871512818:
            await inter.message.delete()

            embed = disnake.Embed(color=3092790)
            embed.set_author(name="Загрузка эмоджи", icon_url=inter.guild.icon.url)
            embed.set_thumbnail(url=inter.author.display_avatar.url)
            embed.description = "### Начинаю загрузку эмоджи в приложение..."
            status_msg = await inter.send(embed=embed)

            emoji_dir = Path(EMOJI_FOLDER)
            
            if not emoji_dir.exists():
                embed.description = f"❌ Папка {EMOJI_FOLDER} не найдена!"
                await status_msg.edit(embed=embed)
                return

            supported_formats = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
            emoji_files = [f for f in emoji_dir.iterdir() if f.is_file() and f.suffix.lower() in supported_formats]
            
            if not emoji_files:
                embed.description = "❌ Не найдено файлов эмоджи для загрузки!"
                await status_msg.edit(embed=embed)
                return

            embed.description = f"🔍 Найдено {len(emoji_files)} файлов эмоджи\n### Загружаю..."
            await status_msg.edit(embed=embed)

            used_names = set()
            success_count = 0
            skipped_count = 0
            failed_count = 0
            progress_text = ""

            for i, file_path in enumerate(emoji_files):
                original_emoji_name = clean_name(file_path.name)
                emoji_name = original_emoji_name
                
                if check_emoji_exists(emoji_name):
                    progress_text += f"⏭️ {file_path.name} - уже в БД\n"
                    skipped_count += 1
                    
                    if len(progress_text) > 1800:
                        progress_text = progress_text[-1500:] + "..."
                    
                    embed.description = f"📊 Прогресс: {i+1}/{len(emoji_files)}\n```{progress_text}```"
                    await status_msg.edit(embed=embed)
                    continue

                counter = 1
                while emoji_name in used_names or check_emoji_exists(emoji_name):
                    emoji_name = f"{original_emoji_name}_{counter}"
                    counter += 1

                used_names.add(emoji_name)

                success, message, emoji_id = upload_emoji_to_discord(file_path, emoji_name)
                
                if success and emoji_id:
                    if save_emoji_to_db(emoji_name, emoji_id):
                        progress_text += f"✅ {emoji_name}\n"
                        success_count += 1
                    else:
                        progress_text += f"⚠️ {emoji_name} - загружен, БД ошибка\n"
                        failed_count += 1
                else:
                    progress_text += f"❌ {emoji_name}: {message}\n"
                    failed_count += 1
                    
                    if "Rate limited" in message:
                        try:
                            wait_time = int(message.split("wait ")[1].split("s")[0])
                            progress_text += f"⏳ Ожидание {wait_time}с...\n"
                            
                            if len(progress_text) > 1800:
                                progress_text = progress_text[-1500:] + "..."
                            
                            embed.description = f"📊 Прогресс: {i+1}/{len(emoji_files)}\n```{progress_text}```"
                            await status_msg.edit(embed=embed)
                            
                            await asyncio.sleep(wait_time)
                            success, message, emoji_id = upload_emoji_to_discord(file_path, emoji_name)
                            
                            if success and emoji_id:
                                if save_emoji_to_db(emoji_name, emoji_id):
                                    progress_text += f"✅ {emoji_name} (повтор)\n"
                                    success_count += 1
                                    failed_count -= 1
                                else:
                                    progress_text += f"⚠️ {emoji_name} - загружен, БД ошибка (повтор)\n"
                        except:
                            pass

                if len(progress_text) > 1800:
                    progress_text = progress_text[-1500:] + "..."

                embed.description = f"📊 Прогресс: {i+1}/{len(emoji_files)}\n```{progress_text}```"
                await status_msg.edit(embed=embed)
                
                await asyncio.sleep(DELAY_SECONDS)

            final_embed = disnake.Embed(color=0x00ff00 if success_count > 0 else 0xff0000)
            final_embed.set_author(name="Загрузка завершена", icon_url=inter.guild.icon.url)
            final_embed.set_thumbnail(url=inter.author.display_avatar.url)
            final_embed.description = f"""
### 📈 Результат загрузки:
✅ **Загружено:** {success_count}
⏭️ **Пропущено:** {skipped_count} 
❌ **Ошибок:** {failed_count}
📁 **Всего файлов:** {len(emoji_files)}

{inter.author.mention}, загрузка эмоджи завершена!
            """
            await status_msg.edit(embed=final_embed)

    @commands.command()
    async def sync_emojis(self, inter):
        if inter.author.id == 685920167871512818:
            await inter.message.delete()

            embed = disnake.Embed(color=3092790)
            embed.set_author(name="Синхронизация эмоджи", icon_url=inter.guild.icon.url)
            embed.set_thumbnail(url=inter.author.display_avatar.url)
            embed.description = "### Получаю эмоджи из приложения..."
            status_msg = await inter.send(embed=embed)

            url = f"https://proxy.discord-bot.net/api/v10/applications/{APPLICATION_ID}/emojis"
            headers = {
                "Authorization": f"Bot {BOT_TOKEN}",
                "Content-Type": "application/json"
            }

            try:
                response = requests.get(url, headers=headers)
                
                if response.status_code != 200:
                    embed.description = f"❌ Ошибка получения эмоджи: {response.status_code}"
                    await status_msg.edit(embed=embed)
                    return

                emojis_data = response.json().get('items', [])
                
                if not emojis_data:
                    embed.description = "❌ Эмоджи в приложении не найдены!"
                    await status_msg.edit(embed=embed)
                    return

                embed.description = f"🔍 Найдено {len(emojis_data)} эмоджи в приложении\n### Синхронизирую с базой данных..."
                await status_msg.edit(embed=embed)

                collection = cluster[database_name][collection_name]
                added_count = 0
                updated_count = 0
                skipped_count = 0
                progress_text = ""

                for i, emoji in enumerate(emojis_data):
                    emoji_name = emoji.get('name')
                    emoji_id = emoji.get('id')
                    
                    if not emoji_name or not emoji_id:
                        progress_text += f"⚠️ Пропущен эмоджи без имени/id\n"
                        skipped_count += 1
                        continue

                    existing = collection.find_one({'_id': str(emoji_name)})
                    
                    emoji_data = {
                        "emoji_take": f"<:{emoji_name}:{emoji_id}>",
                        "emoji_id": str(emoji_id)
                    }

                    if existing:
                        if existing.get('emoji_id') != str(emoji_id):
                            collection.update_one(
                                {'_id': str(emoji_name)},
                                {'$set': emoji_data}
                            )
                            progress_text += f"🔄 {emoji_name} - обновлен\n"
                            updated_count += 1
                        else:
                            progress_text += f"⏭️ {emoji_name} - без изменений\n"
                            skipped_count += 1
                    else:
                        collection.update_one(
                            {'_id': str(emoji_name)},
                            {'$set': emoji_data},
                            upsert=True
                        )
                        progress_text += f"✅ {emoji_name} - добавлен\n"
                        added_count += 1

                    if len(progress_text) > 1800:
                        progress_text = progress_text[-1500:] + "..."

                    embed.description = f"📊 Прогресс: {i+1}/{len(emojis_data)}\n```{progress_text}```"
                    await status_msg.edit(embed=embed)

                final_embed = disnake.Embed(color=0x00ff00)
                final_embed.set_author(name="Синхронизация завершена", icon_url=inter.guild.icon.url)
                final_embed.set_thumbnail(url=inter.author.display_avatar.url)
                final_embed.description = f"""
### 📈 Результат синхронизации:
✅ **Добавлено новых:** {added_count}
🔄 **Обновлено:** {updated_count}
⏭️ **Пропущено:** {skipped_count}
📁 **Всего эмоджи:** {len(emojis_data)}

{inter.author.mention}, синхронизация эмоджи завершена!
                """
                await status_msg.edit(embed=final_embed)

            except Exception as e:
                embed.description = f"❌ Ошибка при синхронизации: {str(e)}"
                await status_msg.edit(embed=embed)

def setup(bot): 
    bot.add_cog(emojicog(bot))