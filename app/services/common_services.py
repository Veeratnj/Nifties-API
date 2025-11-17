

from app.models.models import User


def user_add(db,user,):
    
    # db_user = db.query(User).filter(User.email == user.email).first()
    # if db_user:
    #     raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create and save the new user
    new_user = User(
        name=user.name,
        email=user.email,
        age=user.age,
        gender=user.gender,
        is_subscribe=user.is_subscribe
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    result={
        'name':new_user.name,
        'age':new_user.age,
        'email':new_user.email,
        'gender':new_user.gender,
        'is_subscribe':new_user.is_subscribe
    }
    return result