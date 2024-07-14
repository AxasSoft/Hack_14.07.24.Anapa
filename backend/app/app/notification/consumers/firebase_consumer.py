from typing import Optional, List
import logging

from app.models import Device, Notification
from pyfcm import FCMNotification
from sqlalchemy import desc, func, not_
from sqlalchemy.orm import Session

from .base_consumer import BaseConsumer
from ...models import User, FirebaseToken


class FireBaseConsumer(BaseConsumer):

    def __init__(self, api_key: Optional[str]):
        if api_key is not None and len(api_key) > 0:
            self.push_service = FCMNotification(api_key=api_key)
        else:
            self.push_service = None

    def notify(
            self,
            db: Session,
            recipient: User,
            text: str,
            title: Optional[str] = None,
            icon: Optional[str] = None,
            badge: Optional[int] = None,
            **kwargs
    ):

        old_tokens = []

        badge_count = db.query(func.count('*'))\
            .filter(Notification.user_id == recipient.id, not_(Notification.is_read))\
            .scalar()

        for token in db.query(FirebaseToken)\
                .join(Device)\
                .filter(Device.user == recipient)\
                .order_by(desc(FirebaseToken.created)):

            if self.push_service is not None and token.value is not None and token.value not in old_tokens:

                old_tokens.append(token.value)

                result = self.push_service.notify_single_device(
                    registration_id=token.value,
                    message_title=title or 'Новое уведомление',
                    message_body=text,
                    message_icon=icon,
                    sound='default',
                    badge=badge_count,
                    data_message={"data."+key:value for key,value in kwargs.items()},
                    extra_notification_kwargs={"data."+key:value for key,value in kwargs.items()},
                )
                if int(result.get("success", 0)) > 0:
                    break


    def notify_many(
            self,
            db: Session,
            recipients: List[User],
            text: str,
            title: Optional[str] = None,
            icon: Optional[str] = None,
            **kwargs
    ):

        recipients_id = [user.id for user in recipients]

        badge_map = {
            row[0]: row[1] for row in  db.query(Notification.user_id, func.count('*'))\
                .filter(Notification.user_id.in_(recipients_id), not_(Notification.is_read))\
                .group_by(Notification.user_id)\
                .all()
        }

        old_tokens = []

        for token in db.query(FirebaseToken) \
                .join(Device) \
                .filter(Device.user_id.in_(recipients_id)) \
                .order_by(desc(FirebaseToken.created)):

            if self.push_service is not None and token.value is not None and token.value not in old_tokens:

                old_tokens.append(token.value)

                result = self.push_service.notify_single_device(
                    registration_id=token.value,
                    message_title=title or 'Новое уведомление',
                    message_body=text,
                    message_icon=icon,
                    sound='default',
                    badge=badge_map.get(token.device.user_id,0) if token is not None and token.device is not None else 0,
                    data_message=kwargs,
                    extra_notification_kwargs=kwargs,
                )
