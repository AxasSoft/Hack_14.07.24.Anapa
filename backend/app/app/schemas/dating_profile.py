import enum
from typing import List, Optional

from app.schemas.profile_avatar import ProfileAvatarBase
from app.schemas.user import Gender, GettingUser
from pydantic import BaseModel, EmailStr, Field

from .dating_profile_like import ProfileLikeBase
from .dating_profile_dislike import ProfileDisLikeBase
from .facts import FactsSubFacts
from .genre_music import GenreMusicSubGenreMusic
from .id_model import IdModel
from .interest import InterestsSubinterests


class DatingProfileBase(BaseModel):
    films: Optional[str]
    book: Optional[str]
    about: Optional[str]
    education: Optional[str]
    work: Optional[str]


class CreatingUpdatingDatingBase(DatingProfileBase):
    sub_interest_id: Optional[List[int]]
    sub_facts_id: Optional[List[int]]
    sub_genre_music_id: Optional[List[int]]


class CreatingDatingProfile(CreatingUpdatingDatingBase):
    pass


class UpdatingDatingProfile(CreatingUpdatingDatingBase):
    pass


class GettingDatingProfile(DatingProfileBase):
    id: int
    user_id: int
    avatar_urls: Optional[List[ProfileAvatarBase]]
    profile_interests: List[InterestsSubinterests]
    profile_facts: List[FactsSubFacts]
    profile_genre_music: List[GenreMusicSubGenreMusic]


class GettingDatingProfileWithUser(BaseModel):
    dating_profile: GettingDatingProfile
    user: GettingUser


class GettingDatingProfileLike(ProfileLikeBase):
    pass

class GettingDatingProfileDislike(ProfileDisLikeBase):
    pass