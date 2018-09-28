from functools import wraps
from datetime import datetime, timedelta

import asyncio
import asyncssh


def async_task(func):
    @wraps(func)
    def wrapper(host, *args, context=None, **kwargs):
        client = SshClient(host, context=context)
        return func(client, *args, **kwargs)

    return wrapper


class SshClient:

    def __init__(self, host, context=None):
        self.host = host
        self.context = context
        self.start_time = datetime.now()

    async def run(self, command, connect_timeout_secs=3.0, run_timeout_secs=0.0):
        assert connect_timeout_secs > 0, 'connection_timeout_sec must be greater than 0'

        result = None
        error = None
        try:
            conn = await asyncio.wait_for(
                asyncssh.connect(
                    self.host,
                    known_hosts=None
                ),
                timeout=connect_timeout_secs
            )

        except asyncio.TimeoutError:
            error = asyncio.TimeoutError('connection timed out')
            return result, error

        except Exception as e:
            error = e
            return result, error

        try:
            _task = None
            while True:
                await asyncio.sleep(1)

                if not _task:
                    _task = asyncio.ensure_future(conn.run(command))

                if run_timeout_secs > 0:
                    now = datetime.now()
                    if now - self.start_time > timedelta(seconds=run_timeout_secs):
                        _task.cancel()
                        raise asyncio.TimeoutError('command timed out')

                if _task.done():
                    return _task.result(), error

        except Exception as e:
            error = e
            return result, error

        finally:
            if conn:
                conn.close()

    def output(self, string_data, fields=None):
        show = self._filter_fields(fields)

        return f'{self.host} {show and show or None} ({datetime.now() - self.start_time}):\n{string_data}'

    def _filter_fields(self, fields):
        if fields and self.context:
            return {k: v for k, v in self.context.items() if k in fields}


class ConcurrentExecutor:

    def __init__(self, concurrent=10):
        self.concurrent = concurrent
        self.running = 0
        self.results = []

    async def execute_func(self, host, func, context=None):
        result = await func(host, context=context)
        self.results.append({
            'host': host,
            'result': result
        })
        self.running -= 1

    async def run_func_on_hosts(self, hosts, func, interval=0.2):
        while len(hosts):
            while len(hosts) and self.running < self.concurrent:
                host = hosts.pop()
                self.running += 1

                asyncio.ensure_future(self.execute_func(host, func))

            await asyncio.sleep(interval)

        while self.running > 0:
            await asyncio.sleep(interval)

    async def run_func_on_rows(self, rows, host_field, func, interval=0.2):
        while len(rows):
            while len(rows) and self.running < self.concurrent:
                row = rows.pop()
                self.running += 1

                host = row[host_field]

                asyncio.ensure_future(self.execute_func(host, func, context=row))

            await asyncio.sleep(interval)

        while self.running > 0:
            await asyncio.sleep(interval)
