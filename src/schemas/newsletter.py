from pydantic import BaseModel


class NewsletterBase(BaseModel):
    pass


class NewsletterCreate(NewsletterBase):
    pass


class NewsletterUpdate(NewsletterBase):
    pass
