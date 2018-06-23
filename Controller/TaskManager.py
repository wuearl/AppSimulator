# coding:utf-8
import importlib
import importlib.util
import time
from datetime import datetime
import subprocess
from Controller.setting import *
from Controller.DBLib import MongoDriver
from Controller.NoxConDocker import NoxConDocker


# ------------------------ docker task manager ----------------------
class TaskManager(object):
    def __init__(self):
        self.db = MongoDriver()
        self.db._DEBUG = True
        self._DEBUG = False

    def _log(self, prefix, msg):
        if self._DEBUG:
            print(prefix, msg)

    def run_task(self, task):
        _stdout = ''
        _stderr = ''
        try:
            cmdline = 'python ' + task['script']
            self._log('run_task', cmdline)
            time.sleep(1)
            process = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # process.wait()
            (stdout, stderr) = process.communicate()
            _stdout = stdout.decode('utf8')
            _stderr = stderr.decode('utf8')
        except Exception as e:
            self._log('run_task exception:', e)

        if _stderr:
            self._log('run_task stderr:\n', _stderr)
            return False
        else:
            self._log('run_task stdout:\n', _stdout)
            time.sleep(1)
            return True

    def run_script(self, task):
        # module_spec = importlib.util.find_spec(task['script'])
        # if module_spec:
        #     module = importlib.util.module_from_spec(module_spec)
        #     module_spec.loader.exec_module(module)

        module = importlib.import_module(task['script'])
        module.main()

    def start_tasks(self):
        while True:
            task = self.db.task_get_one_for_build()
            if task:
                task['status'] = STATUS_BUILDING
                self.db.task_change_status(task)

                d = NoxConDocker(task['app_name'], 'nox-' + task['taskId'])
                ret = d.build(force=True, retry_cnt=2, wait_time=30)
                status = STATUS_BUILD_OK if ret else STATUS_BUILD_NG

                docker = {'_id': self.db.docker_create(task), 'status': status}
                self.db.docker_change_status(docker)

                task['status'] = status
                self.db.task_change_status(task)
                if ret:
                    self.db.task_set_docker(task, docker)  # bind docker to task
                    ret = self.run_task(task)
                    task['status'] = STATUS_RUN_OK if ret else STATUS_RUN_NG
                    self.db.task_change_status(task)

                # break
            else:
                time.sleep(1 * 60)
