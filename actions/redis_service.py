import os
import redis
from dotenv import load_dotenv, find_dotenv
import warnings

load_dotenv(find_dotenv())


class RedisService:
    """Class to handle Redis connection"""

    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(RedisService, cls).__new__(cls)

        return cls._instance

    def __init__(self):
        try:
            self.connection_pool = redis.ConnectionPool(
                host=os.environ.get('HOST'),
                port=int(os.environ.get('PORT')),
                db=int(os.environ.get('DB')),
                decode_responses=True
            )
            self.client = redis.StrictRedis(connection_pool=self.connection_pool)
        except redis.ConnectionError:
            self.client = None
            warnings.warn("Redis connection error!")

    def store_password(self, user_email, user_otp) -> None:
        """Stores password in Redis"""
        self.client.setex(user_email, 300, user_otp)

    def check_user(self, user_email, user_otp) -> bool:
        """Checks if user exists with such credentials"""
        return self.client.get(user_email) == user_otp

    def delete_password(self, user_email) -> None:
        """Deletes password from Redis"""
        self.client.delete(user_email)
