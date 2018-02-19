import sched
import time
from threading import Thread, Event


class TimeScheduler:
    """
    Schedules tasks to run in the future on an executor.

    The queue of tasks to execute is inspected every
    resolution_seconds. So the minimal delay for a task
    is the resolution of this scheduler.
    """
    def __init__(self, executor, resolution_seconds=0.1):
        self._executor = executor
        self._resolution_seconds = resolution_seconds

        self._shutting_down = False
        self._shut_down_event = Event()
        self._runner = Thread(target=self._run_scheduler)
        self._scheduler = sched.scheduler(time.time, time.sleep)

    def run_after(self, delay_seconds, function, *args, **kwargs):
        """
        Schedules the specified function on the executor after delay_seconds.

        This returns a handle that can be used with the cancel()
        function to cancel the request to run this function.
        """
        return self._scheduler.enter(
            delay_seconds,
            0,
            self._schedule_on_executor,
            (function, *args),
            kwargs,
        )

    def run_every(self, interval_seconds, function, *args, **kwargs):
        """
        Schedules the specified function at least every interval_seconds.

        This returns a handle that can be used with the cancel()
        function to cancel this interval.

        This only guarantees that at least interval_seconds elapses
        between each invocation of the function. It does not guarantee
        that the function runs exactly every interval_seconds.
        """
        interval_handle = IntervalHandle(interval_seconds)
        self._schedule_interval(
            function,
            interval_handle,
            *args,
            **kwargs,
        )
        return interval_handle

    def cancel(self, handle):
        """
        Cancels the request to run a function or the interval.

        If the handle is invalid the call will be a no-op.
        """
        try:
            event_handle = (
                handle if type(handle) is not IntervalHandle
                else handle.get_event_handle()
            )
            self._scheduler.cancel(event_handle)
        except ValueError:
            pass

    def start(self):
        """
        Starts this scheduler.

        Until this is called, no tasks will actually be scheduled.
        However the scheduler will still accept schedule requests.
        """
        self._runner.start()

    def stop(self):
        """
        Stops this scheduler.

        All remaining pending tasks after this returns will no
        longer be scheduled. This does not wait for all pending
        tasks to be scheduled.
        """
        self._shutting_down = True
        self._shut_down_event.set()
        self._runner.join()

    def _schedule_interval(self, function, interval_handle, *args, **kwargs):
        event_handle = self.run_after(
            interval_handle.get_interval_seconds(),
            self._run_interval,
            function,
            interval_handle,
            *args,
            **kwargs,
        )
        interval_handle.set_event_handle(event_handle)

    def _run_interval(self, function, interval_handle, *args, **kwargs):
        try:
            function(*args, **kwargs)
        finally:
            self._schedule_interval(function, interval_handle, *args, **kwargs)

    def _run_scheduler(self):
        while not self._shutting_down:
            self._scheduler.run(blocking=False)
            self._shut_down_event.wait(timeout=self._resolution_seconds)

    def _schedule_on_executor(self, function, *args, **kwargs):
        self._executor.submit(function, *args, **kwargs)


class IntervalHandle:
    def __init__(self, interval_seconds):
        self._event_handle = None
        self._interval_seconds = interval_seconds

    def get_event_handle(self):
        return self._event_handle

    def get_interval_seconds(self):
        return self._interval_seconds

    def set_event_handle(self, new_handle):
        self._event_handle = new_handle
