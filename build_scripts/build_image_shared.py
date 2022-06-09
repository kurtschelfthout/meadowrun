import os
import io
from typing import cast

import fabric
import paramiko.ssh_exception

from meadowrun.run_job_core import _retry


async def upload_and_configure_meadowrun(
    connection: fabric.Connection, version: str, package_root_dir: str
) -> None:
    # retry with a no-op until we've established a connection
    await _retry(
        lambda: connection.run("echo $HOME"),
        (
            cast(Exception, paramiko.ssh_exception.NoValidConnectionsError),
            cast(Exception, TimeoutError),
        ),
    )

    # install the meadowrun package
    connection.put(
        os.path.join(package_root_dir, "dist", f"meadowrun-{version}-py3-none-any.whl"),
        "/var/meadowrun/",
    )
    connection.run(
        "source /var/meadowrun/env/bin/activate "
        f"&& pip install /var/meadowrun/meadowrun-{version}-py3-none-any.whl"
    )
    connection.run(f"rm /var/meadowrun/meadowrun-{version}-py3-none-any.whl")

    # set deallocate_jobs to run from crontab
    crontab_line = (
        "* * * * * /var/meadowrun/env/bin/python "
        "/var/meadowrun/env/lib/python3.9/site-packages/meadowrun"
        "/deallocate_jobs.py "
        "--cloud EC2 --cloud-region-name default "
        ">> /var/meadowrun/deallocate_jobs.log 2>&1\n"
    )
    with io.StringIO(crontab_line) as sio:
        connection.put(sio, "/var/meadowrun/meadowrun_crontab")
    connection.run("crontab < /var/meadowrun/meadowrun_crontab")
    connection.run("rm /var/meadowrun/meadowrun_crontab")
