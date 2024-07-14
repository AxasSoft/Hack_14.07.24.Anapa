from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.params import Path, Header
from pydantic import Field
from sqlalchemy.orm import Session
from starlette.requests import Request

from app import crud, models, schemas, getters
from app.api import deps
from app.schemas.response import Meta, OkResponse
from ....exceptions import UnprocessableEntity, UnfoundEntity, ListOfEntityError, InaccessibleEntity
from ....schemas import CreatingStory, UpdatingStory
from ....schemas.story import HugBody, HidingBody, IsFavoriteBody

router = APIRouter()


@router.get(
    '/users/me/stories/',
    response_model=schemas.ListOfEntityResponse[schemas.GettingStory],
    name="Получить все истории текущего пользователя",
    responses={
        400: {
            'model': schemas.OkResponse,
            'description': 'Переданны невалидные данные'
        },
        422: {
            'model': schemas.OkResponse,
            'description': 'Переданные некорректные данные'
        },
        403: {
            'model': schemas.OkResponse,
            'description': 'Отказанно в доступе'
        },
        404: {
            'model': schemas.OkResponse,
            'description': 'Пользователь не найден'
        }
    },
    tags=["Мобильное приложение / Истории"]
)
def get_stories_by_user(
        db: Session = Depends(deps.get_db),
        page: Optional[int] = Query(1, title="Номер страницы"),
        current_user: models.User = Depends(deps.get_current_active_user),
        is_hugged: Optional[bool] = Query(None),
        is_favorite: Optional[bool] = Query(None),
):

    data, paginator = crud.story.get_stories_by_user(
        db,
        user=current_user,
        page=page,
        current_user=current_user,
        is_hugged=is_hugged,
        is_favorite=is_favorite
    )

    return schemas.ListOfEntityResponse(
        data=[
            getters.story.get_story(db, datum, current_user)
            for datum
            in data
        ],
        meta=Meta(paginator=paginator)
    )


@router.get(
    '/stories/subscriptions/',
    response_model=schemas.ListOfEntityResponse[schemas.GettingStory],
    name="Получить все истории текущего пользователя",
    responses={
        400: {
            'model': schemas.OkResponse,
            'description': 'Переданны невалидные данные'
        },
        422: {
            'model': schemas.OkResponse,
            'description': 'Переданные некорректные данные'
        },
        403: {
            'model': schemas.OkResponse,
            'description': 'Отказанно в доступе'
        },
        404: {
            'model': schemas.OkResponse,
            'description': 'Пользователь не найден'
        }
    },
    tags=["Мобильное приложение / Истории"]
)
def get_stories_from_subscriptions(
        db: Session = Depends(deps.get_db),
        page: Optional[int] = Query(1, title="Номер страницы"),
        current_user: models.User = Depends(deps.get_current_active_user),
        is_hugged: Optional[bool] = Query(None),
        is_favorite: Optional[bool] = Query(None),
):

    data, paginator = crud.story.get_stories_from_subscriptions(
        db,
        page=page,
        current_user=current_user,
        is_hugged=is_hugged,
        is_favorite=is_favorite
    )

    return schemas.ListOfEntityResponse(
        data=[
            getters.story.get_story(db, datum, current_user)
            for datum
            in data
        ],
        meta=Meta(paginator=paginator)
    )


@router.get(
    '/users/{user_id}/stories/',
    response_model=schemas.ListOfEntityResponse[schemas.GettingStory],
    name="Получить все истории пользователя",
    responses={
        400: {
            'model': schemas.OkResponse,
            'description': 'Переданны невалидные данные'
        },
        422: {
            'model': schemas.OkResponse,
            'description': 'Переданные некорректные данные'
        },
        403: {
            'model': schemas.OkResponse,
            'description': 'Отказанно в доступе'
        },
        404: {
            'model': schemas.OkResponse,
            'description': 'ХПользователь не найден'
        }
    },
    tags=["Мобильное приложение / Истории"]
)
def get_stories_by_user(
        user_id: int = Field(...,title="Идентификатор пользователя"),
        db: Session = Depends(deps.get_db),
        page: Optional[int] = Query(1, title="Номер страницы"),
        is_hugged: Optional[bool] = Query(None),
        is_favorite: Optional[bool] = Query(None),
        current_user: Optional[models.User] = Depends(deps.get_optional_current_user),
):
    user = crud.user.get_by_id(db, user_id)

    if user is None:
        raise UnfoundEntity(num=2, message="Пользовательт не найден")

    data, paginator = crud.story.get_stories_by_user(
        db,
        user=user,
        page=page,
        current_user=current_user,
        is_hugged=is_hugged,
        is_favorite=is_favorite
    )

    return schemas.ListOfEntityResponse(
        data=[
            getters.story.get_story(db, datum,current_user)
            for datum
            in data
        ],
        meta=Meta(paginator=paginator)
    )


