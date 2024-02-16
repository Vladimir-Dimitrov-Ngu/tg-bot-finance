from io import BytesIO
import logging
from telegram import InputFile, Update, constants, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    CallbackQueryHandler,
)
import message_text
import re
import config
import aiosqlite
import sql_query
import matplotlib.pyplot as plt
from datetime import datetime
from keyboard_telegram import _get_keyboard
from connect_db import insert_into_db, get_details_from_db
from yandex_gpt import _get_response_yandex_gpt


CATEGORY_NAME = []
CATEGORY, PRODUCT_NAME = range(2)
AWAITING_NOTE = 1
ID = None

ALL_COST = []
ALL_CATEGORY = []
DETAILS = {}
MAIN_COST = None
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=message_text.START_MESSAGE
    )


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=message_text.HELP_MESSAGE
    )


async def form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text="Давай познакомися. Кто ты?",
        reply_markup=_get_keyboard(
            "Мужчина", "Женщина", "Мужчина", "Женщина", prefix="form"
        ),
    )
    return


async def note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=message_text.NOTE_MESSAGE
    )
    context.user_data["state"] = AWAITING_NOTE
    return


# выбирает категорию и мы ему выплевываем заметки
async def notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=message_text.NOTE_MESSAGE
    )
    return


async def form_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    id = update.effective_chat.id
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    answer = query.data.split("_")[1]
    DETAILS["id"] = id
    if answer == "Мужчина" or answer == "Женщина":
        DETAILS["sex"] = answer
        await query.edit_message_text(
            text="Сколько тебе лет?",
            reply_markup=_get_keyboard(
                "Молодой", "Старший", "10-30", "31-60", prefix="form"
            ),
        )
    elif answer == "Молодой" or answer == "Старший":
        DETAILS["age"] = 20 if answer == "Молодой" else 40
        await query.edit_message_text(
            text="Сколько ты зарабатываешь?",
            reply_markup=_get_keyboard(
                "Средний", "Несредний", "до 50k", "от 50k", prefix="form"
            ),
        )
    elif answer == "Средний" or answer == "Несредний":
        DETAILS["salary"] = 50_000 if answer == "Средний" else 80_000
        await query.edit_message_text(
            text="Ты снимаешь жилье?",
            reply_markup=_get_keyboard(
                "Снимает", "Неснимает", "Да", "Нет", prefix="form"
            ),
        )
    elif answer == "Снимает" or answer == "Неснимает":
        DETAILS["where_live"] = answer
        await query.edit_message_text(
            text="Какие хобби ты предпочитаешь?",
            reply_markup=_get_keyboard(
                "Динамические", "Спокойные", "Динамические", "Спокойные", prefix="form"
            ),
        )
    else:
        DETAILS["hobbies"] = answer
        await insert_into_db(
            sql=sql_query.INSERT_USER_DETAILS.format(
                telegram_id=DETAILS["id"],
                sex=DETAILS["sex"],
                age=DETAILS["age"],
                salary=DETAILS["salary"],
                hobbies=DETAILS["hobbies"],
                where_live=DETAILS["where_live"],
            )
        )
        await query.edit_message_text(text=message_text.MESSAGE_TTT)


# исправить analysis и сделать как в form
async def cost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text=message_text.COST_MESSAGE)
    return CATEGORY


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=message_text.CANCEL_MESSAGE
    )
    return ConversationHandler.END


async def category_cost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = update.message.from_user["id"]
    if len(user_message.split()) == 3:
        category, cost_sum = user_message.split()[:2], user_message.split()[-1]
    elif len(user_message.split()) == 2:
        category, cost_sum = user_message.split()[:1], user_message.split()[-1]
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message_text.CATEGORY_MESSAGE_ERROR,
            parse_mode=constants.ParseMode.HTML,
        )
        return CATEGORY
    month = datetime.now().month
    category = " ".join(category)
    if category in config.CATEGORY:
        category_id = config.CATEGORY_DICT[category]
        async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
            sql = sql_query.INSERT_CATEGORY_COST.format(
                user_id=user_id, cost_sum=cost_sum, category_id=category_id, month=month
            )
            await db.execute(sql)
            await db.commit()
        CATEGORY_NAME.append(category)
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=message_text.CATEGORY_MESSAGE
        )
        return PRODUCT_NAME
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message_text.CATEGORY_MESSAGE_ERROR,
            parse_mode=constants.ParseMode.HTML,
        )
        return CATEGORY


