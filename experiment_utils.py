#!/usr/bin/env python

import runner
import csv
import time
import subprocess
import os
import ConfigParser
import io

os.system('cmake -DCMAKE_BUILD_TYPE=Release CMakeLists.txt; make')
process = subprocess.Popen(['git','rev-parse','HEAD'],stdout=subprocess.PIPE)
REV = process.communicate()[0].rstrip('\n')

def prepare_machines(num_of_parties):
    conf = open("BaseConfig", "rb").read()
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.readfp(io.BytesIO(conf))

    if config.get("General", "remote") == "True":
        for i in xrange(1,int(num_of_parties+1)):
            ip = config.get(str(i), "ip")
            os.system('ssh -i key.pem {0} "cd MultiPartyPSI; git pull"'.format(ip))
            os.system('ssh -i key.pem {0} "rm MultiPartyPSI/MultiPartyPSI"'.format(ip))
            os.system('scp -i key.pem ./bin/MultiPartyPSI {0}:MultiPartyPSI/MultiPartyPSI'.format(ip))

def run_and_add_to_csv(results_file_path,num_of_parties,key_size,set_size,old_method,strategy,bandwidth=None,latency=None):
    start_time = time.time()
    result = runner.main(key_size=key_size,num_parties=num_of_parties,set_size=set_size,old_method=old_method,strategy=strategy)
    if len(result) != num_of_parties:
        return False
    result_str = '|'.join([str(item[1]) for item in sorted(result.items(),key= lambda x:x[0])])
    row = [REV,str(bandwidth),str(latency),str(start_time),str(key_size),str(num_of_parties),str(set_size),str(old_method),runner.getStrategyName(strategy),result_str]

    with open(results_file_path, 'ab') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=' ',
                               quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(row)
    return True

def prepare_results_file(config_file_path):
    if not os.path.isfile(config_file_path):
        with open(config_file_path, 'wb') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=' ',
                                   quotechar='|', quoting=csv.QUOTE_MINIMAL)
            csvwriter.writerow(['rev', 'bandwidth', 'latency', 'start_time', 'key_size', 'num_parties', 'set_size', 'old_method','strategy', 'result'])
    else:
        answer = raw_input("{0} exists. continuing means it would be appended. do you wish to continue ? (y/n)".format(config_file_path))
        if answer=='n':
            exit(0)

def avg_experiments(result_file_path, avg_result_file_path, num_of_parties):
    with open(avg_result_file_path, 'wb') as csvf:
        csvwriter = csv.writer(csvf, delimiter=' ',
                               quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(['rev', 'bandwidth', 'latency', 'start_time', 'key_size', 'num_parties', 'set_size', 'old_method','strategy', 'result'])
        with open(result_file_path, 'rb') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            csvreader.next() # remove title
            try:
                while True:
                    rows = [csvreader.next() for i in xrange(10)]
                    results = [(0,0)]*num_of_parties
                    for i in xrange(10):
                        assert rows[i][0] == rows[0][0] #rev
                        assert rows[i][1] == rows[0][1] #bandwidth
                        assert rows[i][2] == rows[0][2] #latency

                        assert rows[i][4] == rows[0][4] #key_size
                        assert rows[i][5] == rows[0][5] #num_parties
                        assert rows[i][6] == rows[0][6] #set_size
                        assert rows[i][7] == rows[0][7] #old_method
                        assert rows[i][8] == rows[0][8] #strategy
                        times_and_bytes = [eval(x) for x in rows[i][9].split('|')]
                        results = [(results[i][0]+times_and_bytes[i][0],results[i][1]+times_and_bytes[i][1]) for i in xrange(num_of_parties)]
                    results = map(lambda x: str((x[0]/10,x[1]/10)), results)
                    rows[0][9]='|'.join(results)
                    csvwriter.writerow(rows[0])
            except StopIteration:
                print "done !"