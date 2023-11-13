from schemas import AuthDetails
from auth.auth import AuthHandler
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import User

auth_handler = AuthHandler()


# instantiate DB and add dependency
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# app routes
app = FastAPI(title="sqlalchemy + fastapi", description="a basic user DB example")


@app.get("/", tags=["health check"])
async def root():
    return {"message": "Hello World"}


async def get_users_from_db() -> list:
    db = SessionLocal()
    users = db.query(User).all()
    print(users, type(users))
    res = []
    for user in users:
        res.append({"username": user.username, "password": user.password})
    return res


async def check_username(username: str) -> bool:
    print("starting check_username")
    db = SessionLocal()
    users = db.query(User).all()
    print(users, type(users))
    return any(user.username == username for user in users)


@app.post("/user", tags=["user"], description="register a new user in DB")
async def register(auth_details: AuthDetails, db: Session = Depends(get_db)):
    # check DB if username already taken
    print("starts registering new user")
    username_in_db = await check_username(auth_details.username)
    print(username_in_db)
    if username_in_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username already in database")
    # hash password a fake password
    password = auth_handler.get_hash_password(auth_details.password)
    print(f"hashed password:{password}")

    # convert pydantic input to DB format
    db_user = User(username=auth_details.username, password=password)
    print(auth_details.username, password)

    # add to DB
    db.add(db_user)
    # commit and refresh
    db.commit()
    db.refresh(db_user)
    return HTTPException(status_code=status.HTTP_200_OK, detail=f"new user created: {db_user}")


@app.post('/login', tags=["users"], description="login an existed user form database and issued a JWT token")
async def login(auth_details: AuthDetails):
    user = None
    users = await get_users_from_db()
    for x in users:
        if x["username"] == auth_details.username:
            user = x
            break
    # check there is a user with this username and check the password is correct
    if (user is None) or (not auth_handler.verify_password(auth_details.password, user["password"])):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid username and/or password")
    # at this point, there's a valid user, we instantiate a token for them to use the protected route
    token = auth_handler.encode_token(user["username"])
    return {"token": token}


@app.get("/get_user_protected", tags=["user"], description="list all users in DB, unprotected route")
async def get_users(username=Depends(auth_handler.auth_wrapper)):
    users = await get_users_from_db()
    print(f"users from DB:{users}")
    return {
        f"requested by": {username},
        "users": users
    }


@app.get("/get_user_unprotected", tags=["user"], description="list all users in DB, unprotected route")
async def get_users():
    users = await get_users_from_db()
    print(f"users from DB:{users}")
    return {"users": users}
