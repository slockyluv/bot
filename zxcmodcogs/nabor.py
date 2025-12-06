import pymongo
import json
import disnake
import datetime
from disnake.ext import commands
from disnake.enums import ButtonStyle, TextInputStyle

with open('configs/zxc.json', 'r') as f:
    config = json.load(f)

with open('configs/zxc_tokens.json', 'r') as f:
    config1 = json.load(f)

cluster = pymongo.MongoClient(config1['mongodb'])

class InterView(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Назначить собеседование', custom_id="sobes",emoji = '<:add:1005521181585190922>'))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Отказ', custom_id = "decline_nabor"))

class UpdateEmbedView(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(
            style=ButtonStyle.gray,
            label="Обновить эмбед наборов",
            custom_id="update_embed_nabor"
        ))

# Конфигурация модальных окон по умолчанию
default_modal_configs = {
    "Support_nabor": {
        "title": "Заявка на Support",
        "modal_id": "nabor_support",
        "components": [
            {
                "label": "Имя, Возраст(16+), Часовой пояс",
                "placeholder": "Например: Вася, 16 лет, МСК",
                "custom_id": "Имя, возраст",
                "max_length": 20,
                "style": TextInputStyle.short
            },
            {
                "label": "Сколько вы можете уделять времени",
                "placeholder": "Например: с 14:00 до 18:00",
                "custom_id": "Сколько вы можете в день уделять времени серверу",
                "max_length": 20,
                "style": TextInputStyle.short
            },
            {
                "label": "Расскажите немного о себе",
                "placeholder": "Например: Я крутой программист!",
                "custom_id": "Расскажите немного о себе",
                "max_length": 100,
                "style": TextInputStyle.paragraph
            },
            {
                "label": "Работали ли ранее в данной сфере?",
                "placeholder": "Например: Да, на каком-то там сервере работал раньше",
                "custom_id": "Работали ли ранее в данной сфере?",
                "max_length": 100,
                "style": TextInputStyle.short
            },
            {
                "label": "Расскажи о своих хороших чертах характера.",
                "placeholder": "Например: Я отзывчивый, добрый, лидер, умею общаться с людьми",
                "custom_id": "Расскажите о своих хороших чертах характера.",
                "max_length": 100,
                "style": TextInputStyle.paragraph
            }
        ]
    },
    "Helper_nabor": {
        "title": "Заявка на Helper",
        "modal_id": "nabor_helper",
        "components": [
            {
                "label": "Имя, Возраст(16+), Часовой пояс",
                "placeholder": "Например: Вася, 16 лет, МСК",
                "custom_id": "Имя, возраст",
                "max_length": 20,
                "style": TextInputStyle.short
            },
            {
                "label": "Сколько вы можете уделять времени",
                "placeholder": "Например: с 14:00 до 18:00",
                "custom_id": "Сколько вы можете в день уделять времени серверу",
                "max_length": 20,
                "style": TextInputStyle.short
            },
            {
                "label": "Расскажите немного о себе",
                "placeholder": "Например: Я крутой программист!",
                "custom_id": "Расскажите немного о себе",
                "max_length": 100,
                "style": TextInputStyle.paragraph
            },
            {
                "label": "Работали ли ранее в данной сфере?",
                "placeholder": "Например: Да, на каком-то там сервере работал раньше",
                "custom_id": "Работали ли ранее в данной сфере?",
                "max_length": 100,
                "style": TextInputStyle.short
            },
            {
                "label": "Расскажи о своих хороших чертах характера.",
                "placeholder": "Например: Я отзывчивый, добрый, лидер, умею общаться с людьми",
                "custom_id": "Расскажите о своих хороших чертах характера.",
                "max_length": 100,
                "style": TextInputStyle.paragraph
            }
        ]
    },
    "Control_nabor": {
        "title": "Заявка на Control",
        "modal_id": "nabor_control",
        "components": [
            {
                "label": "Имя, Возраст(16+), Часовой пояс",
                "placeholder": "Например: Вася, 16 лет, МСК",
                "custom_id": "Имя, возраст",
                "max_length": 20,
                "style": TextInputStyle.short
            },
            {
                "label": "Сколько вы можете уделять времени",
                "placeholder": "Например: с 14:00 до 18:00",
                "custom_id": "Сколько вы можете в день уделять времени серверу",
                "max_length": 20,
                "style": TextInputStyle.short
            },
            {
                "label": "Расскажите немного о себе",
                "placeholder": "Например: Я крутой программист!",
                "custom_id": "Расскажите немного о себе",
                "max_length": 100,
                "style": TextInputStyle.paragraph
            },
            {
                "label": "Работали ли ранее в данной сфере?",
                "placeholder": "Например: Да, на каком-то там сервере работал раньше",
                "custom_id": "Работали ли ранее в данной сфере?",
                "max_length": 100,
                "style": TextInputStyle.short
            },
            {
                "label": "Расскажи о своих хороших чертах характера.",
                "placeholder": "Например: Я отзывчивый, добрый, лидер, умею общаться с людьми",
                "custom_id": "Расскажите о своих хороших чертах характера.",
                "max_length": 100,
                "style": TextInputStyle.paragraph
            }
        ]
    },
    "Moderator_nabor": {
        "title": "Заявка на Moderator",
        "modal_id": "nabor_moderator",
        "components": [
            {
                "label": "Имя, Возраст(16+)",
                "placeholder": "Например: Вася, 16 лет",
                "custom_id": "Имя, возраст",
                "max_length": 20,
                "style": TextInputStyle.short
            },
            {
                "label": "Сколько вы можете уделять времени",
                "placeholder": "Например: с 14:00 до 18:00",
                "custom_id": "Сколько вы можете в день уделять времени серверу",
                "max_length": 20,
                "style": TextInputStyle.short
            },
            {
                "label": "Почему именно ты должен стать модератором?",
                "placeholder": "",
                "custom_id": "Почему именно ты должен стать модератором?",
                "max_length": 100,
                "style": TextInputStyle.paragraph
            },
            {
                "label": "Работали ли ранее в данной сфере?",
                "placeholder": "",
                "custom_id": "Работали ли ранее в данной сфере?",
                "max_length": 100,
                "style": TextInputStyle.short
            },
            {
                "label": "Расскажи о своих хороших чертах характера.",
                "placeholder": "",
                "custom_id": "Расскажите о своих хороших чертах характера.",
                "max_length": 100,
                "style": TextInputStyle.paragraph
            }
        ]
    },
    "EventMod_nabor": {
        "title": "Заявка на EventMod",
        "modal_id": "nabor_eventer",
        "components": [
            {
                "label": "Имя, Возраст, Часовой пояс",
                "placeholder": "Например: Вася, 16 лет, МСК",
                "custom_id": "Имя, возраст",
                "max_length": 20,
                "style": TextInputStyle.short
            },
            {
                "label": "Почему ты решил(а) стать ивентёром?",
                "placeholder": "Например: Весело проводить ивенты.",
                "custom_id": "Почему ты решил(а) стать ивентёром?",
                "max_length": 100,
                "style": TextInputStyle.paragraph
            },
            {
                "label": "Расскажите немного о себе",
                "placeholder": "Например: Я крутой программист!",
                "custom_id": "Расскажите немного о себе",
                "max_length": 100,
                "style": TextInputStyle.paragraph
            },
            {
                "label": "Какие ивенты ты умеешь проводить?",
                "placeholder": "Например: Мафия, крокодил",
                "custom_id": "Какие ивенты ты умеешь проводить?",
                "max_length": 100,
                "style": TextInputStyle.paragraph
            },
            {
                "label": "Как часто ты будешь проводить ивенты?",
                "placeholder": "Например: 2 раза в день",
                "custom_id": "Как часто ты будешь проводить ивенты?",
                "max_length": 100,
                "style": TextInputStyle.short
            }
        ]
    },
    "CloseMod_nabor": {
        "title": "Заявка на CloseMod",
        "modal_id": "nabor_closemod",
        "components": [
            {
                "label": "Имя, Возраст, Часовой пояс",
                "placeholder": "Например: Вася, 16 лет, МСК",
                "custom_id": "Имя, возраст",
                "max_length": 20,
                "style": TextInputStyle.short
            },
            {
                "label": "Почему ты решил(а) стать CloseMod?",
                "placeholder": "Например: Весело проводить мероприятия.",
                "custom_id": "Почему ты решил(а) стать CloseMod?",
                "max_length": 100,
                "style": TextInputStyle.paragraph
            },
            {
                "label": "Работали ли ранее в данной сфере?",
                "placeholder": "Например: Да, на каком-то там сервере работал раньше",
                "custom_id": "Работали ли ранее в данной сфере?",
                "max_length": 100,
                "style": TextInputStyle.short
            },
            {
                "label": "Почему именно ты?",
                "placeholder": "Например: Я имею связи!",
                "custom_id": "Почему именно ты?",
                "max_length": 100,
                "style": TextInputStyle.short
            },
            {
                "label": "Расскажите немного о себе",
                "placeholder": "Например: Я крутой программист!",
                "custom_id": "Расскажите о себе",
                "max_length": 100,
                "style": TextInputStyle.short
            }
        ]
    },
    "Creative_nabor": {
        "title": "Заявка на Creative",
        "modal_id": "nabor_creative",
        "components": [
            {
                "label": "Имя, Возраст",
                "placeholder": "Например: Вася, 16 лет",
                "custom_id": "Имя, возраст",
                "max_length": 20,
                "style": TextInputStyle.short
            },
            {
                "label": "Сколько вы можете уделять времени",
                "placeholder": "Например: с 14:00 до 18:00",
                "custom_id": "Сколько вы можете в день уделять времени серверу",
                "max_length": 20,
                "style": TextInputStyle.short
            },
            {
                "label": "Почему именно ты должен стать креативом?",
                "placeholder": "",
                "custom_id": "Почему именно ты должен стать креативом?",
                "max_length": 100,
                "style": TextInputStyle.paragraph
            },
            {
                "label": "Работали ли ранее в данной сфере?",
                "placeholder": "",
                "custom_id": "Работали ли ранее в данной сфере?",
                "max_length": 100,
                "style": TextInputStyle.short
            },
            {
                "label": "Расскажи о своих хороших чертах характера.",
                "placeholder": "",
                "custom_id": "Расскажите о своих хороших чертах характера.",
                "max_length": 100,
                "style": TextInputStyle.paragraph
            }
        ]
    },
    "TribuneMod_nabor": {
        "title": "Заявка на TribuneMod",
        "modal_id": "nabor_tribunemod",
        "components": [
            {
                "label": "Имя, Возраст, Часовой пояс",
                "placeholder": "Например: Вася, 16 лет, МСК",
                "custom_id": "Имя, возраст",
                "max_length": 20,
                "style": TextInputStyle.short
            },
            {
                "label": "Какие трибуны умеешь проводить?",
                "placeholder": "Например: Вебкам",
                "custom_id": "Какие трибуны умеешь проводить?",
                "max_length": 100,
                "style": TextInputStyle.paragraph
            },
            {
                "label": "Работали ли ранее в данной сфере?",
                "placeholder": "Например: Да, на каком-то там сервере работал раньше",
                "custom_id": "Работали ли ранее в данной сфере?",
                "max_length": 100,
                "style": TextInputStyle.short
            },
            {
                "label": "Сколько времени в недели у тебя есть?",
                "placeholder": "Например: 24 часа в неделю",
                "custom_id": "Сколько времени в недели у тебя есть?",
                "max_length": 100,
                "style": TextInputStyle.short
            },
            {
                "label": "Расскажите немного о себе",
                "placeholder": "Например: Я крутой трибунер с большим опытом!",
                "custom_id": "Расскажите немного о себе",
                "max_length": 100,
                "style": TextInputStyle.short
            }
        ]
    },
    "Clan_Master_nabor": {
        "title": "Заявка на ClanMaster",
        "modal_id": "nabor_clanmaster",
        "components": [
            {
                "label": "Имя, Возраст, Часовой пояс",
                "placeholder": "Например: Вася, 16 лет, МСК",
                "custom_id": "Имя, возраст",
                "max_length": 20,
                "style": TextInputStyle.short
            },
            {
                "label": "Почему ты решил(а) стать клан мастером?",
                "placeholder": "Например: Хочу помочь в развитии сервера.",
                "custom_id": "Почему ты решил(а) стать ClanMaster?",
                "max_length": 100,
                "style": TextInputStyle.paragraph
            },
            {
                "label": "Работали ли ранее в данной сфере?",
                "placeholder": "Например: Да, на каком-то там сервере работал раньше",
                "custom_id": "Работали ли ранее в данной сфере?",
                "max_length": 100,
                "style": TextInputStyle.short
            },
            {
                "label": "Почему именно ты?",
                "placeholder": "Например: Я имею связи",
                "custom_id": "Почему именно ты?",
                "max_length": 100,
                "style": TextInputStyle.short
            },
            {
                "label": "Расскажите немного о себе",
                "placeholder": "Например: Я крутой клан мастер с большим опытом!",
                "custom_id": "Расскажите о себе",
                "max_length": 100,
                "style": TextInputStyle.short
            }
        ]
    },
    "Content_Manager_nabor": {
        "title": "Заявка на Content Maker",
        "modal_id": "nabor_content",
        "components": [
            {
                "label": "Имя, Возраст(14+), Часовой пояс",
                "placeholder": "Например: Вася, 14 лет, МСК",
                "custom_id": "Имя, возраст",
                "max_length": 20,
                "style": TextInputStyle.short
            },
            {
                "label": "Расскажите о себе",
                "placeholder": "Например: Я крутой программист!",
                "custom_id": "О себе",
                "max_length": 200,
                "style": TextInputStyle.paragraph
            },
            {
                "label": "Сколько вы можете уделять времени",
                "placeholder": "Например: 5-6 часов",
                "custom_id": "Сколько вы можете в день уделять времени серверу",
                "max_length": 20,
                "style": TextInputStyle.short
            },
            {
                "label": "Расскажите о своих навыках.",
                "placeholder": "Например: монтаж",
                "custom_id": "Расскажите о своих навыках.",
                "max_length": 100,
                "style": TextInputStyle.short
            }
        ]
    },
    "MediaScope_nabor": {
        "title": "Заявка на MediaScope",
        "modal_id": "nabor_mediascope",
        "components": [
            {
                "label": "Имя, Возраст(16+), Часовой пояс",
                "placeholder": "Например: Вася, 16 лет, МСК",
                "custom_id": "Имя, возраст",
                "max_length": 20,
                "style": TextInputStyle.short
            },
            {
                "label": "Почему ты решил(а) стать MediaScope?",
                "placeholder": "Например: Хочу помочь в развитии сервера.",
                "custom_id": "Почему ты решил(а) стать MediaScope?",
                "max_length": 100,
                "style": TextInputStyle.paragraph
            },
            {
                "label": "Работали ли ранее в данной сфере?",
                "placeholder": "Например: Да, на каком-то там сервере работал раньше",
                "custom_id": "Работали ли ранее в данной сфере?",
                "max_length": 100,
                "style": TextInputStyle.short
            },
            {
                "label": "Почему именно ты?",
                "placeholder": "Например: Я имею связи",
                "custom_id": "Почему именно ты?",
                "max_length": 100,
                "style": TextInputStyle.short
            },
            {
                "label": "Расскажите немного о себе",
                "placeholder": "Например: Я крутой MediaScope с большим опытом!",
                "custom_id": "Расскажите о себе",
                "max_length": 100,
                "style": TextInputStyle.short
            }
        ]
    }
}

