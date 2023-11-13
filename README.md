# FastAPI_Auth_DB
template for a FastAPI API using JWT token auth and SQLAlchemy backend

# Description
- `app.post("/register")`: create a new user in database
- `app.post("/login")`: login an existed user and provide a JWT token
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
the validity of the JWT token is 5 minutes
- `decode_token(self, token)`: when a JWT token is entered, it checks that it is still valid and has not expired
-`auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security))`: wraps authentication

# Example

## Create a new user
```commandline
url = "http://127.0.0.1:8000/register"
payload = {"username":"johndoe", "password":"password123"}
res = requests.post(url=url, json=payload)
res
# <Response [200]>
res.json()
# {'status_code': 200, 'detail': 'new user created: <models.User object at 0x10ea5dad0>', 'headers': None}
```

## Checking the database
```commandline
sqlite3 users.db 
sqlite> .tables
users
sqlite> select * from users;
1|johndoe|$2b$12$QxR9/hS004khZahR6JVCBOEmbOsXKl7KqXeB6Vvn5./dg17myR/0i
```

## Checking the `unprotected` and the `protected` route
```commandline
url = "http://127.0.0.1:8000/get_user_unprotected"
res = requests.get(url=url)
res.json()
# {'users': [{'username': 'johndoe', 'password': '$2b$12$QxR9/hS004khZahR6JVCBOEmbOsXKl7KqXeB6Vvn5./dg17myR/0i'}]}
url = "http://127.0.0.1:8000/get_user_protected"
res = requests.get(url=url)
res.json()
# {'detail': 'Not authenticated'}
```

## Using the `protected` route
```commandline
>>> url = "http://127.0.0.1:8000/login"
res = requests.post(url=url, json=payload)
res.json()
#{'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTk5MTY2MDMsImlhdCI6MTY5OTkxNjMwMywic3ViIjoiam9obmRvZSJ9.lslh3yrQYM_nEicM7fkoDaVAAPHGnZDGf8p-VFCxbPM'}

headers = {"Authorization": f"Bearer {res.json()['token']}"}
url = "http://127.0.0.1:8000/get_user_protected"
res = requests.get(url=url, headers=headers)
res.json()
#{'requested by': ['johndoe'], 'users': [{'username': 'johndoe', 'password': '$2b$12$QxR9/hS004khZahR6JVCBOEmbOsXKl7KqXeB6Vvn5./dg17myR/0i'}]}

```

