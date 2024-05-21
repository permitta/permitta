import math

from pydantic import BaseModel, Field


class TableQueryDto(BaseModel):
    @property
    def page_count(self) -> int:
        return math.ceil(float(self.record_count) / self.page_size)

    @property
    def previous_page_number(self) -> int:
        return 0 if self.page_number == 0 else self.page_number - 1

    @property
    def next_page_number(self) -> int:
        return min(self.page_number + 1, max(self.page_count - 1, 0))

    @property
    def page_start_record(self) -> int:
        return self.page_number * self.page_size + 1

    @property
    def page_end_record(self) -> int:
        return min((self.page_number + 1) * self.page_size, self.record_count)

    @property
    def next_page_disabled(self) -> bool:
        return self.page_end_record == self.record_count

    @property
    def previous_page_disabled(self) -> bool:
        return self.page_number == 0

    search_term: str = Field(default="")  # TODO validate to avoid sql injection
    sort_key: str = Field(default=None)
    page_number: int = Field(default=0)
    page_size: int = Field(default=20)
    record_count: int = Field(default=0)
