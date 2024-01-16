import config

START_MESSAGE = """Привет, ты находишься в финансовом боте.
Пиши сюда свои расходы, а я буду их анализировать. \n
У меня есть множество функций, вот они:
/start - начало работы бота
/cost - записать расходы
/analysis - анализруют твои расходы
/graph - график расходов
/note - заметки про свои расходы
/cancel - отмена расхода
"""

TRANSFER = "\n"

COST_MESSAGE = """Так, ну рассказывай о своих покупках.\n
Опиши категории и сколько денег ты на них слил.

Желательно как-то так: еда 500

"""

CANCEL_MESSAGE = """
Ну чего-то ты рановато вышел. А зачем спрашивается заходил?

Ну ладно... Погорячился!

P.S: Если тебе нужна аналитика, то пиши скорее /analysis!
"""

SKIP_MESSAGE = """Жду от тебя другую категорию или выходи из меня (тыкай /cancel)"""

CATEGORY_MESSAGE = (
    """Расскажешь поподробнее что купил? Если не хочешь, то тогда нажми /skip"""
)

CATEGORY_MESSAGE_ERROR = (
    """Ты отослал неверную категорию, надо выбрать что то из этого:\n\n"""
)

for index, category in enumerate(config.CATEGORY):
    CATEGORY_MESSAGE_ERROR += f"<b>{index+1}. {category}" + "</b>" + "\n"

PRODUCT_COST_MESSAGE_DONE = (
    """Записал (П.С. чтобы выйти нажми /cancel, перейти к другой категории: /skip)"""
)

ALL_COST_MESSAGE = """Все твои расходы за этот месяц равны: {all_cost} рублей\n\n
Хочешь более подробную аналитику?"""