@router.get(
    '/cp/users/{user_id}/stories/',
    response_model=schemas.ListOfEntityResponse[schemas.GettingStory],
    name="Получить все истории пользователя",
    responses={
        400: {
            'model': schemas.OkResponse,
            'description': 'Переданны невалидные данные'
        },
        422: {
            'model': schemas.OkResponse,
            'description': 'Переданные некорректные данные'
        },
        403: {
            'model': schemas.OkResponse,
            'description': 'Отказанно в доступе'
        },
        404: {
            'model': schemas.OkResponse,
            'description': 'ХПользователь не найден'
        }
    },
    tags=["Административная панель / Истории"]
)
def get_stories_by_user(
        user_id: int = Field(...,title="Идентификатор пользователя"),
        db: Session = Depends(deps.get_db),
        page: Optional[int] = Query(1, title="Номер страницы"),
        current_user: Optional[models.User] = Depends(deps.get_current_active_superuser),
):
    user = crud.user.get_by_id(db, user_id)

    if user is None:
        raise UnfoundEntity(num=2, message="Пользователь не найден")

    data, paginator = crud.story.get_stories_by_user(db, user=user, page=page)

    return schemas.ListOfEntityResponse(
        data=[
            getters.story.get_story(db, datum,current_user)
            for datum
            in data
        ],
        meta=Meta(paginator=paginator)
    )



@router.post(
    '/stories/',
    response_model=schemas.SingleEntityResponse[schemas.GettingStory],
    name="Добавить новую историю",
    responses={
        400: {
            'model': schemas.OkResponse,
            'description': 'Переданны невалидные данные'
        },
        422: {
            'model': schemas.OkResponse,
            'description': 'Переданные некорректные данные'
        },
        403: {
            'model': schemas.OkResponse,
            'description': 'Отказанно в доступе'
        },
        404: {
            'model': schemas.OkResponse,
            'description': 'ХПользователь не найден'
        }
    },
    tags=["Мобильное приложение / Истории"]
)
def add_new_story(
        data: CreatingStory,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
):

    data, code, indexes = crud.story.create_story_by_user(db, user=current_user, obj_in=data)


    if code == -2:
        raise ListOfEntityError(
            errors=[
                UnfoundEntity(
                    message='Изображение не н6айдено',
                    num=2,
                    path=f'$body.gallery[{index}]'
                )
                for index in indexes
            ],
            description='Изображения не найдены',
            http_status=404
        )

    if code == -3:
        raise ListOfEntityError(
            errors=[
                UnfoundEntity(
                    message='Изображение не пренадлежит пользователю',
                    num=2,
                    path=f'$body.gallery[{index}]'
                )
                for index in indexes
            ],
            description='Изображения не пренадлежат пользователю',
            http_status=403
        )

    if code == -4:
        raise ListOfEntityError(
            errors=[
                UnfoundEntity(
                    message='Изображение уже использовалось',
                    num=2,
                    path=f'$body.gallery[{index}]'
                )
                for index in indexes
            ],
            description='Изображения уже использовалось',
            http_status=422
        )

    if code == -5:
        raise UnfoundEntity(message='Видео не найдено', description='Видео не найдено',num=2)
    if code == -6:
        raise InaccessibleEntity(
            message='Видео не принадлежит пользователю',
            description='Видео не принадлежит пользователю'
        )
    if code == -7:
        raise UnprocessableEntity(
            message='Видео уже использовалось',
            description='Видео уже использовалось'
        )

    return schemas.SingleEntityResponse(
        data=getters.story.get_story(db, data, current_user)
    )


