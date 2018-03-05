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

        This returns a handle that has a cancel() method to cancel the
        request to run this function.
        """
        handle = _Handle(self)
        handle.set_event_handle(self._schedule_after(
            delay_seconds,
            function,
            handle,
            lambda: None,
            *args,
            **kwargs,
        ))
        return handle

    def run_every(self, interval_seconds, function, *args, **kwargs):
        """
        Schedules the specified function at least every interval_seconds.

        This returns a handle that has a cancel() method to cancel the
        request to run this function.

        This only guarantees that at least interval_seconds elapses
        between each invocation of the function. It does not guarantee
        that the function runs exactly every interval_seconds.
        """
        handle = _Handle(self)

        def reschedule():
            handle.set_event_handle(self._schedule_after(
                interval_seconds,
                function,
                handle,
                reschedule,
                *args,
                **kwargs,
            ))

        reschedule()
        return handle

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

    def _cancel(self, event_handle):
        try:
            self._scheduler.cancel(event_handle)
        except ValueError:
            pass

    def _schedule_after(
        self,
        delay_seconds,
        function,
        handle,
        epilogue,
        *args,
        **kwargs,
    ):
        return self._scheduler.enter(
            delay_seconds,
            0,
            self._executor.submit,
            (self._run_if_not_cancelled, function, handle, epilogue, *args),
            kwargs,
        )

    def _run_if_not_cancelled(
        self,
        function,
        handle,
        epilogue,
        *args,
        **kwargs,
    ):
        if handle.is_cancelled():
            return
        try:
            function(*args, **kwargs)
        finally:
            epilogue()

    def _run_scheduler(self):
        while not self._shutting_down:
            self._scheduler.run(blocking=False)
            self._shut_down_event.wait(timeout=self._resolution_seconds)


class _Handle:
    def __init__(self, scheduler):
        self._scheduler = scheduler
        self._event_handle = None
        self._cancelled = False

    def cancel(self):
        self._cancelled = True
        self._scheduler._cancel(self._event_handle)

    def is_cancelled(self):
        return self._cancelled

    def set_event_handle(self, new_handle):
        self._event_handle = new_handle
