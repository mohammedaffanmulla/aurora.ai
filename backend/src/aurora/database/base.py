from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""


from aurora.database.models import *

target_metadata = Base.metadata