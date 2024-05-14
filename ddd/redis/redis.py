from contextlib import nullcontext
import redis
from redis.commands.json.path import Path
import os

REDIS_HOST = os.environ.get('REDIS_URL')
REDIS_PORT = os.environ.get('REDIS_PORT')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')

class Redis():

    r = redis.Redis(host='redis-19314.c51.ap-southeast-2-1.ec2.cloud.redislabs.com', port=19314, password='fTjZuqrFufSdxBPiKTTu0LC6LFWLfZs7', decode_responses=True)

    def hget(key, field):
        print("Retrieving from Redis")
        return Redis.r.hget(key, field)


    def hset(key, field, value):
        Redis.r.hset(key, field, value)
        print("Hash Set")

        return Redis.hget(key, field)

    def checkExists(key, field):
        print("Checking Key")

        return Redis.r.hexists(key, field)

    def setExpire(key, duration):
        print("Set Expiration")

        return Redis.r.expire(key, duration)

    def jsonSet(key, field):
        print("Json Set")
        return Redis.r.json().set(key, Path.root_path(), field)

    def jsonGet(key):
        print("Json Get")
        return Redis.r.json().get(key)