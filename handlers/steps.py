from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.steps_service import (
    load_steps,
    get_step,
    get_user_step_progress,
    set_user_step_status,
    load_user_progress,
)
from services.steps_seed import seed_steps


STEP_EXTRA = {
    1: {
        "essence": "Суть шага — перестать доказывать, что я справляюсь сам(а), и честно увидеть факты бессилия и неуправляемости.",
        "defects": ["отрицание", "контроль", "гордыня", "самообман", "избегание"],
        "today": "Сегодня напиши 3 факта, которые показывают, что старый способ жить больше не работает.",
        "sponsor": "Что я всё ещё пытаюсь контролировать и почему мне страшно признать бессилие?"
    },
    2: {
        "essence": "Суть шага — допустить, что помощь возможна, даже если вера пока маленькая.",
        "defects": ["недоверие", "изоляция", "отчаяние", "гордыня"],
        "today": "Сегодня найди один пример, где помощь пришла не через твой контроль.",
        "sponsor": "Что для меня значит здравомыслие и где я его теряю?"
    },
    3: {
        "essence": "Суть шага — принять решение жить не только по своей воле, а сверяться с духовными принципами.",
        "defects": ["своеволие", "контроль", "страх", "упрямство"],
        "today": "Сегодня раздели проблему на две части: что зависит от меня и что не зависит.",
        "sponsor": "Где я говорю, что доверяю, но продолжаю контролировать?"
    },
    4: {
        "essence": "Суть шага — честно исследовать обиды, страхи, мотивы, дефекты и свою ответственность.",
        "defects": ["обида", "страх", "эгоизм", "корысть", "нечестность"],
        "today": "Сегодня заполни одну инвентаризацию: страх, обиду или ситуацию.",
        "sponsor": "Какой повторяющийся сценарий я вижу в своих реакциях?"
    },
    5: {
        "essence": "Суть шага — вынести правду из одиночества и признать её перед Богом, собой и другим человеком.",
        "defects": ["стыд", "страх оценки", "скрытность", "самообман"],
        "today": "Сегодня отметь одну тему, которую страшно проговорить честно.",
        "sponsor": "Что я больше всего боюсь рассказать и что пытаюсь скрыть?"
    },
    6: {
        "essence": "Суть шага — увидеть, что дефекты дают мне ложную выгоду, и стать готовым(ой) отпустить их.",
        "defects": ["гордыня", "контроль", "жалость к себе", "корысть", "страх"],
        "today": "Сегодня выбери один дефект и напиши: какую выгоду он мне даёт и какую цену я плачу.",
        "sponsor": "От какого дефекта я пока не хочу отказаться полностью?"
    },
    7: {
        "essence": "Суть шага — смиренно попросить помощи и начать действовать противоположно дефекту.",
        "defects": ["самонадеянность", "гордыня", "недоверие", "нетерпение"],
        "today": "Сегодня выбери один принцип вместо активного дефекта и сделай маленькое действие по нему.",
        "sponsor": "Где я прошу помощи, но не меняю действие?"
    },
    8: {
        "essence": "Суть шага — честно увидеть людей, которым я причинил(а) вред, и стать готовым(ой) исправлять.",
        "defects": ["избегание", "вина", "гордыня", "самооправдание"],
        "today": "Сегодня запиши одного человека, которому мог быть причинён вред, и какой именно вред.",
        "sponsor": "Где я путаю чувство вины с настоящей ответственностью?"
    },
    9: {
        "essence": "Суть шага — исправлять вред безопасно, честно и без ожидания награды.",
        "defects": ["страх", "гордыня", "желание одобрения", "избегание"],
        "today": "Сегодня выбери один пункт возмещения и обсуди безопасную форму действия.",
        "sponsor": "Что я хочу получить от возмещения ущерба?"
    },
    10: {
        "essence": "Суть шага — ежедневно замечать ошибки, быстро признавать их и возвращаться к принципам.",
        "defects": ["нечестность", "обида", "страх", "эгоизм", "корысть"],
        "today": "Сегодня пройди вечернюю инвентаризацию и выбери принцип на завтра.",
        "sponsor": "Какая ошибка сегодня повторилась и что я могу исправить быстро?"
    },
    11: {
        "essence": "Суть шага — развивать контакт с Богом / Высшей Силой через молитву, медитацию и слушание направления.",
        "defects": ["своеволие", "контроль", "нетерпение", "духовная лень"],
        "today": "Сегодня сделай 3 минуты тишины и задай вопрос: какое действие будет правильным?",
        "sponsor": "Где я ищу свою волю вместо направления?"
    },
    12: {
        "essence": "Суть шага — применять принципы во всех делах и быть полезным(ой) другим.",
        "defects": ["эгоизм", "желание признания", "контроль", "гордыня"],
        "today": "Сегодня сделай одно полезное действие без ожидания благодарности.",
        "sponsor": "Где моё служение превращается в желание управлять или получить признание?"
    },
}


