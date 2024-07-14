from typing import List, Optional

from app import crud, getters, models, schemas
from app.api import deps
from app.core.config import settings
from app.schemas.response import Meta
from botocore.client import BaseClient
from fastapi import APIRouter, Body, Depends, File, Form, Header, Query, UploadFile
from fastapi.params import File, Path
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import StreamingResponse

from ....exceptions import UnfoundEntity, UnprocessableEntity
from ....notification.notificator import Notificator
from ....schemas import GettingStat, SubscribeBody

router = APIRouter()

# @router.post(
#     '/cp/dating/profile/create/',
#     response_model=schemas.SingleEntityResponse[schemas.GettingDatingProfile],
#     tags=['Административная панель / Профиль знакомств'],
#     name="Создать профиль знакомств",
#     responses={
#         401: {
#             'model': schemas.OkResponse,
#             'description': 'Пользователь не прошёл авторизацию'
#         }
#     }
# )
# def get_current_super_user(
#     dating_profile: schemas.dating_profile.CreatingDatingProfile,
#     request: Request,
#     db: Session = Depends(deps.get_db),
#     current_user: models.User = Depends(deps.get_current_active_user),
# ):
#     existing_profile = crud.dating_profile.get_by_user_id(db, user_id=current_user.id)
#     if existing_profile:
#         raise UnfoundEntity(
#             message="Профиль знакомств уже существует"
#         )

#     new_profile = crud.dating_profile.create_with_user(db, obj_in=dating_profile, user=current_user)

#     return schemas.SingleEntityResponse(
#         data=getters.dating_profile.get_dating_profile(new_profile)
#     )


