#!coding=utf-8

__author__ = 'felix'

from xpinyin import Pinyin
#from pypinyin import pinyin, lazy_pinyin
import requests
import time
import sys
import threading

from Queue import Queue
from optparse import OptionParser


class Worker(threading.Thread):
    def __init__(self, work_queue, result_queue):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.result_queue = result_queue
        self.start()

    def run(self):
         while True:
            func, arg, code_index = self.work_queue.get()
            res = func(arg, code_index)
            self.result_queue.put(res)
            if self.result_queue.full():
                res = sorted([self.result_queue.get() for i in range(self.result_queue.qsize())], key=lambda s: s[0], reverse=True)
#                res.insert(0, ('0', u'name    price'))
                print '*'*50
                for obj in res:
                    print '*' + obj[1] + '*'
                   # print obj
            self.work_queue.task_done()


class Stock(object):

    def __init__(self, code, thread_num):
        self.code = code
        self.work_queue = Queue()
        self.threads = []
        self.__init_thread_poll(thread_num)

    def __init_thread_poll(self, thread_num):
        self.params = self.code.split(',')
        self.params.extend(['s_sh000001','s_sz399001'])
#        self.params.extend(['s_sz399001'])
        self.result_queue = Queue(maxsize=len(self.params[::-1]))
        for i in range(thread_num):
            self.threads.append(Worker(self.work_queue, self.result_queue))

    def __add_work(self, stock_code, code_index):
        self.work_queue.put((self.value_get, stock_code, code_index))

    def del_params(self):
        for obj in self.params:
            self.__add_work(obj, self.params.index(obj))

    def wait_all_complete(self):
        for thread in self.threads:
            if thread.isAlive():
                thread.join()

    @classmethod
    def value_get(cls, code, code_index):
        pin = Pinyin()
        slice_num, value_num = 21, 3
        name, now , high = u'——无——', u'  ——无——', u'——无——'
        if code in ['s_sh000001','s_sz399001']:
            slice_num = 23
            value_num = 1
        r = requests.get("http://hq.sinajs.cn/list=%s" % (code,))
        res = r.text.split(',')
        if len(res) > 1:
            if code in ["s_sh000001",'s_sz399001']:
                name, start, now, high, low, tom_stop = res[0][slice_num], "none", res[1], "none", "none", "none"
                tom_now_percent = res[3]
            else:
                name, start, now, high, low, tom_stop = res[0][slice_num:], res[1], res[value_num], res[4], res[5], res[2]
                tom_now_percent = format((float(now) - float(tom_stop))/float(tom_stop)*100,'.3f')
            return code_index, pin.get_pinyin(name)[0:5] + ' start:' + start + ' now:' + now + ' high:' + high + ' low:' +\
    low + ' percent ' + tom_now_percent

if __name__ == '__main__':
    parser = OptionParser(description="Query the stock's value.", usage="%prog [-c] [-s] [-t]", version="%prog 1.0")
    parser.add_option('-c', '--stock-code', dest='codes',
                      help="the stock's code that you want to query.")
    parser.add_option('-s', '--sleep-time', dest='sleep_time', default=1, type="int",
                      help='How long does it take to check one more time.')
    parser.add_option('-t', '--thread-num', dest='thread_num', default=3, type='int',
                      help="thread num.")
    options, args = parser.parse_args(args=sys.argv[1:])

    assert options.codes, "Please enter the stock code!"  
    if filter(lambda s: s[:-6] not in ('sh', 'sz', 's_sh', 's_sz'), options.codes.split(',')):
        raise ValueError

    stock = Stock(options.codes, options.thread_num)

    while True:
        stock.del_params()
        time.sleep(options.sleep_time)
