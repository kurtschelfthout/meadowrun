import asyncio
import os
import platform
import sys
from pprint import pprint
from statistics import median
from time import monotonic
from meadowrun.meadowrun_pb2 import ContainerAtTag, GitRepoCommit

from meadowrun.run_job import (
    AllocCloudInstance,
    Deployment,
    run_function,
)
import meadowrun.optional_eliot as eliot


async def main():

    nb_runs = 1

    # hack to find the automated module.
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from automated.test_aws_automated import EC2InstanceRegistrarProvider

    def remote_function():
        return os.getpid(), platform.node()

    irp = EC2InstanceRegistrarProvider()
    times = []
    async with await irp.get_instance_registrar() as instance_registrar:
        for i in range(nb_runs):
            start_time = monotonic()
            pid1, host1 = await run_function(
                remote_function,
                AllocCloudInstance(1, 0.5, 80, irp.cloud_provider()),
                Deployment(
                    interpreter=ContainerAtTag(
                        repository="python", tag="3.9.8-slim-buster"
                    ),
                    code=GitRepoCommit(
                        repo_url="https://github.com/meadowdata/test_repo",
                        commit="cb277fa1d35bfb775ed1613b639e6f5a7d2f5bb6",
                    ),
                ),
            )
            times.append(monotonic() - start_time)
            await irp.clear_instance_registrar(instance_registrar)
    print("Times in secs:")
    pprint(times)
    print(f"Min: {min(times):.2f}")
    print(f"Median: {median(times):.2f}")
    print(f"Max: {max(times):.2f}")


if __name__ == "__main__":
    with open("ec2_startup_time.log", "w", encoding="utf-8") as file:
        eliot.to_file(file)
        asyncio.run(main())
