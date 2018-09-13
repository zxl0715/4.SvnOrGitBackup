import multiprocessing
import os
import random
import time


def run_proc(job_id):
    print('Child process Job  {0} {1} Running begin! {2}'.format(job_id, os.getpid() , time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
    time.sleep(random.randint(3,6))
    print('Child process Job  {0} {1} Running end! {2}'.format(job_id, os.getpid() , time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))



if __name__ == '__main__':

    num_cores = multiprocessing.cpu_count()
    print('内核数为num_cores :{}'.format(num_cores))
    print('Parent process {0} is Running'.format(os.getpid()))
    for i in range(5):
        p = multiprocessing.Process(target=run_proc, args=(str(i),))
        print('process start {0}'.format(i))
        p.start()
    p.join()
    print('Process close')