@router.post(
    '/cp/users/{user_id}/stories/',
    response_model=schemas.SingleEntityResponse[schemas.GettingStory],
    name="Добавить новую историю",
    responses={
        400: {
            'model': schemas.OkResponse,
            'description': 'Переданны невалидные данные'
        },
        422: {
            'model': schemas.OkResponse,
            'description': 'Переданные некорректные данные'
        },
        403: {
            'model': schemas.OkResponse,
            'description': 'Отказанно в доступе'
        },
        404: {
            'model': schemas.OkResponse,
            'description': 'ХПользователь не найден'
        }
    },
    tags=["Мобильное приложение / Истории"]
)
def add_new_story(
        data: CreatingStory,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser),
        user_id: int = Path(...,title="Идентификатор пользователя"),
):

    user = crud.user.get_by_id(db, user_id)
    if user is None:
        raise UnfoundEntity(num=2, message="Пользователь не найден")

    data, code, indexes = crud.story.create_story_by_user(db, user=user, obj_in=data)


    if code == -2:
        raise ListOfEntityError(
            errors=[
                UnfoundEntity(
                    message='Изображение не н6айдено',
                    num=2,
                    path=f'$body.gallery[{index}]'
                )
                for index in indexes
            ],
            description='Изображения не найдены',
            http_status=404
        )

    if code == -3:
        raise ListOfEntityError(
            errors=[
                UnfoundEntity(
                    message='Изображение не пренадлежит пользователю',
                    num=2,
                    path=f'$body.gallery[{index}]'
                )
                for index in indexes
            ],
            description='Изображения не пренадлежат пользователю',
            http_status=403
        )

    if code == -4:
        raise ListOfEntityError(
            errors=[
                UnfoundEntity(
                    message='Изображение уже использовалось',
                    num=2,
                    path=f'$body.gallery[{index}]'
                )
                for index in indexes
            ],
            description='Изображения уже использовалось',
            http_status=422
        )

    if code == -5:
        raise UnfoundEntity(message='Видео не найдено', description='Видео не найдено',num=2)
    if code == -6:
        raise InaccessibleEntity(
            message='Видео не принадлежит пользователю',
            description='Видео не принадлежит пользователю'
        )
    if code == -7:
        raise UnprocessableEntity(
            message='Видео уже использовалось',
            description='Видео уже использовалось'
        )

    return schemas.SingleEntityResponse(
        data=getters.story.get_story(db, data, current_user)
    )



