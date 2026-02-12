from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    @classmethod
    def default_order_by(cls) -> None:
        return None
