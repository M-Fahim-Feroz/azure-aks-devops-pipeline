from api.database import db_context
from api.models import User, Weather, UserIn, UserOut, WeatherIn, WeatherOut
from sqlmodel import select


def crud_add_user(user: UserIn):
    db_user = User.model_validate(user)
    with db_context() as db:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    return db_user


def crud_get_user(user_id: int):
    with db_context() as db:
        user = db.get(User, user_id)
    if user:
        return UserOut.model_validate(user)
    return None


def crud_get_users():
    with db_context() as db:
        statement = select(User)
        users = db.exec(statement).all()
    return [UserOut.model_validate(user) for user in users]


def crud_delete_user(user_id: int):
    with db_context() as db:
        user = db.get(User, user_id)
        if user:
            db.delete(user)
            db.commit()
            return True
    return False


def crud_update_user(user_id: int, user_in: UserIn):
    with db_context() as db:
        user = db.get(User, user_id)
        if user:
            user.first_name = user_in.first_name
            user.last_name = user_in.last_name
            user.mail = user_in.mail
            user.age = user_in.age
            db.add(user)
            db.commit()
            db.refresh(user)
            return UserOut.model_validate(user)
    return None


def crud_add_weather(weather: WeatherIn):
    db_weather = Weather.model_validate(weather)
    with db_context() as db:
        statement = select(Weather).where(
            Weather.city == weather.city, Weather.date == weather.date
        )
        exist = db.exec(statement).first()
        if exist:
            return None
        db.add(db_weather)
        db.commit()
        db.refresh(db_weather)
    return db_weather


def crud_get_weather(city: str):
    with db_context() as db:
        statement = (
            select(Weather)
            .where(Weather.city == city)
            .order_by(Weather.date.desc())
            .limit(7)
        )
        weather = db.exec(statement).all()
    if weather:
        result = []
        for item in weather:
            result.append(WeatherOut.model_validate(item))
        return {city: result[::-1]}
    return None


def crud_error_message(message):
    return {"error": message}
