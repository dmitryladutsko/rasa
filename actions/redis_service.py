import os
import redis
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class RedisService:
    def __init__(self, user_email, user_otp):
        self.user_otp = user_otp
        self.user_email = user_email
        self.connection_pool = redis.ConnectionPool(
                                                     host=os.environ.get('HOST'),
                                                     port=int(os.environ.get('PORT')),
                                                     db=int(os.environ.get('DB'))
                                                        )
        self.client = redis.StrictRedis(connection_pool=self.connection_pool)

    async def store_password(self) -> None:
        """Stores password in Redis"""
        self.client.setex(self.user_email, 300, self.user_otp)

    async def check_user(self) -> bool:
        """Checks if user exists with such credentials"""
        return self.client.get(self.user_email) == self.user_otp