modal_configs_doc = cluster.zxc.settings.find_one({'_id': 'ModalConfigs'})
if not modal_configs_doc:
    cluster.zxc.settings.insert_one({'_id': 'ModalConfigs', **default_modal_configs})
    modal_configs = default_modal_configs
else:
    modal_configs = {key: value for key, value in modal_configs_doc.items() if key != '_id'}

def build_modal_components(components_config):
    """
    Функция для создания компонентов модального окна на основе переданной конфигурации.
    """
    components = []
    for comp in components_config:
        components.append(
            disnake.ui.TextInput(
                label=comp["label"],
                placeholder=comp["placeholder"],
                custom_id=comp["custom_id"],
                max_length=comp["max_length"],
                style=comp["style"]
            )
        )
    return components

class NaborSettingsDropdown(disnake.ui.Select):
    def __init__(self):
        nabor_data = cluster.zxc.settings.find_one({'_id': 'Nabor'}) or {}

        options = []

        positions = {
            "Support": "Пропускать новичков на сервер",
            "Moderator": "Следят за порядком в войсе",
            "Control": "Модерирует чаты",
            "EventMod": "Проводят мероприятия на сервере",
            "CloseMod": "Организуют веселые и интересные ивенты 5х5",
            "Creative": "Отвечают за зону отдыха",
            "TribuneMod": "Проводят глобальные мероприятия на сервере",
            "Helper": "Занимаются бампами и следят за чатом",
            "Content Manager": "Отвечают за контент на сервере",
            "Clan Master": "Разбираются в кланах",
            "MediaScope": "Разбираются в медиасфере",
            "MafiaMod": "Проводят мафию",
        }

        for position, description in positions.items():
            label = position
            value = f"{position.replace(' ', '_')}_choice"

            if nabor_data.get(position) == "Добавлена":
                option_description = "Вакансия Уже Добавлена в меню"
            else:
                option_description = "Вакансия Отсутствует в меню"

            options.append(disnake.SelectOption(label=label, value=value, description=option_description))

        super().__init__(
            placeholder="Выберите вакансию которую вы хотите добавить/убрать.",
            options=options,
        )

