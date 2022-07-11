import asyncio
import os
import platform
import sys
from pprint import pprint
from statistics import median
from time import monotonic
from typing import Any

from meadowrun.run_job import (
    AllocCloudInstance,
    AllocCloudInstances,
    run_function,
    run_map,
)
import meadowrun.optional_eliot as eliot


def remote_function():
    return os.getpid(), platform.node()


async def do_run_function(irp, instance_registrar, times):
    start_time = monotonic()
    result: Any = await run_function(
        remote_function,
        # "example_package.example.example_runner",
        AllocCloudInstance(1, 0.5, 80, irp.cloud_provider()),
        # Deployment(
        #     interpreter=ContainerAtTag(repository="python", tag="3.9.8-slim-buster"),
        #     code=GitRepoCommit(
        #         repo_url="https://github.com/meadowdata/test_repo",
        #         commit="cb277fa1d35bfb775ed1613b639e6f5a7d2f5bb6",
        #     ),
        # ),
        # args=["foo"],
    )
    times.append(monotonic() - start_time)
    print(result)
    # await irp.clear_instance_registrar(instance_registrar)


async def do_run_map(irp, instance_registrar, times):
    start_time = monotonic()
    result: Any = await run_map(
        lambda i: remote_function(),
        list(range(20)),
        AllocCloudInstances(1, 0.5, 80, irp.cloud_provider(), num_concurrent_tasks=20),
    )
    times.append(monotonic() - start_time)
    print(result)
    # await irp.clear_instance_registrar(instance_registrar)


async def main():

    nb_runs = 10
    # hack to find the automated module.
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from automated.test_aws_automated import EC2InstanceRegistrarProvider

    irp = EC2InstanceRegistrarProvider()
    times: list = []
    async with await irp.get_instance_registrar() as instance_registrar:
        for i in range(nb_runs):
            await do_run_map(irp, instance_registrar, times)
    print("Times in secs:")
    pprint(times)
    print(f"Min: {min(times):.2f}")
    print(f"Median: {median(times):.2f}")
    print(f"Max: {max(times):.2f}")


if __name__ == "__main__":
    with open("ec2_startup_time.log", "w", encoding="utf-8") as file:
        eliot.to_file(file)
        asyncio.run(main())
