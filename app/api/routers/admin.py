from typing import List
from fastapi import status, Depends, HTTPException, APIRouter
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import schemas, oath, database, models, hashing

router = APIRouter()


@router.post('/admin/towns', status_code=status.HTTP_201_CREATED, response_model=schemas.Towns_response, tags=['Admin'])
def create_town(request: schemas.Towns_schema, db: Session = Depends(database.get_db)):
    try:
        new_town = models.Towns(town_name=request.town_name)
        db.add(new_town)
        db.commit()
        db.refresh(new_town)
        return new_town
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Город {request.town_name} уже существует в БД')


@router.get('/admin/users/{user_id}', response_model=schemas.ShowUser, status_code=status.HTTP_200_OK, tags=['Admin'])
def show_user(user_id: int, db: Session = Depends(database.get_db)):
    """
        To view details related to a single contact

        - **id**: The integer id of the contact you want to view details.
    """
    user = db.query(models.Users).filter(models.Users.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Пользователь с ID {user_id} не найден')
    else:
        return user


@router.delete('/admin/users/{user_id}', status_code=status.HTTP_200_OK, tags=['Admin'])
def delete_user(user_id: int, db: Session = Depends(database.get_db)):
    """
        To remove a single contact

        - **id**: The integer id of the contact you want to remove.
    """
    removable_user = db.query(models.Users).filter(models.Users.id == user_id).first()
    if not removable_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'user {user_id} not found')
    else:
        db.query(models.Users).filter(models.Users.id == user_id).delete(synchronize_session=False)
    db.commit()
    return {'detail': f'пользователь с ID {user_id} удален'}


@router.post('/admin/filters', status_code=status.HTTP_201_CREATED, response_model=schemas.Show_Categories, tags=['Admin'])
def create_category(request: schemas.Categories_schema, db: Session = Depends(database.get_db)):
    try:
        new_category = models.Categories(category_name=request.category_name)
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return new_category
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Категория {request.category_name} уже существует')


@router.get('/admin/filters', status_code=status.HTTP_200_OK, response_model=List[schemas.Show_Categories], tags=['Admin'])
def show_all_categories(db: Session = Depends(database.get_db)):
    return db.query(models.Categories).all()


@router.get('/admin/filters/{filter_id}', status_code=status.HTTP_200_OK, response_model=schemas.Show_Categories, tags=['Admin'])
def show_category(filter_id: int, db: Session = Depends(database.get_db)):
    return db.query(models.Categories).filter(models.Categories.id == filter_id).first()