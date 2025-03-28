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
        self.edit_states = {}

    def _register_handlers(self) -> None:
        # Разделяем обработчики для кнопок и ввода возраста
        handlers = [
            MessageHandler(
                filters.Text(['👤 Просмотреть профиль']), self.show_profile
            ),
            MessageHandler(
                filters.Text(['📧 Изменить email']), self.start_edit_email
            ),
            MessageHandler(
                filters.Text(['📝 Изменить имя']), self.start_edit_name
            ),
            MessageHandler(
                filters.Text(['🏷️ Изменить никнейм']), self.start_edit_nickname
            ),
            MessageHandler(
                filters.Text(['🎂 Изменить дату рождения']),
                self.start_edit_birthdate,
            ),
            MessageHandler(
                filters.Text(['📱 Изменить телефон']), self.start_edit_phone
            ),
            MessageHandler(
                filters.Text(['🔙 Вернуться в меню']), self.back_to_menu
            ),
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, self.check_data_input
            ),
        ]
        for handler in handlers:
            self.app.add_handler(handler)

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

    def _get_profile_keyboard(self) -> ReplyKeyboardMarkup:
        """Клавиатура для редактирования профиля."""
        buttons = [
            ['📧 Изменить email', '📝 Изменить имя'],
            ['🏷️ Изменить никнейм', '🎂 Изменить дату рождения'],
            ['📱 Изменить телефон'],
            ['🔙 Вернуться в меню'],
        ]
        return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

    async def show_profile(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Показывает профиль пользователя с кнопками редактирования."""
        user_data = await self._fetch_user_data(update.effective_user.id)
        age_ver = user_data.get('age_verified')

        profile_text = (
            '👤 Ваш профиль:\n\n'
            f'📧 Email: {user_data.get("email") or "не указан"}\n'
            f'📝 Имя: {user_data["name"]}\n'  # name обязательное поле
            f'🏷️ Никнейм: {user_data.get("nickname") or "не указан"}\n'
            f'🎂 Дата рождения: {user_data.get("birth_date") or "не указана"}'
            f'\n📱 Телефон: {user_data.get("phone_number") or "не указан"}\n'
            f'🔞 Возраст подтверждён: {"✅" if age_ver else "❌"}'
        )

        keyboard = self._get_profile_keyboard()
        await update.message.reply_text(
            text=profile_text, reply_markup=keyboard
        )

    async def start_edit_email(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Начало редактирования email."""
        self.edit_states[update.effective_user.id] = 'email'
        await update.message.reply_text(
            'Введите новый email:', reply_markup=ReplyKeyboardRemove()
        )

    async def start_edit_name(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Начало редактирования имени."""
        self.edit_states[update.effective_user.id] = 'name'
        await update.message.reply_text(
            'Введите новое имя:', reply_markup=ReplyKeyboardRemove()
        )

    async def start_edit_nickname(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Начало редактирования никнейма."""
        self.edit_states[update.effective_user.id] = 'nickname'
        await update.message.reply_text(
            'Введите новый никнейм:', reply_markup=ReplyKeyboardRemove()
        )

    async def start_edit_birthdate(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Начало редактирования даты рождения."""
        self.edit_states[update.effective_user.id] = 'birth_date'
        await update.message.reply_text(
            'Введите дату рождения в формате ГГГГ-ММ-ДД:',
            reply_markup=ReplyKeyboardRemove(),
        )

    async def start_edit_phone(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Начало редактирования телефона."""
        self.edit_states[update.effective_user.id] = 'phone_number'
        await update.message.reply_text(
            'Введите новый телефон:', reply_markup=ReplyKeyboardRemove()
        )

    async def back_to_menu(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Возврат в главное меню."""
        user_data = await self._fetch_user_data(update.effective_user.id)  # noqa
        await self._send_main_menu(update)

    async def check_data_input(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Обработка ввода данных для редактирования."""
        user_id = update.effective_user.id

        # Если пользователь в режиме редактирования
        if user_id in self.edit_states:
            field = self.edit_states.pop(user_id)
            value = update.message.text

            try:
                await self._update_profile(update, field, value)
                await update.message.reply_text('✅ Данные успешно обновлены!')
                await self.show_profile(update, context)
            except Exception as e:
                await update.message.reply_text(f'❌ Ошибка: {str(e)}')
                await self.show_profile(update, context)

        # Если НЕ в режиме редактирования - стандартная обработка
        else:
            # Ваша оригинальная логика проверки возраста
            if not await self.check_registration(update.effective_user.id):
                success = await self.register_user(update, context)
                if not success:
                    await update.message.reply_text(
                        'Пожалуйста, введите корректный возраст:'
                    )

    async def _update_profile(
        self, update: Update, field: str, value: str
    ) -> None:
        """Обновление данных через API."""
        try:
            user_telegram_id = update.effective_user.id
            logging.debug(f'Отправка PATCH-запроса для поля {field}')

            async with ClientSession() as session:
                async with session.patch(
                    f'{API_URL}/users/{user_telegram_id}',
                    json={field: value},
                ) as response:
                    response_data = await response.json()
                    logging.debug(
                        f'Ответ сервера: {response.status} {response_data}'
                    )

                    if response.status != 200:
                        error_msg = response_data.get(
                            'detail', 'Неизвестная ошибка'
                        )
                        raise Exception(f'API Error: {error_msg}')

        except Exception as e:
            logging.error(f'Ошибка при обновлении профиля: {str(e)}')
            raise

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
