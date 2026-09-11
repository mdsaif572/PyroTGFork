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

import os
from concurrent.futures.thread import ThreadPoolExecutor


def _default_crypto_workers() -> int:
    override = os.environ.get("PYROTGFORK_CRYPTO_WORKERS", os.environ.get("WZGRAM_CRYPTO_WORKERS"))

    if override:
        try:
            return max(1, int(override))
        except ValueError:
            pass

    return min(4, max(2, os.cpu_count() or 1))


_crypto_pool = None


def get_crypto_executor() -> ThreadPoolExecutor:
    global _crypto_pool
    if _crypto_pool is None:
        _crypto_pool = ThreadPoolExecutor(
            max_workers=_default_crypto_workers(),
            thread_name_prefix="Crypto"
        )
    return _crypto_pool


def set_crypto_executor(executor: ThreadPoolExecutor):
    global _crypto_pool
    _crypto_pool = executor


def create_crypto_executor() -> ThreadPoolExecutor:
    return ThreadPoolExecutor(
        max_workers=1,
        thread_name_prefix="Crypto"
    )
