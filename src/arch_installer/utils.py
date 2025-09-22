import subprocess, logging, shlex

logger = logging.getLogger(__name__)

class CommandError(RuntimeError):
    pass

def run(cmd, *, check=True, capture_output=True, shell=False, env=None):
    logger.info("RUN: %s", cmd)
    if shell:
        proc = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True, env=env)
    else:
        proc = subprocess.run(shlex.split(cmd), capture_output=capture_output, text=True, env=env)
    if check and proc.returncode != 0:
        logger.error("Command failed (%s): %s", proc.returncode, proc.stderr)
        raise CommandError(f"Command failed: {cmd}\n{proc.stderr}")
    return proc.stdout