def safe_html(text):
    if text is None:
        return "—"
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def list_to_text(items):
    if not items:
        return "—"
    return "\n".join(f"• {safe_html(item)}" for item in items)


def steps_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("1️⃣ Шаг 1", callback_data="steps:open:1"),
         InlineKeyboardButton("2️⃣ Шаг 2", callback_data="steps:open:2")],
        [InlineKeyboardButton("3️⃣ Шаг 3", callback_data="steps:open:3"),
         InlineKeyboardButton("4️⃣ Шаг 4", callback_data="steps:open:4")],
        [InlineKeyboardButton("5️⃣ Шаг 5", callback_data="steps:open:5"),
         InlineKeyboardButton("6️⃣ Шаг 6", callback_data="steps:open:6")],
        [InlineKeyboardButton("7️⃣ Шаг 7", callback_data="steps:open:7"),
         InlineKeyboardButton("8️⃣ Шаг 8", callback_data="steps:open:8")],
        [InlineKeyboardButton("9️⃣ Шаг 9", callback_data="steps:open:9"),
         InlineKeyboardButton("🔟 Шаг 10", callback_data="steps:open:10")],
        [InlineKeyboardButton("1️⃣1️⃣ Шаг 11", callback_data="steps:open:11"),
         InlineKeyboardButton("1️⃣2️⃣ Шаг 12", callback_data="steps:open:12")],
        [InlineKeyboardButton("🎯 Где я сейчас?", callback_data="steps:where"),
         InlineKeyboardButton("📈 Прогресс", callback_data="steps:progress")],
    ])


def step_keyboard(step_number):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🧭 Суть шага", callback_data=f"steps:section:{step_number}:essence")],
        [InlineKeyboardButton("📖 Описание", callback_data=f"steps:section:{step_number}:description")],
        [InlineKeyboardButton("🛠 Практика", callback_data=f"steps:section:{step_number}:practice"),
         InlineKeyboardButton("❓ Вопросы", callback_data=f"steps:section:{step_number}:questions")],
        [InlineKeyboardButton("🧩 Дефекты", callback_data=f"steps:section:{step_number}:defects"),
         InlineKeyboardButton("🌱 Принципы", callback_data=f"steps:section:{step_number}:principles")],
        [InlineKeyboardButton("🎯 Практика сегодня", callback_data=f"steps:section:{step_number}:today")],
        [InlineKeyboardButton("👥 Вопрос спонсору", callback_data=f"steps:section:{step_number}:sponsor")],
        [InlineKeyboardButton("🙏 Молитва", callback_data=f"steps:section:{step_number}:prayer"),
         InlineKeyboardButton("📚 Литература", callback_data=f"steps:section:{step_number}:literature")],
        [InlineKeyboardButton("▶️ В работе", callback_data=f"steps:status:{step_number}:in_progress"),
         InlineKeyboardButton("✅ Завершён", callback_data=f"steps:status:{step_number}:completed")],
        [InlineKeyboardButton("⬅️ К 12 шагам", callback_data="steps:menu")],
    ])


async def show_steps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 <b>12 Шагов</b>\n\nВыбери шаг для изучения или практики.",
        reply_markup=steps_main_keyboard(),
        parse_mode="HTML"
    )


def build_step_card(user_id, step_number):
    step = get_step(step_number)

    if not step:
        return "Этот шаг пока не загружен.\n\nНапиши /seed_steps.", steps_main_keyboard()

    progress = get_user_step_progress(user_id, step_number)
    status = progress.get("status") if progress else "not_started"

    status_text = {
        "not_started": "не начат",
        "in_progress": "в работе",
        "completed": "завершён",
    }.get(status, status)

    extra = STEP_EXTRA.get(step_number, {})

    text = (
        f"📖 <b>{safe_html(step.get('title'))}</b>\n\n"
        f"<b>Статус:</b> {safe_html(status_text)}\n\n"
        f"<b>Кратко:</b>\n{safe_html(step.get('short_description'))}\n\n"
        f"<b>Суть:</b>\n{safe_html(extra.get('essence'))}\n\n"
        f"<b>Связанные принципы:</b>\n{list_to_text(step.get('related_principles'))}"
    )

    return text, step_keyboard(step_number)


