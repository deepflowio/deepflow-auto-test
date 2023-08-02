import time
import sys
from common.redis import redis
from common import common_config
from common import const
from common import logger
from common.redis.dfenvs import DFEnvs

log = logger.getLogger()
ENV_STATUS_FREE = "0"
ENV_STATUS_MONOPOLIZE = "-1"
ENV_RESERVED_FREE = "0"
ENV_RESERVED_CONCURRENCY = "1"
ENV_RESERVED_MONOPOLIZE = "-1"


def apply_env(func):

    def wapper(self, *args, **kwargs):
        status = ""
        success = False
        env_name = ""
        # Get env, wait if both are occupied.
        while not success:
            # add  lock
            identifier = redis.acquire_lock(common_config.df_env_uuid)
            # log.warning(f"acquier lock success {common_config.df_env_uuid}")
            start = time.time()
            envs = df_envs.get_df_envs()
            if not envs:
                log.error("Get DF Envs Failed!")
                assert False
            for name, env in envs.items():
                # The envt has been monopolized
                if env["status"] == ENV_STATUS_MONOPOLIZE:
                    continue
                if self.CASE_TYPE == const.CASE_TYPE_MONOPOLIZE:
                    if env["reserved"] == ENV_RESERVED_CONCURRENCY:
                        continue
                    # The environment is already occupied by concurrent use cases
                    if env["status"] != ENV_STATUS_FREE and env["concurrency"
                                                                ] != "0":
                        continue
                    else:
                        # free
                        success = True
                        env_name = name
                        self.df_ce_info = env
                        status = ENV_STATUS_MONOPOLIZE
                        df_envs.update_env_status(env_name, status)
                        break
                elif self.CASE_TYPE == const.CASE_TYPE_CONCURRENCY:
                    # The envt has been monopolized
                    if env["reserved"] == ENV_RESERVED_MONOPOLIZE:
                        continue
                    if env["status"] == ENV_STATUS_MONOPOLIZE:
                        continue
                    else:
                        success = True
                        status = ENV_STATUS_FREE
                        env_name = name
                        self.df_ce_info = env
                        # concurrency+1
                        concurrency = str(int(env["concurrency"]) + 1)
                        df_envs.update_env_concurrency(env_name, concurrency)
                        break
            # release  lock
            redis.release_lock(common_config.df_env_uuid, identifier)
            #log.warning(
            #    f"release lock success {common_config.df_env_uuid} {time.time()-start}s"
            #
            if not success:
                time.sleep(3)
        # case run
        print(
            f"case: {self.class_name()} Apply Env Success: {self.df_ce_info} Status: {status}",
            file=sys.stderr
        )
        func(self, *args, **kwargs)

    return wapper


def release_env(func):

    def wapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        # release env
        status = ""
        identifier = redis.acquire_lock(common_config.df_env_uuid)
        envs = df_envs.get_df_envs()
        for name, env in envs.items():
            if env["mgt_ip"] != self.df_ce_info["mgt_ip"]:
                continue
            if self.CASE_TYPE == const.CASE_TYPE_MONOPOLIZE:
                status = ENV_STATUS_FREE
                df_envs.update_env_status(name, status)
            elif self.CASE_TYPE == const.CASE_TYPE_CONCURRENCY:
                concurrency = str(int(env["concurrency"]) - 1)
                status = ENV_STATUS_FREE
                df_envs.update_env_concurrency(name, concurrency)
        redis.release_lock(common_config.df_env_uuid, identifier)
        print(
            f"case: {self.class_name()} Release Env Success: {self.df_ce_info} Status: {status}",
            file=sys.stderr
        )

    return wapper


df_envs = DFEnvs(common_config.df_env_uuid)
