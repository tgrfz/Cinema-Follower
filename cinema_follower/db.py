import os

import redis
from flask_rq import RQ
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

redis_client = redis.Redis(
    host=os.getenv('CF_REDIS_HOST', 'localhost'),
    port=int(os.getenv('CF_REDIS_PORT', 6379)),
    db=int(os.getenv('CF_REDIS_DB', 0)),
    decode_responses=True  # Return strings instead of bytes
)

rq = RQ()
