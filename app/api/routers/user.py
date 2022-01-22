from pathlib import Path
from typing import List
from os import remove
from aiofiles import open
from fastapi import status, Depends, HTTPException, File, UploadFile, Form, APIRouter
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy.orm import Session

import schemas, oath, database, models, hashing

router = APIRouter()


@router.post('/auth', status_code=status.HTTP_201_CREATED, response_model=schemas.ShowUser, tags=['Users'])
def create_user(request: schemas.ShowUser, db: Session = Depends(database.get_db)):
    """
        - **email** is unique.
        - **mobile_phone** is unique.
    """
    try:
        new_user = models.Users(first_name=request.first_name,
                                last_name=request.last_name,
                                email=request.email,
                                mobile_phone=request.mobile_phone,
                                town_id=request.town_id,
                                password_hash=hashing.Hash.bcrypt(request.password_hash))
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Введенные email {request.email} или '
                   f' мобильный номер {request.mobile_phone} уже зарегистрированы')
    except DataError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Введенные данные некоректны',
        )


@router.post('/create_announcement', response_model=schemas.Announcement_schema_response, tags=['Users'])
async def create_announcement(price: float = Form(...), category_id: int = Form(...), text: str = Form(...),
                              town_id: int = Form(...), files: List[UploadFile] = File(...),
                              db: Session = Depends(database.get_db),
                              current_user_id: models.Users = Depends(oath.get_current_user_id)):
    """
        - **email** is unique.
        - **mobile_phone** is unique.
    """
    new_announcement = models.Announcements(
        user_id=current_user_id,
        price=price,
        category_id=category_id,
        text=text,
        town_id=town_id
    )
    db.add(new_announcement)
    db.commit()
    db.refresh(new_announcement)

    for file in files:
        parts = ["data", file.filename]
        file_path = Path.cwd().joinpath(*parts)

        async with open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        new_image = models.Images(
            announcement_id=new_announcement.id,
            data_path=str(file_path)
        )
        db.add(new_image)
        db.commit()
        db.refresh(new_image)
    return new_announcement


@router.put('/announcements/{announcement_id}', status_code=status.HTTP_202_ACCEPTED, tags=['Users'])
def update_announcement(announcement_id: int, request: schemas.Announcement_schema, db: Session = Depends(database.get_db),
                        current_user: models.Users = Depends(oath.get_current_user_id)):
    if not db.query(models.Announcements).filter(models.Announcements.id == announcement_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Announcement with id {announcement_id} not found')
    db.query(models.Announcements).filter(models.Announcements.id == announcement_id).update({
        'price': request.price,
        'category_id': request.category_id,
        'text': request.text,
        'town_id': request.town_id
    }, synchronize_session='evaluate')
    db.commit()
    return {'data': f'Anouncement with id№{announcement_id} successfully updated'}


@router.get('/announcements', response_model=List[schemas.Announcement_schema_response], status_code=status.HTTP_200_OK,
            tags=['Users'])
def show_all_announcements(db: Session = Depends(database.get_db)):
    return db.query(models.Announcements).all()


@router.get('/announcements/{announcement_id}', response_model=schemas.Announcement_schema_response,
            status_code=status.HTTP_200_OK,
            tags=['Users'])
def show_announcement(announcement_id: int, db: Session = Depends(database.get_db)):
    announcement = db.query(models.Announcements).filter(models.Announcements.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'announcement with id {announcement_id} not found')
    return announcement


@router.get('/announcements/user/{user_id}', response_model=List[schemas.Announcement_schema_response],
            status_code=status.HTTP_200_OK,
            tags=['Users'])
def show_announcements_of_the_user(user_id: int, db: Session = Depends(database.get_db)):
    announcement = db.query(models.Announcements).filter(models.Announcements.user_id == user_id).all()
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'user with id {user_id} not found')
    return announcement


@router.get('/announcements/town/{town_id}',
            status_code=status.HTTP_200_OK, response_model=List[schemas.Announcement_schema_response], tags=['Users'])
def show_announcements_towns_filtered(town_id: int, db: Session = Depends(database.get_db)):
    town = db.query(models.Announcements).filter(models.Announcements.town_id == town_id).all()

    if not town:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Town with id {town_id} not found')
    return town


@router.get('/announcements/category/{category_id}', response_model=List[schemas.Announcement_schema_response],
            status_code=status.HTTP_200_OK,
            tags=['Users'])
def show_announcements_category_filtered(category_id: int, db: Session = Depends(database.get_db)):
    category = db.query(models.Announcements).filter(models.Announcements.category_id == category_id).all()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Сategory with id {category_id} not found')
    return category


@router.post('/user/{current_user_id}/favorite/{announcement_id}', status_code=status.HTTP_200_OK,
             tags=['Users'])
def add_favorite(announcement_id: int, db: Session = Depends(database.get_db),
                 current_user_id: models.Users = Depends(oath.get_current_user_id)):
    favorite = models.Favorites(
        user_id=current_user_id,
        announcement_id=announcement_id,
    )
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return {'detail': f'обьявление с ID {announcement_id} добавлено в избранные'}


@router.get('/user/{current_user_id}/favorite/', response_model=List[schemas.ShowFav], status_code=status.HTTP_200_OK,
            tags=['Users'])
def get_favorites(db: Session = Depends(database.get_db), current_user_id: models.Users = Depends(oath.get_current_user_id)):
    return db.query(models.Favorites).filter(models.Favorites.user_id == current_user_id).all()


@router.delete('/user/{current_user_id}/favorite/{announcement_id}', status_code=status.HTTP_200_OK, tags=['Users'])
def delete_from_favorite(announcement_id: int, db: Session = Depends(database.get_db),
                         current_user_id: models.Users = Depends(oath.get_current_user_id)):
    removable_announcement = db.query(models.Favorites).filter(models.Favorites.announcement_id == announcement_id)
    if not removable_announcement.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Announcement with id {announcement_id} not found')
    removable_announcement.delete(synchronize_session=False)
    db.commit()
    return {'detail': f'announcement with id {announcement_id} deleted'}


@router.delete('/announcements/{announcement_id}', status_code=status.HTTP_200_OK, tags=['Users'])
def delete_announcement(announcement_id: int, db: Session = Depends(database.get_db),
                        current_user_id: models.Users = Depends(oath.get_current_user_id)):
    removable_announcement = db.query(models.Announcements).filter(models.Announcements.id == announcement_id).first()
    removable_files = db.query(models.Images).filter(models.Images.announcement_id == announcement_id).all()
    if not removable_announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Announcement with id {announcement_id} not found')
    for file in removable_files:
        remove(file.data_path)
    db.query(models.Announcements).filter(models.Announcements.id == announcement_id).delete(synchronize_session=False)
    db.commit()
    return {'detail': f'обьявление с ID {announcement_id} удалено'}


@router.get('/announcements/search/{word}', response_model=List[schemas.Announcement_schema_response], tags=['Users'])
def search(word: str, db: Session = Depends(database.get_db)):
    search_regex = f"%{word}%"
    exact_match = db.query(models.Announcements).filter(models.Announcements.text == word).all()
    like_match = db.query(models.Announcements).filter(models.Announcements.text.like(search_regex)).all()
    return exact_match or like_match
