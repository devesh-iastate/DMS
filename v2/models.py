from pydantic import BaseModel
from pydantic.class_validators import Optional


class Filter(BaseModel):
    # filter_id: int
    category_id: str
    train_size: float
    test_size: float
    validation_size: float
    sample_size: int
    user: str

    # @validator(train_size, test_size, validation_size)


class DataFilter(BaseModel):
    filter_id: int
    data_type: str
    fetch_meta_data: Optional[bool] = False


class User(BaseModel):
    username: str


class DataCategory(BaseModel):
    category_name: str


class SearchParameters(BaseModel):
    search_terms: str = None
    category_name: str = None

