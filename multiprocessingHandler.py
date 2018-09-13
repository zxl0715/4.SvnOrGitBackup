import multiprocessing
import os
import time

def run_task(name):
    print('{3} Task {0} pid {1} is running, parent id is {2} '.format(name, os.getpid(), os.getppid(),time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) ))
    time.sleep(1)
    print('{1} Task {0} end.'.format(name,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) ))

if __name__ == '__main__':
    num_cores = multiprocessing.cpu_count()
    print('current process {0}'.format(os.getpid()))
    pool = multiprocessing.Pool(processes=num_cores)
    for i in range(8):
        pool.apply_async(run_task, args=(i,))
    print('Waiting for all subprocesses done...')
    pool.terminate()
    pool.join()
    print('All processes done!')