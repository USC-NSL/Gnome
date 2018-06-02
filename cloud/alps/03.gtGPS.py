'''
Author: Yurong Jiang, Xiaochen Liu
Function: Get the ground truth location of the google SV image
How to use: 
    - Before using, specify the path of streetview-events.html at line 20
    - $ python gtGPS.py [path_of_location_file]
    - You can test the program with given file 'input.txt'
Input: the location file should contain lines of location data like 'lat,lng'
Output: 'gtLocations.txt' contains corresponding ground truth 'lat,lng' 
'''

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest, time, re
import sys
import multiprocessing
import threading

import os

query_city = open("./alps/config/query_city.info", "r").readline().rstrip()
query_area = open("./alps/config/query_area.info", "r").readline().rstrip()
work_dir = "./alps/data/%s/%s/" % (query_city, query_area.replace(" ", "").replace(",", "|"))

GTLOC = '03.gps_hacking_output.txt' # the output file name
SVHTML = '%s/libs/streetview-events.html' % os.path.dirname(os.path.abspath(__file__))  # path to the html file # Modify this!

class ProcManager(object):
    def __init__(self):
        self.procs = []
        self.errors_flag = False
        self._threads = []
        self._lock = threading.Lock()

    def terminate_all(self):
        with self._lock:
            for p in self.procs:
                if p.is_alive():
                    print "Terminating %s" % p
                    p.terminate()

    def launch_proc(self, func, args=(), kwargs= {}):
        t = threading.Thread(target=self._proc_thread_runner,
                             args=(func, args, kwargs))
        self._threads.append(t)
        t.start()

    def _proc_thread_runner(self, func, args, kwargs):
        p = multiprocessing.Process(target=func, args=args, kwargs=kwargs)
        self.procs.append(p)
        p.start()
        while p.exitcode is None:
            p.join()
        if p.exitcode > 0:
            self.errors_flag = True
            self.terminate_all()

    def wait(self):
        for t in self._threads:
            t.join()

def testworker_simpleload(weburl):   
    driver = webdriver.Firefox()
    while True:
        try:
            driver.get(weburl)
            time.sleep(0.2)
        except (KeyboardInterrupt, SystemExit):
            raise Exception("keyboard captured")
        except:
            raise Exception("something wrong")

def bad_worker():
    print "[BadWorker] Starting"
    time.sleep(2)
    raise Exception("ups!")

def simpletest():
    driver = webdriver.Firefox()
    for i in range(5):
        driver.get("http://www.python.org")
        assert "Python" in driver.title
        elem = driver.find_element_by_name("q")
        elem.send_keys("pycon")
        elem.send_keys(Keys.RETURN)
        assert "No results found." not in driver.page_source

def GetLatLon(din, outFileName):
    driver = webdriver.Firefox()
    fout = open(work_dir + outFileName,'w')
    for i in xrange(len(din)):
        inloc = din[i].strip().split(',')
        url = 'file://' + SVHTML + '?lat=' + inloc[0] + '&&lng=' + inloc[1]
        # print url
        driver.get(url)
        table = driver.find_element_by_xpath('//td[@id="position-cell"]')
        table_html = table.get_attribute('innerHTML')
        if '(' in table_html and ')' in table_html:
            print `i` + '\t' + `inloc` + ' -> ' + table_html
            fout.write(table_html.split('(')[-1].split(')')[0] + '\n')
        else:
            print `i` + '\t' + `inloc` + ': No data received'
            # continue
            fout.write("Error on %s,%s...\n" % (inloc[0], inloc[1]))
    fout.close()
    driver.close()

if __name__ == '__main__':
    # if len(sys.argv) != 2:
    #     print 'Wrong argc! Should be: $ python gtGPS.py [path_of_location_file]'
    #     sys.exit(0)
    f = open(work_dir + "02.gps_hacking_input.txt", 'r')
    din = f.readlines()
    f.close()
    GetLatLon(din, GTLOC)
