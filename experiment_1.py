#!/usr/bin/env python

import runner
import subprocess
import time
import csv
import os
import ConfigParser
import io
import experiment_utils

SET_SIZES = [2**10,2**12,2**14,2**16,2**18]
#KEY_SIZES = [80,128]
KEY_SIZES = [80, 128]
#STRATEGIES = [runner.Strategy.POLYNOMIALS, runner.Strategy.BLOOM_FILTER, runner.Strategy.POLYNOMIALS_SIMPLE_HASH, runner.Strategy.GAUSS_SIMPLE_HASH]
STRATEGIES = [runner.Strategy.SIMPLE_HASH, runner.Strategy.GAUSS_SIMPLE_HASH,
              runner.Strategy.BLOOM_FILTER, runner.Strategy.POLYNOMIALS,
              runner.Strategy.POLYNOMIALS_SIMPLE_HASH, runner.Strategy.TWO_PARTY]
NUM_THREADS = [1,2,3,4,None]

# and ofcourse kissner
NUM_OF_PARTIES = 5

experiment_utils.prepare_machines(NUM_OF_PARTIES)

experiment_utils.prepare_results_file('experiment1.csv')

for num_threads in NUM_THREADS:
    for set_size in SET_SIZES:
        for key_size in KEY_SIZES:
            for strategy in STRATEGIES:
                for i in xrange(10):
                    while not experiment_utils.run_and_add_to_csv('experiment1.csv',NUM_OF_PARTIES,key_size,set_size,False,strategy,num_threads=num_threads):
                        pass

experiment_utils.avg_experiments('experiment1.csv', 'experiment1_avg.csv')