class NaborSettings(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(NaborSettingsDropdown())
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Эмбед сообщения', custom_id = "embed_settings"))

class CancelDisabled(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Назначить собеседование', emoji = '<:add:1005521181585190922>', disabled = True))
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = 'Отказ', disabled = True))

class Dropdown(disnake.ui.Select):
    def __init__(self):
        nabor_data = cluster.zxc.settings.find_one({'_id': 'Nabor'}) or {}

        options = []

        positions = {
            "Support": "Пропускать новичков на сервер",
            "Moderator": "Следят за порядком в войсе",
            "Control": "Модерирует чаты",
            "EventMod": "Проводят мероприятия на сервере",
            "CloseMod": "Организуют веселые и интересные ивенты 5х5",
            "Creative": "Отвечают за зону отдыха",
            "TribuneMod": "Проводят глобальные мероприятия на сервере",
            "Helper": "Занимаются бампами и следят за чатом",
            "Content Manager": "Отвечают за контент на сервере",
            "Clan Master": "Разбираются в кланах",
            "MediaScope": "Разбираются в медиасфере",
            "MafiaMod": "Проводят мафию",
        }

        for position, description in positions.items():
            label = position
            value = f"{position.replace(' ', '_')}_nabor"
            if nabor_data.get(position) == "Добавлена":
                options.append(disnake.SelectOption(label=label, value=value, description=description))

        super().__init__(
            placeholder="Выберите интересующую вас вакансию.",
            options=options,
        )

class DropdownView(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Dropdown())
        self.add_item(disnake.ui.Button(style = ButtonStyle.gray, label = '⠀', custom_id="nabor_settings",emoji = '<a:9093settings:1239315974499336222>'))
        
