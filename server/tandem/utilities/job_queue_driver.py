from tandem.database.instances import redis

JOB_WAIT_QUEUE_KEY = 'tandem:jobs:waiting'
JOB_WORKING_PREFIX = 'tandem:jobs:working:'


class _JobQueueDriver:
    def __init__(self, inprogress_queue_key):
        self.inprogress_queue_key = inprogress_queue_key

    def _to_job(self, flow_id, run_id):
        return str(flow_id) + ':' + str(run_id)

    def _from_job(self, job):
        parts = job.split(':')
        print(parts, flush=True)
        return int(parts[0]), int(parts[1])

    def get_flow_job_blocking(self, timeout):
        job = redis.brpoplpush(
            JOB_WAIT_QUEUE_KEY, self.inprogress_queue_key, timeout)
        return self._from_job(job) if job is not None else None

    def mark_flow_job_completed(self, flow_id, run_id):
        job = self._to_job(flow_id, run_id)
        return redis.lrem(self.inprogress_queue_key, -1, job)

    def submit_flow_job(self, flow_id, run_id):
        job = self._to_job(flow_id, run_id)
        redis.lpush(JOB_WAIT_QUEUE_KEY, job)


class WorkerDriver:
    def __init__(self, worker_id):
        self.worker_id = worker_id
        self.inprogress_queue_key = JOB_WORKING_PREFIX + str(worker_id)
        self.driver = _JobQueueDriver(self.inprogress_queue_key)

    def get_flow_job_blocking(self, timeout):
        return self.driver.get_flow_job_blocking(timeout)

    def mark_flow_job_completed(self, flow_id, job_id):
        return self.driver.mark_flow_job_completed(flow_id, job_id)


class JobSubmitDriver:
    def __init__(self):
        self.driver = _JobQueueDriver(None)

    def submit_flow_job(self, flow_id, run_id):
        self.driver.submit_flow_job(flow_id, run_id)