@router.put(
    '/stories/{story_id}/',
    response_model=schemas.SingleEntityResponse[schemas.GettingStory],
    name="Изменить историю текущего пользователя",
    responses={
        400: {
            'model': schemas.OkResponse,
            'description': 'Переданны невалидные данные'
        },
        422: {
            'model': schemas.OkResponse,
            'description': 'Переданные некорректные данные'
        },
        403: {
            'model': schemas.OkResponse,
            'description': 'Отказанно в доступе'
        },
        404: {
            'model': schemas.OkResponse,
            'description': 'ХПользователь не найден'
        }
    },
    tags=["Мобильное приложение / Истории"]
)
def edit_story(
        data: UpdatingStory,
        story_id: int = Path(..., title="Идентификатор истории"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
):

    story = crud.story.get_by_id(db, id=story_id)
    if story is None:
        raise UnfoundEntity(message="История не найдена", description="Исторрия не найдена",num=1)
    if story.user != current_user:
        raise InaccessibleEntity(
            message="История не принадлежит порльзователю",
            description="История не принадлежит порльзователю"
        )

    data, code, indexes = crud.story.update(db, db_obj=story, obj_in=data)

    if code == -2:
        raise ListOfEntityError(
            errors=[
                UnfoundEntity(
                    message='Изображение не н6айдено',
                    num=2,
                    path=f'$body.gallery[{index}]'
                )
                for index in indexes
            ],
            description='Изображения не найдены',
            http_status=404
        )

    if code == -3:
        raise ListOfEntityError(
            errors=[
                UnfoundEntity(
                    message='Изображение не пренадлежит пользователю',
                    num=2,
                    path=f'$body.gallery[{index}]'
                )
                for index in indexes
            ],
            description='Изображения не пренадлежат пользователю',
            http_status=403
        )

    if code == -4:
        raise ListOfEntityError(
            errors=[
                UnfoundEntity(
                    message='Изображение уже использовалось',
                    num=2,
                    path=f'$body.gallery[{index}]'
                )
                for index in indexes
            ],
            description='Изображения уже использовалось',
            http_status=422
        )

    if code == -5:
        raise UnfoundEntity(
            message='Видео не найдено',
            description='Видео не найдено',
            num=2
        )
    if code == -6:
        raise InaccessibleEntity(
            message='Видео не принадлежит пользователю',
            description='Видео не принадлежит пользователю'
        )
    if code == -7:
        raise UnprocessableEntity(
            message='Видео уже использовалось',
            description='Видео уже использовалось'
        )

    return schemas.SingleEntityResponse(
        data=getters.story.get_story(db, data, current_user)
    )


@router.get(
    '/stories/{story_id}/',
    response_model=schemas.SingleEntityResponse[schemas.GettingStory],
    name="Получить одну историю",
    responses={
        400: {
            'model': schemas.OkResponse,
            'description': 'Переданны невалидные данные'
        },
        422: {
            'model': schemas.OkResponse,
            'description': 'Переданные некорректные данные'
        },
        403: {
            'model': schemas.OkResponse,
            'description': 'Отказанно в доступе'
        },
        404: {
            'model': schemas.OkResponse,
            'description': 'ХПользователь не найден'
        }
    },
    tags=["Мобильное приложение / Истории"]
)
def get_story(
        story_id: int = Path(..., title="Идентификатор истории"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
):

    story = crud.story.get_by_id(db, id=story_id)
    if story is None:
        raise UnfoundEntity(message="История не найдена", description="Исторрия не найдена",num=1)

    return schemas.SingleEntityResponse(
        data=getters.story.get_story(db, story, current_user)
    )


@router.put(
    '/cp/stories/{story_id}/',
    response_model=schemas.SingleEntityResponse[schemas.GettingStory],
    name="Изменить историю текущего пользователя",
    responses={
        400: {
            'model': schemas.OkResponse,
            'description': 'Переданны невалидные данные'
        },
        422: {
            'model': schemas.OkResponse,
            'description': 'Переданные некорректные данные'
        },
        403: {
            'model': schemas.OkResponse,
            'description': 'Отказанно в доступе'
        },
        404: {
            'model': schemas.OkResponse,
            'description': 'ХПользователь не найден'
        }
    },
    tags=["Мобильное приложение / Истории"]
)
def edit_story(
        data: UpdatingStory,
        story_id: int = Path(..., title="Идентификатор истории"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser),
):

    story = crud.story.get_by_id(db, id=story_id)
    if story is None:
        raise UnfoundEntity(message="История не найдена", description="Исторрия не найдена",num=1)

    data, code, indexes = crud.story.update(db, db_obj=story, obj_in=data)

    if code == -2:
        raise ListOfEntityError(
            errors=[
                UnfoundEntity(
                    message='Изображение не н6айдено',
                    num=2,
                    path=f'$body.gallery[{index}]'
                )
                for index in indexes
            ],
            description='Изображения не найдены',
            http_status=404
        )

    if code == -3:
        raise ListOfEntityError(
            errors=[
                UnfoundEntity(
                    message='Изображение не пренадлежит пользователю',
                    num=2,
                    path=f'$body.gallery[{index}]'
                )
                for index in indexes
            ],
            description='Изображения не пренадлежат пользователю',
            http_status=403
        )

    if code == -4:
        raise ListOfEntityError(
            errors=[
                UnfoundEntity(
                    message='Изображение уже использовалось',
                    num=2,
                    path=f'$body.gallery[{index}]'
                )
                for index in indexes
            ],
            description='Изображения уже использовалось',
            http_status=422
        )

    if code == -5:
        raise UnfoundEntity(
            message='Видео не найдено',
            description='Видео не найдено',
            num=2
        )
    if code == -6:
        raise InaccessibleEntity(
            message='Видео не принадлежит пользователю',
            description='Видео не принадлежит пользователю'
        )
    if code == -7:
        raise UnprocessableEntity(
            message='Видео уже использовалось',
            description='Видео уже использовалось'
        )

    return schemas.SingleEntityResponse(
        data=getters.story.get_story(db, data, current_user)
    )




@router.post(
    '/stories/{story_id}/viewed/',
    response_model=schemas.SingleEntityResponse[schemas.GettingStory],
    name="Отметить историю как просмотренную текущим пользователем",
    responses={
        400: {
            'model': schemas.OkResponse,
            'description': 'Переданны невалидные данные'
        },
        422: {
            'model': schemas.OkResponse,
            'description': 'Переданные некорректные данные'
        },
        403: {
            'model': schemas.OkResponse,
            'description': 'Отказанно в доступе'
        },
        404: {
            'model': schemas.OkResponse,
            'description': 'ХПользователь не найден'
        }
    },
    tags=["Мобильное приложение / Истории"]
)
def mark_viewed(
        story_id: int = Path(..., title="Идентификатор истории"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
):

    story = crud.story.get_by_id(db, id=story_id)
    if story is None:
        raise UnfoundEntity(message="История не найдена", description="Исторрия не найдена", num=1)

    crud.story.mark_story_as_viewed(db, story=story, user=current_user)

    return schemas.SingleEntityResponse(
        data=getters.story.get_story(db, story, current_user)
    )


@router.post(
    '/stories/{story_id}/hugged/',
    response_model=schemas.SingleEntityResponse[schemas.GettingStory],
    name="Обнять историю",
    responses={
        400: {
            'model': schemas.OkResponse,
            'description': 'Переданны невалидные данные'
        },
        422: {
            'model': schemas.OkResponse,
            'description': 'Переданные некорректные данные'
        },
        403: {
            'model': schemas.OkResponse,
            'description': 'Отказанно в доступе'
        },
        404: {
            'model': schemas.OkResponse,
            'description': 'ХПользователь не найден'
        }
    },
    tags=["Мобильное приложение / Истории"]
)
def mark_hugged(
        hugbody: HugBody,
        story_id: int = Path(..., title="Идентификатор истории"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
):

    story = crud.story.get_by_id(db, id=story_id)
    if story is None:
        raise UnfoundEntity(message="История не найдена", description="Исторрия не найдена",num=1)

    crud.story.hug_story(db, story=story, user=current_user,hugs=hugbody.hugs)

    return schemas.SingleEntityResponse(
        data=getters.story.get_story(db, story, current_user)
    )


@router.post(
    '/stories/{story_id}/is-favorite/',
    response_model=schemas.SingleEntityResponse[schemas.GettingStory],
    name="Добавить или убрать историю из избранного",
    responses={
        400: {
            'model': schemas.OkResponse,
            'description': 'Переданны невалидные данные'
        },
        422: {
            'model': schemas.OkResponse,
            'description': 'Переданные некорректные данные'
        },
        403: {
            'model': schemas.OkResponse,
            'description': 'Отказанно в доступе'
        },
        404: {
            'model': schemas.OkResponse,
            'description': 'ХПользователь не найден'
        }
    },
    tags=["Мобильное приложение / Истории"]
)
def mark_favorite(
        favbody: IsFavoriteBody,
        story_id: int = Path(..., title="Идентификатор истории"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
):

    story = crud.story.get_by_id(db, id=story_id)
    if story is None:
        raise UnfoundEntity(message="История не найдена", description="История не найдена",num=1)

    crud.story.favorite_story(db, story=story, user=current_user,is_favorite=favbody.is_favorite)

    return schemas.SingleEntityResponse(
        data=getters.story.get_story(db, story, current_user)
    )


@router.post(
    '/stories/{story_id}/is-hidden/',
    response_model=OkResponse,
    name="Скрыть историю",
    responses={
        400: {
            'model': schemas.OkResponse,
            'description': 'Переданны невалидные данные'
        },
        422: {
            'model': schemas.OkResponse,
            'description': 'Переданные некорректные данные'
        },
        403: {
            'model': schemas.OkResponse,
            'description': 'Отказанно в доступе'
        },
        404: {
            'model': schemas.OkResponse,
            'description': 'Пользователь не найден'
        }
    },
    tags=["Мобильное приложение / Истории"]
)
def mark_hidden(
        hiding_body: HidingBody,
        story_id: int = Path(..., title="Идентификатор истории"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
):

    story = crud.story.get_by_id(db, id=story_id)
    if story is None:
        raise UnfoundEntity(message="История не найдена", description="Исторрия не найдена",num=1)

    crud.story.hide_story(db, story=story, user=current_user,hide=hiding_body.hiding)

    return OkResponse()


@router.delete(
    '/stories/{story_id}/',
    response_model=schemas.OkResponse,
    name="Удалить историю текущего пользователя",
    responses={
        400: {
            'model': schemas.OkResponse,
            'description': 'Переданны невалидные данные'
        },
        422: {
            'model': schemas.OkResponse,
            'description': 'Переданные некорректные данные'
        },
        403: {
            'model': schemas.OkResponse,
            'description': 'Отказанно в доступе'
        },
        404: {
            'model': schemas.OkResponse,
            'description': 'ХПользователь не найден'
        }
    },
    tags=["Мобильное приложение / Истории"]
)
def delete_profile_story(
        story_id: int = Path(...,title="Идентификатор истории"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
):
    story = crud.story.get_by_id(db, id=story_id)
    if story is None:
        raise UnfoundEntity(message="История не найдена", description="Исторрия не найдена",num=1)
    if story.user != current_user:
        raise InaccessibleEntity(
            message="История не принадлежит порльзователю",
            description="История не принадлежит порльзователю"
        )
    crud.story.remove(db, id=story_id)
    return schemas.OkResponse()


@router.delete(
    '/cp/stories/{story_id}/',
    response_model=schemas.OkResponse,
    name="Удалить историю",
    responses={
        400: {
            'model': schemas.OkResponse,
            'description': 'Переданны невалидные данные'
        },
        422: {
            'model': schemas.OkResponse,
            'description': 'Переданные некорректные данные'
        },
        403: {
            'model': schemas.OkResponse,
            'description': 'Отказанно в доступе'
        },
        404: {
            'model': schemas.OkResponse,
            'description': 'ХПользователь не найден'
        }
    },
    tags=["Административная панель / Истории"]
)
def delete_user_story(
        story_id: int = Path(...,title="Идентификатор истории"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser),
):
    story = crud.story.get_by_id(db, id=story_id)
    if story is None:
        raise UnfoundEntity(message="История не найдена", description="Исторрия не найдена",num=1)
    crud.story.remove(db,id=story_id)
    return schemas.OkResponse()


@router.get(
    '/stories/',
    response_model=schemas.ListOfEntityResponse[schemas.GettingStory],
    name="Получить все истории по теме, хештегу и пользователю",
    responses={
        400: {
            'model': schemas.OkResponse,
            'description': 'Переданны невалидные данные'
        },
        422: {
            'model': schemas.OkResponse,
            'description': 'Переданные некорректные данные'
        },
        403: {
            'model': schemas.OkResponse,
            'description': 'Отказанно в доступе'
        },
        404: {
            'model': schemas.OkResponse,
            'description': 'Пользователь, хештег или тема не найдены'
        }
    },
    tags=["Мобильное приложение / Истории"]
)
def get_stories_by_criteria(
        request: Request,
        db: Session = Depends(deps.get_db),
        user_id: Optional[int] = Query(None, title="Идентификатор пользователя"),
        hashtag_id: Optional[int] = Query(None, title="Идентификатопр хештега"),
        search: Optional[str] = Query(None, title="Текст истории, название хештега или темы"),
        is_hugged: Optional[bool] = Query(None),
        is_favorite: Optional[bool] = Query(None),
        page: Optional[int] = Query(1, title="Номер страницы"),
        current_user: Optional[models.User] = Depends(deps.get_optional_current_user),
        x_real_ip: Optional[str] = Header(None),
        accept_language: Optional[str] = Header(None),
        user_agent: Optional[str] = Header(None),
        x_firebase_token: Optional[str] = Header(None),

):
    if user_id is not None:
        user = crud.user.get_by_id(db,user_id)
        if user is None:
            raise UnfoundEntity(description="Пользователь не найден", message="Пользователь не найден", num=2)
    else:
        user = None

    if hashtag_id is not None:
        hashtag = crud.hashtag.get_by_id(db, hashtag_id)
        if hashtag is None:
            raise UnfoundEntity(description="Хештег не найден", message="Хештег не найден", num=2)
    else:
        hashtag = None

    if current_user is not None:
        data, paginator = crud.story.get_stories(
            db,
            user=user,
            hashtag=hashtag,
            page=page,
            current_user=current_user,
            search=search,
            host=request.client.host,
            x_real_ip=x_real_ip,
            accept_language=accept_language,
            user_agent=user_agent,
            x_firebase_token=x_firebase_token,
            is_hugged=is_hugged,
            is_favorite=is_favorite
        )
    else:
        data, paginator = crud.story.get_stories(
            db,
            user=user,
            hashtag=hashtag,
            page=page,
            current_user=current_user,
            search=search,
            host=None,
            x_real_ip=None,
            accept_language=None,
            user_agent=None,
            x_firebase_token=None
        )

    a = schemas.ListOfEntityResponse(
        data=[
            getters.story.get_story(db, datum, current_user)
            for datum
            in data
        ],
        meta=Meta(paginator=paginator)
    )

    return a
