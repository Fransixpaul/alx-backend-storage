#!/usr/bin/env python3
"""
This module defines a Cache class for storing data in Redis with unique keys,
counting method calls, and storing call history.
"""
import redis
import uuid
from typing import Union, Callable, Optional
import functools


def count_calls(method: Callable) -> Callable:
    """
    A decorator that counts the number of calls to a method of the Cache class.

    Args:
        method (Callable): The method to be decorated.

    Returns:
        Callable: The wrapped function with call counting.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        # Increment the count for the method's qualified name
        key = method.__qualname__
        self._redis.incr(key)
        # Call the original method and return its result
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    A decorator that stores the history of inputs and outputs for a function.

    Args:
        method (Callable): The function to be decorated.

    Returns:
        Callable: The wrapped function with input/output history tracking.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        # Define keys for input and output lists in Redis
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        print(f"Calling {method.__qualname__} with arguments {args}")

        # Store the input arguments by pushing them to the inputs list
        self._redis.rpush(input_key, str(args))

        # Call the original method and store the output
        result = method(self, *args, **kwargs)
        print(f"{method.__qualname__} returned {result}")
        
        self.redis.rpush(output_key, str(result))

        return result
    
    return wrapper


class Cache:
    def __init__(self):
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        random_key = str(uuid.uuid4())
        self._redis.set(random_key, data)
        return random_key

    def get(
        self,
        key: str,
        fn: Optional[Callable] = None
    ) -> Union[str, bytes, int, float, None]:
        data = self._redis.get(key)
        if data is not None and fn is not None:
            return fn(data)
        return data

    def get_str(self, key: str) -> Union[str, None]:
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Union[int, None]:
        return self.get(key, fn=int)