async def skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=message_text.SKIP_MESSAGE
    )
    return CATEGORY


async def handle_text(update, context):
    user_message = update.message.text
    if (
        context.user_data.get("state") == AWAITING_NOTE
        and user_message in config.CATEGORY
    ):
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=message_text.NOTE_CATEGORY_DONE
        )
        context.user_data["state"] = AWAITING_NOTE + 1
    elif context.user_data.get("state") == AWAITING_NOTE + 1:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=message_text.NOTE_END
        )

        context.user_data["state"] = None
    elif (
        context.user_data.get("state") == AWAITING_NOTE
        and user_message not in config.CATEGORY
    ):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message_text.NOTE_MESSAGE_ERROR,
            parse_mode=constants.ParseMode.HTML,
        )

    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message_text.MEESAGE_FOR_ALL_TEXT,
            parse_mode=constants.ParseMode.HTML,
        )


async def product_cost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.split()
    user_id = update.message.from_user["id"]
    product_name, cost = (
        " ".join(user_message[: len(user_message) - 1]),
        user_message[-1],
    )
    category_id = config.CATEGORY_DICT[CATEGORY_NAME[-1]]

    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        sql = sql_query.INSERT_PRODUCT_COST.format(
            user_id=user_id,
            category_id=category_id,
            product_name=product_name,
            cost=cost,
            created_at=datetime.now(),
        )
        await db.execute(sql)
        await db.commit()

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=message_text.PRODUCT_COST_MESSAGE_DONE
    )
    return PRODUCT_NAME


# доделать
async def personal_reccomend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text={"Исходя из ваших персональных данных"}
    )
    return


async def analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user["id"]
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            sql_query.GET_ALL_COST_PER_CATEGORY.format(telegram_id=user_id)
        ) as cursor:
            async for row in cursor:
                all_cost = row["cost"]
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=message_text.ALL_COST_MESSAGE.format(all_cost=all_cost),
                    reply_markup=_get_keyboard("Выйти", "Графики", prefix="analys"),
                )


async def analys_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global MAIN_COST
    query = update.callback_query
    id = update.effective_chat.id
    await query.answer()
    if not query.data or not query.data.strip():
        return
    answer = query.data.split("_")[1]
    if answer == "Графики":
        ALL_COST.clear()
        ALL_CATEGORY.clear()
        # нужно починить user
        user_id = id
        async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                sql_query.GET_COST_PER_CATEGORY_FOR_NOW_MONTH.format(user_id=user_id)
            ) as cursor:
                async for row in cursor:
                    сost_category = row["cost"]
                    category = row["category"]
                    ALL_COST.append(сost_category)
                    ALL_CATEGORY.append(config.CATEGORY_DICT_INVERSE[category])
        plt.figure(figsize=(5, 5))
        plt.pie(
            ALL_COST,
            labels=ALL_CATEGORY,
            autopct="%1.1f%%",
            startangle=90,
            colors=config.COLORS,
        )
        plt.axis("equal")
        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight", dpi=300)
        buffer.seek(0)
        await context.bot.send_photo(
            chat_id=update.effective_chat.id, photo=InputFile(buffer)
        )
        await query.edit_message_text(
            text="Вот твои расходы в виде графика. Пойдем дальше?",
            reply_markup=_get_keyboard("Выйти", "Детализация", prefix="analys"),
        )
        return
    elif answer == "Детализация":
        response = "Полная детализация: \n\n"
        index = 1
        cost_category_dict_sorted = dict(
            sorted(
                dict(zip(ALL_CATEGORY, ALL_COST)).items(),
                key=lambda x: x[1],
                reverse=True,
            )
        )
        MAIN_COST = list(cost_category_dict_sorted.keys())[0]
        for category, cost in cost_category_dict_sorted.items():
            response += f"{index}. <b>{category.capitalize()}</b> - {cost} рублей\n"
            index += 1
        await query.edit_message_text(
            text=response + "\n\n" + "Нужен совет?",
            reply_markup=_get_keyboard(
                "Выйти",
                "Совет",
                "Выйти",
                "Совет",
                prefix="analys",
            ),
            parse_mode=constants.ParseMode.HTML,
        )
        return
    elif answer == "Совет":
        details = await get_details_from_db(
            sql_query.GET_DETAILS_PER_USER.format(telegram_id=id)
        )
        if len(details) == 0:
            await query.edit_message_text(
                text="Чтобы я лучше смог узнать тебя и дать совет: заполни форму /form"
            )
            return
        details["all_cost"] = sum(ALL_COST)
        details["main_category"] = MAIN_COST
        answer_yandex_gpt, prompt = _get_response_yandex_gpt(details)
        await insert_into_db(
            sql=sql_query.INSERT_GPT_ANSWER.format(
                telegram_id=id,
                gpt_answer=answer_yandex_gpt,
                prompt=prompt,
                name_gpt=config.NAME_GPT,
            )
        )

        await query.edit_message_text(text="Ждем-с")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=answer_yandex_gpt,
            parse_mode=constants.ParseMode.HTML,
        )

        await query.edit_message_text(text="На этом все")
        return
    elif answer == "Выйти":
        await query.edit_message_text(
            text="Давай тогда записывать дальше.\n\n Жмякай /cost",
            parse_mode=constants.ParseMode.HTML,
        )


