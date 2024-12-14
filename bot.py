"""
Telegram Bot for Zodiac Signs

This bot provides horoscopes, zodiac information, and compatibility between zodiac signs.
It uses `python-telegram-bot` for interaction and `BeautifulSoup` for web scraping.

Attributes:
    PERIODS (list): List of time periods supported for horoscopes.
    ZODIAC_SIGNS (dict): Mapping of zodiac signs (Russian) to their English counterparts.
    ZODIAC_INDEXES (dict): Index numbers for zodiac signs used for compatibility calculation.
    ZODIAC_INFO (dict): Descriptions of each zodiac sign, including its ruler and traits.

Constants:
    SELECT_SIGN (int): State for selecting a zodiac sign.
    SELECT_OPTION (int): State for choosing an action (horoscope, info, compatibility).
    SELECT_COMPATIBILITY_MALE (int): State for selecting the male zodiac sign for compatibility.
    SELECT_COMPATIBILITY_FEMALE (int): State for selecting the female zodiac sign for compatibility.

"""

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)
import requests
from bs4 import BeautifulSoup

PERIODS = ["today", "week", "month"]

ZODIAC_SIGNS = {  # Полный словарь знаков зодиака
    "♈ Овен": "aries",
    "♉ Телец": "taurus",
    "♊ Близнецы": "gemini",
    "♋ Рак": "cancer",
    "♌ Лев": "leo",
    "♍ Дева": "virgo",
    "♎ Весы": "libra",
    "♏ Скорпион": "scorpio",
    "♐ Стрелец": "sagittarius",
    "♑ Козерог": "capricorn",
    "♒ Водолей": "aquarius",
    "♓ Рыбы": "pisces",
}

ZODIAC_INDEXES = { # Полный список индексов
    "♈ Овен": 1,
    "♉ Телец": 2,
    "♊ Близнецы": 3,
    "♋ Рак": 4,
    "♌ Лев": 5,
    "♍ Дева": 6,
    "♎ Весы": 7,
    "♏ Скорпион": 8,
    "♐ Стрелец": 9,
    "♑ Козерог": 10,
    "♒ Водолей": 11,
    "♓ Рыбы": 12,
}

ZODIAC_INFO = { # Полный словарь информации о знаках зодиака
    "♈ Овен": "♈ Управитель Марс дает знаку такие черты как резкость, яркость, живость, энергичность и стремительность.",
    "♉ Телец": "♉ Управитель Венера дарует стабильность, уверенность и материальную гармонию.",
    "♊ Близнецы": "♊ Управитель Меркурий отвечает за любознательность, общительность, умение налаживать контакты.",
    "♋ Рак": "♋ Управитель Луна несет душевность, чувственность, внутреннее спокойствие и умение заботиться о других.",
    "♌ Лев": "♌ Управитель Солнце наделяет энергичностью, страстностью, умением быть в центре внимания, устойчивостью и творческим началом.",
    "♍ Дева": "♍ Управитель Меркурий дарит внимательность, стремление к идеальности и порядку, аккуратность и перфекционизм.",
    "♎ Весы": "♎ Управитель Венера отвечает за плавность, мягкость, баланс, красоту и утонченность.",
    "♏ Скорпион": "♏ Управитель Плутон несет страсть, интуицию, загадочность, умение видеть суть событий.",
    "♐ Стрелец": "♐ Управитель Юпитер дает человеку сообразительность, широту души, тягу к расширению границ, умение вести за собой.",
    "♑ Козерог": "♑ Управитель Сатурн привнесет в характер конкретность и дисциплину, умение видеть цель и идти к ней.",
    "♒ Водолей": "♒ Управитель Уран отвечает за революционность, новые прорывные идеи, предвосхищение будущего и внутреннюю свободу.",
    "♓ Рыбы": "♓ Управитель Нептун подарит творческую жилку, вдохновение, умение копнуть глубоко и наличие своей философии.",
}

SELECT_SIGN, SELECT_OPTION, SELECT_COMPATIBILITY_MALE, SELECT_COMPATIBILITY_FEMALE = range(4)

def calculate_combination_number(male_sign: str, female_sign: str) -> int:
    """
       Calculates a unique combination number for two zodiac signs.

       Args:
           male_sign (str): The male zodiac sign in Russian.
           female_sign (str): The female zodiac sign in Russian.

       Returns:
           int: A unique combination number for the given zodiac signs.
       """
    male_index = ZODIAC_INDEXES[male_sign]
    female_index = ZODIAC_INDEXES[female_sign]
    return 12 * (male_index - 1) + female_index

