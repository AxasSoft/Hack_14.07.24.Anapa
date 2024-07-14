from typing import Optional, List

from pydantic import BaseModel, Field

from . import GettingUserShortInfo, GettingEventCategory
from .id_model import IdModel
from .image import GettingImage
from ..enums.mod_status import ModStatus
from ..models.event_member import AcceptingStatus


class CreatingEvent(BaseModel):
    name: Optional[str]
    description: Optional[str]
    # type_: str
    started: int
    ended: Optional[int]
    # period: Optional[str]
    is_private: bool
    # price: int = Field(0)
    # start_link: Optional[str]
    # report_link: Optional[str]
    place: Optional[str]
    lat: float
    lon: float
    members: List[int]
    max_event_members: Optional[int]
    category_id: Optional[int]
    age: int
    link: Optional[str]


class UpdatingEvent(BaseModel):
    name: Optional[str]
    description: Optional[str]
    # type_: str
    started: Optional[int]
    ended: Optional[int]
    # period: Optional[str]
    is_private: Optional[bool]
    # price: int = Field(0)
    # start_link: Optional[str]
    # report_link: Optional[str]
    place: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    age: Optional[int]
    members: Optional[List[int]]
    max_event_members: Optional[int]
    category_id: Optional[int]
    link: Optional[str]


class GettingEventMember(IdModel, BaseModel):
    user: GettingUserShortInfo
    status: AcceptingStatus


class GettingEvent(IdModel, BaseModel):
    created: int
    name: Optional[str]
    description: Optional[str]
    # type_: str
    started: int
    ended: Optional[int]
    # period: Optional[str]
    is_private: bool
    # price: int = Field(0)
    # start_link: Optional[str]
    # report_link: Optional[str]
    place: Optional[str]
    lat: float
    lon: float
    age: Optional[int]
    user: GettingUserShortInfo
    members: List[GettingEventMember]
    images: List[GettingImage]
    max_event_members: Optional[int]
    category: Optional[GettingEventCategory]
    link: Optional[str]
    status: ModStatus
    moderation_comment: Optional[str]



class StatusBody(BaseModel):
    status: AcceptingStatus


class CreatingEventMember(BaseModel):
    user_id: int
    status: AcceptingStatus


class ModerationBody(BaseModel):
    status: ModStatus
    comment: Optional[str]