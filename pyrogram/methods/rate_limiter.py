#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
import time
from typing import Optional


class TokenBucket:
    def __init__(self, rate: float, burst: Optional[float] = None):
        self._rate = rate
        self._burst = burst if burst is not None else rate
        self._tokens = float(self._burst)
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()
        self._total_taken = 0

    @property
    def rate(self) -> float:
        return self._rate

    @rate.setter
    def rate(self, value: float):
        self._refill()
        self._rate = value

    @property
    def available(self) -> float:
        self._refill()
        return self._tokens

    def _refill(self):
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._burst, self._tokens + elapsed * self._rate)
        self._last_refill = now

    def _try_consume(self, tokens: float = 1.0) -> bool:
        self._refill()
        if self._tokens >= tokens:
            self._tokens -= tokens
            self._total_taken += tokens
            return True
        return False

    def _wait_time(self, tokens: float = 1.0) -> float:
        self._refill()
        if self._tokens >= tokens:
            return 0.0
        return (tokens - self._tokens) / max(self._rate, 0.0001)

    async def acquire(self, tokens: float = 1.0):
        async with self._lock:
            while True:
                self._refill()

                if self._tokens >= tokens:
                    self._tokens -= tokens
                    self._total_taken += tokens
                    return

                wait_time = (tokens - self._tokens) / max(self._rate, 0.0001)
                await asyncio.sleep(wait_time)