def hex_to_rgb(value):
    value = value.lstrip('#')
    RGB = list(tuple(int(value[i:i + len(value) // 3], 16) for i in range(0, len(value), len(value) // 3)))
    return (RGB[0]<<16) + (RGB[1]<<8) + RGB[2]

class nabor_cog(commands.Cog):
    def __init__(self, bot: commands.Bot(intents=disnake.Intents.all(), command_prefix = '%')): # type: ignore
        self.bot = bot

    @commands.Cog.listener()
    async def on_button_click(self, inter):
        custom_id = inter.component.custom_id

        if custom_id == "embed_settings":
            # Получаем документ настроек набора из базы
            settings_doc = cluster.zxc.settings.find_one({'_id': 'Nabor'})
            if settings_doc and 'nabor_message_id' in settings_doc and 'nabor_channel_id' in settings_doc:
                channel = inter.guild.get_channel(settings_doc['nabor_channel_id'])
                try:
                    nabor_msg = await channel.fetch_message(settings_doc['nabor_message_id'])
                    # Если эмбед отсутствует в сообщении, берем сохранённый в базе
                    if nabor_msg.embeds:
                        current_embed = nabor_msg.embeds[0]
                    else:
                        current_embed = disnake.Embed.from_dict(settings_doc.get('embed_content', {}))
                except Exception as e:
                    current_embed = disnake.Embed(title="Ошибка", description="Не удалось получить сообщение эмбеда")
            else:
                # Если настроек нет – используем дефолтный эмбед
                current_embed = disnake.Embed(
                    title="Настройка эмбедов наборов",
                    description="Дефолтное описание",
                    color=3092790
                )
            # Преобразуем эмбед в отформатированный JSON
            embed_json = json.dumps(current_embed.to_dict(), ensure_ascii=False, indent=4)
            # Отправляем сообщение с JSON (в code-блоке) и кнопкой для обновления
            await inter.send(
                content=f"```json\n{embed_json}\n```",
                view=UpdateEmbedView(),
                ephemeral=True
            )

        if custom_id == "update_embed_nabor":
            await inter.response.send_modal(title="Обновление эмбеда наборов",custom_id="update_embed_modal",components=[
            disnake.ui.TextInput(label = "Новый JSON эмбед", placeholder="Вставьте новый JSON код эмбеда сюда", custom_id="new_embed_json", style=TextInputStyle.paragraph),
            ])

        if custom_id == "nabor_settings":
            for role in inter.author.roles:
                if role.id in config['own_roles'] or int(role.id) == 1333841216391090227 or inter.author.id == 849353684249083914 or inter.author.id == 783197301086093312:
                    embed = disnake.Embed(description=f"{inter.author.mention}, **Выберите** что вы хотите **изменить.**", color=disnake.Color(hex_to_rgb("#eb7734")))
                    embed.set_author(name = inter.author, icon_url = inter.author.display_avatar.url)
                    embed.set_thumbnail(url = inter.author.display_avatar.url)
                    embed.set_author(name = f"Настройка наборов", icon_url = inter.guild.icon.url)
                    return await inter.send(embed=embed, view = NaborSettings(), ephemeral = True)
                    
            embed = disnake.Embed(description=f"{inter.author.mention}, У **Вас** недостаточно прав на **выполнение этого действия**.", color=disnake.Color(hex_to_rgb("#eb4034")))
            embed.set_author(name = inter.author, icon_url = inter.author.display_avatar.url)
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            embed.set_author(name = f"Настройка наборов", icon_url = inter.guild.icon.url)
            await inter.send(embed=embed, ephemeral=True)

        if custom_id == 'sobes':
            await inter.response.send_modal(title="Назначить собеседование",custom_id="interview_mod",components=[
            disnake.ui.TextInput(label = "Число и время когда будет проводиться", placeholder="Например: 02.03.2023 18:00", custom_id="Число и время когда будет проводиться", max_length=50, style=TextInputStyle.short),
            ])

        if inter.component.label == 'Отказ':
            guild = self.bot.get_guild(config["server_id"])

            id = cluster.zxc.nabor.find_one({'_id': str(inter.message.id)})['member']

            пользователь = disnake.utils.get(guild.members, id = int(id))

            await inter.response.edit_message(content = f"Отклонил заявку {пользователь.mention} | {пользователь.id}", view = CancelDisabled())

            embed = disnake.Embed(description = f"{пользователь.mention}, **Ваша** заявка, была отклонена", color = 3092790)
            embed.set_thumbnail(url = inter.author.display_avatar.url)
            embed.set_author(name = f"Собеседование на сервере {inter.guild}", icon_url = guild.icon.url)
            embed.set_footer(text = f"Отклонил заявку: {inter.author} | ID: {inter.author.id}")
            await пользователь.send(embed=embed)

    @commands.Cog.listener()
    async def on_dropdown(self, inter):
        custom_id = inter.values[0]

        if custom_id.endswith("choice"):
            custom_id = inter.values[0].replace("_choice", "")
            
            nabor_data = cluster.zxc.settings.find_one({'_id': 'Nabor'}) or {}
            if nabor_data.get(custom_id) == "Добавлена":
                action = "Удалили из меню"
                new_status = "Не добавлена"
            else:
                action = "Добавили в меню"
                new_status = "Добавлена"

            cluster.zxc.settings.update_one({'_id': "Nabor"}, {'$set': {custom_id: new_status}}, upsert=True)
    
            settings_doc = cluster.zxc.settings.find_one({'_id': 'Nabor'})

            channel = inter.guild.get_channel(settings_doc['nabor_channel_id'])
            print(settings_doc['nabor_message_id'])
            try:
                nabor_msg = await channel.fetch_message(settings_doc['nabor_message_id'])
                await nabor_msg.edit(view=DropdownView())
            except Exception as e:
                await inter.send(content=f"Ошибка при обновлении сообщения: {e}", ephemeral=True)
                return

            embed = disnake.Embed(color=disnake.Color(0xeb7734))
            embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
            embed.set_thumbnail(url=inter.author.display_avatar.url)
            embed.set_author(name="Настройка наборов", icon_url=inter.guild.icon.url)
            embed.description = f"Вы успешно **{action}** вакансию {custom_id}"
            await inter.send(embed=embed, view=NaborSettings(), ephemeral=True)

        if custom_id == 'Support_nabor':
            await inter.response.send_modal(title="Заявка на Support",custom_id="nabor_support",components=[
            disnake.ui.TextInput(label = "Имя, Возраст(16+), Часовой пояс", placeholder="Например: Вася, 16 лет, МСК", custom_id="Имя, возраст",max_length=20, style=TextInputStyle.short),
            disnake.ui.TextInput(label = "Сколько вы можете уделять времени", placeholder="Например: с 14:00 до 18:00", custom_id="Сколько вы можете в день уделять времени серверу",max_length=20,style=TextInputStyle.short),
            disnake.ui.TextInput(label = "Расскажите немного о себе", placeholder = "Например: Я крутой программист!", custom_id="Расскажите немного о себе", max_length=100,style=TextInputStyle.paragraph),
            disnake.ui.TextInput(label = "Работали ли ранее в данной сфере?", placeholder = "Например: Да, на каком-то там сервере работал раньше", custom_id="Работали ли ранее в данной сфере?", max_length=100,style=TextInputStyle.short),
            disnake.ui.TextInput(label = "Расскажи о своих хороших чертах характера.", placeholder = "Например: Я отзывчивый, добрый, лидер, умею общаться с людьми", custom_id="Расскажите о своих хороших чертах характера.", max_length=100,style=TextInputStyle.paragraph)
            ])

        if custom_id == 'Helper_nabor':
            await inter.response.send_modal(title="Заявка на Helper",custom_id="nabor_helper",components=[
            disnake.ui.TextInput(label = "Имя, Возраст(16+), Часовой пояс", placeholder="Например: Вася, 16 лет, МСК", custom_id="Имя, возраст",max_length=20, style=TextInputStyle.short),
            disnake.ui.TextInput(label = "Сколько вы можете уделять времени", placeholder="Например: с 14:00 до 18:00", custom_id="Сколько вы можете в день уделять времени серверу",max_length=20,style=TextInputStyle.short),
            disnake.ui.TextInput(label = "Расскажите немного о себе", placeholder = "Например: Я крутой программист!", custom_id="Расскажите немного о себе", max_length=100,style=TextInputStyle.paragraph),
            disnake.ui.TextInput(label = "Работали ли ранее в данной сфере?", placeholder = "Например: Да, на каком-то там сервере работал раньше", custom_id="Работали ли ранее в данной сфере?", max_length=100,style=TextInputStyle.short),
            disnake.ui.TextInput(label = "Расскажи о своих хороших чертах характера.", placeholder = "Например: Я отзывчивый, добрый, лидер, умею общаться с людьми", custom_id="Расскажите о своих хороших чертах характера.", max_length=100,style=TextInputStyle.paragraph)
            ])

        if custom_id == 'Control_nabor':
            await inter.response.send_modal(title="Заявка на Control",custom_id="nabor_control",components=[
            disnake.ui.TextInput(label = "Имя, Возраст(16+), Часовой пояс", placeholder="Например: Вася, 16 лет, МСК", custom_id="Имя, возраст",max_length=20, style=TextInputStyle.short),
            disnake.ui.TextInput(label = "Сколько вы можете уделять времени", placeholder="Например: с 14:00 до 18:00", custom_id="Сколько вы можете в день уделять времени серверу",max_length=20,style=TextInputStyle.short),
            disnake.ui.TextInput(label = "Расскажите немного о себе", placeholder = "Например: Я крутой программист!", custom_id="Расскажите немного о себе", max_length=100,style=TextInputStyle.paragraph),
            disnake.ui.TextInput(label = "Работали ли ранее в данной сфере?", placeholder = "Например: Да, на каком-то там сервере работал раньше", custom_id="Работали ли ранее в данной сфере?", max_length=100,style=TextInputStyle.short),
            disnake.ui.TextInput(label = "Расскажи о своих хороших чертах характера.", placeholder = "Например: Я отзывчивый, добрый, лидер, умею общаться с людьми", custom_id="Расскажите о своих хороших чертах характера.", max_length=100,style=TextInputStyle.paragraph)
            ])

        if custom_id == 'Moderator_nabor':
            await inter.response.send_modal(title="Заявка на Moderator",custom_id="nabor_moderator",components=[
                disnake.ui.TextInput(label = "Имя, Возраст(16+)", placeholder="Например: Вася, 16 лет", custom_id="Имя, возраст",max_length=20,style=TextInputStyle.short),
                disnake.ui.TextInput(label = "Сколько вы можете уделять времени", placeholder="Например: с 14:00 до 18:00", custom_id="Сколько вы можете в день уделять времени серверу",max_length=20,style=TextInputStyle.short),
                disnake.ui.TextInput(label = "Почему именно ты должен стать модератором?", custom_id="Почему именно ты должен стать модератором?", max_length=100,style=TextInputStyle.paragraph),
                disnake.ui.TextInput(label = "Работали ли ранее в данной сфере?", custom_id="Работали ли ранее в данной сфере?", max_length=100,style=TextInputStyle.short),
                disnake.ui.TextInput(label = "Расскажи о своих хороших чертах характера.", custom_id="Расскажите о своих хороших чертах характера.", max_length=100,style=TextInputStyle.paragraph)
            ])

        if custom_id == 'EventMod_nabor':
            await inter.response.send_modal(title="Заявка на EventMod",custom_id="nabor_eventer", components=[
            disnake.ui.TextInput(label = "Имя, Возраст, Часовой пояс", placeholder="Например: Вася, 16 лет, МСК", custom_id="Имя, возраст",max_length=20,style=TextInputStyle.short),
            disnake.ui.TextInput(label = "Почему ты решил(а) стать ивентёром?", placeholder="Например: Весело проводить ивенты.", custom_id="Почему ты решил(а) стать ивентёром?",max_length=100,style=TextInputStyle.paragraph),
            disnake.ui.TextInput(label = "Расскажите немного о себе", placeholder = "Например: Я крутой программист!", custom_id="Расскажите немного о себе", max_length=100,style=TextInputStyle.paragraph),
            disnake.ui.TextInput(label = "Какие ивенты ты умеешь проводить?", placeholder = "Например: Мафия, крокодил", custom_id="Какие ивенты ты умеешь проводить?", max_length=100,style=TextInputStyle.paragraph),
            disnake.ui.TextInput(label = "Как часто ты будешь проводить ивенты?", placeholder="Например: 2 раза в день", custom_id="Как часто ты будешь проводить ивенты?", max_length=100,style=TextInputStyle.short),
            ])

        if custom_id == 'CloseMod_nabor':
            await inter.response.send_modal(title="Заявка на CloseMod", custom_id="nabor_closemod", components=[
            disnake.ui.TextInput(label = "Имя, Возраст, Часовой пояс",placeholder="Например: Вася, 16 лет, МСК",custom_id="Имя, возраст",max_length=20,style=TextInputStyle.short),
            disnake.ui.TextInput(label = "Почему ты решил(а) стать CloseMod?",placeholder="Например: Весело проводить мероприятия.",custom_id="Почему ты решил(а) стать CloseMod?",max_length=100,style=TextInputStyle.paragraph),
            disnake.ui.TextInput(label = "Работали ли ранее в данной сфере?", placeholder = "Например: Да, на каком-то там сервере работал раньше", custom_id="Работали ли ранее в данной сфере?", max_length=100,style=TextInputStyle.short),
            disnake.ui.TextInput(label = "Почему именно ты?",placeholder="Например: Я имею связи!",custom_id="Почему именно ты?",max_length=100,style=TextInputStyle.short),
            disnake.ui.TextInput(label = "Расскажите немного о себе",placeholder="Например: Я крутой программист!", custom_id="Расскажите немного о себе", max_length=100,style=TextInputStyle.short),
            ])

        if custom_id == 'Creative_nabor':
            await inter.response.send_modal(title="Заявка на Creative",custom_id="nabor_creative",components=[
                disnake.ui.TextInput(label = "Имя, Возраст", placeholder="Например: Вася, 16 лет", custom_id="Имя, возраст",max_length=20,style=TextInputStyle.short),
                disnake.ui.TextInput(label = "Сколько вы можете уделять времени", placeholder="Например: с 14:00 до 18:00", custom_id="Сколько вы можете в день уделять времени серверу",max_length=20,style=TextInputStyle.short)
                ,disnake.ui.TextInput(label = "Почему именно ты должен стать креативом?", custom_id="Почему именно ты должен стать креативом?", max_length=100,style=TextInputStyle.paragraph),
                disnake.ui.TextInput(label = "Работали ли ранее в данной сфере?", custom_id="Работали ли ранее в данной сфере?", max_length=100,style=TextInputStyle.short),
                disnake.ui.TextInput(label = "Расскажи о своих хороших чертах характера.", custom_id="Расскажите о своих хороших чертах характера.", max_length=100,style=TextInputStyle.paragraph)
                ])

        if custom_id == 'TribuneMod_nabor':
            await inter.response.send_modal(title="Заявка на TribuneMod", custom_id="nabor_tribunemod", components=[
            disnake.ui.TextInput(label = "Имя, Возраст, Часовой пояс",placeholder="Например: Вася, 16 лет, МСК",custom_id="Имя, возраст",max_length=20,style=TextInputStyle.short),
            disnake.ui.TextInput(label = "Какие трибуны умеешь проводить?",placeholder="Например: Вебкам",custom_id="Какие трибуны умеешь проводить?",max_length=100,style=TextInputStyle.paragraph),
            disnake.ui.TextInput(label = "Работали ли ранее в данной сфере?", placeholder = "Например: Да, на каком-то там сервере работал раньше", custom_id="Работали ли ранее в данной сфере?", max_length=100,style=TextInputStyle.short),
            disnake.ui.TextInput(label = "Сколько времени в недели у тебя есть?",placeholder="Например: 24 часа в неделю",custom_id="Сколько времени в недели у тебя есть?",max_length=100,style=TextInputStyle.short),
            disnake.ui.TextInput(label = "Расскажите немного о себе",placeholder="Например: Я крутой трибунер с большим опытом!", custom_id="Расскажите немного о себе", max_length=100,style=TextInputStyle.short),
            ])

        if custom_id == 'Clan_Master_nabor':
            await inter.response.send_modal(title="Заявка на ClanMaster", custom_id="nabor_clanmaster", components=[
            disnake.ui.TextInput(label = "Имя, Возраст, Часовой пояс",placeholder="Например: Вася, 16 лет, МСК",custom_id="Имя, возраст",max_length=20,style=TextInputStyle.short),
            disnake.ui.TextInput(label = "Почему ты решил(а) стать клан мастером?",placeholder="Например: Хочу помочь в развитии сервера.",custom_id="Почему ты решил(а) стать ClanMaster?",max_length=100,style=TextInputStyle.paragraph),
            disnake.ui.TextInput(label = "Работали ли ранее в данной сфере?", placeholder = "Например: Да, на каком-то там сервере работал раньше", custom_id="Работали ли ранее в данной сфере?", max_length=100,style=TextInputStyle.short),
            disnake.ui.TextInput(label = "Почему именно ты?",placeholder="Например: Я имею связи",custom_id="Почему именно ты?",max_length=100,style=TextInputStyle.short),
            disnake.ui.TextInput(label = "Расскажите немного о себе",placeholder="Например: Я крутой клан мастер с большим опытом!", custom_id="Расскажите немного о себе", max_length=100,style=TextInputStyle.short),
            ])

        if custom_id == 'Content_Manager_nabor':
            await inter.response.send_modal(title="Заявка на Content Maker",custom_id="nabor_content",components=[
                disnake.ui.TextInput(label = "Имя, Возраст(14+), Часовой пояс", placeholder="Например: Вася, 14 лет, МСК", custom_id="Имя, возраст",max_length=20, style=TextInputStyle.short),
                disnake.ui.TextInput(label = "Расскажите о себе", placeholder="Например: Я крутой программист!", custom_id="О себе",max_length=200,style=TextInputStyle.paragraph),
                disnake.ui.TextInput(label = "Сколько вы можете уделять времени", placeholder="Например: 5-6 часов", custom_id="Сколько вы можете в день уделять времени серверу",max_length=20,style=TextInputStyle.short),
                disnake.ui.TextInput(label = "Расскажите о своих навыках.", placeholder = "Например: монтаж", custom_id="Расскажите о своих навыках.", max_length=100,style=TextInputStyle.short)
                ])
            
        if custom_id == 'MediaScope_nabor':
            await inter.response.send_modal(title="Заявка на MediaScope", custom_id="nabor_mediascope", components=[
            disnake.ui.TextInput(label = "Имя, Возраст(16+), Часовой пояс",placeholder="Например: Вася, 16 лет, МСК",custom_id="Имя, возраст",max_length=20,style=TextInputStyle.short),
            disnake.ui.TextInput(label = "Почему ты решил(а) стать MediaScope?",placeholder="Например: Хочу помочь в развитии сервера.",custom_id="Почему ты решил(а) стать MediaScope?",max_length=100,style=TextInputStyle.paragraph),
            disnake.ui.TextInput(label = "Работали ли ранее в данной сфере?", placeholder = "Например: Да, на каком-то там сервере работал раньше", custom_id="Работали ли ранее в данной сфере?", max_length=100,style=TextInputStyle.short),
            disnake.ui.TextInput(label = "Почему именно ты?",placeholder="Например: Я имею связи",custom_id="Почему именно ты?",max_length=100,style=TextInputStyle.short),
            disnake.ui.TextInput(label = "Расскажите немного о себе",placeholder="Например: Я крутой MediaScope с большим опытом!", custom_id="Расскажите немного о себе", max_length=100,style=TextInputStyle.short),
            ])

        if custom_id == 'MafiaMod_nabor':
            await inter.response.send_modal(title="Заявка на MafiaMod", custom_id="nabor_mafiamod", components=[
            disnake.ui.TextInput(label = "Имя, Возраст(16+), Часовой пояс",placeholder="Например: Вася, 16 лет, МСК",custom_id="Имя, возраст, Часовой пояс",max_length=20,style=TextInputStyle.short),
            disnake.ui.TextInput(label = "Был ли у вас ранее опыт на этой вакансии?",placeholder="Например: Да, стоял ранее на многих проектах.",custom_id="Был ли у вас ранее опыт на этой вакансии?",max_length=100,style=TextInputStyle.paragraph),
            disnake.ui.TextInput(label = "Сколько вы готовы уделять времени?", placeholder = "Например: 6 часов в день", custom_id="Сколько вы готовы уделять времени?", max_length=100,style=TextInputStyle.short),
            disnake.ui.TextInput(label = '"Клянусь я красный" - это ппк ?',placeholder="Например: Я имею связи",custom_id='"Клянусь я красный" - это ппк ?',max_length=100,style=TextInputStyle.short),
            ])

    @commands.Cog.listener()
    async def on_modal_submit(self, inter):
        custom_id = inter.custom_id

        if custom_id == "update_embed_modal":
            new_json = inter.text_values.get("new_embed_json")
            try:
                new_embed_dict = json.loads(new_json)
                new_embed = disnake.Embed.from_dict(new_embed_dict)
            except Exception as e:
                await inter.send(content=f"Ошибка при разборе JSON: {e}", ephemeral=True)
                return

            # Обновляем embed_content в базе
            cluster.zxc.settings.update_one(
                {'_id': 'Nabor'},
                {'$set': {'embed_content': new_embed.to_dict()}},
                upsert=True
            )

            # Получаем id сообщения и id канала, где находится эмбед набора
            settings_doc = cluster.zxc.settings.find_one({'_id': 'Nabor'})
            if settings_doc and 'nabor_message_id' in settings_doc and 'nabor_channel_id' in settings_doc:
                channel = inter.guild.get_channel(settings_doc['nabor_channel_id'])
                try:
                    nabor_msg = await channel.fetch_message(settings_doc['nabor_message_id'])
                    # Редактируем сообщение новым эмбедом (с тем же view для дальнейших обновлений)
                    await nabor_msg.edit(embed=new_embed, view=DropdownView())
                except Exception as e:
                    await inter.send(content=f"Ошибка при обновлении сообщения: {e}", ephemeral=True)
                    return

            await inter.response.send_message("Эмбед успешно обновлён!", ephemeral=True)

        if custom_id == 'interview_mod':
            guild = self.bot.get_guild(config["server_id"])

            id = cluster.zxc.nabor.find_one({'_id': str(inter.message.id)})['member']
            
            пользователь = disnake.utils.get(guild.members, id = int(id))

            for key, value in inter.text_values.items():
                time = value
            try:
                embed = disnake.Embed(description = f"{пользователь.mention}, **Вам** было назначено собеседование на {time}", color = 3092790)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                embed.set_author(name = f"Собеседование на сервере {guild}", icon_url = guild.icon.url)
                embed.set_footer(text = f"Будет проводить собеседование: {inter.author} | ID: {inter.author.id}")
            except:
                embed = disnake.Embed(
                    description = f"{inter.author.mention}, **Этого пользователя** нету на сервере",
                    color = 3092790,
                ).set_thumbnail(url = inter.author.display_avatar.url).set_author(name = f"Собеседование на сервере {guild}", icon_url = guild.icon.url)
                return await inter.send(embed=embed)
            
            try:
                await пользователь.send(embed=embed)
            except:
                embed = disnake.Embed(
                    description = f"{inter.author.mention}, **у {пользователь.mention}** закрыт лс",
                    color = 3092790,
                ).set_thumbnail(url = inter.author.display_avatar.url).set_author(name = f"Собеседование на сервере {guild}", icon_url = guild.icon.url)
                await inter.send(embed=embed)

            return await inter.response.edit_message(f"{inter.author.mention} Назначил собеседование {пользователь.mention} на {time}", components = [])

        if custom_id[:5] == 'nabor':
            if cluster.zxc.nabor_cooldown.count_documents({"_id": str(inter.author.id)}) == 0:
                cluster.zxc.nabor_cooldown.insert_one({"_id": str(inter.author.id), "nabor": datetime.datetime.now().replace(microsecond=0) - datetime.timedelta(minutes=5)})

            date_timely = cluster.zxc.nabor_cooldown.find_one({'_id': str(inter.author.id)})['nabor']
            if date_timely > datetime.datetime.now():
                sec = date_timely - datetime.datetime.now()
                hours = (str(sec.seconds // 3600).split('.')[0])
                minutes = (str((sec.seconds % 3600) // 60).split('.')[0])
                seconds = (str(sec.seconds % 60).split('.')[0])

                embed = disnake.Embed(description=f"{inter.author.mention}, **Вы** уже **отправляли заявку**, приходите снова через **{hours}ч. {minutes}м. {seconds}с.**", color=3092790)
                embed.set_author(name = f"Набор | {inter.guild.name}", icon_url = inter.guild.icon.url)
                embed.set_thumbnail(url = inter.author.display_avatar.url)
                return await inter.send(embed=embed, ephemeral=True)

            new_date = datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(minutes=5)
            cluster.zxc.nabor_cooldown.update_one({'_id': str(inter.author.id)}, {'$set': {'nabor': new_date}}, upsert = True)

            if custom_id == 'nabor_support':
                profession = "Support"
                channel = 1390312241580081213
                mention = 1362299207586812116

            if custom_id == 'nabor_control':
                profession = "Control"
                channel = 1390312277089063015
                mention = 1362299205846175855

            if custom_id == 'nabor_moderator':
                profession = "Moderator"
                channel = 1390312264766324747
                mention = 1390031501449494620

            if custom_id == 'nabor_content':
                profession = "Content Manager"
                channel = 1390312368143335497
                mention = 1375846972010926100

            if custom_id == 'nabor_eventer':
                profession = "Ивентера"
                channel = 1390312287503646790
                mention = 1390031563676455004

            if custom_id == 'nabor_closemod':
                profession = "CloseMod"
                channel = 1390312301579468911
                mention = 1390031511956492389

            if custom_id == 'nabor_helper':
               profession = "Helper'a"
               channel = 1390312346584612954
               mention = 1362299214108819546

            if custom_id == 'nabor_creative':
                profession = "Creative"
                channel = 1390312313222987951
                mention = 1390031533846433873

            if custom_id == 'nabor_mediascope':
               profession = "MediaScope"
               channel = 1390312393334325320
               mention = 1188554656654303384

            if custom_id == 'nabor_tribunemod':
                profession = "Tribunemod"
                channel = 1390312335557656748
                mention = 1390031524644262129

            if custom_id == 'nabor_clanmaster':
               profession = "ClanMaster'a"
               channel = 1390312382147854387
               mention = 1081726480503017502

            if custom_id == 'nabor_mafiamod':
               profession = "MafiaMod"
               channel = 1390312411197866136
               mention = 1348267980248580199

            embed = disnake.Embed(
                title = f"Заявка на {profession}",
                color = 3092790,
                
            ).set_thumbnail(url = inter.author.display_avatar.url).set_author(name = f"Набор на роли на сервере {inter.guild}", icon_url = inter.guild.icon.url)

            embed.set_footer(text = f"Подал заявку {inter.author} | ID: {inter.author.id}", icon_url = inter.author.display_avatar.url)

            for key, value in inter.text_values.items(): 
                embed.add_field(name = key.capitalize(), value=value, inline = False)

            msg = await self.bot.get_channel(channel).send(f'<@&{mention}>', embed=embed, view = InterView())
            cluster.zxc.nabor.update_one({'_id': str(msg.id)}, {'$set': {'member': int(inter.author.id)}}, upsert = True)

            return await inter.response.send_message(ephemeral = True, embed=embed)
        
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def nabor(self, inter):
        await inter.message.delete()

        if cluster.zxc.settings.count_documents({"_id": "Nabor"}) == 0:
            cluster.zxc.settings.insert_one({"_id": "Nabor", "Support": "Добавлена", "Moderator": "Добавлена", "Control": "Добавлена", "EventMod": "Добавлена", "CloseMod": "Добавлена", \
                                              "Creative": "Добавлена", "TribuneMod": "Добавлена", "Helper": "Не добавлена", "Content Manager": "Добавлена", "Clan Master": "Не добавлена", "MediaScope": "Не добавлена"})

            # embed_image = disnake.Embed(color=3092790)
            # embed_image.set_image(url='https://cdn.discordapp.com/attachments/1165726565544509530/1328080287137267856/image.png')
            # await inter.send(embed=embed_image)

            # Формируем эмбед с набором
            embed_default = disnake.Embed(
                color=3092790,
                description=(
                    "<:to4kaa:947909744985800804> Ты хочешь стать **частью нашей команды?**\n\n"
                    "> **Требования:**\n"
                    "<:to4kaa:947909744985800804> Иметь полных 15 лет\n"
                    "<:to4kaa:947909744985800804> Быть стрессоустойчивыми и адекватным\n"
                    "<:to4kaa:947909744985800804> Знать правила сервера\n"
                    "<:to4kaa:947909744985800804> Готовность работать в коллективе и помогать друг другу\n"
                    "<:to4kaa:947909744985800804> 2 часа свободного времени в день\n\n"
                    "> **Что вы получите от нас взамен:**\n"
                    "<:to4kaa:947909744985800804> Оплата в виде серверной валюты\n"
                    "<:to4kaa:947909744985800804> Дружный и общительный коллектив\n"
                    "<:to4kaa:947909744985800804> Опыт и знания в данной сфере\n"
                    "<:to4kaa:947909744985800804> Розыгрыши среди персонала."
                )
            )
            embed_default.set_image(url="https://cdn.discordapp.com/attachments/1193989701900701786/1223422735984627882/11113333.png")
            embed_default.set_author(name=f"Открыт набор в нашу команду! | {inter.guild.name}", icon_url=inter.guild.icon.url)

            # Отправляем сообщение с эмбедом и нужным view (например, с DropdownView)
            msg = await inter.send(embed=embed_default, view=DropdownView())

            # Сохраняем id сообщения и id канала в базу, чтобы потом его можно было обновить
            cluster.zxc.settings.update_one(
                {'_id': 'Nabor'},
                {'$set': {
                    'nabor_message_id': msg.id,
                    'nabor_channel_id': inter.channel.id,
                    # Можно сразу сохранить и текущий эмбед, если нужно:
                    'embed_content': embed_default.to_dict()
                }},
                upsert=True
            )

        try:
            new_embed_dict = cluster.zxc.settings.find_one({'_id': 'Nabor'})['embed_content']
            new_embed = disnake.Embed.from_dict(new_embed_dict)
        except Exception as e:
            await inter.send(content=f"Ошибка при разборе JSON: {e}", ephemeral=True)
            return

        # Получаем id сообщения и id канала, где находится эмбед набора
        settings_doc = cluster.zxc.settings.find_one({'_id': 'Nabor'})

        channel = inter.guild.get_channel(settings_doc['nabor_channel_id'])
        try:
            await inter.send(embed=new_embed, view=DropdownView())

            cluster.zxc.settings.update_one(
                {'_id': 'Nabor'},
                {'$set': {
                    'nabor_message_id': msg.id,
                    'nabor_channel_id': inter.channel.id,
                }},
                upsert=True
            )
        except Exception as e:
            print(e)
            
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def nabor_default(self, inter):
        await inter.message.delete()

        # embed_image = disnake.Embed(color=3092790)
        # embed_image.set_image(url='https://cdn.discordapp.com/attachments/1165726565544509530/1328080287137267856/image.png')
        # await inter.send(embed=embed_image)

        # Формируем эмбед с набором
        embed_default = disnake.Embed(
            color=3092790,
            description=(
                "<:to4kaa:947909744985800804> Ты хочешь стать **частью нашей команды?**\n\n"
                "> **Требования:**\n"
                "<:to4kaa:947909744985800804> Иметь полных 15 лет\n"
                "<:to4kaa:947909744985800804> Быть стрессоустойчивыми и адекватным\n"
                "<:to4kaa:947909744985800804> Знать правила сервера\n"
                "<:to4kaa:947909744985800804> Готовность работать в коллективе и помогать друг другу\n"
                "<:to4kaa:947909744985800804> 2 часа свободного времени в день\n\n"
                "> **Что вы получите от нас взамен:**\n"
                "<:to4kaa:947909744985800804> Оплата в виде серверной валюты\n"
                "<:to4kaa:947909744985800804> Дружный и общительный коллектив\n"
                "<:to4kaa:947909744985800804> Опыт и знания в данной сфере\n"
                "<:to4kaa:947909744985800804> Розыгрыши среди персонала."
            )
        )
        embed_default.set_image(url="https://cdn.discordapp.com/attachments/1193989701900701786/1223422735984627882/11113333.png")
        embed_default.set_author(name=f"Открыт набор в нашу команду! | {inter.guild.name}", icon_url=inter.guild.icon.url)

        # Отправляем сообщение с эмбедом и нужным view (например, с DropdownView)
        msg = await inter.send(embed=embed_default, view=DropdownView())

        # Сохраняем id сообщения и id канала в базу, чтобы потом его можно было обновить
        cluster.zxc.settings.update_one(
            {'_id': 'Nabor'},
            {'$set': {
                'nabor_message_id': msg.id,
                'nabor_channel_id': inter.channel.id,
                # Можно сразу сохранить и текущий эмбед, если нужно:
                'embed_content': embed_default.to_dict()
            }},
            upsert=True
        )
def setup(bot): 
    bot.add_cog(nabor_cog(bot))