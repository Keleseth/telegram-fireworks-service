import logging

from aiohttp import ClientSession
from telegram import (
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.bot.keyboards import keyboard_main  # Импортируем keyboard_main

API_URL = 'http://127.0.0.1:8000'


class UserManager:
    def __init__(self, application: ApplicationBuilder) -> None:
        """Инициализация."""
        self.app = application
        self._register_handlers()

    def _register_handlers(self) -> None:
        # Разделяем обработчики для кнопок и ввода возраста
        self.app.add_handler(
            MessageHandler(
                filters.Text(['👤 Просмотреть профиль', '🛡️ Перейти в админку'])
                & ~filters.COMMAND,
                self.handle_menu_buttons,
            )
        )
        self.app.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, self.check_age_input
            )
        )

    async def get_dynamic_keyboard(
        self, telegram_id: int
    ) -> ReplyKeyboardMarkup:
        """Создаёт клавиатуру с актуальными правами."""
        user_data = await self._fetch_user_data(telegram_id)
        is_admin = user_data.get('is_admin', False) if user_data else False

        buttons = [['👤 Просмотреть профиль']]
        if is_admin:
            buttons[0].append('🛡️ Перейти в админку')

        return ReplyKeyboardMarkup(
            buttons, resize_keyboard=True, one_time_keyboard=False
        )

    async def refresh_keyboard(self, update: Update):
        """Обновляет клавиатуру в реальном времени."""
        try:
            new_keyboard = await self.get_dynamic_keyboard(
                update.effective_user.id
            )
            await update.message.reply_text(
                text='🤖 загрузка...',  # Невидимый символ
                reply_markup=new_keyboard,
            )
        except Exception as e:
            logging.error(f'Ошибка обновления клавиатуры: {str(e)}')

    async def _fetch_user_data(self, telegram_id: int) -> dict | None:
        """Общая функция для получения данных пользователя."""
        async with ClientSession() as session:
            async with session.get(
                f'{API_URL}/users/{telegram_id}'
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None

    async def _send_main_menu(self, update: Update) -> None:
        """Отправка меню с актуальной клавиатурой."""
        keyboard = await self.get_dynamic_keyboard(update.effective_user.id)
        await update.message.reply_text(
            text='🤖 загрузка...', reply_markup=keyboard
        )

        await update.message.reply_text(
            'Главное меню:', reply_markup=InlineKeyboardMarkup(keyboard_main)
        )

    async def check_registration(self, user_telegram_id: int) -> dict | None:
        """Проверка регистрации с возвратом данных пользователя."""
        return await self._fetch_user_data(user_telegram_id)

    async def register_user(
        self,
        update: Update,
        context: CallbackContext,
    ):
        try:
            age = int(update.message.text)
            if age < 18:
                await update.message.reply_text(
                    'Доступ запрещен!', reply_markup=ReplyKeyboardRemove()
                )
                return False

            async with ClientSession() as session:
                async with session.post(
                    f'{API_URL}/auth/telegram-register',
                    json={
                        'telegram_id': update.effective_user.id,
                        'name': update.effective_user.full_name,
                        'age_verified': True,
                    },
                ) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        is_admin = user_data.get('is_admin', False)
                        await update.message.reply_text(
                            '✅ Регистрация успешно завершена!',
                            reply_markup=self.main_keyboard(is_admin),
                        )
                        await self._send_main_menu(
                            update,
                        )
                        return True
                    return False
        except ValueError:
            await update.message.reply_text('Введите число!')
            return False

    def main_keyboard(self, is_admin: bool = False):
        """Генерация reply-клавиатуры."""
        buttons = [['👤 Просмотреть профиль']]
        if is_admin:
            buttons[0].append('🛡️ Перейти в админку')
        return ReplyKeyboardMarkup(
            buttons,
            resize_keyboard=True,
            one_time_keyboard=False,
            input_field_placeholder='↓ Выберите действие ↓',
        )

    async def check_age_input(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        if not await self.check_registration(update.effective_user.id):
            success = await self.register_user(update, context)
            if not success:
                await update.message.reply_text(
                    'Пожалуйста, введите корректный возраст:'
                )

    async def handle_menu_buttons(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        # Проверяем права перед каждым действием
        user_data = await self._fetch_user_data(update.effective_user.id)

        text = update.message.text
        if text == '👤 Просмотреть профиль':
            await self.refresh_keyboard(update)
            await update.message.reply_text("Раздел 'Просмотр профиля'...")

        elif text == '🛡️ Перейти в админку':
            await self.refresh_keyboard(update)
            if user_data and user_data.get('is_admin'):
                await update.message.reply_text('Админ-панель...')
            else:
                await update.message.reply_text('Доступ запрещён!')
