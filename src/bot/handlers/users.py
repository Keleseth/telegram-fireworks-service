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
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.bot.keyboards import keyboard_main  # Импортируем keyboard_main

API_URL = 'http://localhost:8000'
(
    MAIN_MENU,
    EDIT_PROFILE,
    EDIT_EMAIL,
    EDIT_NAME,
    EDIT_NICKNAME,
    EDIT_BIRTHDATE,
    EDIT_PHONE,
    ADMIN_MENU,
    ADMIN_EDIT_EMAIL,
    ADMIN_EDIT_PASSWORD,
    AGE_VERIFICATION,
) = range(11)




class TelegramUserManager:
    def __init__(self, application: ApplicationBuilder) -> None:
        """Инициализация."""
        self.app = application
        self._register_handlers()

    def _register_handlers(self) -> None:
        # Основной ConversationHandler
        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler('start', self.start),
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, self.start_conversation
                ),
            ],
            states={
                MAIN_MENU: [
                    MessageHandler(
                        filters.Text(['👤 Просмотреть профиль']),
                        self.show_profile,
                    ),
                    MessageHandler(
                        filters.Text(['🚧 Перейти в админку']),
                        self.handle_admin_menu_buttons,
                    ),
                ],
                EDIT_PROFILE: [
                    MessageHandler(
                        filters.Text(['📧 Изменить email']),
                        self.start_edit_email,
                    ),
                    MessageHandler(
                        filters.Text(['📝 Изменить имя']), self.start_edit_name
                    ),
                    MessageHandler(
                        filters.Text(['🏷️ Изменить никнейм']),
                        self.start_edit_nickname,
                    ),
                    MessageHandler(
                        filters.Text(['🎂 Изменить дату рождения']),
                        self.start_edit_birthdate,
                    ),
                    MessageHandler(
                        filters.Text(['📱 Изменить телефон']),
                        self.start_edit_phone,
                    ),
                    MessageHandler(
                        filters.Text(['🔙 Вернуться в меню']),
                        self.back_to_menu,
                    ),
                    MessageHandler(
                        filters.Text(['🚧 Перейти в админку']),
                        self.handle_admin_menu_buttons,
                    ),
                ],
                EDIT_EMAIL: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, self.edit_email
                    )
                ],
                EDIT_NAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, self.edit_name
                    )
                ],
                EDIT_NICKNAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, self.edit_nickname
                    )
                ],
                EDIT_BIRTHDATE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, self.edit_birthdate
                    )
                ],
                EDIT_PHONE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, self.edit_phone
                    )
                ],
                ADMIN_MENU: [
                    MessageHandler(
                        filters.Text(['🚧 🔑 Изменить пароль 🚧']),
                        self.admin_start_edit_password,
                    ),
                    MessageHandler(
                        filters.Text(['🚧 📧 Изменить email 🚧']),
                        self.admin_start_edit_email,
                    ),
                    MessageHandler(
                        filters.Text(['🔙 Вернуться в меню']),
                        self.back_to_menu,
                    ),
                ],
                ADMIN_EDIT_EMAIL: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, self.admin_edit_email
                    )
                ],
                ADMIN_EDIT_PASSWORD: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        self.admin_edit_password,
                    )
                ],
                AGE_VERIFICATION: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        self.handle_age_verification,
                    )
                ],
            },
            fallbacks=[CommandHandler('cancel', self.cancel_conversation)],
            map_to_parent={
                ConversationHandler.END: MAIN_MENU,
            },
        )

        self.app.add_handler(conv_handler)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /start."""
        user = await self._fetch_user_data(update.effective_user.id)
        if not user:
            await update.message.reply_text(
                'Добро пожаловать! Для начала работы подтвердите ваш возраст:'
            )
            return AGE_VERIFICATION
        return await self.show_main_menu(update, context)

    async def start_conversation(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Начало разговора, проверка возраста."""
        if not await self.check_registration(update.effective_user.id):
            await update.message.reply_text('Пожалуйста, введите ваш возраст:')
            return AGE_VERIFICATION
        return await self.show_main_menu(update, context)

    async def handle_age_verification(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Обработка ввода возраста."""
        try:
            age = int(update.message.text)
            if not (18 <= age <= 115):
                raise ValueError

            if await self.register_user(update, age):
                return await self.show_main_menu(update, context)

        except ValueError:
            await update.message.reply_text(
                '❌ Некорректный возраст! Введите число от 18 до 115:'
            )

        return AGE_VERIFICATION

    async def refresh_keyboard(self, update: Update):
        """Обновляет клавиатуру в реальном времени."""
        try:
            new_keyboard = await self._get_main_keyboard(
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
        """Обработка входа в админ-панель."""
        user_data = await self._admin_fetch_user_data(update.effective_user.id)

        if not user_data.get('is_admin'):
            await update.message.reply_text('🚫 Доступ запрещён!')
            return MAIN_MENU

        if not (user_data.get('email') and user_data.get('hashed_password')):
            buttons = []
            if not user_data.get('email'):
                buttons.append(['🚧 📧 Изменить email 🚧'])
            if not user_data.get('hashed_password'):
                buttons.append(['🚧 🔑 Изменить пароль 🚧'])
            buttons.append(['🔙 Вернуться в меню'])

            await update.message.reply_text(
                (
                    '⚠️ Для доступа в админку необходимо'
                    ' установить email и пароль!'
                ),
                reply_markup=ReplyKeyboardMarkup(
                    buttons, resize_keyboard=True
                ),
            )
            return ADMIN_MENU

        # TODO: заменить на ссылку на вход в админку!!!
        web_app_url = 'https://habr.com/ru/companies/amvera/articles/849836/'
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    'Открыть админку 🚀', web_app=WebAppInfo(url=web_app_url)
                )
            ]
        ])

        await update.message.reply_text(
            '🔐 Панель администратора:', reply_markup=keyboard
        )
        return MAIN_MENU

    async def _fetch_user_data(self, telegram_id: int) -> dict | None:
        """Общая функция для получения данных пользователя."""
        async with ClientSession() as session:
            async with session.post(
                f'{API_URL}/users',
                json={'telegram_id': telegram_id},
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None

    async def _admin_fetch_user_data(self, telegram_id: int) -> dict | None:
        """Общая функция для получения данных пользователя."""
        async with ClientSession() as session:
            async with session.post(
                f'{API_URL}/moderator',
                json={'telegram_id': telegram_id},
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None

    def _get_profile_keyboard(self, is_admin: bool) -> List[List[str]]:
        """Клавиатура для редактирования профиля."""
        buttons = [
            ['📧 Изменить email', '📝 Изменить имя'],
            ['🏷️ Изменить никнейм', '🎂 Изменить дату рождения'],
            ['📱 Изменить телефон'],
            ['🔙 Вернуться в меню'],
        ]
        if is_admin:
            buttons[-1].append('🚧 Перейти в админку')
        return buttons

    async def show_profile(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Показ профиля пользователя."""
        user_data = await self._fetch_user_data(update.effective_user.id)

        profile_text = (
            '👤 Ваш профиль:\n\n'
            f'📧 Email: {user_data.get("email", "не указан")}\n'
            f'📝 Имя: {user_data["name"]}\n'
            f'🏷️ Никнейм: {user_data.get("nickname", "не указан")}\n'
            f'🎂 Дата рождения: {user_data.get("birth_date", "не указана")}\n'
            f'📱 Телефон: {user_data.get("phone_number", "не указан")}\n'
            f'🔞 Возраст подтверждён: ✅'
        )

        keyboard = ReplyKeyboardMarkup(
            self._get_profile_keyboard(user_data.get('is_admin', False)),
            resize_keyboard=True,
        )

        await update.message.reply_text(profile_text, reply_markup=keyboard)
        return EDIT_PROFILE

    async def start_edit_email(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Начало редактирования email."""
        await update.message.reply_text(
            'Введите новый email:', reply_markup=ReplyKeyboardRemove()
        )
        return EDIT_EMAIL

    async def edit_email(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Обработка ввода email."""
        try:
            await self._update_profile(update, 'email', update.message.text)
            await update.message.reply_text('✅ Email успешно обновлен!')
            return await self.show_profile(update, context)
        except Exception as e:
            await update.message.reply_text('❌ Ошибка ❌')
            logging.error(f'{e}')
            return await self.show_profile(update, context)

    async def admin_start_edit_email(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Начало редактирования email."""
        await update.message.reply_text(
            'Введите новый email:', reply_markup=ReplyKeyboardRemove()
        )
        return ADMIN_EDIT_EMAIL

    async def admin_edit_email(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Обработка ввода email."""
        try:
            await self._update_profile(update, 'email', update.message.text)
            await update.message.reply_text('✅ Email успешно обновлен!')
            return await self.show_profile(update, context)
        except Exception as e:
            await update.message.reply_text('❌ Ошибка ❌')
            logging.error(f'{e}')
            return await self.show_profile(update, context)

    async def admin_start_edit_password(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Начало редактирования password."""
        await update.message.reply_text(
            'Введите новый пароль:', reply_markup=ReplyKeyboardRemove()
        )
        return ADMIN_EDIT_PASSWORD

    async def admin_edit_password(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Обработка ввода password."""
        try:
            await self._admin_update_profile(
                update, 'hashed_password', update.message.text
            )
            await update.message.reply_text('✅ Пароль успешно обновлен!')
            return await self.show_profile(update, context)
        except Exception as e:
            await update.message.reply_text('❌ Ошибка ❌')
            logging.error(f'{e}')
            return await self.handle_admin_menu_buttons(update, context)

    async def start_edit_name(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Начало редактирования name."""
        await update.message.reply_text(
            'Введите новое имя:', reply_markup=ReplyKeyboardRemove()
        )
        return EDIT_NAME

    async def edit_name(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Обработка ввода name."""
        try:
            await self._update_profile(update, 'name', update.message.text)
            await update.message.reply_text('✅ Имя успешно обновлено!')
            return await self.show_profile(update, context)
        except Exception as e:
            await update.message.reply_text('❌ Ошибка ❌')
            logging.error(f'{e}')
            return await self.show_profile(update, context)

    async def start_edit_nickname(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Начало редактирования nickname."""
        await update.message.reply_text(
            'Введите новый nickname:', reply_markup=ReplyKeyboardRemove()
        )
        return EDIT_NICKNAME

    async def edit_nickname(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Обработка ввода nickname."""
        try:
            await self._update_profile(update, 'nickname', update.message.text)
            await update.message.reply_text('✅ nickname успешно обновлено!')
            return await self.show_profile(update, context)
        except Exception as e:
            await update.message.reply_text('❌ Ошибка ❌')
            logging.error(f'{e}')
            return await self.show_profile(update, context)

    async def start_edit_birthdate(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Начало редактирования birthdate."""
        await update.message.reply_text(
            'Введите новую дату рождения:', reply_markup=ReplyKeyboardRemove()
        )
        return EDIT_BIRTHDATE

    async def edit_birthdate(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Обработка ввода birthdate."""
        try:
            await self._update_profile(
                update, 'birth_date', update.message.text
            )
            await update.message.reply_text(
                '✅ дата рождения успешно обновлена!'
            )
            return await self.show_profile(update, context)
        except Exception as e:
            await update.message.reply_text('❌ Ошибка ❌')
            logging.error(f'{e}')
            return await self.show_profile(update, context)

    async def start_edit_phone(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Начало редактирования phone."""
        await update.message.reply_text(
            'Введите новый номер телефона формата +7**********:',
            reply_markup=ReplyKeyboardRemove(),
        )
        return EDIT_BIRTHDATE

    async def edit_phone(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Обработка ввода phone."""
        try:
            await self._update_profile(update, 'phone', update.message.text)
            await update.message.reply_text(
                '✅ номерт телефона успешно обновлен!'
            )
            return await self.show_profile(update, context)
        except Exception as e:
            await update.message.reply_text('❌ Ошибка ❌')
            logging.error(f'{e}')
            return await self.show_profile(update, context)

    async def back_to_menu(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Возврат в главное меню."""
        return await self.show_main_menu(update, context)

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
                    f'{API_URL}/users',
                    json={field: value, 'telegram_id': user_telegram_id},
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

    async def show_main_menu(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Показ главного меню."""
        await self.refresh_keyboard(update)
        await update.message.reply_text(
            'Главное меню:', reply_markup=InlineKeyboardMarkup(keyboard_main)
        )
        return MAIN_MENU

    async def _get_main_keyboard(self, user_id: int) -> ReplyKeyboardMarkup:
        """Генерирует главную клавиатуру."""
        user_data = await self._fetch_user_data(user_id)
        is_admin = user_data.get('is_admin', False) if user_data else False

        buttons = [['👤 Просмотреть профиль']]
        if is_admin:
            buttons[0].append('🚧 Перейти в админку')

        return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

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

    async def cancel_conversation(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Отмена текущего диалога."""
        await update.message.reply_text(
            'Действие отменено',
            reply_markup=await self._get_main_keyboard(
                update.effective_user.id
            ),
        )
        return ConversationHandler.END
