import disnake
import asyncio
import json
import os
import pymongo
from disnake.ext import commands

# загружаем конфиги
with open('configs/zxc.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

with open('configs/zxc_tokens.json', 'r', encoding='utf-8') as f:
    config1 = json.load(f)

intents = disnake.Intents.all()
intents.message_content = True

bot = commands.Bot(
    command_prefix='!',
    intents=disnake.Intents.all(),
    test_guilds = [config['server_id']],
    help_command=None,
    command_sync_flags=commands.CommandSyncFlags.default(),
)


@bot.event
async def on_ready():
    print("Bot Ready")
    guild = bot.get_guild(config['server_id'])
    if guild is not None:
        await bot.change_presence(
            status=disnake.Status.online,
            activity=disnake.Activity(
                type=disnake.ActivityType.watching,
                name=f"за {guild.name}",
            ),
        )
    else:
        # на случай, если бот ещё не видит гильдию
        await bot.change_presence(
            status=disnake.Status.online,
            activity=disnake.Game("загрузка..."),
        )

    # Явная синхронизация слэш-команд, чтобы они появились в клиенте
    if not getattr(bot, "_commands_synced", False):
        sync = getattr(bot, "sync_application_commands", None)
        if callable(sync):
            await sync()
            bot._commands_synced = True


def load_extensions():
    """
    1) сначала грузим emoji-ког (он нужен для !upload_emojis)
    2) потом пытаемся грузить остальные коги
       - если какой-то падает -> просто пишем ошибку и пропускаем его
    """

    # 1. Пытаемся явно загрузить emoji-ког
    # имя файла в папке zxcmodcogs должно быть emoji.py
    try:
        bot.load_extension("zxcmodcogs.emoji")
        print("[OK] Загружен ког: emoji")
    except Exception as e:
        print("[ERROR] Не удалось загрузить ког emoji:")
        print(e)

    # 2. Грузим остальные коги с try/except
    for filename in os.listdir("./zxcmodcogs"):
        if not filename.endswith(".py"):
            continue

        name = filename[:-3]

        # emoji уже пытались загрузить выше
        if name == "emoji":
            continue

        try:
            bot.load_extension(f"zxcmodcogs.{name}")
            print(f"[OK] Загружен ког: {name}")
        except Exception as e:
            # вот тут как раз будут “проблемные” коги
            print(f"[SKIP] Ког {name} отключён из-за ошибки при загрузке:")
            print(e)


if __name__ == '__main__':
    load_extensions()
    bot.run(config1['moderation'])