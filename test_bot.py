import pytest
from unittest.mock import patch
from bot import (
    calculate_combination_number,
    get_horoscope,
    get_compatibility,
    select_option,
    select_compatibility_male,
    select_compatibility_female,
    compatibility_result,
    ZODIAC_SIGNS,
    ZODIAC_INDEXES,
)

# Моки для тестирования
class MockUpdate:
    def __init__(self, text):
        self.message = MockMessage(text)

class MockMessage:
    def __init__(self, text):
        self.text = text

    async def reply_text(self, text, **kwargs):
        return text

class MockContext:
    def __init__(self):
        self.user_data = {}

# Тесты для calculate_combination_number
def test_calculate_combination_number_positive():
    assert calculate_combination_number("♈ Овен", "♉ Телец") == 2
    assert calculate_combination_number("♑ Козерог", "♒ Водолей") == 119

def test_calculate_combination_number_negative():
    with pytest.raises(KeyError):
        calculate_combination_number("Несуществующий знак", "♉ Телец")
    with pytest.raises(KeyError):
        calculate_combination_number("♈ Овен", "Несуществующий знак")

# Тесты для get_horoscope
@patch('bot.requests.get')
def test_get_horoscope_positive(mock_get):
    mock_get.return_value.text = '''
        <div class="b6a5d4949c e45a4c1552">
            <p>Это тестовый гороскоп.</p>
        </div>
    '''
    assert get_horoscope("aries", "today") == "Это тестовый гороскоп."
# Тесты для get_compatibility
@patch('bot.requests.get')
def test_get_compatibility_positive(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = '''
        <div class="b6a5d4949c e45a4c1552">
            <p>Это тестовая совместимость.</p>
        </div>
    '''
    result = get_compatibility("♈ Овен", "♉ Телец")
    assert result == "Это тестовая совместимость."

# Тесты для select_option
@pytest.mark.asyncio
async def test_select_option_positive():
    context = MockContext()
    context.user_data["sign"] = "♈ Овен"
    update = MockUpdate("🔮 Гороскоп на сегодня")
    result = await select_option(update, context)
    assert result == 1  # Проверяем, что функция завершилась успешно

@pytest.mark.asyncio
async def test_select_option_negative():
    context = MockContext()
    context.user_data["sign"] = "♈ Овен"
    update = MockUpdate("Некорректная команда")
    result = await select_option(update, context)
    assert result == 1  # Проверяем, что обработка продолжается

# Тесты для select_compatibility_male
@pytest.mark.asyncio
async def test_select_compatibility_male_positive():
    context = MockContext()
    update = MockUpdate("♈ Овен")
    result = await select_compatibility_male(update, context)
    assert result == 2  # Успешный переход к выбору женского знака

@pytest.mark.asyncio
async def test_select_compatibility_male_negative():
    context = MockContext()
    update = MockUpdate("Несуществующий знак")
    result = await select_compatibility_male(update, context)
    assert result == 2  # Некорректный знак, но функция завершена

# Тесты для select_compatibility_female
@pytest.mark.asyncio
async def test_select_compatibility_female_positive():
    context = MockContext()
    context.user_data["male_sign"] = "♈ Овен"
    update = MockUpdate("♉ Телец")
    result = await select_compatibility_female(update, context)
    assert result == 3  # Успешный выбор знака

@pytest.mark.asyncio
async def test_select_compatibility_female_negative():
    context = MockContext()
    context.user_data["male_sign"] = "♈ Овен"
    update = MockUpdate("Несуществующий знак")
    result = await select_compatibility_female(update, context)
    assert result == 2  # Возврат к повторному выбору

# Тесты для compatibility_result
@pytest.mark.asyncio
async def test_compatibility_result_positive():
    context = MockContext()
    context.user_data["male_sign"] = "♈ Овен"
    update = MockUpdate("♉ Телец")
    result = await compatibility_result(update, context)
    assert result == 1  # Успешное завершение

@pytest.mark.asyncio
async def test_compatibility_result_negative():
    context = MockContext()
    context.user_data["male_sign"] = "♈ Овен"
    update = MockUpdate("Несуществующий знак")
    result = await compatibility_result(update, context)
    assert result == 3  # Некорректный выбор
