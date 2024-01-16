import logging
from telegram import Update, constants
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)
import message_text
import re
import config
import aiosqlite
import sql_query
from datetime import datetime


CATEGORY_NAME = []
CATEGORY, PRODUCT_NAME = range(2)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=message_text.START_MESSAGE
    )


async def cost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=message_text.COST_MESSAGE
    )
    return CATEGORY


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=message_text.CANCEL_MESSAGE
    )
    return ConversationHandler.END


async def category_cost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    category, cost_sum = user_message.split()[0], user_message.split()[1]
    user_id = update.message.from_user["id"]
    if category in config.CATEGORY:
        category_id = config.CATEGORY_DICT[category]
        async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
            sql = sql_query.INSERT_CATEGORY_COST.format(
                user_id=user_id, cost_sum=cost_sum, category_id=category_id
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


async def product_cost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = update.message.from_user["id"]
    product_name, cost = user_message.split()[0], user_message.split()[1]
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


async def analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user["id"]
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            sql_query.GET_ALL_COST_PRODUCT.format(user_id=user_id)
        ) as cursor:
            async for row in cursor:
                all_cost = row["all_cost"]
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=message_text.ALL_COST_MESSAGE.format(all_cost=all_cost),
                )


if __name__ == "__main__":
    application = (ApplicationBuilder().token(config.BOT_TOKEN)).build()

    start_handler = CommandHandler("start", start)
    cancel_handler = CommandHandler("cancel", cancel)
    cost_handler = CommandHandler("cost", cost)
    skip_handler = CommandHandler("skip", skip)
    analysis_handler = CommandHandler("analysis", analysis)

    category_handler = MessageHandler(
        filters.Regex(pattern=re.compile(r"\b(\w+)\s+(\d+)")), category_cost
    )
    product_handler = MessageHandler(
        filters.Regex(pattern=re.compile(r"\b(\w+)\s+(\d+)")), product_cost
    )

    conv_handler = ConversationHandler(
        entry_points=[cost_handler],
        states={
            CATEGORY: [category_handler],
            PRODUCT_NAME: [product_handler, skip_handler],
        },
        fallbacks=[cancel_handler],
    )
    application.add_handler(start_handler)
    application.add_handler(analysis_handler)
    # application.add_handler(category_handler)
    application.add_handler(conv_handler)

    application.run_polling()
