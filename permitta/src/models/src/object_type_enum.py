from enum import Enum


class ObjectTypeEnum(Enum):
    DATA_OBJECT: str = "data_object"
    PRINCIPAL: str = "principal"
    PRINCIPAL_ATTRIBUTE: str = "principal_attribute"
    PRINCIPAL_GROUP: str = "principal_group"
