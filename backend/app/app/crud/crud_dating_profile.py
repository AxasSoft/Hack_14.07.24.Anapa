import os
import uuid
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar, Union
from sqlalchemy import exists
from app.api import deps
from app.crud.base import CRUDBase
from app.exceptions import UnfoundEntity
from app.models import (
    DatingProfile,
    Facts,
    GenreMusic,
    Interests,
    ProfileAvatar,
    ProfileFacts,
    ProfileGenreMusic,
    ProfileInterests,
    ProfileLike,
    User,
    ProfileDislike,
)
from app.schemas.dating_profile import (
    CreatingDatingProfile,
    GettingDatingProfile,
    UpdatingDatingProfile,
)
from app.schemas.response import Paginator
from app.schemas.sub_facts import AddUserProfilSubFacts
from app.schemas.sub_genre_music import AddUserProfilSubGenreMusic
from app.schemas.sub_interest import AddUserProfilSubInterest
from app.utils import pagination
from botocore.client import BaseClient
from fastapi import UploadFile
from sqlalchemy.orm import Session, joinedload


class CRUDDatingProfile(
    CRUDBase[DatingProfile, CreatingDatingProfile, UpdatingDatingProfile]
):
    T = TypeVar("T")

    def __init__(self, model: Type[DatingProfile]):
        self.s3_bucket_name: Optional[str] = deps.get_bucket_name()
        self.s3_client: Optional[BaseClient] = deps.get_s3_client()
        super().__init__(model=model)

    # Создание добавление/ Интересов / Важных фактов / Музыка
    def add_other_models_for_dating_profile(
        self,
        db: Session,
        obj_in: T,
        user: User,
        model: Type[T],
        profile_relation_model: Type[ProfileInterests],
        id_field_name: str,
    ) -> List[T]:
        # Удаление существующих записей
        db.query(profile_relation_model).filter(
            profile_relation_model.dating_profile_id == user.dating_profile_id
        ).delete()

        created_objects = []
        for item_id in obj_in.id:
            # Проверка
            item = db.query(model).filter(model.id == item_id).first()
            if not item:
                continue
                # raise UnfoundEntity(message=f"{model.__name__} с идентификатором {item_id} не существует")

            db_user_item = profile_relation_model(
                dating_profile_id=user.dating_profile_id, **{id_field_name: item_id}
            )
            db.add(db_user_item)
            created_objects.append(db_user_item)

        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise e

        for db_user_item in created_objects:
            db.refresh(db_user_item)

        return created_objects

    # Загрузка изображений для профиля знакомств
    def upload_image_to_s3(
        self, db: Session, db_obj: DatingProfile, image: UploadFile
    ) -> Optional[ProfileAvatar]:
        host = self.s3_client._endpoint.host
        bucket_name = self.s3_bucket_name
        url_prefix = host + "/" + bucket_name + "/"
        name = (
            "dating_profile/images/"
            + uuid.uuid4().hex
            + os.path.splitext(image.filename)[1]
        )
        new_url = url_prefix + name

        result = self.s3_client.put_object(
            Bucket=bucket_name,
            Key=name,
            Body=image.file,
            ContentType=image.content_type,
        )

        if not (
            200 <= result.get("ResponseMetadata", {}).get("HTTPStatusCode", 500) < 300
        ):
            return None

        avatar = ProfileAvatar()
        avatar.dating_profile_id = db_obj.id
        avatar.url = new_url
        db.add(avatar)
        db.commit()
        db.refresh(avatar)

        return avatar

    def create_with_user(
        self, db: Session, *, obj_in: CreatingDatingProfile, user: User
    ) -> GettingDatingProfile:
        # obj_in_data = obj_in.dict(exclude_unset=True)
        db_obj = DatingProfile(
            user_id=user.id,
            films=obj_in.films,
            book=obj_in.book,
            about=obj_in.about,
            education=obj_in.education,
            work=obj_in.work,
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # Обновляем поле is_dating_profile в модели User
        user.is_dating_profile = True
        user.dating_profile_id = db_obj.id
        db.add(user)
        db.commit()
        db.refresh(user)

        if obj_in.sub_interest_id:
            sub_interest_obj = AddUserProfilSubInterest(id=obj_in.sub_interest_id)
            self.add_other_models_for_dating_profile(
                db=db,
                obj_in=sub_interest_obj,
                user=user,
                model=Interests,
                profile_relation_model=ProfileInterests,
                id_field_name="interest_id",
            )

        if obj_in.sub_facts_id:
            sub_facts_obj = AddUserProfilSubFacts(id=obj_in.sub_facts_id)
            self.add_other_models_for_dating_profile(
                db=db,
                obj_in=sub_facts_obj,
                user=user,
                model=Facts,
                profile_relation_model=ProfileFacts,
                id_field_name="subfacts_id",
            )

        if obj_in.sub_genre_music_id:
            sub_genre_music_obj = AddUserProfilSubGenreMusic(
                id=obj_in.sub_genre_music_id
            )
            self.add_other_models_for_dating_profile(
                db=db,
                obj_in=sub_genre_music_obj,
                user=user,
                model=GenreMusic,
                profile_relation_model=ProfileGenreMusic,
                id_field_name="sub_genre_music_id",
            )

        return db_obj

    def get_by_user_id(self, db: Session, user_id: Any) -> GettingDatingProfile:
        profile = (
            db.query(DatingProfile)
            .options(
                joinedload(DatingProfile.profile_interests)
                .joinedload(ProfileInterests.interest)
                .joinedload(Interests.subinterests)
            )
            .filter(DatingProfile.user_id == user_id)
            .first()
        )

        return profile

    # def get_by_filter(self, db: Session, filter_by: Any) -> GettingDatingProfile:
    #         return db.query(DatingProfile).filter(filter_by).first()

    def update_dating_profile(
        self,
        db: Session,
        *,
        user: User,
        db_obj: DatingProfile,
        obj_in: Union[UpdatingDatingProfile, Dict[str, Any]],
    ) -> GettingDatingProfile:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        if "sub_interest_id" in update_data:
            sub_interest_obj = AddUserProfilSubInterest(
                id=update_data["sub_interest_id"]
            )
            self.add_other_models_for_dating_profile(
                db=db,
                obj_in=sub_interest_obj,
                user=user,
                model=Interests,
                profile_relation_model=ProfileInterests,
                id_field_name="interest_id",
            )

        if "sub_facts_id" in update_data:
            sub_facts_obj = AddUserProfilSubFacts(id=update_data["sub_facts_id"])
            self.add_other_models_for_dating_profile(
                db=db,
                obj_in=sub_facts_obj,
                user=user,
                model=Facts,
                profile_relation_model=ProfileFacts,
                id_field_name="subfacts_id",
            )

        if "sub_genre_music_id" in update_data:
            sub_genre_music_obj = AddUserProfilSubGenreMusic(
                id=update_data["sub_genre_music_id"]
            )
            self.add_other_models_for_dating_profile(
                db=db,
                obj_in=sub_genre_music_obj,
                user=user,
                model=GenreMusic,
                profile_relation_model=ProfileGenreMusic,
                id_field_name="sub_genre_music_id",
            )

        return db_obj

    def add_dating_profile_photo(
        self, db: Session, *, db_obj: DatingProfile, images: List[UploadFile]
    ):
        for image in images:
            self.upload_image_to_s3(db, db_obj, image)

        return

    def get_image_by_id(self, db: Session, id: Any):
        return db.query(ProfileAvatar).filter(ProfileAvatar.id == id).first()

    def delete_image(self, db: Session, *, image: ProfileAvatar) -> None:
        db.delete(image)
        db.commit()

    def delete_dating_profile(self, db: Session, user: User):
        if user.dating_profile_id is not None:
            dating_profile = (
                db.query(DatingProfile)
                .filter(DatingProfile.id == user.dating_profile_id)
                .first()
            )

            if dating_profile:
                users_with_dating_profile = (
                    db.query(User)
                    .filter(User.dating_profile_id == dating_profile.id)
                    .all()
                )
                for u in users_with_dating_profile:
                    u.is_dating_profile = False
                    u.dating_profile_id = None

                db.delete(dating_profile)
                db.commit()
            else:
                raise UnfoundEntity(message="Профиль для знакомств не найден")
        else:
            raise UnfoundEntity(message="У пользователя нет профиля для знакомств")

    def get_search_dating_profiles(
        self,
        db: Session,
        user: User,
        page: Optional[int] = None,
        per_page: int = 30,
        gender_filter: str = None,
        age_filter: int = None,
        relationship_type_filter: str = None,
    ):
        offset = (page - 1) * per_page
        current_dating_profile_id = user.dating_profile_id

        query = db.query(DatingProfile).filter(
            DatingProfile.id != current_dating_profile_id
        )

        liked_profiles = (
            db.query(ProfileLike.liked_dating_profile_id)
            .filter(ProfileLike.liker_dating_profile_id == current_dating_profile_id)
            .subquery()
        )

        disliked_profiles = (
            db.query(ProfileDislike.disliked_dating_profile_id)
            .filter(ProfileDislike.disliker_dating_profile_id == current_dating_profile_id)
            .subquery()
        )

        query = query.filter(DatingProfile.id.notin_(liked_profiles))
        query = query.filter(DatingProfile.id.notin_(disliked_profiles))

        if gender_filter:
            query = query.filter(DatingProfile.gender == gender_filter)
        if age_filter:
            query = query.filter(DatingProfile.age == age_filter)
        if relationship_type_filter:
            query = query.filter(
                DatingProfile.relationship_type == relationship_type_filter
            )

        query = query.join(User, User.id == DatingProfile.user_id)
        query = query.add_columns(User)

        profiles = query.offset(offset).limit(per_page).all()

        result = []
        for profile, user in profiles:
            profile_info = {"profile": profile, "user": user}
            result.append(profile_info)

        return result

    def save_like(self, db: Session, user: User, liked_dating_profile_id: int) -> ProfileLike:
        # Проверяем на взаим
        mutual_like_exists = db.query(exists().where(
            ProfileLike.liker_dating_profile_id == liked_dating_profile_id,
            ProfileLike.liked_dating_profile_id == user.dating_profile_id
        )).scalar()

        like = ProfileLike(
            liker_dating_profile_id=user.dating_profile_id,
            liked_dating_profile_id=liked_dating_profile_id,
            mutual=mutual_like_exists 
        )
        
        db.add(like)
        db.commit()
        db.refresh(like)

        return like
    
    def save_dislike(self, db: Session, user: User, disliked_dating_profile_id: int) -> ProfileDislike:
        dislike = ProfileDislike(
            disliker_dating_profile_id=user.dating_profile_id,
            disliked_dating_profile_id=disliked_dating_profile_id,
        )
        
        db.add(dislike)
        db.commit()
        db.refresh(dislike)
        return dislike

    def get_like_dating_profile(self, db: Session, user: User) -> List[GettingDatingProfile]:
        # Запрашиваем все лайки, где пользователь является  получившим лайк
        likes = db.query(ProfileLike).filter(
            ProfileLike.liked_dating_profile_id == user.dating_profile_id
        ).all()
        dating_profiles = []
        
        for like in likes:
            profile = like.liker_profile
            user = db.query(User).filter(
            User.id == like.liker_profile.user_id
            ).first()
            dating_profiles.append({"profile": profile, "user": user})

        return dating_profiles

dating_profile = CRUDDatingProfile(DatingProfile)
