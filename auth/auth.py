import jwt
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from datetime import datetime, timedelta


class AuthHandler():
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = "SECRET"
    algorithm = "HS256"

    def get_hash_password(self, password):
        """
        hash a plain password
        :param password:
        :return:
        """
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str):
        """
        compare user's input password with a saved hashed one
        :param plain_password:
        :param hashed_password:
        :return:
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def encode_token(self, user_id):
        """
        encode a payload: {username, expiration, creation date} as a JWT token
        :param user_id:
        :return:
        """
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, minutes=5),
            'iat': datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            self.secret,
            algorithm='HS256'
        )

    def decode_token(self, token):
        """
        decode a JWT token in order to check its validity
        :param token:
        :return:
        """
        try:
            payload = jwt.decode(token, key=self.secret, algorithms=[self.algorithm])
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)

