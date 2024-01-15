from pydantic import BaseModel
from src.models import intpk, created_at_type
from ..Comments.comments_schemas import NestedCommentDTO


class PostBaseDTO(BaseModel):

    id: intpk
    title: str
    text: str
    date_made: created_at_type|str
    img_path: str

    class Config:
        arbitrary_types_allowed = True

class PostDTO(PostBaseDTO):

    comments: list[NestedCommentDTO] = []











