import os

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
TEMPLATES_DIR = os.path.join(BASE_DIR, 'src', 'admin', 'templates')
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter()


@router.get('/admin/import-fireworks')
async def upload_form(
    request: Request,
):
    return templates.TemplateResponse(
        'sqladmin/csv_manager.html', {'request': request}
    )
