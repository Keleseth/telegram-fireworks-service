import contextlib

import anyio  # встроенная зависимость FastAPI
from fastapi import Request, UploadFile
from sqladmin import BaseView, expose
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from src.database.db_dependencies import get_async_session
from src.service.csv_loader import load_data

CSV_DESTINATION = 'price.csv'
templates = Jinja2Templates(directory='src/admin/templates')


class AdminUploadCSVView(BaseView):
    name = 'Загрузка CSV'
    icon = 'fa-upload'
    slug = 'upload-csv'

    @expose('/upload', methods=['GET', 'POST'])
    async def upload(self, request: Request):
        if request.method == 'POST':
            form = await request.form()
            file: UploadFile = form['file']
            content = await file.read()

            # Записываем синхронно, но в отдельном потоке
            def write_file() -> None:
                with open(CSV_DESTINATION, 'wb') as buffer:
                    buffer.write(content)

            await anyio.to_thread.run_sync(write_file)

            session_gen = get_async_session()
            session = await anext(session_gen)
            try:
                await load_data(session)
            finally:
                with contextlib.suppress(StopAsyncIteration):
                    await anext(session_gen)

            return RedirectResponse(url=request.url.path, status_code=303)

        return templates.TemplateResponse(
            'sqladmin/upload_csv.html', {'request': request}
        )
