from dataclasses import dataclass


@dataclass
class PrincipalDio:
    source_uid: str
    first_name: str
    last_name: str
    user_name: str
    email: str


@dataclass
class PrincipalAttributeDio:
    source_uid: str
    attribute_key: str
    attribute_value: str


@dataclass
class DataObjectTableDio:
    source_uid: str


@dataclass
class DataObjectColumnDio:
    source_uid: str


@dataclass
class DataObjectAttributeDio:
    source_uid: str
    attribute_key: str
    attribute_value: str
