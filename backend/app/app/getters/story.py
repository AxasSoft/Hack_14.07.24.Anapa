import logging
import datetime
from typing import Optional

from app.models import User
from sqlalchemy import not_
from sqlalchemy.orm import Session

from . import get_hashtag, get_user_short_info, get_story_attachment
from .timestamp import to_timestamp
from ..models import Story, StoryAttachment
from ..models.view import View
from ..models.hug import Hug
from ..schemas import GettingStory


def get_story(db: Session, db_obj: Story, db_user: Optional[User] = None) -> GettingStory:

    videos = [att for att in db_obj.attachments if not att.is_image]
    video = videos[0] if len(videos) > 0 else  None
    images = [att for att in db_obj.attachments if att.is_image]

    a = GettingStory(
        id=db_obj.id,
        created=to_timestamp(db_obj.created),
        user=get_user_short_info(db_obj.user),
        text=db_obj.text,
        video=get_story_attachment(video) if video is not None else None,
        gallery=[get_story_attachment(item) for item in images],
        is_private=db_obj.is_private,
        hashtags=[
            get_hashtag(db, story_hashtag.hashtag) for story_hashtag in db_obj.story_hashtags
        ],
        views_count=len(db_obj.views),
        viewed=len([view for view in db_obj.views if view.user == db_user]) > 0 if db_user is not None else None,
        hugs_count=len(db_obj.hugs),
        hugged=len([hug for hug in db_obj.hugs if hug.user == db_user]) > 0 if db_user is not None else None,
        comments_count=db_obj.comments.count(),
        is_favorite=len([fav for fav in db_obj.favorite_stories if fav.user == db_user]) > 0 if db_user is not None else None,
    )


    return a
