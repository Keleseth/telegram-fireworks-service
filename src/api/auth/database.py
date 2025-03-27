from fastapi_users.db import SQLAlchemyUserDatabase


class CustomUserDB(SQLAlchemyUserDatabase):
    def get_by_email(self, email: str):
        return super().get_by_email(email)
