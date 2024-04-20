from ..src.table_query_dto import TableQueryDto


def test_props():
    dto = TableQueryDto(sort_key="sort_key")
    assert dto.page_count == 0
    assert dto.page_start_record == 1
    assert dto.page_end_record == 0

    assert dto.previous_page_number == 0
    assert dto.previous_page_disabled

    assert dto.next_page_number == 0
    assert dto.next_page_disabled

    dto = TableQueryDto(page_number=0, page_size=50, record_count=244)
    assert dto.page_count == 5

    assert dto.page_start_record == 1
    assert dto.page_end_record == 50

    assert dto.previous_page_number == 0
    assert dto.previous_page_disabled

    assert dto.next_page_number == 1
    assert not dto.next_page_disabled

    dto = TableQueryDto(page_size=50, page_number=1, record_count=244)
    assert dto.page_start_record == 51
    assert dto.page_end_record == 100

    assert dto.previous_page_number == 0
    assert not dto.previous_page_disabled

    assert dto.next_page_number == 2
    assert not dto.next_page_disabled

    dto = TableQueryDto(page_size=50, page_number=4, record_count=244)
    assert dto.page_start_record == 201
    assert dto.page_end_record == 244

    assert dto.previous_page_number == 3
    assert not dto.previous_page_disabled

    assert dto.next_page_number == 4
    assert dto.next_page_disabled
