import disnake
import asyncio
import json
import os
import pymongo
from disnake.ext import commands

with open('configs/zxc.json', 'r') as f:
    config = json.load(f)

with open('configs/zxc_tokens.json', 'r') as f:
    config1 = json.load(f)

bot = commands.Bot(command_prefix = commands.when_mentioned_or('m!'), intents = disnake.Intents.all(), test_guilds = [config['server_id']], help_command = None, sync_commands = True)

@bot.event
async def on_ready():
    print("Bot Ready")
    await bot.change_presence(status=disnake.Status.online, activity=disnake.Activity(type=disnake.ActivityType.watching, name=f"за {bot.get_guild(config['server_id']).name}"))

    # guild = bot.get_guild(999609134922092626)
    # member = disnake.utils.get(guild.members, id = 1432506652459929715)
    # role = guild.get_role(1392924533261865050)
    # await member.remove_roles(role)

    # role = guild.get_role(1383126511762145330)
    # await member.add_roles(role)

if __name__ == '__main__':
    for filename in os.listdir("./zxcmodcogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"zxcmodcogs.{filename[:-3]}")
            
bot.run(config1['moderation'])