def build_step_section(step_number, section):
    step = get_step(step_number)
    extra = STEP_EXTRA.get(step_number, {})

    if not step:
        return "Шаг не найден.", steps_main_keyboard()

    if section == "essence":
        text = f"🧭 <b>Суть шага {step_number}</b>\n\n{safe_html(extra.get('essence'))}"

    elif section == "description":
        text = f"📖 <b>{safe_html(step.get('title'))}</b>\n\n{safe_html(step.get('full_description'))}"

    elif section == "practice":
        text = f"🛠 <b>Практика шага {step_number}</b>\n\n{list_to_text(step.get('practice'))}"

    elif section == "questions":
        text = f"❓ <b>Вопросы шага {step_number}</b>\n\n{list_to_text(step.get('questions'))}"

    elif section == "defects":
        text = f"🧩 <b>Дефекты, связанные с шагом {step_number}</b>\n\n{list_to_text(extra.get('defects'))}"

    elif section == "principles":
        text = f"🌱 <b>Принципы шага {step_number}</b>\n\n{list_to_text(step.get('related_principles'))}"

    elif section == "today":
        text = f"🎯 <b>Практика на сегодня</b>\n\n{safe_html(extra.get('today'))}"

    elif section == "sponsor":
        text = f"👥 <b>Вопрос для спонсора / наставника</b>\n\n{safe_html(extra.get('sponsor'))}"

    elif section == "prayer":
        text = f"🙏 <b>Молитва шага {step_number}</b>\n\n{safe_html(step.get('prayer'))}"

    elif section == "literature":
        text = (
            f"📚 <b>Литература для шага {step_number}</b>\n\n"
            f"{list_to_text(step.get('literature'))}\n\n"
            "Материал дан как ориентир для самостоятельного чтения и краткий пересказ своими словами."
        )

    else:
        text = "Раздел не найден."

    return text, step_keyboard(step_number)


def build_progress(user_id):
    steps = load_steps()
    progress = load_user_progress(user_id)

    progress_map = {item["step_number"]: item["status"] for item in progress}

    completed = 0
    in_progress = 0

    text = "📈 <b>Прогресс по 12 Шагам</b>\n\n"

    for step in steps:
        number = step["step_number"]
        status = progress_map.get(number, "not_started")

        if status == "completed":
            icon = "✅"
            completed += 1
        elif status == "in_progress":
            icon = "▶️"
            in_progress += 1
        else:
            icon = "▫️"

        text += f"{icon} Шаг {number}: {safe_html(step.get('title'))}\n"

    text += (
        f"\n<b>Итого:</b>\n"
        f"✅ Завершено: {completed}\n"
        f"▶️ В работе: {in_progress}\n"
        f"▫️ Не начато: {len(steps) - completed - in_progress}"
    )

    return text, InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ К 12 шагам", callback_data="steps:menu")]])


def build_where_now():
    text = (
        "🎯 <b>Где я сейчас?</b>\n\n"
        "• Отрицаю проблему — <b>Шаг 1</b>\n"
        "• Нет надежды — <b>Шаг 2</b>\n"
        "• Всё контролирую — <b>Шаг 3</b>\n"
        "• Много обид, страхов, дефектов — <b>Шаг 4</b>\n"
        "• Страшно рассказать правду — <b>Шаг 5</b>\n"
        "• Вижу дефекты, но держусь за них — <b>Шаг 6</b>\n"
        "• Нужна просьба об освобождении — <b>Шаг 7</b>\n"
        "• Есть причинённый вред — <b>Шаги 8–9</b>\n"
        "• Нужна ежедневная честность — <b>Шаг 10</b>\n"
        "• Нужен контакт с Богом / ВС — <b>Шаг 11</b>\n"
        "• Хочу быть полезным(ой) — <b>Шаг 12</b>"
    )

    return text, InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ К 12 шагам", callback_data="steps:menu")]])


async def handle_steps_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    parts = query.data.split(":")
    action = parts[1]

    if action == "menu":
        await query.edit_message_text(
            "📖 <b>12 Шагов</b>\n\nВыбери шаг для изучения или практики.",
            reply_markup=steps_main_keyboard(),
            parse_mode="HTML"
        )
        return

    if action == "open":
        step_number = int(parts[2])
        text, keyboard = build_step_card(user_id, step_number)
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")
        return

    if action == "section":
        step_number = int(parts[2])
        section = parts[3]
        text, keyboard = build_step_section(step_number, section)
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")
        return

    if action == "status":
        step_number = int(parts[2])
        status = parts[3]
        set_user_step_status(user_id, step_number, status)
        text, keyboard = build_step_card(user_id, step_number)
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")
        return

    if action == "progress":
        text, keyboard = build_progress(user_id)
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")
        return

    if action == "where":
        text, keyboard = build_where_now()
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")
        return


async def seed_steps_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = seed_steps()
    await update.message.reply_text(
        "✅ 12 Шагов загружены в облако.\n\n"
        f"Добавлено/обновлено: {count}"
    )
