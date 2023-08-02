import redis
import time
import uuid
from redis.exceptions import WatchError

conn_pool = redis.ConnectionPool(
    host='redis-master', port=6379, max_connections=10, password='root', db=0
)
KEY_NAME_DF_ENV_NAMES = "df-env-names"
DF_ENV_TIMEOUT = 3600 * 24
ENVS_LIST_KEY = "env_uuids"
GLOBAL_LOCK = "get_env_info"


def acquire_lock(lockname, acquite_timeout=30, time_out=20):
    """
    :param lockname: Name of the lock
    :param acquire_timeout: Timeout for lock acquisition, default 30 seconds.
    :param lock_timeout: Lock timeout, default 20 seconds
    :return: uuid
    """
    identifier = str(uuid.uuid4())
    end = time.time() + acquite_timeout
    conn = redis.Redis(connection_pool=conn_pool)
    while time.time() < end:
        if conn.setnx(lockname, identifier):
            # Set the expiration time of the key and automatically release the lock when it expires
            conn.expire(lockname, time_out)
            return identifier
        # Resetting the expiration time of a lock when it has not been set
        elif conn.ttl(lockname) == -1:
            conn.expire(lockname, time_out)
        time.sleep(0.001)
    return identifier


def release_lock(lockname, identifier):
    """
    :param lockname: Name of the lock
    :param identifier: Lock Identification
    """
    conn = redis.Redis(connection_pool=conn_pool)
    with conn.pipeline() as pipe:
        while True:
            try:
                # If the key is changed by another client, the transaction throws a WatchError exception.
                pipe.watch(lockname)
                iden = pipe.get(lockname)
                if iden and iden.decode('utf-8') == identifier:
                    pipe.multi()
                    pipe.delete(lockname)
                    pipe.execute()
                    return True
                pipe.unwatch()
                break
            except WatchError:
                pass
        return False


def get_envs():
    conn = redis.Redis(connection_pool=conn_pool)
    envs = []
    envs_prefixs = conn.lrange(ENVS_LIST_KEY, 0, -1)
    for prefix in envs_prefixs:
        env = {}
        env["prefix"] = prefix.decode('utf-8')
        list_key_name = f"{env['prefix']}-{KEY_NAME_DF_ENV_NAMES}"
        env_names = conn.lrange(list_key_name, 0, -1)
        env["names"] = [name.decode('utf-8') for name in env_names]
        envs.append(env)
    return envs


def get_prefix_envs(prefix=""):
    list_key_name = f"{prefix}-{KEY_NAME_DF_ENV_NAMES}"
    conn = redis.Redis(connection_pool=conn_pool)
    env_names = conn.lrange(list_key_name, 0, -1)
    envs = {}
    for name in env_names:
        name = name.decode('utf-8')
        env = conn.hgetall(name)
        if env:
            env_decode = {}
            for k, v in env.items():
                env_decode[k.decode('utf-8')] = v.decode('utf-8')
            envs[name] = env_decode
    return envs


def init_envs(envs, prefix=""):
    """
    envs = [{
        "name": "df-ce-0",
        "status": "0",
        "mgt_ip": "10.1.19.1",
        "updated_time": "1600000000",
        "type": "deepflow",
    }]
    """
    conn = redis.Redis(connection_pool=conn_pool)
    list_key_name = f"{prefix}-{KEY_NAME_DF_ENV_NAMES}"
    for env in envs:
        env_name = env['name']
        # env list
        conn.lpush(list_key_name, env_name)
        # env metadata
        conn.hmset(env_name, env)
        # env timeout
        conn.expire(env_name, DF_ENV_TIMEOUT)
    # List timeout reset
    conn.expire(list_key_name, DF_ENV_TIMEOUT)
    envs_prefixs = conn.lrange(ENVS_LIST_KEY, 0, -1)
    if prefix not in [prefix.decode('utf-8') for prefix in envs_prefixs]:
        conn.lpush(ENVS_LIST_KEY, prefix)


def update(env_name, info: dict):
    conn = redis.Redis(connection_pool=conn_pool)
    update = False
    for k, v in info.items():
        if conn.hget(env_name, k) != v:
            conn.hset(env_name, k, v)
            update = True
    if update:
        updated = int(time.time())
        conn.hset(env_name, "updated_time", updated)


def update_env_status(env_name, status):
    conn = redis.Redis(connection_pool=conn_pool)
    conn.hset(env_name, "status", status)
    updated = conn.hget(env_name, "updated_time")
    updated = int(time.time()) - int(updated)
    conn.hset(env_name, "updated_time", updated)


def update_env_concurrency(env_name, concurrency):
    conn = redis.Redis(connection_pool=conn_pool)
    conn.hset(env_name, "concurrency", concurrency)
    updated = conn.hget(env_name, "updated_time")
    updated = int(time.time()) - int(updated)
    conn.hset(env_name, "updated_time", updated)


def delete_env(prefix):
    print(f"delete env {prefix}")
    conn = redis.Redis(connection_pool=conn_pool)

    # get envs list
    list_key_name = f"{prefix}-{KEY_NAME_DF_ENV_NAMES}"
    env_names = conn.lrange(list_key_name, 0, -1)
    for name in env_names:
        name = name.decode('utf-8')
        conn.delete(name)

    # delete env key list
    conn.delete(list_key_name)

    # delete env uuid
    conn.lrem(ENVS_LIST_KEY, 0, prefix)


def delete_instance_by_name(prefix, instance_name):
    conn = redis.Redis(connection_pool=conn_pool)
    list_key_name = f"{prefix}-{KEY_NAME_DF_ENV_NAMES}"
    env_names = conn.lrange(list_key_name, 0, -1)
    for name in env_names:
        name = name.decode('utf-8')
        if name == instance_name:
            conn.delete(name)
    conn.lrem(list_key_name, 0, instance_name)


def clear():
    conn = redis.Redis(connection_pool=conn_pool)
    conn.flushdb()
