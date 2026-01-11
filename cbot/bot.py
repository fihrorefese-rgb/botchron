import disnake
from disnake.ext import commands
import json
import os
from datetime import datetime
from dotenv import load_dotenv

intents = disnake.Intents.default()  # или .all()
intents.members = True       # Чтобы видеть участников и их роли
intents.message_content = True  # Чтобы читать содержимое сообщений
intents.guilds = True        # Чтобы видеть серверы

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix=".", help_command=None, intents=disnake.Intents.all(), test_guilds=[1457765884155134095])

CHARACTERS_FILE = "characters.json"

def init_characters_file():
    """Инициализирует файл characters.json если его нет"""
    if not os.path.exists(CHARACTERS_FILE):
        initial_data = {
            "next_id": 0,
            "characters": []
        }
        with open(CHARACTERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=4, ensure_ascii=False)
        print(f"Файл {CHARACTERS_FILE} создан")

# Вызовите при запуске бота
def init_characters_file():
    """Инициализирует файл characters.json если его нет"""
    if not os.path.exists(CHARACTERS_FILE):
        initial_data = {
            "next_id": 0,
            "characters": []
        }
        with open(CHARACTERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=4, ensure_ascii=False)
        print(f"✅ Файл {CHARACTERS_FILE} создан")

# Загружаем существующих персонажей
def load_characters():
    if os.path.exists(CHARACTERS_FILE):
        try:
            with open(CHARACTERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"next_id": 0, "characters": []}
    return {"next_id": 0, "characters": []}

# Сохраняем персонажей
def save_characters(data):
    with open(CHARACTERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

init_characters_file()

@bot.event
async def on_ready():
 print(f"Bot {bot.user} is ready to work!")

 @bot.event
 async def on_command_error(ctx, error):
    print(error)

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"{ctx.author}, у вас недостаточно прав для выполнения данной команды!")
    elif isinstance(error, commands.UserInputError):
        await ctx.send(embed=disnake.Embed(
    description=f"Правильное использование команды: '{ctx.prefix}{ctx.command.name}'"
    ))

@bot.command(name="бан", hidden=True, aliases=["ban", "b"])
@commands.has_permissions(ban_members=True, administrator=True)
async def ban(ctx, member: disnake.Member, *, reason="Нарушение правил."):
    await ctx.send(f"Администратор {ctx.author.mention} забанил пользователя {member.mention}", delete_after=6)
    await member.ban(reason=reason)
    await ctx.message.delete()

@bot.slash_command(description="Калькулятор")
async def calc(inter, number1: int, operation: str, number2: int):
    if oper == "+":
        result = a + b
    elif oper == "-":
        result = a - b
    else:
        result = "Вы ввели что-то неверно!"

    await inter.send(str(result))

@bot.slash_command(description="Пинг-Понг")
async def ping(ctx):
    await ctx.send(f"Понг!")

@bot.slash_command(description="Бан",
    default_member_permissions=disnake.Permissions(ban_members=True, administrator=True)
    )
async def ban(ctx, member: disnake.Member, *, reason="Нарушение правил."):
    await ctx.send(f"Администратор {ctx.author.mention} забанил пользователя {member.mention}")
    await member.ban(reason=reason)

@bot.slash_command(
    name="unban",
    description="Разбанить пользователя по ID",
    default_member_permissions=disnake.Permissions(ban_members=True, administrator=True)
)
async def unban_simple(
    inter: disnake.ApplicationCommandInteraction,
    user_id: str = commands.Param(description="ID пользователя (только цифры)")
):
    await inter.response.defer()
    
    if not user_id.isdigit():
        await inter.edit_original_message(content="❌ ID должен содержать только цифры!")
        return
    
    try:
        user_id_int = int(user_id)
        
        # Пытаемся разбанить
        user = await bot.fetch_user(user_id_int)
        await inter.guild.unban(user)
        
        await inter.edit_original_message(
            content=f"✅ Пользователь **{user}** (`{user_id}`) разбанен!"
        )
        
    except disnake.NotFound:
        await inter.edit_original_message(
            content=f"❌ Пользователь с ID `{user_id}` не найден или не забанен."
        )
    except disnake.Forbidden:
        await inter.edit_original_message(
            content="❌ У бота нет прав на разбан!"
        )
    except Exception as e:
        await inter.edit_original_message(
            content=f"❌ Ошибка: `{e}`"
        )

