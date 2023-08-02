import subprocess

from common import logger

log = logger.getLogger()


def run_cmd(cmd: str):
    log.info(f"exec cmd ==> {cmd}")
    return subprocess.run(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )


def run_cmds(cmds: list):
    for cmd in cmds:
        p = run_cmd(cmd)
        log.info(
            f"exec cmd {cmd} stdout: {p.stdout.decode('utf-8')} stderr: {p.stderr.decode('utf-8')}"
        )
