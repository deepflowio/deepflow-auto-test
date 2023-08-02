import time
from common.redis import redis
from automation_deploy import const as deploy_const

ENV_STATUS_FREE = "0"
ENV_STATUS_MONOPOLIZE = "-1"

ENV_RESERVED_FREE = "0"
ENV_RESERVED_CONCURRENCY = "1"
ENV_RESERVED_MONOPOLIZE = "-1"

ENV_DEPLOY_STATUS_INIT = "init"


class DFEnvs(object):

    def __init__(self, uuid=None):
        self.envs = []
        self.uuid = uuid
        self.df_envs = []

    def append(self, name, type):
        info = {
            "name": name,
            "deploy_status": ENV_DEPLOY_STATUS_INIT,
            "status": ENV_STATUS_FREE,
            "concurrency": "0",
            "mgt_ip": "",
            "server_query_port": "",
            "server_controller_port": "",
            "updated_time": str(int(time.time())),
            "reserved": "0",  # Reserve environments to prevent concurrent use cases from being blocked when all environments are occupied
            "type": type,
        }
        self.envs.append(info)

    def update(self, name, **kwargs):
        lock = redis.acquire_lock(redis.GLOBAL_LOCK)
        for env in self.envs:
            if env["name"] == name:
                env.update(kwargs)
                redis.update(name, kwargs)
        redis.release_lock(redis.GLOBAL_LOCK, lock)

    def insert(self):
        lock = redis.acquire_lock(redis.GLOBAL_LOCK)
        envs = redis.get_envs()
        envs = {env["prefix"]: env["names"] for env in envs}
        print(self.uuid)
        print(envs)
        if self.uuid not in envs.keys():
            self.init()
        else:
            redis.init_envs(self.envs, self.uuid)
        redis.release_lock(redis.GLOBAL_LOCK, lock)

    def init(self):
        if not self.uuid:
            return
        for env in self.envs:
            if env["type"] == deploy_const.ENV_TYPE_DEEPFLOW_CE:
                self.df_envs.append(env)
        if len(self.df_envs) > 2:
            self.df_envs[0]["reserved"] = ENV_RESERVED_FREE
            self.df_envs[1]["reserved"] = ENV_RESERVED_CONCURRENCY
            self.df_envs[2]["reserved"] = ENV_RESERVED_MONOPOLIZE
        if len(self.df_envs) > 3:
            for env in self.df_envs[3:]:
                env["reserved"] = ENV_RESERVED_MONOPOLIZE
        print(self.envs)
        redis.init_envs(self.envs, self.uuid)

    def get_df_envs(self):
        # Simple LB Sort by concurrency Lowest to highest
        if not self.uuid:
            return
        lock = redis.acquire_lock(redis.GLOBAL_LOCK)
        envs = redis.get_prefix_envs(self.uuid)
        redis.release_lock(redis.GLOBAL_LOCK, lock)
        envs = {
            name: env for name, env in envs.items() if env["type"] ==
            deploy_const.ENV_NAME_MAP[deploy_const.ENV_TYPE_DEEPFLOW_CE]
        }
        keys = sorted(envs, key=lambda x: get_concurrency(envs, x))
        new_envs = {}
        for key in keys:
            new_envs[key] = envs[key]
        return new_envs

    def get_all(self):
        if not self.uuid:
            return
        lock = redis.acquire_lock(redis.GLOBAL_LOCK)
        envs = redis.get_prefix_envs(self.uuid)
        redis.release_lock(redis.GLOBAL_LOCK, lock)
        return envs

    def update_env_status(self, env_name, status):
        lock = redis.acquire_lock(redis.GLOBAL_LOCK)
        redis.update_env_status(env_name, status)
        redis.release_lock(redis.GLOBAL_LOCK, lock)

    def update_env_concurrency(self, env_name, concurrency):
        lock = redis.acquire_lock(redis.GLOBAL_LOCK)
        redis.update_env_concurrency(env_name, concurrency)
        redis.release_lock(redis.GLOBAL_LOCK, lock)

    def list_env_uuids(self):
        lock = redis.acquire_lock(redis.GLOBAL_LOCK)
        envs = redis.get_envs()
        redis.release_lock(redis.GLOBAL_LOCK, lock)
        return envs

    def delete_envs_by_uuid(self):
        lock = redis.acquire_lock(redis.GLOBAL_LOCK)
        redis.delete_env(self.uuid)
        redis.release_lock(redis.GLOBAL_LOCK, lock)

    def delete_instance_by_name(self, instance_name):
        lock = redis.acquire_lock(redis.GLOBAL_LOCK)
        redis.delete_instance_by_name(self.uuid, instance_name)
        envs = redis.get_prefix_envs(self.uuid)
        if not envs:
            redis.delete_env(self.uuid)
        redis.release_lock(redis.GLOBAL_LOCK, lock)


def get_concurrency(envs, name):
    if envs[name]['status'] == ENV_STATUS_MONOPOLIZE:
        return 9999
    else:
        return int(envs[name]['concurrency'])