def get_horoscope(sign: str, period: str) -> str:
    """
       Fetches the horoscope for a specific zodiac sign and time period.

       Args:
           sign (str): The zodiac sign in English.
           period (str): The period for the horoscope ("today", "week", "month").

       Returns:
           str: The horoscope text if available, otherwise an error message.
       """
    url = f"https://horo.mail.ru/prediction/{sign}/{period}/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    horoscope_div = soup.find('div', class_='b6a5d4949c e45a4c1552')
    if horoscope_div:
        return horoscope_div.find('p').text.strip()
    return "Гороскоп не найден."

def get_compatibility(male_sign: str, female_sign: str) -> str:
    """
        Fetches compatibility information for two zodiac signs.

        Args:
            male_sign (str): The male zodiac sign in Russian.
            female_sign (str): The female zodiac sign in Russian.

        Returns:
            str: Compatibility details or an error message.
        """
    combination_number = calculate_combination_number(male_sign, female_sign)
    url = f"https://horo.mail.ru/compatibility/zodiac/{combination_number}/"
    
    response = requests.get(url)
    if response.status_code != 200:
        return "Не удалось получить данные с сайта."

    soup = BeautifulSoup(response.text, "html.parser")
    compatibility_divs = soup.find_all('div', class_='b6a5d4949c e45a4c1552')

    if compatibility_divs:
        compatibility_details = []

        for div in compatibility_divs:
            title_tag = div.find("h2")
            paragraph_tag = div.find("p")

            if title_tag:
                title = title_tag.text.strip()  
            else:
                title = "Без заголовка"

            if paragraph_tag:
                paragraph = paragraph_tag.text.strip()  
            else:
                paragraph = "Информация отсутствует."

            compatibility_details.append(f"{paragraph}")
            
        return "\n\n".join(compatibility_details)
        
    return "Информация о совместимости не найдена."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
       Initiates the bot and prompts the user to select a zodiac sign.

       Args:
           update (Update): Telegram update object.
           context (ContextTypes.DEFAULT_TYPE): Context object for the current conversation.

       Returns:
           int: The next state, SELECT_SIGN.
       """
    reply_keyboard = [[zodiac] for zodiac in ZODIAC_SIGNS.keys()]
    await update.message.reply_text(
        "🌟 Привет! Выберите ваш знак зодиака:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return SELECT_SIGN

async def select_sign(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
       Handles the user's zodiac sign selection.

       Args:
           update (Update): Telegram update object.
           context (ContextTypes.DEFAULT_TYPE): Context object for the current conversation.

       Returns:
           int: The next state, SELECT_OPTION, or repeats SELECT_SIGN for invalid input.
       """
    user_sign = update.message.text
    if user_sign not in ZODIAC_SIGNS:
        await update.message.reply_text("⏳ Пожалуйста, подождите немного перед следующим сообщением.")
        return SELECT_SIGN
    context.user_data["sign"] = user_sign
    reply_keyboard = [
        ["🔮 Гороскоп на сегодня", "📅 Гороскоп на неделю", "🌙 Гороскоп на месяц"],
        ["♻️ Сменить знак", "ℹ️ Информация о знаке", "💑 Совместимость"],
    ]
    await update.message.reply_text(
        f"Вы выбрали {user_sign}. Что вас интересует?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True),
    )
    return SELECT_OPTION

