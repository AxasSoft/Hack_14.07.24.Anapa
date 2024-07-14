from typing import Optional, Union, Dict, Any, Type, List
import os
import uuid
import datetime as dt

from botocore.client import BaseClient
from sqlalchemy import text, alias, func, or_, and_
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.crud.base import CRUDBase
from app.enums.mod_status import ModStatus
from app.models import User, EventMember, AcceptingStatus, EventImage
from app.models.event import Event
from app.schemas.event import CreatingEvent, UpdatingEvent, ModerationBody
from app.utils import pagination
from app.utils.datetime import from_unix_timestamp




class CRUDEvent(CRUDBase[Event, CreatingEvent, UpdatingEvent]):

    def __init__(self, model: Type[Event]):

        self.s3_bucket_name: Optional[str] = None
        self.s3_client: Optional[BaseClient] = None
        super().__init__(model=model)

    def get_image_by_id(self, db: Session, id: Any):
        return db.query(EventImage).filter(EventImage.id == id).first()

    def add_image(self, db: Session, *, event: Event, image: UploadFile, num: Optional[int] = None) -> Optional[EventImage]:

        host = self.s3_client._endpoint.host

        bucket_name = self.s3_bucket_name

        url_prefix = host + '/' + bucket_name + '/'

        name = 'event/images/' + uuid.uuid4().hex + os.path.splitext(image.filename)[1]

        new_url = url_prefix + name

        result = self.s3_client.put_object(
            Bucket=bucket_name,
            Key=name,
            Body=image.file,
            ContentType=image.content_type
        )

        if not (200 <= result.get('ResponseMetadata', {}).get('HTTPStatusCode', 500) < 300):
            return None

        image = EventImage()
        image.event = event
        image.image = new_url
        image.num = num
        db.add(image)

        db.commit()
        db.refresh(event)

        return image

    def delete_image(self, db: Session, *, image: EventImage) -> None:
        event = image.event
        event.updated = dt.datetime.utcnow()
        db.add(event)
        db.delete(image)
        db.commit()

    def search(
            self,
            db: Session,
            name: Optional[str] = None,
            started_from: Optional[int]= None,
            started_to: Optional[int]= None,
            ended_from: Optional[int]= None,
            ended_to: Optional[int]= None,
            # price_from: Optional[int]= None,
            # price_to: Optional[int]= None,
            place: Optional[str]= None,
            current_lon: Optional[float]= None,
            current_lat: Optional[float]= None,
            current_user: Optional[User] = None,
            distance: Optional[int]= None,
            page:Optional[int]= None,
            for_su: bool = False,
            is_private: Optional[bool] = None,
            user_id: Optional[int] = None,
            creator_id: Optional[int] = None,
            statuses: Optional[List[ModStatus]] = None
    ):
        query = db.query(self.model)

        if user_id is not None:
            query = query.filter(EventMember.user_id == user_id)

        if creator_id is not None:
            query = query.filter(Event.user_id == creator_id)

        if is_private is not None:
            query = query.filter(Event.is_private == is_private)

        if not for_su and current_user is not None and user_id is None:

            query = query.join(EventMember, isouter=True).filter(
                or_(
                    Event.is_private == False,
                    and_(
                        Event.is_private == True,
                        or_(
                            EventMember.user_id == current_user.id,
                            Event.user_id == current_user.id,
                        )
                    )
                )
            )

        if name is not None:
            query = query.filter(self.model.name.ilike(f'@{name}%'))

        if started_from is not None:
            query = query.filter(self.model.started >= from_unix_timestamp(started_from))

        if started_to is not None:
            query = query.filter(self.model.started <= from_unix_timestamp(started_to))

        if ended_from is not None:
            query = query.filter(self.model.ended >= from_unix_timestamp(ended_from))

        if ended_to is not None:
            query = query.filter(self.model.ended <= from_unix_timestamp(ended_to))

        # if price_from is not None:
        #     query = query.filter(self.model.price >= price_from)
        #
        # if price_to is not None:
        #     query = query.filter(self.model.price <= price_to)

        if place is not None:
            query = query.filter(self.model.place.ilike(f'%{place}%'))

        if statuses is not None and len(statuses) > 0:
            query = query.filter(self.model.status.in_(statuses))

        if all(x is not None for x in (current_lon, current_lat, distance,)):

            sq = db.query(
                self.model.id.label('event_id'),
                func.st_distancespheroid(
                    text('''ST_SetSRID(ST_MakePoint(event.lat, event.lon), 4326)'''),
                    text('''ST_SetSRID(ST_MakePoint(:current_lat, :current_lon), 4326)''').bindparams(
                        current_lat=current_lat,
                        current_lon=current_lon
                    ),
                ).label('d')
            ).subquery()

            query = query.join(sq, sq.c.event_id == self.model.id,isouter=True).filter(sq.c.d < distance).order_by(sq.c.d)

        return pagination.get_page(query,page)


    def create_for_user(self, db: Session, *, obj_in: CreatingEvent, user: User) -> Event:
        db_obj = self.model()
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if 'started' in update_data:
            update_data['started'] = from_unix_timestamp(update_data['started'])
        if 'ended' in update_data:
            update_data['ended'] = from_unix_timestamp(update_data['ended'])
        if update_data.get('age', None) is None:
            update_data['age'] = 0
        member_ids = update_data.pop('members')

        for field in dir(db_obj):
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db_obj.user = user

        db.add(db_obj)

        for member_id in member_ids:
            event_member = EventMember()
            event_member.event = db_obj
            event_member.user_id = member_id
            db.add(event_member)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: Event,
        obj_in: Union[UpdatingEvent, Dict[str, Any]]
    ) -> Event:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if 'started' in update_data:
            update_data['started'] = from_unix_timestamp(update_data['started'])
        if 'ended' in update_data:
            update_data['ended'] = from_unix_timestamp(update_data['ended'])
        for field in dir(db_obj):
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)


        if 'members' in update_data:

            member_ids = update_data.pop('members')
            member_statuses = {

            }

            for em in db.query(EventMember).filter(EventMember.event_id == db_obj.id).all():
                member_statuses[em.user_id] = em.status
                db.delete(em)

            for member_id in member_ids:
                event_member = EventMember()
                event_member.event = db_obj
                event_member.user_id = member_id
                event_member.status = member_statuses.get(member_id, AcceptingStatus.wait)
                db.add(event_member)

        db.commit()
        db.refresh(db_obj)
        return db_obj


    def edit_member_status(self, db: Session, *, event_member: EventMember, new_status: AcceptingStatus) -> EventMember:
        event_member.status = new_status
        db.add(event_member)
        db.commit()
        db.refresh(event_member)
        return event_member


    def member_exist(self, db: Session, user_id: int, event_id: int) -> bool:
        return db.query(EventMember).filter(EventMember.user_id == user_id, EventMember.event_id == event_id).first() is not None

    def add_member(self, db: Session, user_id: int, event_id: int, status: AcceptingStatus) -> EventMember:
        event_member = EventMember()
        event_member.event_id = event_id
        event_member.user_id = user_id
        event_member.status = status
        db.add(event_member)
        db.commit()
        db.refresh(event_member)
        return event_member


    def delete_member(self, db: Session, *, event_member: EventMember) -> None:
        db.delete(event_member)
        db.commit()


    def get_member(self, db: Session, event_member_id: int) -> Optional[EventMember]:
        return db.query(EventMember).filter(EventMember.id == event_member_id).first()

    def moderate(self, db: Session, *, event: Event, moderation_body: ModerationBody):
        event.status = moderation_body.status
        event.moderation_comment = moderation_body.comment
        db.add(event)
        db.commit()
        return event

event = CRUDEvent(Event)