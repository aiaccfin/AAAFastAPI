from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.db     import conn, crud, models
from app.utils  import u_hash

class UserClass:
    def __init__(self, _db: Session):
        self._db = _db


    def get_user_by_username(self, username: str):
        statement = select(models.Biz_User).where(models.Biz_User.username == username)
        result = self._db.exec(statement).first()
        return result


    def create_user(self, user: models.UserCreate):
        hashed_password = u_hash.hash_password(user.password)
        db_user = models.Biz_User(
            username        = user.username, 
            hashed_password = hashed_password,
            primary_group_id= user.primary_group_id,
            primary_role_id = user.primary_role_id
            )
        self._db.add(db_user)
        self._db.commit()
        self._db.refresh(db_user)
        return db_user


# def read_all_coa(offset1: int = 0, limit1: int = 20, db: Session = None):
#     print(offset1 + limit1)
#     all_coa = db.exec(select(model_coa.COA_Standard).offset(offset1).limit(limit1)).all()
#     return all_coa

# def read_one_coa(one_id: int, db: Session = None):
#     one_coa = db.get(model_coa.COA_Standard, one_id)
#     if not one_coa:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"COA not found with id: {one_id}",
#         )
#     return one_coa

# def create_coa(COA: model_coa.COACreate, db: Session = None):
#     COA_to_db = model_coa.COA_Standard.model_validate(COA)
#     db.add(COA_to_db)
#     db.commit()
#     db.refresh(COA_to_db)
#     return COA_to_db


# def update_coa(one_id: int, COA: model_coa.COAUpdate, db: Session = None):
#     COA_to_update = db.get(model_coa.COA_Standard, one_id)
#     if not COA_to_update:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"COA not found with id: {one_id}",
#         )

#     # if COA.coa_note is not None:
#     #         COA_to_update.coa_note = COA.coa_note
    
#     for field, value in COA.model_dump(exclude_unset=True).items():
#             setattr(COA_to_update, field, value)

#     db.add(COA_to_update)
#     db.commit()
#     db.refresh(COA_to_update)
#     return COA_to_update


# def delete_coa(one_id: int, db: Session = None):
#     coa  = db.get(model_coa.COA_Standard, one_id)
#     if not coa:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Hero not found with id: {one_id}",
#         )

#     db.delete(coa)
#     db.commit()
#     return {"ok": True}