async def select_option(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
        Handles the user's action selection.

        Args:
            update (Update): Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): Context object for the current conversation.

        Returns:
            int: The next state depending on the user's choice.
        """
    user_choice = update.message.text
    sign = context.user_data.get("sign")
    if user_choice == "🔮 Гороскоп на сегодня":
        await update.message.reply_text(get_horoscope(ZODIAC_SIGNS[sign], "today"))
    elif user_choice == "📅 Гороскоп на неделю":
        await update.message.reply_text(get_horoscope(ZODIAC_SIGNS[sign], "week"))
    elif user_choice == "🌙 Гороскоп на месяц":
        await update.message.reply_text(get_horoscope(ZODIAC_SIGNS[sign], "month"))
    elif user_choice == "♻️ Сменить знак":
        return await start(update, context)
    elif user_choice == "ℹ️ Информация о знаке":
        await update.message.reply_text(ZODIAC_INFO.get(sign, "Информация о знаке недоступна."))
    elif user_choice == "💑 Совместимость":
        return await select_compatibility_male(update, context)
    else:
        await update.message.reply_text("🚫 Пожалуйста, выберите опцию из списка.")
    return SELECT_OPTION

async def select_compatibility_male(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
        Initiates the compatibility check process by prompting the user to select a male zodiac sign.

        Args:
            update (Update): The incoming Telegram update containing the user's message.
            context (ContextTypes.DEFAULT_TYPE): The current conversation context.

        Returns:
            int: The next state, SELECT_COMPATIBILITY_MALE, for the compatibility check.
        """
    reply_keyboard = [[zodiac] for zodiac in ZODIAC_SIGNS.keys()]
    await update.message.reply_text("Выберите знак мужчины:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return SELECT_COMPATIBILITY_MALE

async def select_compatibility_female(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
        Handles the selection of the male zodiac sign and prompts the user to select a female zodiac sign.

        Args:
            update (Update): The incoming Telegram update containing the user's message.
            context (ContextTypes.DEFAULT_TYPE): The current conversation context, where the selected male sign is stored.

        Returns:
            int: The next state, SELECT_COMPATIBILITY_FEMALE, for the compatibility check.
        """
    male_sign = update.message.text
    if male_sign not in ZODIAC_SIGNS:
        await update.message.reply_text("Пожалуйста, выберите знак из предложенного списка.")
        return SELECT_COMPATIBILITY_MALE
    context.user_data["male_sign"] = male_sign
    reply_keyboard = [[zodiac] for zodiac in ZODIAC_SIGNS.keys()]
    await update.message.reply_text(f"Вы выбрали {male_sign}. Теперь выберите знак женщины:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return SELECT_COMPATIBILITY_FEMALE

async def compatibility_result(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
        Completes the compatibility check by fetching and displaying compatibility information
        for the selected male and female zodiac signs.

        Args:
            update (Update): The incoming Telegram update containing the user's message.
            context (ContextTypes.DEFAULT_TYPE): The current conversation context, which stores the selected male and female signs.

        Returns:
            int: The next state, SELECT_OPTION, to prompt the user for further actions.
        """
    female_sign = update.message.text
    male_sign = context.user_data.get("male_sign")
    if female_sign not in ZODIAC_SIGNS:
        await update.message.reply_text("Пожалуйста, выберите знак из предложенного списка.")
        return SELECT_COMPATIBILITY_FEMALE

    compatibility = get_compatibility(male_sign, female_sign)
    
    await update.message.reply_text(compatibility)

    reply_keyboard = [
        ["🔮 Гороскоп на сегодня", "📅 Гороскоп на неделю", "🌙 Гороскоп на месяц"],
        ["♻️ Сменить знак", "ℹ️ Информация о знаке", "💑 Совместимость"],
    ]
    await update.message.reply_text(
        f"Что вас интересует?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True),
    )

    return SELECT_OPTION


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
        Ends the conversation and exits the bot.

        Args:
            update (Update): Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): Context object for the current conversation.

        Returns:
            int: Ends the conversation with ConversationHandler.END.
        """
    await update.message.reply_text("👋 До свидания!", reply_markup=None)
    return ConversationHandler.END

def main():
    """
        Configures and starts the bot application.

        The bot is configured with states to handle user input for:
            - Zodiac sign selection.
            - Action selection (horoscope, info, compatibility).
            - Compatibility checks for male and female zodiac signs.

        Entry Points:
            - "/start": Starts the bot and initiates conversation.

        States:
            - SELECT_SIGN: Prompts the user to select their zodiac sign.
            - SELECT_OPTION: Allows the user to choose an action.
            - SELECT_COMPATIBILITY_MALE: Requests the male zodiac sign for compatibility.
            - SELECT_COMPATIBILITY_FEMALE: Requests the female zodiac sign for compatibility.

        Fallbacks:
            - "/cancel": Ends the conversation.
        """
    application = Application.builder().token("7846818689:AAF_nsCeUMWOp5ef14HlBFBtTa9hepliGno").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_SIGN: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_sign)],
            SELECT_OPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_option)],
            SELECT_COMPATIBILITY_MALE: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_compatibility_female)],
            SELECT_COMPATIBILITY_FEMALE: [MessageHandler(filters.TEXT & ~filters.COMMAND, compatibility_result)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
