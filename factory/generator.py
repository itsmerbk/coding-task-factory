import json
import random
from dataclasses import dataclass, asdict
from typing import List

@dataclass
class CodingTask:
    task_id: str
    domain: str
    difficulty: str
    function_name: str
    prompt: str
    reference_solution: str
    test_code: str

DOMAINS = ["algorithms", "systems_security", "data_structures"]
DIFFICULTIES = ["easy", "medium", "hard"]

def synthesize_tasks(count: int = 15, seed: int = 2026) -> List[CodingTask]:
    rng = random.Random(seed)
    tasks: List[CodingTask] = []

    for idx in range(1, count + 1):
        domain = DOMAINS[(idx - 1) % len(DOMAINS)]
        difficulty = DIFFICULTIES[(idx - 1) % len(DIFFICULTIES)]
        k = rng.randint(2, 9)
        modulus = rng.choice([7, 11, 13, 17, 19])

        if domain == "algorithms":
            fn = f"sliding_window_mod_max_{idx}"
            prompt = (
                f"Implement `{fn}(nums: list[int], k: int = {k}) -> int` that returns the "
                f"maximum sum among all contiguous subarrays of length `k` whose sum is "
                f"divisible by {modulus}. Return -1 if no such subarray exists."
            )
            ref = f"""def {fn}(nums: list[int], k: int = {k}) -> int:
    if k <= 0 or k > len(nums):
        return -1
    best = -1
    curr = sum(nums[:k])
    if curr % {modulus} == 0:
        best = curr
    for i in range(k, len(nums)):
        curr += nums[i] - nums[i - k]
        if curr % {modulus} == 0 and curr > best:
            best = curr
    return best
"""
            tests = f"""assert {fn}([], {k}) == -1
assert {fn}([1] * ({k} - 1), {k}) == -1
arr = [{modulus} * (i + 1) for i in range({k} + 3)]
assert {fn}(arr, {k}) == sum(arr[-{k}:])
assert {fn}([1] * ({k} + 2), {k}) == (-1 if {k} % {modulus} != 0 else {k})
"""

        elif domain == "systems_security":
            fn = f"validate_token_window_{idx}"
            max_reqs = rng.randint(3, 6)
            window_sec = rng.randint(10, 30)
            prompt = (
                f"Implement `{fn}(timestamps: list[int]) -> list[bool]` simulating a sliding-window "
                f"rate limiter allowing at most {max_reqs} requests within any {window_sec}-second "
                f"inclusive window `[t - {window_sec}, t]`. Only accepted requests count toward the window."
            )
            ref = f"""from collections import deque

def {fn}(timestamps: list[int]) -> list[bool]:
    accepted = deque()
    result = []
    for ts in timestamps:
        while accepted and accepted[0] < ts - {window_sec}:
            accepted.popleft()
        if len(accepted) < {max_reqs}:
            accepted.append(ts)
            result.append(True)
        else:
            result.append(False)
    return result
"""
            tests = f"""assert {fn}([]) == []
burst = [100] * ({max_reqs} + 2)
assert {fn}(burst) == [True] * {max_reqs} + [False, False]
spaced = [i * ({window_sec} + 1) for i in range({max_reqs} + 3)]
assert {fn}(spaced) == [True] * ({max_reqs} + 3)
"""

        else:
            fn = f"compact_lsm_segments_{idx}"
            prompt = (
                f"Implement `{fn}(segments: list[list[tuple[str, int | None]]]) -> dict[str, int]` "
                f"that merges ordered key-value segments from oldest to newest. A value of `None` "
                f"represents a tombstone deletion; return only live keys with their latest integer values."
            )
            ref = f"""def {fn}(segments: list[list[tuple[str, int | None]]]) -> dict[str, int]:
    state: dict[str, int] = {{}}
    for seg in segments:
        for key, val in seg:
            if val is None:
                state.pop(key, None)
            else:
                state[key] = val
    return state
"""
            tests = f"""assert {fn}([]) == {{}}
assert {fn}([[("a", 1), ("b", 2)], [("a", None), ("b", 5), ("c", 9)]]) == {{"b": 5, "c": 9}}
assert {fn}([[("x", None)]]) == {{}}
"""

        tasks.append(
            CodingTask(
                task_id=f"CTF-2026-{idx:03d}",
                domain=domain,
                difficulty=difficulty,
                function_name=fn,
                prompt=prompt,
                reference_solution=ref,
                test_code=tests,
            )
        )
    return tasks

if __name__ == "__main__":
    generated = [asdict(t) for t in synthesize_tasks(15)]
    print(json.dumps(generated[:2], indent=2))
