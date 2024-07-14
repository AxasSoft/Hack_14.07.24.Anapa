from typing import Dict, List, Optional, Type

from app import getters
from app.models import DatingProfile, ProfileLike, User, ProfileDislike
from app.schemas import (
    FactsSubFacts,
    GenreMusicSubGenreMusic,
    GettingDatingProfile,
    GettingDatingProfileWithUser,
    InterestsSubinterests,
    SubFacts,
    SubGenreMusic,
    Subinterest,
    GettingDatingProfileLike,
    GettingDatingProfileDislike,
)
from sqlalchemy.orm import Session


def get_dating_profile(dating_profile: DatingProfile) -> GettingDatingProfile:
    profile_interests = process_interests(dating_profile)
    profile_facts = process_facts(dating_profile)
    profile_genre_music = process_genre_music(dating_profile)

    avatar_urls = (
        [{"id": avatar.id, "url": avatar.url} for avatar in dating_profile.avatars]
        if dating_profile.avatars
        else None
    )

    return GettingDatingProfile(
        id=dating_profile.id,
        user_id=dating_profile.user_id,
        films=dating_profile.films,
        book=dating_profile.book,
        about=dating_profile.about,
        education=dating_profile.education,
        work=dating_profile.work,
        avatar_urls=avatar_urls,
        profile_interests=profile_interests,
        profile_facts=profile_facts,
        profile_genre_music=profile_genre_music,
    )


def get_dating_profile_with_user(
    db: Session, dating_profile: DatingProfile, user: User
) -> GettingDatingProfileWithUser:
    dating_profile_data = get_dating_profile(dating_profile)
    user_data = getters.user.get_user(db, user, user)

    return GettingDatingProfileWithUser(
        dating_profile=dating_profile_data,
        user=user_data,
    )


def get_dating_profile_like(
    obj: ProfileLike,
) -> GettingDatingProfileLike:
    return GettingDatingProfileLike(
        id=obj.id,
        liker_dating_profile_id=obj.liker_dating_profile_id,
        liked_dating_profile_id=obj.liked_dating_profile_id,
        mutual=obj.mutual
    )

def get_dating_profile_dislike(
        obj: ProfileDislike
        ) -> GettingDatingProfileDislike:
    return GettingDatingProfileDislike(
        id=obj.id,
        disliker_dating_profile_id=obj.disliker_dating_profile_id,
        disliked_dating_profile_id=obj.disliked_dating_profile_id
    )


# Обработка интересов
def process_interests(dating_profile: DatingProfile) -> List[InterestsSubinterests]:
    interests_dict: Dict[int, Dict] = {}

    for profile_interest in dating_profile.profile_interests:
        subinterest = profile_interest.interest
        interest_id = subinterest.parent_interest_id
        name_interes = (
            subinterest.subinterests.interest_name if subinterest.subinterests else None
        )

        if interest_id not in interests_dict:
            interests_dict[interest_id] = {
                "interest_id": interest_id,
                "interest_name": name_interes,
                "subinterests": [],
            }

        interests_dict[interest_id]["subinterests"].append(
            Subinterest(
                subinterest_id=subinterest.id,
                subinterest_name=subinterest.interest_name,
            )
        )

    # Преобразуем словарь в список InterestsSubinterests
    return [
        InterestsSubinterests(
            interest_id=data["interest_id"],
            interest_name=data["interest_name"],
            subinterests=data["subinterests"],
        )
        for data in interests_dict.values()
    ]


# Обработка фактов
def process_facts(dating_profile: DatingProfile) -> List[FactsSubFacts]:
    facts_dict: Dict[int, Dict] = {}

    for profile_fact in dating_profile.profile_facts:
        subfact = profile_fact.facts
        fact_id = subfact.parent_facts.id
        name_fact = subfact.parent_facts.facts_name if subfact.parent_facts else None

        if fact_id not in facts_dict:
            facts_dict[fact_id] = {
                "facts_id": fact_id,
                "facts_name": name_fact,
                "sub_facts": [],
            }

        facts_dict[fact_id]["sub_facts"].append(
            SubFacts(sub_facts_id=subfact.id, sub_facts_name=subfact.facts_name)
        )

    return [
        FactsSubFacts(
            facts_id=data["facts_id"],
            facts_name=data["facts_name"],
            sub_facts=data["sub_facts"],
        )
        for data in facts_dict.values()
    ]


# Обработка жанров музыки


def process_genre_music(dating_profile: DatingProfile) -> List[GenreMusicSubGenreMusic]:
    genre_music_dict: Dict[int, Dict] = {}

    for profile_genre_music in dating_profile.profile_genre_music:
        sub_genre_music = profile_genre_music.genre_music
        genre_music_id = sub_genre_music.parent_genre_music.id
        name_genre_music = (
            sub_genre_music.parent_genre_music.genre_music_name
            if sub_genre_music.parent_genre_music
            else None
        )

        if genre_music_id not in genre_music_dict:
            genre_music_dict[genre_music_id] = {
                "genre_music_id": genre_music_id,
                "genre_music_name": name_genre_music,
                "sub_genre_music": [],
            }

        genre_music_dict[genre_music_id]["sub_genre_music"].append(
            SubGenreMusic(
                sub_genre_music_id=sub_genre_music.id,
                sub_genre_music_name=sub_genre_music.genre_music_name,
            )
        )

    return [
        GenreMusicSubGenreMusic(
            genre_music_id=data["genre_music_id"],
            genre_music_name=data["genre_music_name"],
            sub_genre_music=data["sub_genre_music"],
        )
        for data in genre_music_dict.values()
    ]