@router.post(
    "/dating/profile/create/",
    response_model=schemas.SingleEntityResponse[schemas.GettingDatingProfile],
    name="Создать профиль знакомств текущему пользователю",
    tags=["Мобильное приложение / Профиль знакомств"],
    responses={
        401: {
            "model": schemas.OkResponse,
            "description": "Пользователь не прошёл авторизацию",
        }
    },
)
def add_current_user(
    dating_profile: schemas.dating_profile.CreatingDatingProfile,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    existing_profile = crud.dating_profile.get_by_user_id(db, user_id=current_user.id)
    if existing_profile:
        raise UnfoundEntity(message="Профиль знакомств уже существует")

    new_profile = crud.dating_profile.create_with_user(
        db, obj_in=dating_profile, user=current_user
    )

    return schemas.SingleEntityResponse(
        data=getters.dating_profile.get_dating_profile(new_profile)
    )


@router.post(
    "/dating/profile/add/images/",
    response_model=schemas.SingleEntityResponse[schemas.GettingDatingProfile],
    name="Добавить фото в профиль знакомств текущему пользователю",
    tags=["Мобильное приложение / Профиль знакомств"],
    responses={
        401: {
            "model": schemas.OkResponse,
            "description": "Пользователь не прошёл авторизацию",
        }
    },
)
def add_current_user(
    images: List[UploadFile] = File(...),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    s3_client: BaseClient = Depends(deps.get_s3_client),
    s3_bucket_name: str = Depends(deps.get_bucket_name),
):
    existing_profile = crud.dating_profile.get_by_user_id(db, user_id=current_user.id)
    if existing_profile is None:
        raise UnfoundEntity(message="Профиль знакомств не существует")
    crud.dating_profile.s3_client = s3_client
    crud.dating_profile.s3_bucket_name = s3_bucket_name

    new_photo = crud.dating_profile.add_dating_profile_photo(
        db, images=images, db_obj=existing_profile
    )

    return schemas.SingleEntityResponse(
        data=getters.dating_profile.get_dating_profile(existing_profile)
    )


@router.delete(
    "/dating/profile/del/{image_id}/",
    response_model=schemas.response.SingleEntityResponse[schemas.GettingDatingProfile],
    name="Удалить изображение профиля знакомств",
    responses={
        400: {
            "model": schemas.response.OkResponse,
            "description": "Переданы невалидные данные",
        },
        422: {
            "model": schemas.response.OkResponse,
            "description": "Переданы некорректные данные",
        },
        403: {
            "model": schemas.response.OkResponse,
            "description": "Отказано в доступе",
        },
    },
    tags=["Мобильное приложение / Профиль знакомств"],
)
def delete_image(
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
    s3_client: BaseClient = Depends(deps.get_s3_client),
    s3_bucket_name: str = Depends(deps.get_bucket_name),
    image_id: int = Path(..., title="Идентификатор объявления"),
):
    existing_profile = crud.dating_profile.get_by_user_id(db, user_id=current_user.id)
    if existing_profile is None:
        raise UnfoundEntity(message="Профиля знакомств не существует")
    image = crud.dating_profile.get_image_by_id(db=db, id=image_id)
    if image is None:
        raise UnfoundEntity(num=1, message="Картинка не найдена")

    crud.crud_order.order.s3_client = s3_client
    crud.crud_order.order.s3_bucket_name = s3_bucket_name
    crud.dating_profile.delete_image(db=db, image=image)
    return schemas.SingleEntityResponse(
        data=getters.dating_profile.get_dating_profile(existing_profile)
    )


@router.get(
    "/dating/profile/",
    response_model=schemas.SingleEntityResponse[schemas.GettingDatingProfileWithUser],
    name="Получить профиль знакомств текущего пользователя",
    tags=["Мобильное приложение / Профиль знакомств"],
    responses={
        401: {
            "model": schemas.OkResponse,
            "description": "Пользователь не прошёл авторизацию",
        }
    },
)
def get_current_user(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    existing_profile = crud.dating_profile.get_by_user_id(db, user_id=current_user.id)
    if existing_profile is None:
        raise UnfoundEntity(message="У пользователя нет профиля для знакомств")
    return schemas.SingleEntityResponse(
        data=getters.dating_profile.get_dating_profile_with_user(
            db, existing_profile, current_user
        )
    )


# @router.get(
#     '/cp/dating/profile/{user_id}',
#     response_model=schemas.SingleEntityResponse[schemas.GettingDatingProfile],
#     tags=['Административная панель / Профиль знакомств'],
#     name="Получить профиль знакомств по идентификатору пользователя",
#     responses={
#         401: {
#             'model': schemas.OkResponse,
#             'description': 'Пользователь не прошёл авторизацию'
#         }
#     }
# )
# def get_current_user(
#     db: Session = Depends(deps.get_db),
#     user: models.User = Depends(deps.get_current_active_superuser),
#     user_id: Optional[int] = Path(..., title="Идентификатор пользователя"),
# ):
#     existing_profile = crud.dating_profile.get_by_user_id(db, user_id=user_id)
#     if existing_profile is None:
#         raise UnfoundEntity(message="Пользователь не найден")
#     return schemas.SingleEntityResponse(
#         data=getters.dating_profile.get_dating_profile(existing_profile)
#     )


@router.put(
    "/dating/profile/edit/",
    response_model=schemas.SingleEntityResponse[schemas.GettingDatingProfile],
    name="Изменить профиль знакомств текущего пользователя",
    description="Любые поля запроса могут быть опущены. Измененены будут только переданные поля",
    tags=["Мобильное приложение / Профиль знакомств"],
    responses={
        401: {
            "model": schemas.OkResponse,
            "description": "Пользователь не прошёл авторизацию",
        },
        400: {
            "model": schemas.OkResponse,
            "description": "Переданны невалидные данные",
        },
        422: {
            "model": schemas.OkResponse,
            "description": "Переданные некорректные данные",
        },
    },
)
def edit_user(
    data: schemas.UpdatingDatingProfile,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    dating_profile_user = crud.dating_profile.get_by_user_id(
        db, user_id=current_user.id
    )
    if dating_profile_user is None:
        raise UnfoundEntity(message="У пользователя нет профиля для знакомств")
    update_dating_profile = crud.dating_profile.update_dating_profile(
        db=db, user=current_user, db_obj=dating_profile_user, obj_in=data
    )

    return schemas.SingleEntityResponse(
        data=getters.dating_profile.get_dating_profile(update_dating_profile)
    )


@router.delete(
    "/dating/profile/",
    response_model=schemas.OkResponse,
    name="Удалить профиль знакомств текущего пользователя",
    description="Удалить профиль знакомств текущего пользователя",
    tags=["Мобильное приложение / Профиль знакомств"],
    responses={
        400: {
            "model": schemas.OkResponse,
            "description": "Переданны невалидные данные",
        },
        422: {
            "model": schemas.OkResponse,
            "description": "Переданные некорректные данные",
        },
        403: {"model": schemas.OkResponse, "description": "Отказанно в доступе"},
        401: {"model": schemas.OkResponse, "description": "Не авторизорван"},
    },
)
def delete_profile(
    db: Session = Depends(deps.get_db),
    user: models.User = Depends(deps.get_current_user),
):
    crud.dating_profile.delete_dating_profile(db=db, user=user)

    return schemas.OkResponse()


# # Вывод всех анкет для знакомств
@router.get(
    "/dating/profile/search/",
    response_model=schemas.ListOfEntityResponse[schemas.GettingDatingProfileWithUser],
    name="Получить профили знакомств",
    description="Получить список профилей знакомств",
    tags=["Мобильное приложение / Профиль знакомств"],
)
def get_ssearch_dating_profiles(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    page: Optional[int] = Query(1, title="Номер страницы"),
    #   фильтр по гендеру
    #   фильтр по возрасту
    #   фильтр по типу отношений
):
    data = crud.dating_profile.get_search_dating_profiles(db, user=current_user, page=page)

    return schemas.ListOfEntityResponse(
        data=[
            getters.dating_profile.get_dating_profile_with_user(
                db, item["profile"], item["user"]
            )
            for item in data
        ]
    )


@router.post(
    "/dating/profile/like/{liked_profile_id}/",
    response_model=schemas.SingleEntityResponse[schemas.GettingDatingProfileLike],
    name="Добавить профиль знакомств в понравившиеся",
    tags=["Мобильное приложение / Профиль знакомств"],
    responses={
        401: {
            "model": schemas.OkResponse,
            "description": "Пользователь не прошёл авторизацию",
        },
        400: {
            "model": schemas.OkResponse,
            "description": "Переданны невалидные данные",
        },
        422: {
            "model": schemas.OkResponse,
            "description": "Переданные некорректные данные",
        },
    },
)
def add_like_dating_profile(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    liked_profile_id: int = Path(..., title="Идентификатор профиля знакомств"),
):
    save_like_user = crud.dating_profile.save_like(db, user=current_user, liked_dating_profile_id=liked_profile_id)

    return schemas.SingleEntityResponse(
        data=getters.dating_profile.get_dating_profile_like(save_like_user)
    )


@router.post(
    "/dating/profile/dislike/{disliked_profile_id}/",
    response_model=schemas.SingleEntityResponse[schemas.GettingDatingProfileDislike],
    name="Добавить профиль знакомств в не нравится",
    tags=["Мобильное приложение / Профиль знакомств"],
    responses={
        401: {
            "model": schemas.OkResponse,
            "description": "Пользователь не прошёл авторизацию",
        },
        400: {
            "model": schemas.OkResponse,
            "description": "Переданны невалидные данные",
        },
        422: {
            "model": schemas.OkResponse,
            "description": "Переданные некорректные данные",
        },
    },
)
def add_dislike_dating_profile(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    disliked_profile_id: int = Path(..., title="Идентификатор профиля знакомств"),
):
    save_dislike_user = crud.dating_profile.save_dislike(db, user=current_user, disliked_dating_profile_id=disliked_profile_id)

    return schemas.SingleEntityResponse(
        data=getters.dating_profile.get_dating_profile_dislike(save_dislike_user)
    )


@router.get(
    '/dating/profile/like/',
    response_model=schemas.ListOfEntityResponse[schemas.GettingDatingProfileWithUser],
    name="Получить все отметки нравится текущего профиля знакомств",
    tags=['Мобильное приложение / Профиль знакомств'],
    responses={
        401: {
            'model': schemas.OkResponse,
            'description': 'Пользователь не прошёл авторизацию'
        },
        400: {
            'model': schemas.OkResponse,
            'description': 'Переданны невалидные данные'
        },
        422: {
            'model': schemas.OkResponse,
            'description': 'Переданные некорректные данные'
        }
    }
)
def get_like_dating_profile(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    like_dating_profile = crud.dating_profile.get_like_dating_profile(db, user=current_user)

    return schemas.ListOfEntityResponse(
        data=[
            getters.dating_profile.get_dating_profile_with_user(
                db, item["profile"], item["user"]
            )
            for item in like_dating_profile    
        ]
    )