@bot.slash_command(
    name="givechar",
    description="Создать персонажа и выдать его пользователю",
    default_member_permissions=disnake.Permissions(manage_roles=True)
)
async def givechar(
    inter: disnake.ApplicationCommandInteraction,
    character_name: str = commands.Param(name="имя", description="Название персонажа"),
    user: disnake.Member = commands.Param(name="пользователь", description="Владелец персонажа")
):
    """Создать персонажа и назначить его пользователю"""
    
    await inter.response.defer()
    
    # Загружаем данные
    data = load_characters()
    
    # Генерируем ID
    char_id = data["next_id"]
    
    # Создаем запись о персонаже
    character = {
        "id": char_id,
        "name": character_name,
        "owner_id": user.id,
        "owner_name": str(user),
        "created_by": inter.author.id,
        "created_at": datetime.utcnow().isoformat(),
        "guild_id": inter.guild.id
    }
    
    # Добавляем в список
    data["characters"].append(character)
    data["next_id"] = char_id + 1
    
    # Сохраняем
    save_characters(data)
    
    # Создаем Embed сообщение
    embed = disnake.Embed(
        title="✅ Персонаж создан!",
        color=disnake.Color.green(),
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(
        name="📝 Информация о персонаже",
        value=f"**Персонаж по имени `{character_name}` успешно создан!**",
        inline=False
    )
    
    embed.add_field(
        name="👤 Владелец персонажа",
        value=f"{user.mention}\n`{user}`",
        inline=True
    )
    
    embed.add_field(
        name="🆔 ID персонажа",
        value=f"`{char_id}`",
        inline=True
    )
    
    embed.add_field(
        name="🗓️ Дата создания",
        value=f"<t:{int(datetime.utcnow().timestamp())}:R>",
        inline=False
    )
    
    # Добавляем аватарку создателя, если есть
    footer_text = f"Создал: {inter.author}"
    footer_icon = None
    
    if inter.author.avatar:
        footer_icon = inter.author.avatar.url
    elif inter.author.default_avatar:
        footer_icon = inter.author.default_avatar.url
    
    embed.set_footer(text=footer_text, icon_url=footer_icon)
    
    # Добавляем аватарку владельца, если есть
    if user.avatar:
        embed.set_thumbnail(url=user.avatar.url)
    elif user.default_avatar:
        embed.set_thumbnail(url=user.default_avatar.url)
    
    await inter.edit_original_message(embed=embed)

# Дополнительная команда для просмотра персонажей
@bot.slash_command(
    name="mychars",
    description="Показать ваших персонажей"
)
async def mychars(
    inter: disnake.ApplicationCommandInteraction,
    user: disnake.Member = commands.Param(
        name="пользователь", 
        description="Пользователь для просмотра персонажей", 
        default=None
    )
):
    """Показать персонажей пользователя"""
    
    await inter.response.defer()
    
    target_user = user or inter.author
    
    # Загружаем данные
    data = load_characters()
    
    # Фильтруем персонажей пользователя
    user_chars = [char for char in data["characters"] 
                  if char["owner_id"] == target_user.id and char["guild_id"] == inter.guild.id]
    
    if not user_chars:
        embed = disnake.Embed(
            title="📂 Персонажи",
            description=f"У {target_user.mention} нет персонажей.",
            color=disnake.Color.orange()
        )
        await inter.edit_original_message(embed=embed)
        return
    
    # Создаем Embed со списком персонажей
    embed = disnake.Embed(
        title=f"📂 Персонажи {target_user}",
        color=disnake.Color.blue(),
        timestamp=datetime.utcnow()
    )
    
    for char in user_chars[:10]:  # Ограничиваем 10 персонажами
        # Парсим дату создания
        try:
            created_at = datetime.fromisoformat(char["created_at"])
            date_str = f"<t:{int(created_at.timestamp())}:D>"
        except (KeyError, ValueError):
            date_str = "Неизвестно"
        
        # Получаем создателя
        creator = inter.guild.get_member(char.get("created_by", 0))
        creator_name = str(creator) if creator else "Неизвестно"
        
        embed.add_field(
            name=f"🆔 {char['id']}: {char['name']}",
            value=f"Создал: {creator_name}\nДата: {date_str}",
            inline=False
        )
    
    embed.set_footer(text=f"Всего персонажей: {len(user_chars)}")
    
    # Добавляем аватарку пользователя
    if target_user.avatar:
        embed.set_thumbnail(url=target_user.avatar.url)
    elif target_user.default_avatar:
        embed.set_thumbnail(url=target_user.default_avatar.url)
    
    await inter.edit_original_message(embed=embed)

# Команда для просмотра информации о конкретном персонаже
# Команда для просмотра информации о персонаже
@bot.slash_command(
    name="charinfo",
    description="Показать информацию о персонаже"
)
async def charinfo(
    inter: disnake.ApplicationCommandInteraction,
    char_id: int = commands.Param(name="id", description="ID персонажа", ge=0)
):
    """Показать детальную информацию о персонаже"""
    
    await inter.response.defer()
    
    data = load_characters()
    
    # Ищем персонажа
    character = None
    for char in data["characters"]:
        if char["id"] == char_id and char["guild_id"] == inter.guild.id:
            character = char
            break
    
    if not character:
        embed = disnake.Embed(
            title="❌ Персонаж не найден",
            description=f"Персонаж с ID `{char_id}` не найден.",
            color=disnake.Color.red()
        )
        await inter.edit_original_message(embed=embed)
        return
    
    # Получаем кастомный цвет
    custom_color = character.get("embed_color")
    if custom_color is not None:
        embed_color = disnake.Color(custom_color)
    else:
        embed_color = disnake.Color.dark_purple()
    
    # Получаем место в топе
    sorted_chars = sorted(data["characters"], key=lambda x: sum(x.get("stats", {}).values()), reverse=True)
    top_position = next((i+1 for i, char in enumerate(sorted_chars) if char["id"] == char_id), "N/A")
    
    # Получаем объект пользователя
    owner = inter.guild.get_member(character["owner_id"])
    
    # Создаем Embed
    embed = disnake.Embed(
        title="Информация о персонаже",
        color=embed_color
    )
    
    # Заголовок
    embed.add_field(
        name="》═══════~Revius~═══════《",
        value=f"  **ID:** `{character['id']}`   ---   **TOP:** `{top_position}`",
        inline=False
    )
    
    # Основная информация
    char_info = f"""
> • Имя: `{character.get('name', '[  ]')}`
> • Возраст: `{character.get('age', '[ ]')}`
> • Гендер: `{character.get('gender', '[  ]')}`
> • Сексуальность: `{character.get('sexuality', '[  ]')}`
> • Прозвище: `{character.get('nickname', '[  ]')}`
> • Организация: `{character.get('organization', '[  ]')}`
> • Должность: `{character.get('position', '[  ]')}`
> • Упоминание: {owner.mention if owner else '[ <user> ]'}
    """
    
    embed.add_field(
        name="》═══════~◈~═══════《\n**Персонаж**",
        value=char_info,
        inline=False
    )
    
    # Характеристики
    stats = character.get('stats', {})
    total_stats = sum(stats.values()) if stats else 0
    
    stats_info = f"""
> • Количество Секса: `{stats.get('sex_count', 0)}`
> • Чувствительность: `{stats.get('sensitivity', 0)}`
> • Сила Феромон: `{stats.get('pheromone_power', 0)}`
> • Стойкость: `{stats.get('endurance', 0)}`
> • Умственное развитие: `{stats.get('intelligence', 0)}`
    """
    
    embed.add_field(
        name=f"》═══════~◈~═══════《\n**Характеристики:**  `{total_stats}`",
        value=stats_info,
        inline=False
    )
    
    # Дополнительное
    additional = character.get('additional', {})
    
    additional_info = f"""
> • Покровительство: `{additional.get('patronage', '[  ]')}`
> • Вагинальный: `{additional.get('vaginal', '[  ]')}`
> • Анальный: `{additional.get('anal', '[  ]')}`
> • Минет: `{additional.get('blowjob', '[  ]')}`
> • Куни: `{additional.get('cuni', '[  ]')}`
> • Боевые Искусства: `{additional.get('martial_arts', '[  ]')}`
> • Бюджет: `{additional.get('budget', 0)}`
> • Дополнительное: `{additional.get('extra', '[ ]')}`
    """
    
    embed.add_field(
        name="》═══════~◈~═══════《\n**Дополнительное**",
        value=additional_info,
        inline=False
    )
    
    # Добавляем кастомную аватарку ПОСЛЕ раздела "Дополнительное"
    custom_avatar = character.get('custom_avatar')
    if custom_avatar:
        # Добавляем разделитель перед аватаркой
        embed.add_field(
            name="》═══════~◈~═══════《",
            value="**🖼️ Аватарка персонажа**",
            inline=False
        )
        
        # Устанавливаем изображение (будет в самом конце embed)
        embed.set_image(url=custom_avatar)
    
    # Футер с информацией
    footer_text = f"📅 Создан: {datetime.fromisoformat(character['created_at']).strftime('%d.%m.%Y')}"
    
    if custom_color is not None:
        color_hex = f"#{hex(custom_color)[2:].upper().zfill(6)}"
        footer_text += f" | 🎨 Цвет: {color_hex}"
    
    footer_text += f" | 👤 Запросил: {inter.author.name}"
    
    embed.set_footer(text=footer_text, icon_url=inter.author.avatar.url if inter.author.avatar else None)
    
    await inter.edit_original_message(embed=embed)
# Команда для редактирования персонажа
# ========== КОНФИГУРАЦИЯ РОЛЕЙ ==========
@bot.slash_command(
    name="editchar",
    description="Редактировать несколько характеристик персонажа (требуется специальная роль)",
    default_member_permissions=disnake.Permissions(view_audit_log=True)
)
async def editchar(
    inter: disnake.ApplicationCommandInteraction,
    char_id: int = commands.Param(name="id", description="ID персонажа", ge=0),
    # Основные поля
    имя: str = commands.Param(name="имя", description="Новое имя персонажа", default=None),
    возраст: str = commands.Param(name="возраст", description="Новый возраст", default=None),
    гендер: str = commands.Param(name="гендер", description="Новый гендер", default=None),
    сексуальность: str = commands.Param(name="сексуальность", description="Новая сексуальность", default=None),
    прозвище: str = commands.Param(name="прозвище", description="Новое прозвище", default=None),
    организация: str = commands.Param(name="организация", description="Новая организация", default=None),
    должность: str = commands.Param(name="должность", description="Новая должность", default=None),
    # Статистики (числовые)
    количество_секса: int = commands.Param(name="секс", description="Количество секса", ge=0, default=None),
    чувствительность: int = commands.Param(name="чувствительность", description="Чувствительность", ge=0, default=None),
    сила_феромон: int = commands.Param(name="феромоны", description="Сила феромонов", ge=0, default=None),
    стойкость: int = commands.Param(name="стойкость", description="Стойкость", ge=0, default=None),
    умственное_развитие: int = commands.Param(name="интеллект", description="Умственное развитие", ge=0, default=None),
    # Дополнительные поля (БЕЗ ДЬЯВОЛЬСКОГО ФРУКТА)
    покровительство: str = commands.Param(name="покровительство", description="Покровительство", default=None),
    вагинальный: str = commands.Param(name="вагинальный", description="Вагинальный опыт", default=None),
    анальный: str = commands.Param(name="анальный", description="Анальный опыт", default=None),
    минет: str = commands.Param(name="минет", description="Минет", default=None),
    куни: str = commands.Param(name="куни", description="Куни", default=None),
    боевые_искусства: str = commands.Param(name="боевые_искусства", description="Боевые искусства", default=None),
    бюджет: int = commands.Param(name="бюджет", description="Бюджет", ge=0, default=None),
    дополнительное: str = commands.Param(name="доп_инфо", description="Дополнительная информация", default=None),
    # Кастомная аватарка
    аватарка: str = commands.Param(
        name="аватарка", 
        description="URL кастомной аватарки (http/https) или 'удалить'", 
        default=None
    )
):
    """Редактировать несколько характеристик персонажа одновременно (требуется особая роль)"""
    
    await inter.response.defer()
    
    # ========== ПРОВЕРКА РОЛЕЙ ==========
    has_required_role = False
    
    # Проверяем стандартные права администратора
    if inter.author.guild_permissions.administrator:
        has_required_role = True
    
    # ========== ПОИСК ПЕРСОНАЖА ==========
    data = load_characters()
    
    char_index = -1
    character = None
    
    for i, char in enumerate(data["characters"]):
        if char["id"] == char_id and char["guild_id"] == inter.guild.id:
            character = char
            char_index = i
            break
    
    if not character:
        embed = disnake.Embed(
            title="❌ Персонаж не найден",
            description=f"Персонаж с ID `{char_id}` не найден.",
            color=disnake.Color.red()
        )
        await inter.edit_original_message(embed=embed)
        return
    
    # ========== ОБРАБОТКА ИЗМЕНЕНИЙ ==========
    changes = {}
    
    # Основные поля
    if имя is not None:
        character["name"] = имя
        changes["Имя"] = имя
    
    if возраст is not None:
        if возраст.strip():
            try:
                character["age"] = int(возраст)
                changes["Возраст"] = возраст
            except ValueError:
                character["age"] = возраст
                changes["Возраст"] = возраст
        else:
            character["age"] = "[ ]"
            changes["Возраст"] = "[ ]"
    
    if гендер is not None:
        character["gender"] = гендер
        changes["Гендер"] = гендер
    
    if сексуальность is not None:
        character["sexuality"] = сексуальность
        changes["Сексуальность"] = сексуальность
    
    if прозвище is not None:
        character["nickname"] = прозвище
        changes["Прозвище"] = прозвище
    
    if организация is not None:
        character["organization"] = организация
        changes["Организация"] = организация
    
    if должность is not None:
        character["position"] = должность
        changes["Должность"] = должность
    
    # Статистики
    if "stats" not in character:
        character["stats"] = {}
    
    if количество_секса is not None:
        character["stats"]["sex_count"] = количество_секса
        changes["Количество секса"] = количество_секса
    
    if чувствительность is not None:
        character["stats"]["sensitivity"] = чувствительность
        changes["Чувствительность"] = чувствительность
    
    if сила_феромон is not None:
        character["stats"]["pheromone_power"] = сила_феромон
        changes["Сила феромон"] = сила_феромон
    
    if стойкость is not None:
        character["stats"]["endurance"] = стойкость
        changes["Стойкость"] = стойкость
    
    if умственное_развитие is not None:
        character["stats"]["intelligence"] = умственное_развитие
        changes["Умственное развитие"] = умственное_развитие
    
    # Дополнительные поля (БЕЗ ДЬЯВОЛЬСКОГО ФРУКТА)
    if "additional" not in character:
        character["additional"] = {}
    
    # Удаляем дьявольский фрукт из данных, если он есть
    if "devil_fruit" in character["additional"]:
        del character["additional"]["devil_fruit"]
    
    if покровительство is not None:
        character["additional"]["patronage"] = покровительство
        changes["Покровительство"] = покровительство
    
    if вагинальный is not None:
        character["additional"]["vaginal"] = вагинальный
        changes["Вагинальный"] = вагинальный
    
    if анальный is not None:
        character["additional"]["anal"] = анальный
        changes["Анальный"] = анальный
    
    if минет is not None:
        character["additional"]["blowjob"] = минет
        changes["Минет"] = минет
    
    if куни is not None:
        character["additional"]["cuni"] = куни
        changes["Куни"] = куни
    
    if боевые_искусства is not None:
        character["additional"]["martial_arts"] = боевые_искусства
        changes["Боевые искусства"] = боевые_искусства
    
    if бюджет is not None:
        character["additional"]["budget"] = бюджет
        changes["Бюджет"] = бюджет
    
    if дополнительное is not None:
        character["additional"]["extra"] = дополнительное
        changes["Дополнительное"] = дополнительное
    
    # Кастомная аватарка
    if аватарка is not None:
        if аватарка.strip().lower() in ["удалить", "remove", "clear", "очистить", ""]:
            # Удаляем аватарку
            if "custom_avatar" in character:
                del character["custom_avatar"]
                changes["Аватарка"] = "🗑️ Удалена"
        elif аватарка.startswith(('http://', 'https://')):
            # Сохраняем аватарку
            character["custom_avatar"] = аватарка
            changes["Аватарка"] = "✅ Обновлена"
        else:
            embed = disnake.Embed(
                title="❌ Неверный URL",
                description="URL аватарки должен начинаться с http:// или https://\nИли напишите 'удалить' чтобы убрать аватарку.",
                color=disnake.Color.red()
            )
            await inter.edit_original_message(embed=embed)
            return
    
    # ========== СОХРАНЕНИЕ ИЗМЕНЕНИЙ ==========
    if not changes:
        embed = disnake.Embed(
            title="ℹ️ Ничего не изменено",
            description="Вы не указали ни одного поля для изменения.",
            color=disnake.Color.blue()
        )
        await inter.edit_original_message(embed=embed)
        return
    
    # Сохраняем изменения
    data["characters"][char_index] = character
    save_characters(data)
    
    # ========== СОЗДАНИЕ ОТЧЕТА ==========
    owner_user = inter.guild.get_member(character["owner_id"])
    owner_name = owner_user.mention if owner_user else f"ID: {character['owner_id']}"
    
    embed = disnake.Embed(
        title="✅ Персонаж отредактирован",
        description=f"**{character.get('name', 'Без имени')}** (ID: `{char_id}`)\nВладелец: {owner_name}",
        color=disnake.Color.green(),
        timestamp=datetime.utcnow()
    )
    
    # Группируем изменения по категориям
    basic_changes = []
    stats_changes = []
    additional_changes = []
    avatar_changes = []
    
    for field, value in changes.items():
        if field in ["Имя", "Возраст", "Гендер", "Сексуальность", "Прозвище", "Организация", "Должность"]:
            basic_changes.append((field, value))
        elif field in ["Количество секса", "Чувствительность", "Сила феромон", "Стойкость", "Умственное развитие"]:
            stats_changes.append((field, value))
        elif field == "Аватарка":
            avatar_changes.append((field, value))
        else:
            additional_changes.append((field, value))
    
    # Добавляем изменения в embed
    if basic_changes:
        basic_text = "\n".join([f"**{field}:** `{value}`" for field, value in basic_changes])
        embed.add_field(name="📝 Основное", value=basic_text, inline=False)
    
    if stats_changes:
        stats_text = "\n".join([f"**{field}:** `{value}`" for field, value in stats_changes])
        embed.add_field(name="📊 Статистики", value=stats_text, inline=False)
    
    if additional_changes:
        additional_text = "\n".join([f"**{field}:** `{value}`" for field, value in additional_changes])
        embed.add_field(name="🎭 Дополнительное", value=additional_text, inline=False)
    
    if avatar_changes:
        for field, value in avatar_changes:
            if value == "✅ Обновлена":
                # Показываем предпросмотр аватарки
                embed.set_thumbnail(url=character.get("custom_avatar"))
                embed.add_field(name="🖼️ Аватарка", value="✅ Установлена новая аватарка", inline=False)
            else:
                embed.add_field(name="🖼️ Аватарка", value="🗑️ Аватарка удалена", inline=False)
    
    await inter.edit_original_message(embed=embed)

# Команда для удаления персонажа
@bot.slash_command(
    name="deletechar",
    description="Удалить персонажа",
    default_member_permissions=disnake.Permissions(manage_roles=True)
)
async def deletechar(
    inter: disnake.ApplicationCommandInteraction,
    char_id: int = commands.Param(name="id", description="ID персонажа для удаления", ge=0)
):
    """Удалить персонажа"""
    
    await inter.response.defer()
    
    data = load_characters()
    
    # Ищем персонажа
    character_to_delete = None
    index_to_delete = -1
    
    for i, char in enumerate(data["characters"]):
        if char["id"] == char_id and char["guild_id"] == inter.guild.id:
            character_to_delete = char
            index_to_delete = i
            break
    
    if character_to_delete is None:
        embed = disnake.Embed(
            title="❌ Персонаж не найден",
            description=f"Персонаж с ID `{char_id}` не найден.",
            color=disnake.Color.red()
        )
        await inter.edit_original_message(embed=embed)
        return
    
    # Проверяем права (владелец или админ)
    is_owner = inter.author.id == character_to_delete["owner_id"]
    has_perms = inter.author.guild_permissions.manage_roles
    
    if not (is_owner or has_perms):
        embed = disnake.Embed(
            title="❌ Доступ запрещен",
            description="Вы не можете удалить этого персонажа!",
            color=disnake.Color.red()
        )
        await inter.edit_original_message(embed=embed)
        return
    
    # Удаляем персонажа
    data["characters"].pop(index_to_delete)
    save_characters(data)
    
    embed = disnake.Embed(
        title="🗑️ Персонаж удален",
        description=f"Персонаж **{character_to_delete['name']}** (ID: `{character_to_delete['id']}`) был удален.",
        color=disnake.Color.orange()
    )
    await inter.edit_original_message(embed=embed)

@bot.slash_command(
    name="top",
    description="Топ персонажей по сумме характеристик"
)
async def top(
    inter: disnake.ApplicationCommandInteraction,
    количество: int = commands.Param(
        name="лимит", 
        description="Сколько персонажей показать", 
        ge=1, 
        le=20, 
        default=10
    )
):
    """Показать топ персонажей по общей сумме характеристик"""
    
    await inter.response.defer()
    
    data = load_characters()
    
    # Фильтруем персонажей только с текущего сервера
    server_characters = [char for char in data["characters"] if char["guild_id"] == inter.guild.id]
    
    if not server_characters:
        embed = disnake.Embed(
            title="🏆 Топ персонажей",
            description="На этом сервере еще нет персонажей.",
            color=disnake.Color.orange()
        )
        await inter.edit_original_message(embed=embed)
        return
    
    # Считаем общую сумму характеристик для каждого персонажа
    ranked_characters = []
    
    for char in server_characters:
        stats = char.get("stats", {})
        
        # Сумма всех характеристик
        total = (
            stats.get("sex_count", 0) +
            stats.get("sensitivity", 0) +
            stats.get("pheromone_power", 0) +
            stats.get("endurance", 0) +
            stats.get("intelligence", 0)
        )
        
        # Получаем владельца
        owner = inter.guild.get_member(char["owner_id"])
        
        ranked_characters.append({
            "id": char["id"],
            "name": char.get("name", "Без имени"),
            "owner": owner,
            "total": total,
            "stats": stats
        })
    
    # Сортируем по убыванию общей суммы
    ranked_characters.sort(key=lambda x: x["total"], reverse=True)
    
    # Ограничиваем количество
    ranked_characters = ranked_characters[:количество]
    
    # Создаем Embed
    embed = disnake.Embed(
        title="🏆 Топ персонажей",
        description=f"Рейтинг по **общей сумме характеристик**",
        color=disnake.Color.gold(),
        timestamp=datetime.utcnow()
    )
    
    # Добавляем поля для каждого персонажа в топе
    for i, char in enumerate(ranked_characters, 1):
        # Эмодзи для мест
        if i == 1:
            medal = "🥇"
            medal_name = "Первое место"
        elif i == 2:
            medal = "🥈"
            medal_name = "Второе место"
        elif i == 3:
            medal = "🥉"
            medal_name = "Третье место"
        elif i <= 10:
            medal = f"**{i}.**"
            medal_name = f"{i} место"
        else:
            medal = f"{i}."
            medal_name = f"{i} место"
        
        # Форматируем информацию
        owner_mention = char["owner"].mention if char["owner"] else f"`{char.get('owner_name', 'Неизвестно')}`"
        
        field_value = (
            f"{medal_name}\n"
            f"👤 **{char['name']}** (ID: `{char['id']}`)\n"
            f"👑 Владелец: {owner_mention}\n"
            f"📊 **Общая сумма:** `{char['total']}`"
        )
        
        embed.add_field(
            name=f"{medal} {char['name']}",
            value=field_value,
            inline=False
        )
    
    # Общая статистика сервера
    total_chars = len(server_characters)
    all_totals = [char["total"] for char in ranked_characters]
    avg_stats = sum(all_totals) / len(all_totals) if all_totals else 0
    max_stats = max(all_totals) if all_totals else 0
    
    embed.set_footer(
        text=f"Всего персонажей: {total_chars} • Максимум: {max_stats} • Среднее: {avg_stats:.1f}"
    )
    
    # Добавляем трофей в thumbnail для первого места
    if ranked_characters and ranked_characters[0]["owner"] and ranked_characters[0]["owner"].avatar:
        embed.set_thumbnail(url=ranked_characters[0]["owner"].avatar.url)
    
    await inter.edit_original_message(embed=embed)

# Команда для быстрого просмотра своего места в топе
@bot.slash_command(
    name="mytop",
    description="Узнать свое место в топе"
)
async def mytop(inter: disnake.ApplicationCommandInteraction):
    """Показать позицию пользователя в общем топе"""
    
    await inter.response.defer()
    
    data = load_characters()
    
    # Фильтруем персонажей только с текущего сервера
    server_characters = [char for char in data["characters"] if char["guild_id"] == inter.guild.id]
    
    if not server_characters:
        embed = disnake.Embed(
            title="🏆 Мое место в топе",
            description="На этом сервере еще нет персонажей.",
            color=disnake.Color.orange()
        )
        await inter.edit_original_message(embed=embed)
        return
    
    # Считаем общую сумму для каждого персонажа и сортируем
    ranked_characters = []
    
    for char in server_characters:
        stats = char.get("stats", {})
        
        total = (
            stats.get("sex_count", 0) +
            stats.get("sensitivity", 0) +
            stats.get("pheromone_power", 0) +
            stats.get("endurance", 0) +
            stats.get("intelligence", 0)
        )
        
        ranked_characters.append({
            "id": char["id"],
            "name": char.get("name", "Без имени"),
            "owner_id": char["owner_id"],
            "total": total
        })
    
    # Сортируем по убыванию
    ranked_characters.sort(key=lambda x: x["total"], reverse=True)
    
    # Находим персонажей пользователя
    user_characters = [char for char in ranked_characters if char["owner_id"] == inter.author.id]
    
    if not user_characters:
        embed = disnake.Embed(
            title="🏆 Мое место в топе",
            description="У вас нет персонажей на этом сервере.",
            color=disnake.Color.orange()
        )
        await inter.edit_original_message(embed=embed)
        return
    
    # Находим позиции всех персонажей пользователя
    user_positions = []
    
    for user_char in user_characters:
        position = None
        for i, char in enumerate(ranked_characters, 1):
            if char["id"] == user_char["id"]:
                position = i
                break
        
        if position:
            user_positions.append({
                "name": user_char["name"],
                "id": user_char["id"],
                "total": user_char["total"],
                "position": position
            })
    
    # Сортируем по позиции
    user_positions.sort(key=lambda x: x["position"])
    
    # Создаем Embed
    embed = disnake.Embed(
        title=f"🏆 Место в топе: {inter.author}",
        color=disnake.Color.blue(),
        timestamp=datetime.utcnow()
    )
    
    # Добавляем лучшего персонажа пользователя
    best_char = user_positions[0]
    
    # Определяем медаль для позиции
    if best_char["position"] == 1:
        medal = "🥇"
    elif best_char["position"] == 2:
        medal = "🥈"
    elif best_char["position"] == 3:
        medal = "🥉"
    else:
        medal = "📊"
    
    embed.add_field(
        name=f"{medal} Лучший персонаж",
        value=(
            f"**{best_char['name']}** (ID: `{best_char['id']}`)\n"
            f"🏆 **Позиция:** `{best_char['position']}` из `{len(ranked_characters)}`\n"
            f"📊 **Сумма характеристик:** `{best_char['total']}`"
        ),
        inline=False
    )
    
    # Если у пользователя несколько персонажей
    if len(user_positions) > 1:
        other_chars = ""
        for char in user_positions[1:4]:  # Показываем до 3 дополнительных
            other_chars += f"• **{char['name']}** - `{char['position']}` место (`{char['total']}`)\n"
        
        if other_chars:
            embed.add_field(
                name="📋 Другие ваши персонажи",
                value=other_chars,
                inline=False
            )
    
    # Показываем ближайших конкурентов
    if best_char["position"] > 1:
        # Персонаж выше
        above_char = ranked_characters[best_char["position"] - 2] if best_char["position"] > 1 else None
        # Персонаж ниже
        below_char = ranked_characters[best_char["position"]] if best_char["position"] < len(ranked_characters) else None
        
        competitors = ""
        
        if above_char:
            diff = above_char["total"] - best_char["total"]
            competitors += f"⬆️ **Выше:** {above_char.get('name', 'Неизвестно')} (+{diff})\n"
        
        if below_char:
            diff = best_char["total"] - below_char["total"]
            competitors += f"⬇️ **Ниже:** {below_char.get('name', 'Неизвестно')} (+{diff})"
        
        if competitors:
            embed.add_field(
                name="🎯 Ближайшие конкуренты",
                value=competitors,
                inline=False
            )
    
    # Общая статистика
    user_total_chars = len(user_characters)
    user_total_stats = sum([char["total"] for char in user_characters])
    user_avg_stats = user_total_stats / user_total_chars if user_total_chars > 0 else 0
    
    embed.add_field(
        name="📈 Ваша статистика",
        value=(
            f"**Персонажей:** `{user_total_chars}`\n"
            f"**Общая сумма:** `{user_total_stats}`\n"
            f"**Средний показатель:** `{user_avg_stats:.1f}`"
        ),
        inline=True
    )
    
    embed.set_footer(text=f"Всего участников в топе: {len(ranked_characters)}")
    
    # Добавляем аватар пользователя
    if inter.author.avatar:
        embed.set_thumbnail(url=inter.author.avatar.url)
    
    await inter.edit_original_message(embed=embed)
# Дополнительная команда для детальной статистики
@bot.slash_command(
    name="stats",
    description="Детальная статистика по персонажам"
)
async def stats(inter: disnake.ApplicationCommandInteraction):
    """Показать детальную статистику по всем персонажам"""
    
    await inter.response.defer()
    
    data = load_characters()
    
    # Фильтруем персонажей только с текущего сервера
    server_characters = [char for char in data["characters"] if char["guild_id"] == inter.guild.id]
    
    if not server_characters:
        embed = disnake.Embed(
            title="📈 Статистика",
            description="На этом сервере еще нет персонажей.",
            color=disnake.Color.orange()
        )
        await inter.edit_original_message(embed=embed)
        return
    
    # Собираем статистику
    total_stats = {
        "sex": 0,
        "sens": 0,
        "pheromone": 0,
        "endurance": 0,
        "intelligence": 0,
        "total": 0
    }
    
    max_stats = {
        "sex": {"value": 0, "name": "", "id": 0},
        "sens": {"value": 0, "name": "", "id": 0},
        "pheromone": {"value": 0, "name": "", "id": 0},
        "endurance": {"value": 0, "name": "", "id": 0},
        "intelligence": {"value": 0, "name": "", "id": 0},
        "total": {"value": 0, "name": "", "id": 0}
    }
    
    for char in server_characters:
        stats = char.get("stats", {})
        
        char_stats = {
            "sex": stats.get("sex_count", 0),
            "sens": stats.get("sensitivity", 0),
            "pheromone": stats.get("pheromone_power", 0),
            "endurance": stats.get("endurance", 0),
            "intelligence": stats.get("intelligence", 0)
        }
        
        char_total = sum(char_stats.values())
        
        # Суммируем общую статистику
        for key in total_stats:
            if key in char_stats:
                total_stats[key] += char_stats[key]
        total_stats["total"] += char_total
        
        # Проверяем максимальные значения
        for key, value in char_stats.items():
            if value > max_stats[key]["value"]:
                max_stats[key] = {"value": value, "name": char.get("name", "Без имени"), "id": char["id"]}
        
        if char_total > max_stats["total"]["value"]:
            max_stats["total"] = {"value": char_total, "name": char.get("name", "Без имени"), "id": char["id"]}
    
    # Создаем Embed
    embed = disnake.Embed(
        title="📊 Детальная статистика",
        description=f"Анализ **{len(server_characters)}** персонажей",
        color=disnake.Color.purple(),
        timestamp=datetime.utcnow()
    )
    
    # Общая статистика
    avg_total = total_stats["total"] / len(server_characters) if server_characters else 0
    
    embed.add_field(
        name="📈 Общие показатели",
        value=(
            f"**Всего персонажей:** `{len(server_characters)}`\n"
            f"**Общая сумма статов:** `{total_stats['total']}`\n"
            f"**Средний показатель:** `{avg_total:.1f}`\n"
            f"**Макс. сумма статов:** `{max_stats['total']['value']}`"
        ),
        inline=False
    )
    
    # Статистика по характеристикам
    stats_text = ""
    stat_icons = {
        "sex": "🔞 Количество секса",
        "sens": "💓 Чувствительность",
        "pheromone": "🌸 Сила феромонов",
        "endurance": "🛡️ Стойкость",
        "intelligence": "🧠 Умственное развитие"
    }
    
    for key, icon_name in stat_icons.items():
        avg = total_stats[key] / len(server_characters) if server_characters else 0
        stats_text += (
            f"{icon_name}:\n"
            f"  • Всего: `{total_stats[key]}`\n"
            f"  • Среднее: `{avg:.1f}`\n"
            f"  • Максимум: `{max_stats[key]['value']}` "
            f"(**{max_stats[key]['name']}**)\n"
        )
    
    embed.add_field(
        name="📊 По характеристикам",
        value=stats_text,
        inline=False
    )
    
    # Лидеры по каждой характеристике
    leaders_text = ""
    for key, icon_name in stat_icons.items():
        if max_stats[key]["value"] > 0:
            leaders_text += f"**{icon_name.split(' ')[1]}:** "
            leaders_text += f"**{max_stats[key]['name']}** (`{max_stats[key]['value']}`)\n"
    
    if leaders_text:
        embed.add_field(
            name="👑 Лидеры по характеристикам",
            value=leaders_text,
            inline=False
        )
    
    embed.set_footer(text=f"Статистика обновлена")
    
    await inter.edit_original_message(embed=embed)

# Команда для сравнения двух персонажей
@bot.slash_command(
    name="compare",
    description="Сравнить двух персонажей"
)
async def compare(
    inter: disnake.ApplicationCommandInteraction,
    id1: int = commands.Param(name="первый", description="ID первого персонажа", ge=0),
    id2: int = commands.Param(name="второй", description="ID второго персонажа", ge=0)
):
    """Сравнить характеристики двух персонажей"""
    
    await inter.response.defer()
    
    data = load_characters()
    
    # Находим персонажей
    char1 = None
    char2 = None
    
    for char in data["characters"]:
        if char["id"] == id1 and char["guild_id"] == inter.guild.id:
            char1 = char
        if char["id"] == id2 and char["guild_id"] == inter.guild.id:
            char2 = char
    
    if not char1:
        await inter.edit_original_message(content=f"❌ Персонаж с ID `{id1}` не найден!")
        return
    
    if not char2:
        await inter.edit_original_message(content=f"❌ Персонаж с ID `{id2}` не найден!")
        return
    
    # Получаем статистику
    stats1 = char1.get("stats", {})
    stats2 = char2.get("stats", {})
    
    # Считаем общую сумму
    total1 = (
        stats1.get("sex_count", 0) +
        stats1.get("sensitivity", 0) +
        stats1.get("pheromone_power", 0) +
        stats1.get("endurance", 0) +
        stats1.get("intelligence", 0)
    )
    
    total2 = (
        stats2.get("sex_count", 0) +
        stats2.get("sensitivity", 0) +
        stats2.get("pheromone_power", 0) +
        stats2.get("endurance", 0) +
        stats2.get("intelligence", 0)
    )
    
    # Определяем победителя
    if total1 > total2:
        winner = char1.get("name", "Без имени")
        diff = total1 - total2
        result = f"🏆 **{winner}** выигрывает на `{diff}` очков!"
    elif total2 > total1:
        winner = char2.get("name", "Без имени")
        diff = total2 - total1
        result = f"🏆 **{winner}** выигрывает на `{diff}` очков!"
    else:
        result = "⚖️ **Ничья!** Оба персонажа имеют одинаковую сумму характеристик."
    
    # Создаем сравнение
    embed = disnake.Embed(
        title="⚔️ Сравнение персонажей",
        description=result,
        color=disnake.Color.blue(),
        timestamp=datetime.utcnow()
    )
    
    # Получаем владельцев
    owner1 = inter.guild.get_member(char1["owner_id"])
    owner2 = inter.guild.get_member(char2["owner_id"])
    
    embed.add_field(
        name=f"👤 {char1.get('name', 'Без имени')}",
        value=(
            f"ID: `{char1['id']}`\n"
            f"Владелец: {owner1.mention if owner1 else 'Не найден'}\n"
            f"**Общая сумма:** `{total1}`"
        ),
        inline=True
    )
    
    embed.add_field(
        name="🆚",
        value="\n".join(["🔞", "💓", "🌸", "🛡️", "🧠", "**∑**"]),
        inline=True
    )
    
    embed.add_field(
        name=f"👤 {char2.get('name', 'Без имени')}",
        value=(
            f"ID: `{char2['id']}`\n"
            f"Владелец: {owner2.mention if owner2 else 'Не найден'}\n"
            f"**Общая сумма:** `{total2}`"
        ),
        inline=True
    )
    
    # Подробное сравнение характеристик
    comparison_text = ""
    
    characteristics = [
        ("🔞 Количество секса", "sex_count"),
        ("💓 Чувствительность", "sensitivity"),
        ("🌸 Сила феромонов", "pheromone_power"),
        ("🛡️ Стойкость", "endurance"),
        ("🧠 Умственное развитие", "intelligence")
    ]
    
    for name, key in characteristics:
        val1 = stats1.get(key, 0)
        val2 = stats2.get(key, 0)
        
        if val1 > val2:
            comparison_text += f"{name}: `{val1}` **>** `{val2}`\n"
        elif val2 > val1:
            comparison_text += f"{name}: `{val1}` **<** `{val2}`\n"
        else:
            comparison_text += f"{name}: `{val1}` **=** `{val2}`\n"
    
    embed.add_field(
        name="📊 Подробное сравнение",
        value=comparison_text,
        inline=False
    )
    
    # Процентное соотношение
    if total1 + total2 > 0:
        percent1 = (total1 / (total1 + total2)) * 100
        percent2 = (total2 / (total1 + total2)) * 100
        
        # Создаем прогресс-бар
        bar_length = 20
        filled1 = int(bar_length * (percent1 / 100))
        filled2 = bar_length - filled1
        
        progress_bar = "█" * filled1 + "░" * filled2
        
        embed.add_field(
            name="📈 Соотношение сил",
            value=(
                f"```\n"
                f"{char1.get('name', 'П1')[:10]:<10} {'▏'}{progress_bar}{'▕'} {char2.get('name', 'П2')[:10]}\n"
                f"{percent1:6.1f}% {' ' * (bar_length-10)} {percent2:6.1f}%\n"
                f"```"
            ),
            inline=False
        )
    
    embed.set_footer(text=f"Запросил: {inter.author}")
    
    await inter.edit_original_message(embed=embed)

# Конфигурация ролей для изменения цвета
# Определяем ID разрешенной роли ПЕРЕД командой
ALLOWED_ROLE_ID = 1457795541680394303  # ID роли для доступа к команде setcolor

@bot.slash_command(
    name="setcolor",
    description="Изменить цвет embed сообщения персонажа",
    default_member_permissions=disnake.Permissions(view_audit_log=True)
)
async def setcolor(
    inter: disnake.ApplicationCommandInteraction,
    char_id: int = commands.Param(name="id", description="ID персонажа", ge=0),
    цвет: str = commands.Param(
        name="цвет", 
        description="HEX код цвета (например: #FF0000) или название цвета",
        choices=[
            "Красный", "Синий", "Зеленый", "Фиолетовый", "Оранжевый",
            "Золотой", "Розовый", "Бирюзовый", "Черный", "Белый",
            "Сбросить"
        ],
        default=None
    ),
    hex_код: str = commands.Param(
        name="hex_код", 
        description="Кастомный HEX код (например: #1ABC9C)", 
        default=None
    )
):
    """Изменить цвет embed сообщения персонажа (только для определенной роли)"""
    
    await inter.response.defer()
    
    # ========== ПРОВЕРКА ДОСТУПА ПО РОЛИ ==========
    has_access = False
    
    # Проверяем права администратора Discord (опционально)
    if inter.author.guild_permissions.administrator:
        has_access = True
    
    # Проверяем наличие конкретной роли по ID
    user_role_ids = [role.id for role in inter.author.roles]
    if ALLOWED_ROLE_ID in user_role_ids:
        has_access = True
    
    # Если у пользователя нет доступа
    if not has_access:
        # Получаем информацию о роли для сообщения
        role = inter.guild.get_role(ALLOWED_ROLE_ID)
        role_name = role.name if role else f"ID: {ALLOWED_ROLE_ID}"
        
        embed = disnake.Embed(
            title="⛔ Доступ запрещен",
            description=f"Для этой команды требуется роль **{role_name}**",
            color=disnake.Color.red()
        )
        await inter.edit_original_message(embed=embed)
        return
    
    # ========== ПОИСК ПЕРСОНАЖА ==========
    data = load_characters()
    
    char_index = -1
    character = None
    
    for i, char in enumerate(data["characters"]):
        if char["id"] == char_id and char["guild_id"] == inter.guild.id:
            character = char
            char_index = i
            break
    
    if not character:
        embed = disnake.Embed(
            title="❌ Персонаж не найден",
            description=f"Персонаж с ID `{char_id}` не найден.",
            color=disnake.Color.red()
        )
        await inter.edit_original_message(embed=embed)
        return
    
    # ========== ОБРАБОТКА ЦВЕТА ==========
    color_value = None
    
    # Если выбран "Сбросить"
    if цвет == "Сбросить":
        if "embed_color" in character:
            del character["embed_color"]
            color_value = "сброшен"
        else:
            embed = disnake.Embed(
                title="ℹ️ Цвет уже сброшен",
                description="У персонажа уже установлен цвет по умолчанию.",
                color=disnake.Color.blue()
            )
            await inter.edit_original_message(embed=embed)
            return
    
    # Если указан HEX код
    elif hex_код:
        hex_код = hex_код.strip().upper()
        
        # Проверяем формат HEX кода
        if hex_код.startswith("#"):
            hex_код = hex_код[1:]
        
        if len(hex_код) != 6:
            embed = disnake.Embed(
                title="❌ Неверный HEX код",
                description="HEX код должен содержать 6 символов (например: FF0000 или #FF0000)",
                color=disnake.Color.red()
            )
            await inter.edit_original_message(embed=embed)
            return
        
        # Проверяем, что это валидный HEX код
        try:
            color_value = int(hex_код, 16)
            # Проверяем, что число в пределах 0-FFFFFF
            if color_value < 0 or color_value > 0xFFFFFF:
                raise ValueError
        except ValueError:
            embed = disnake.Embed(
                title="❌ Неверный HEX код",
                description="Укажите правильный HEX код (например: FF0000 для красного)",
                color=disnake.Color.red()
            )
            await inter.edit_original_message(embed=embed)
            return
        
        character["embed_color"] = color_value
    
    # Если выбран цвет из списка
    elif цвет:
        color_map = {
            "Красный": 0xFF0000,
            "Синий": 0x0000FF,
            "Зеленый": 0x00FF00,
            "Фиолетовый": 0x800080,
            "Оранжевый": 0xFFA500,
            "Золотой": 0xFFD700,
            "Розовый": 0xFFC0CB,
            "Бирюзовый": 0x40E0D0,
            "Черный": 0x000000,
            "Белый": 0xFFFFFF
        }
        
        if цвет in color_map:
            color_value = color_map[цвет]
            character["embed_color"] = color_value
        else:
            embed = disnake.Embed(
                title="❌ Неизвестный цвет",
                description="Выберите цвет из списка или укажите HEX код.",
                color=disnake.Color.red()
            )
            await inter.edit_original_message(embed=embed)
            return
    else:
        embed = disnake.Embed(
            title="❌ Не указан цвет",
            description="Укажите цвет из списка или HEX код.",
            color=disnake.Color.red()
        )
        await inter.edit_original_message(embed=embed)
        return
    
    # ========== СОХРАНЕНИЕ ИЗМЕНЕНИЙ ==========
    data["characters"][char_index] = character
    save_characters(data)
    
    # ========== СОЗДАНИЕ ОТЧЕТА ==========
    if цвет == "Сбросить":
        color_display = "**стандартный цвет**"
        embed_color = disnake.Color.dark_purple()
    else:
        if hex_код:
            color_display = f"`#{hex(color_value)[2:].upper().zfill(6)}`"
        else:
            color_display = f"`{цвет}`"
        embed_color = disnake.Color(color_value)
    
    embed = disnake.Embed(
        title="🎨 Цвет изменен",
        description=f"**{character.get('name', 'Без имени')}** (ID: `{char_id}`)",
        color=embed_color,
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(
        name="Новый цвет",
        value=f"Установлен цвет: {color_display}",
        inline=False
    )
    
    # Показываем предпросмотр цвета
    if color_value != "сброшен":
        # Создаем маленький цветной квадрат в виде текста
        color_square = "`████`"
        embed.add_field(
            name="Предпросмотр",
            value=f"{color_square} Вот так будет выглядеть embed",
            inline=False
        )
    
    # Получаем владельца персонажа
    owner = inter.guild.get_member(character["owner_id"])
    if owner:
        embed.add_field(name="👤 Владелец", value=owner.mention, inline=True)
    
    # Добавляем информацию о том, кто изменил
    # Получаем информацию о роли пользователя
    user_role = inter.guild.get_role(ALLOWED_ROLE_ID)
    role_name = user_role.name if user_role else f"ID: {ALLOWED_ROLE_ID}"
    
    embed.set_footer(text=f"Изменил: {inter.author} • Роль: {role_name}")
    
    await inter.edit_original_message(embed=embed)

@bot.slash_command(
    name="resetallcolors",
    description="Сбросить цвета у всех персонажей (админ)",
    default_member_permissions=disnake.Permissions(administrator=True)
)
async def resetallcolors(inter: disnake.ApplicationCommandInteraction):
    """Сбросить все кастомные цвета персонажей"""
    
    await inter.response.defer()
    
    data = load_characters()
    
    reset_count = 0
    for char in data["characters"]:
        if "embed_color" in char:
            del char["embed_color"]
            reset_count += 1
    
    save_characters(data)
    
    embed = disnake.Embed(
        title="🔄 Сброс цветов",
        description=f"Сброшены цвета у **{reset_count}** персонажей",
        color=disnake.Color.orange()
    )
    
    if reset_count > 0:
        embed.add_field(
            name="Статистика",
            value=f"Всего персонажей: {len(data['characters'])}\nСброшено цветов: {reset_count}",
            inline=True
        )
    
    embed.set_footer(text=f"Выполнил: {inter.author}")
    
    await inter.edit_original_message(embed=embed)

@bot.slash_command(name="intents_test", description="Проверить intents бота")
async def intents_test(inter: disnake.ApplicationCommandInteraction):
    """Проверить, правильно ли настроены intents"""
    
    member_count = len(inter.guild.members)
    role_count = len(inter.guild.roles)
    
    embed = disnake.Embed(
        title="🔍 Проверка Intents",
        color=disnake.Color.blue()
    )
    
    embed.add_field(
        name="Статистика сервера",
        value=f"**Участников:** {member_count}\n**Ролей:** {role_count}",
        inline=False
    )
    
    embed.add_field(
        name="Ваши роли",
        value=", ".join([role.mention for role in inter.author.roles[:10]]),
        inline=False
    )
    
    if member_count < 10:
        embed.add_field(
            name="⚠️ Внимание",
            value="Кажется, intents.members не работает правильно!",
            inline=False
        )
    
    await inter.response.send_message(embed=embed)
@bot.slash_command(
    name="own-change",
    description="Изменить владельца персонажа (только для администраторов)",
    default_member_permissions=disnake.Permissions(administrator=True)  # Только админы Discord
)
async def own_change(
    inter: disnake.ApplicationCommandInteraction,
    char_id: int = commands.Param(name="id", description="ID персонажа", ge=0),
    новый_владелец: disnake.Member = commands.Param(name="владелец", description="Новый владелец персонажа")
):
    """Изменить владельца персонажа (требуются права администратора)"""
    
    await inter.response.defer()
    
    data = load_characters()
    
    # Ищем персонажа
    char_index = -1
    character = None
    
    for i, char in enumerate(data["characters"]):
        if char["id"] == char_id and char["guild_id"] == inter.guild.id:
            character = char
            char_index = i
            break
    
    if not character:
        embed = disnake.Embed(
            title="❌ Персонаж не найден",
            description=f"Персонаж с ID `{char_id}` не найден.",
            color=disnake.Color.red()
        )
        await inter.edit_original_message(embed=embed)
        return
    
    # Получаем старого владельца
    старый_владелец = inter.guild.get_member(character["owner_id"])
    старое_имя = character["owner_name"]
    
    # Сохраняем старые данные для отчета
    old_owner_info = f"{старый_владелец.mention if старый_владелец else 'Не найден'}\n`{старое_имя}`"
    
    # Обновляем владельца
    character["owner_id"] = новый_владелец.id
    character["owner_name"] = str(новый_владелец)
    
    # Обновляем в базе данных
    data["characters"][char_index] = character
    save_characters(data)
    
    # Создаем отчет
    embed = disnake.Embed(
        title="🔄 Владелец персонажа изменен",
        description=f"**{character.get('name', 'Без имени')}** (ID: `{char_id}`)",
        color=disnake.Color.green(),
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(
        name="👤 Бывший владелец",
        value=old_owner_info,
        inline=True
    )
    
    embed.add_field(
        name="➡️",
        value="🔀",
        inline=True
    )
    
    embed.add_field(
        name="👤 Новый владелец",
        value=f"{новый_владелец.mention}\n`{новый_владелец}`",
        inline=True
    )
    
    # Добавляем информацию о персонаже
    stats = character.get('stats', {})
    total_stats = sum(stats.values()) if stats else 0
    
    # Добавляем информацию о редакторе
    embed.add_field(
        name="👑 Изменил",
        value=f"{inter.author.mention}\n`{inter.author}`",
        inline=True
    )
    
    # Дата создания персонажа
    try:
        created_at = datetime.fromisoformat(character["created_at"])
        embed.add_field(
            name="📅 Дата создания персонажа",
            value=f"<t:{int(created_at.timestamp())}:D>",
            inline=True
        )
    except:
        pass
    
    embed.set_footer(text=f"ID персонажа: {char_id}")
    
    await inter.edit_original_message(embed=embed)

# Дополнительная команда для передачи ВСЕХ персонажей пользователя
@bot.slash_command(
    name="own-transfer-all",
    description="Передать все персонажи пользователя другому (только для администраторов)",
    default_member_permissions=disnake.Permissions(administrator=True)
)
async def own_transfer_all(
    inter: disnake.ApplicationCommandInteraction,
    старый_владелец: disnake.Member = commands.Param(name="старый_владелец", description="Текущий владелец"),
    новый_владелец: disnake.Member = commands.Param(name="новый_владелец", description="Новый владелец")
):
    """Передать ВСЕХ персонажей одного пользователя другому"""
    
    await inter.response.defer()
    
    data = load_characters()
    
    # Ищем всех персонажей старого владельца на этом сервере
    transferred_chars = []
    
    for i, char in enumerate(data["characters"]):
        if char["owner_id"] == старый_владелец.id and char["guild_id"] == inter.guild.id:
            # Сохраняем информацию о персонаже
            transferred_chars.append({
                "id": char["id"],
                "name": char.get("name", "Без имени"),
                "old_owner": char["owner_name"]
            })
            
            # Меняем владельца
            char["owner_id"] = новый_владелец.id
            char["owner_name"] = str(новый_владелец)
            
            # Обновляем в массиве
            data["characters"][i] = char
    
    if not transferred_chars:
        embed = disnake.Embed(
            title="❌ Персонажи не найдены",
            description=f"У {старый_владелец.mention} нет персонажей на этом сервере.",
            color=disnake.Color.red()
        )
        await inter.edit_original_message(embed=embed)
        return
    
    # Сохраняем изменения
    save_characters(data)
    
    # Создаем отчет
    embed = disnake.Embed(
        title="🔄 Массовая передача персонажей",
        color=disnake.Color.green(),
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(
        name="👤 От кого",
        value=f"{старый_владелец.mention}\n`{старый_владелец}`",
        inline=True
    )
    
    embed.add_field(
        name="➡️",
        value="🔀",
        inline=True
    )
    
    embed.add_field(
        name="👤 Кому",
        value=f"{новый_владелец.mention}\n`{новый_владелец}`",
        inline=True
    )
    
    # Список переданных персонажей (первые 10)
    chars_list = ""
    for char in transferred_chars[:10]:
        chars_list += f"• **{char['name']}** (ID: `{char['id']}`)\n"
    
    if len(transferred_chars) > 10:
        chars_list += f"• ... и еще {len(transferred_chars) - 10} персонажей"
    
    embed.add_field(
        name=f"📋 Переданные персонажи ({len(transferred_chars)})",
        value=chars_list,
        inline=False
    )
    
    # Статистика
    embed.add_field(
        name="📊 Статистика",
        value=(
            f"**Всего передано:** {len(transferred_chars)} персонажей\n"
            f"**Новый владелец:** {новый_владелец.mention}\n"
            f"**Изменил:** {inter.author.mention}"
        ),
        inline=False
    )
    
    embed.set_footer(text=f"Выполнил: {inter.author}")
    
    await inter.edit_original_message(embed=embed)


bot.run("TOKEN")




