import logging
from typing import List

from aiohttp import ClientSession
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    WebAppInfo,
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


class TelegramUserManager:
    def __init__(self, application: ApplicationBuilder) -> None:
        """Инициализация."""
        self.app = application
        self._register_handlers()
        self.edit_states = {}
        self.admin_setup_states = {}

    def _register_handlers(self) -> None:
        # Разделяем обработчики для кнопок и ввода возраста
        handlers = [
            MessageHandler(
                filters.Text(['👤 Просмотреть профиль']), self.show_profile
            ),
            MessageHandler(
                filters.Text(['🚧 Перейти в админку']),
                self.handle_admin_menu_buttons,
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
                filters.Text(['🚧 🔑 Изменить пароль 🚧']),
                self.admin_start_edit_password,
            ),
            MessageHandler(
                filters.Text(['🚧 📧 Изменить email 🚧']),
                self.admin_start_edit_email,
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
        if user_data:
            is_admin = user_data.get('is_admin', False) if user_data else False
            buttons = [['👤 Просмотреть профиль']]
            if is_admin:
                buttons[0].append('🚧 Перейти в админку')

            return ReplyKeyboardMarkup(
                buttons, resize_keyboard=True, one_time_keyboard=False
            )
        return ReplyKeyboardRemove()

    async def refresh_keyboard(self, update: Update):
        """Обновляет клавиатуру в реальном времени."""
        try:
            new_keyboard = await self.get_dynamic_keyboard(
                update.effective_user.id
            )
            await update.effective_message.reply_text(
                text='🤖 загрузка...',  # Невидимый символ
                reply_markup=new_keyboard,
            )
        except Exception as e:
            logging.error(f'Ошибка обновления клавиатуры: {str(e)}')

    async def handle_admin_menu_buttons(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user_data = await self._admin_fetch_user_data(update.effective_user.id)

        # 1. Проверяем права админа
        if not user_data.get('is_admin'):
            await update.message.reply_text('🚫 Доступ запрещён! 🚫')
            return

        if not user_data.get('email') or not user_data.get('hashed_password'):
            buttons = [[], ['🔙 Вернуться в меню', '👤 Просмотреть профиль']]
            if not user_data.get('email'):
                buttons[0].append('🚧 📧 Изменить email 🚧')
            if not user_data.get('hashed_password'):
                buttons[0].append('🚧 🔑 Изменить пароль 🚧')
            await update.message.reply_text(
                ('⚠️ Внимание! Для входа в админку нужны почта и пароль ⚠️'),
                reply_markup=ReplyKeyboardMarkup(
                    buttons, resize_keyboard=True
                ),
            )
            return

        # 2. TODO: заменить на домен серввера/admin
        web_app_url = 'https://habr.com/ru/companies/amvera/articles/849836/'

        # 3. Создаём кнопку с WebView
        await self.refresh_keyboard(update)
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text='Открыть админку 🚀',
                    web_app=WebAppInfo(url=web_app_url),
                )
            ]
        ])

        # 4. Отправляем сообщение с кнопкой
        await update.message.reply_text(
            '🔐 Панель администратора:', reply_markup=keyboard
        )

    async def _fetch_user_data(self, telegram_id: int) -> dict | None:
        """Общая функция для получения данных пользователя."""
        async with ClientSession() as session:
            async with session.get(
                f'{API_URL}/users/{telegram_id}'
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None

    async def _admin_fetch_user_data(self, telegram_id: int) -> dict | None:
        """Общая функция для получения данных пользователя."""
        async with ClientSession() as session:
            async with session.get(
                f'{API_URL}/moderator/{telegram_id}'
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None

    def _get_profile_keyboard(self) -> List:
        """Клавиатура для редактирования профиля."""
        return [
            ['📧 Изменить email', '📝 Изменить имя'],
            ['🏷️ Изменить никнейм', '🎂 Изменить дату рождения'],
            ['📱 Изменить телефон'],
            ['🔙 Вернуться в меню'],
        ]

    async def show_profile(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Показывает профиль пользователя с кнопками редактирования."""
        await self.check_age_input(update=update, context=context)
        await self.refresh_keyboard(update)
        user_data = await self._fetch_user_data(update.effective_user.id)
        if user_data:
            age_ver = user_data.get('age_verified')

            profile_text = (
                '👤 Ваш профиль:\n\n'
                f'📧 Email: {user_data.get("email") or "не указан"}\n'
                f'📝 Имя: {user_data["name"]}\n'  # name обязательное поле
                f'🏷️ Никнейм: {user_data.get("nickname") or "не указан"}\n'
                f'🎂 Дата рождения: {
                    user_data.get("birth_date") or "не указана"
                }'
                f'\n📱 Телефон: {user_data.get("phone_number") or "не указан"}'
                f'\n🔞 Возраст подтверждён: {"✅" if age_ver else "❌"}'
            )

            user_data = await self._fetch_user_data(update.effective_user.id)
            is_admin = user_data.get('is_admin', False) if user_data else False
            buttons = self._get_profile_keyboard()
            if is_admin:
                buttons[-1].append('🚧 Перейти в админку')
            keyboard = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
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

    async def admin_start_edit_email(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Начало редактирования email."""
        self.admin_setup_states[update.effective_user.id] = 'email'
        await update.message.reply_text(
            'Введите новый email:', reply_markup=ReplyKeyboardRemove()
        )

    async def admin_start_edit_password(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Начало редактирования email."""
        user_data = await self._fetch_user_data(update.effective_user.id)
        is_admin = user_data.get('is_admin', False) if user_data else False
        if not is_admin:
            await update.message.reply_text('🚫 У вас недостаточно прав 🚫')
            return
        self.admin_setup_states[update.effective_user.id] = 'hashed_password'
        await update.message.reply_text(
            'Введите новый пароль:', reply_markup=ReplyKeyboardRemove()
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
            'Введите новый телефон формата +7**********:',
            reply_markup=ReplyKeyboardRemove(),
        )

    async def back_to_menu(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Возврат в главное меню."""
        user_data = await self._fetch_user_data(update.effective_user.id)
        if user_data:
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
                await update.message.reply_text(
                    '❌ Ошибка, попробуйте позже ❌'
                )
                logging.debug(f'Ошибка: {e}')
                await self.show_profile(update, context)

        elif user_id in self.admin_setup_states:
            user_data = await self._admin_fetch_user_data(user_id)
            is_admin = user_data.get('is_admin', False) if user_data else False
            if not is_admin:
                await update.message.reply_text(
                    '🚫 У вас недостаточно прав 🚫'
                )
                return

            field = self.admin_setup_states.pop(user_id)
            value = update.message.text

            try:
                await self._admin_update_profile(update, field, value)
                await update.message.reply_text('✅ Данные успешно обновлены!')
                await self.handle_admin_menu_buttons(update, context)
            except Exception as e:
                await update.message.reply_text(
                    '❌ Ошибка, попробуйте позже ❌'
                )
                logging.debug(f'Ошибка: {e}')
                await self.handle_admin_menu_buttons(update, context)

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

    async def _admin_update_profile(
        self, update: Update, field: str, value: str
    ) -> None:
        """Обновление данных через API."""
        try:
            user_telegram_id = update.effective_user.id
            logging.debug(f'Отправка PATCH-запроса для поля {field}')

            async with ClientSession() as session:
                async with session.patch(
                    f'{API_URL}/moderator/{user_telegram_id}',
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
            'Чтобы вернуться в Главное меню напишите /menu\nГлавное меню:',
            reply_markup=InlineKeyboardMarkup(keyboard_main),
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
            if age > 115:
                await update.message.reply_text(
                    'Слишком высокое значение!',
                    reply_markup=ReplyKeyboardRemove(),
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
                    print(response.status)
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
            buttons[0].append('🚧 Перейти в админку')
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
