import subprocess

def exec(cmd, timeout=None, **kwargs):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    communicate_kwargs = {}
    if timeout is not None:
        communicate_kwargs['timeout'] = timeout

    out, err = p.communicate(**communicate_kwargs)
    if p.returncode != 0:
        raise Exception(cmd, out, err)

    return out.decode('utf-8').strip()