async def graph(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_cost, all_category = [], []
    user_id = id
    media_group = []
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            sql_query.GET_COST_PER_CATEGORY_FOR_NOW_MONTH.format(user_id=user_id)
        ) as cursor:
            async for row in cursor:
                сost_category = row["cost"]
                category = row["category"]
                all_cost.append(сost_category)
                all_category.append(config.CATEGORY_DICT_INVERSE[category])
    plt.figure(figsize=(5, 5))
    plt.pie(
        all_cost,
        labels=all_category,
        autopct="%1.1f%%",
        startangle=90,
        colors=config.COLORS,
    )
    plt.axis("equal")
    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight", dpi=300)
    buffer.seek(0)
    media_group.append(InputMediaPhoto(buffer))
    plt.clf()
    buffer = BytesIO()
    plt.bar(all_category, all_cost, color=config.COLORS[: len(all_category)])
    plt.xlabel("Категории")
    plt.ylabel("Траты")
    plt.title("Гистограмма трат")
    plt.savefig(buffer, format="png", bbox_inches="tight", dpi=300)
    buffer.seek(0)
    media_group.append(InputMediaPhoto(buffer))
    plt.clf()
    buffer = BytesIO()
    plt.scatter(all_category, all_cost, color=config.COLORS[: len(all_category)])
    plt.xlabel("Категории", fontsize=12)
    plt.ylabel("Траты", fontsize=12)
    plt.title("Точечная диаграмма затрат", fontsize=14)
    plt.savefig(buffer, format="png", bbox_inches="tight", dpi=300)
    buffer.seek(0)
    media_group.append(InputMediaPhoto(buffer))
    await context.bot.send_media_group(
        chat_id=update.effective_chat.id, media=media_group
    )
    return


if __name__ == "__main__":
    application = (ApplicationBuilder().token(config.BOT_TOKEN)).build()

    start_handler = CommandHandler("start", start)
    help_handler = CommandHandler("help", help)
    cancel_handler = CommandHandler("cancel", cancel)
    cost_handler = CommandHandler("cost", cost)
    skip_handler = CommandHandler("skip", skip)
    analysis_handler = CommandHandler("analysis", analysis)
    form_handler = CommandHandler("form", form)
    note_handler = CommandHandler("note", note)
    graph_handler = CommandHandler("graph", graph)

    category_handler = MessageHandler(
        filters.Regex(pattern=re.compile(r"\b\w+\s|\w+\d+\b")), category_cost
    )
    product_handler = MessageHandler(
        filters.Regex(pattern=re.compile(r"\b\w+\s|\w+\d+\b")), product_cost
    )
    message_all_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)

    button_analysis = CallbackQueryHandler(analys_button, pattern=r"analys_\w+")
    button_form = CallbackQueryHandler(form_button, pattern=r"form_\w+")
    conv_handler = ConversationHandler(
        entry_points=[cost_handler],
        states={
            CATEGORY: [category_handler],
            PRODUCT_NAME: [product_handler, skip_handler],
        },
        fallbacks=[cancel_handler],
    )
    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(analysis_handler)
    application.add_handler(form_handler)
    application.add_handler(note_handler)
    # application.add_handler(category_handler)
    application.add_handler(conv_handler)
    application.add_handler(message_all_handler)
    application.add_handler(graph_handler)

    application.add_handler(button_analysis)
    application.add_handler(button_form)

    application.run_polling()
