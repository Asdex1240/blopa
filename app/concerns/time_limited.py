from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeout


class TimeLimited:
    time_limit = 15

    def within_time_limit(self, function, *arguments):
        executor = ThreadPoolExecutor(max_workers=1)
        try:
            return executor.submit(function, *arguments).result(timeout=self.time_limit)
        except FutureTimeout:
            raise TimeoutError(f"no respondió en {self.time_limit} segundos")
        finally:
            executor.shutdown(wait=False, cancel_futures=True)
