from app.getters import get_user_short_info, get_event_category
from app.models import Event, EventMember
from app.schemas import GettingEvent, GettingEventMember, GettingImage
from app.utils.datetime import to_unix_timestamp


def get_event_member(event_member: EventMember) -> GettingEventMember:
    return GettingEventMember(
        id=event_member.id,
        user=get_user_short_info(event_member.user),
        status=event_member.status,
    )


def get_event(event: Event) -> GettingEvent:
    return GettingEvent(
        id=event.id,
        created=to_unix_timestamp(event.created),
        name=event.name,
        description=event.description,
        # type_=event.type_,
        started=to_unix_timestamp(event.started),
        # period=event.period,
        ended=to_unix_timestamp(event.ended),
        is_private=event.is_private,
        place=event.place,
        lat=event.lat,
        lon=event.lon,
        # price=event.price,
        # start_link=event.start_link,
        # report_link=event.report_link,
        user=get_user_short_info(event.user),
        images=[
            GettingImage(
                id=image.id,
                link=image.image
            )
            for image in event.images
        ],
        members=[
            get_event_member(event_member=member)
            for member in event.event_members
        ],
        category=get_event_category(event.category) if event.category else None,
        link=event.link,
        status=event.status,
        moderation_comment=event.moderation_comment
    )
