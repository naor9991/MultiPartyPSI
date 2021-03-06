#!/usr/bin/env python

import csv
from collections import namedtuple
import sys
import math
import table_utils

place = {'SIMPLE_HASH' : 1, 'GAUSS_SIMPLE_HASH' : 2, 'BLOOM_FILTER' : 3, 'POLYNOMIALS' : 4, 'POLYNOMIALS_SIMPLE_HASH' : 5, 'TWO_PARTY' : 6}

KEY_SIZE = 80
dir_name = sys.argv[1]
NUM_OF_PARTIES = [2,3,5,6,7,9]

with open("{0}/experiment3_avg.csv".format(dir_name), 'rb') as csvfile:
    results = table_utils.readRows(csvfile)

    results = filter(lambda x: x.key_size==str(KEY_SIZE),results)

    res = {'SIMPLE_HASH' : {}, 'GAUSS_SIMPLE_HASH' : {}, 'BLOOM_FILTER' : {}, 'POLYNOMIALS' : {}, 'POLYNOMIALS_SIMPLE_HASH' : {}, 'TWO_PARTY' : {}}
    params = []

    for num_of_parties in NUM_OF_PARTIES:
        row = filter(lambda x: x.num_parties == str(num_of_parties),results)

        time_vals = dict(map(lambda x: (x.strategy, "%.2f" % eval(x.result1.split('|')[0])), row))

        byte_vals = dict(map(lambda x: (x.strategy, "%.2f"% (sum([eval(y.split('|')[1]) for y in
                                                                  [getattr(x, 'result{0}'.format(id)) for id in xrange(1, 10+1)] if y is not None])/1000000.0)),row))

        for strategy in res.keys():
            if time_vals.has_key(strategy):
                res[strategy][num_of_parties] = (time_vals[strategy],byte_vals[strategy])
            else:
                res[strategy][num_of_parties] = (' ',' ')
    
    with open("{0}/experiment3.txt".format(dir_name), 'wb') as f:

        f.write('\\begin{table*}[t]\n')
        f.write('\\hspace*{-2cm}\n')
        f.write('\\begin{tabular}{| l | l | l | l | l | l | l |}\n')
        f.write('\\hline\n')
        f.write('Number of parties & ' + ' & '.join(["{0}".format(num_of_parties) for num_of_parties in NUM_OF_PARTIES]) + " \\\\\n")
        
        f.write('\\hline\n')
        f.write('\\hline\n')
        
        for strategy in res.keys():
            f.write(" & ".join([strategy.replace('_',' ')]+[res[strategy][num_of_parties][0] for num_of_parties in NUM_OF_PARTIES]) + " \\\\\\hline\n")
        
        f.write('\\end{tabular}\n')
        f.write('\\caption{Runtimes in seconds for PSI protocols over 10GBit LAN, $\sigma=64$, $\symsec=80$, up to $4$ threads and set size $2^{16}$ with different number of parties}\n')
        f.write('\\label{tab:results3}\n')
        f.write('\\end{table*}\n')

        f.write('\n')

        f.write('\\begin{table*}[t]\n')
        f.write('\\hspace*{-2cm}\n')
        f.write('\\begin{tabular}{| l | l | l | l | l | l | l |}\n')
        f.write('\\hline\n')

        f.write('Num of parties & ' + ' & '.join(["{0}".format(num_of_parties) for num_of_parties in NUM_OF_PARTIES]) + " \\\\\n")

        f.write('\\hline\n')
        f.write('\\hline\n')

        for strategy in res.keys():
            f.write(" & ".join([strategy.replace('_',' ')]+[res[strategy][num_of_parties][1] for num_of_parties in NUM_OF_PARTIES]) + " \\\\\\hline\n")

        f.write('\\end{tabular}\n')
        f.write('\\caption{Communication complexity (in MB) for PSI protocols over 10Gbit LAN, $\sigma=64$, $\symsec=80$, up to $4$ threads and set size $2^{16}$ with different number of parties}\n')
        f.write('\\label{tab:results3_mb}\n')
        f.write('\\end{table*}\n')