# pylint: disable=[missing-module-docstring, missing-function-docstring, wrong-import-order]

import random
import time
import pytest


@pytest.mark.retry
@pytest.mark.flaky(reruns=2, reruns_delay=1)
def test_random_flaky():
    value = random.randint(1, 10)
    print(f"\nGenerated value: {value}")
    time.sleep(0.5)
    assert value > 5, f"Value {value} is not greater than 5"

