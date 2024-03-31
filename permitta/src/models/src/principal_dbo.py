from ..src import sql_alchemy
from sqlalchemy.orm import Mapped, mapped_column


class PrincipalDbo(sql_alchemy.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    user_name: Mapped[str] = mapped_column()
    job_title: Mapped[str] = mapped_column()
    tag_name: Mapped[str] = mapped_column()
    tag_value: Mapped[str] = mapped_column()