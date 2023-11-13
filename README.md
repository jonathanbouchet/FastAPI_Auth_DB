# FastAPI_Auth_DB
template for a FastAPI API using JWT token auth and SQLAlchemy backend

# Description
- `app.post("/user")`: create a new user in database
- `app.post('/login')`: login an existed user and provide a JWT token
- `@app.get("/get_user_unprotected")`: list all users from the database
- `@app.get("/get_user_protected")`: 
  - list all users from the database
  - this is an example of a protected route where a JWT token is required


Authentication is done  in `auth/auth.py`
- `get_hash_password(self, password)`: hash a plain password using `bcrypt`
- `verify_password(self, plain_password: str, hashed_password: str)`: check the input plain password is the same  as the hashed one stored in database
- `encode_token(self, user_id)`: provide a JWT token based on the payload:
```commandline
payload = {
            'exp': datetime.utcnow() + timedelta(days=0, minutes=5),
            'iat': datetime.utcnow(),
            'sub': user_id
        }
```
the validity of the JWT token is 5 inutes
- `decode_token(self, token)`: wen a JWT token is entered, it checks that it is still valid and has not expired
-`auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security))`: wraps authentication
