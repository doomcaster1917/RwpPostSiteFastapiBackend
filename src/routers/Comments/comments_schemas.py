from pydantic import BaseModel


class CommentBase(BaseModel):
    pass


class CommentCreateDTO(CommentBase):

     text: str
     owner_id: int
     post_id: int

class CommentEditDTO(CommentBase):

    comment_id: int
    new_comment_text: str


class CommentJoinedDTO(CommentBase):

    comment_id: int
    comment_text: str
    comment_date: str
    owner_id: int
    post_id: int
    post_title: str
    post_img: str
    owner_avatar: str|None
    owner_nickname: str

class NestedCommentDTO(BaseModel):
    comment_text: str
    owner_id: int
    nickname: str
    avatar_path: str|None
    date_made: str
    comment_id: int
    is_owner_locked: bool|None

class UserCommentsDTO(BaseModel):

    comment_id: int|str
    comment_text: str|str
    comment_date: str
    owner_id: int|str
    post_id: int
    title: str
    post_img: str