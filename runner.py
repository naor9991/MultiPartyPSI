#!/usr/bin/env python

import ConfigParser
import io
import socket
from subprocess import Popen
import thread
import struct
import random
import os
import optparse

#docker images
#docker run -it scapicryptobiu/multipartypsi
# docker rmi -f scapicryptobiu/multipartypsi
# docker build --no-cache -t scapicryptobiu/multipartypsi:latest .

# dpkg-divert --local --rename --add /sbin/initctl
# ln -s /bin/true /sbin/initctl

# sudo service docker stop
# sudo pkill -f docker
# sudo service docker start

# ssh naor@cybhead1.lnx.biu.ac.il
# ssh cybnode11

# cp PSI/src/externals/Miracl/lib/linux64.bak PSI/src/externals/Miracl/lib/linux64
# cp PSI/src/externals/Miracl/include/mirdef.h64.bak PSI/src/externals/Miracl/include/mirdef.h64

MAX_INT = 2**32-1
MIN_INT = 0

LOOPBACK_ADDRESS = "127.0.0.1"
class Strategy:
    NAIVE_METHOD_SMALL_N = 0 # too slow
    NAIVE_METHOD_LARGE_N = 1 # too slow
    SIMPLE_HASH = 2
    POLYNOMIALS = 3
    BLOOM_FILTER = 4
    POLYNOMIALS_SIMPLE_HASH = 5
    GAUSS_SIMPLE_HASH = 6
    TWO_PARTY = 7

DEFAULT_STRATEGY = Strategy.POLYNOMIALS_SIMPLE_HASH

config = None

CLOCKS_PER_SEC = 1000000.0

def startPrograms(processes, numOfParties, program_type):
    if config.get("General", "debug") == "True":
        for i in xrange(2,numOfParties+1):
            processes.append(Popen(['bin/MultiPartyPSI', str(i),'Config',str(program_type)]))
    elif config.get("General", "profile") == "True":
        processes.append(Popen(['valgrind','--tool=callgrind','bin/MultiPartyPSI', str(1),'Config',str(program_type)]))
        for i in xrange(2,numOfParties+1):
            processes.append(Popen(['bin/MultiPartyPSI', str(i),'Config',str(program_type)]))
    else:
        for i in xrange(1,numOfParties+1):
            processes.append(Popen(['bin/MultiPartyPSI', str(i),'Config',str(program_type)]))

conf = open("BaseConfig", "rb").read()
config = ConfigParser.RawConfigParser(allow_no_value=True)
config.readfp(io.BytesIO(conf))

serverIp = config.get("server", "ip")
isLocalHost = (config.get("General", "remote") == "False")
if isLocalHost:
    serverIp = LOOPBACK_ADDRESS
serverPort = int(config.get("server", "port"))

MAX_ELEMENT_SIZE = int(config.get("General", "elementsizeinbits"))
MAX_ELEMENT = 2**MAX_ELEMENT_SIZE-1

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((serverIp, serverPort))

def runMPPSI(strategy):
    numOfParties = int(config.get("General", "numofparties"))
    leaderId = int(config.get("General", "leaderid"))
    setSize = int(config.get("General", "setsize"))
    seedSizeInBytes=int(config.get("General", "seedsizeinbytes"))

    s.listen(numOfParties)

    if config.get("General", "remote") == "True":
        for i in xrange(1,numOfParties+1):
            ip = config.get(str(i), "ip")

            #os.system('ssh -i key.pem {0} "cd MultiPartyPSI; git pull"'.format(ip))
            #os.system('scp -i key.pem ./bin/MultiPartyPSI {0}:MultiPartyPSI/MultiPartyPSI'.format(ip))
            os.system('scp -i key.pem ./Config {0}:MultiPartyPSI/Config'.format(ip))

    processes = []
    program_type = 1 if strategy is None else 0
    if config.get("General", "remote") == "False":
        thread.start_new_thread(startPrograms, (processes,numOfParties, program_type))
    else:
        '''
        for i in xrange(1,numOfParties+1):
            name = config.get(str(i), "name")

            port_list = ""
            basePort = int(config.get(str(i), "port"))
            for j in xrange(1,numOfParties+1):
                port_list = port_list + ' -p {0}:{0}'.format(basePort+j)
            command_line = 'docker run' + port_list + 'scapicryptobiu/multipartypsi ./bin/MultiPartyPSI ' + str(i) + ' Config ' + str(PROGRAM_TYPE)
            print command_line
            os.system('sshpass -p "305151094" ssh naor@{0} "{1} &"'.format(name, command_line))
        '''


        if config.get("General", "profile") == "True":
            for i in xrange(1,numOfParties+1):
                ip = config.get(str(i), "ip")
                processes.append(Popen(['ssh', '-i', 'key.pem', ip, 'valgrind','--tool=callgrind', './MultiPartyPSI/MultiPartyPSI', str(i), './MultiPartyPSI/Config', str(program_type)]))
        else:
            for i in xrange(1,numOfParties+1):
                ip = config.get(str(i), "ip")
                processes.append(Popen(['ssh', '-i', 'key.pem', ip, './MultiPartyPSI/MultiPartyPSI', str(i), './MultiPartyPSI/Config', str(program_type)]))


    parties = {}
    for _ in xrange(numOfParties):
        conn, addr = s.accept()
        partyId = struct.unpack("<I",conn.recv(4))[0]
        parties[partyId] = conn

    # make elements to each party and send to them
    intersectSize = random.randint(1,setSize)
    intersection = [random.randint(0, MAX_ELEMENT) for _ in xrange(intersectSize)]

    counter = intersectSize

    for i in xrange(numOfParties):
        els = intersection + [random.randint(0, MAX_ELEMENT) for _ in xrange(setSize-intersectSize)]

        counter = counter+setSize-intersectSize

        random.shuffle(els)

        # print "elements to party %d are %s" % (i, " ".join([str(el) for el in s]))

        buffer = ""
        for e in els:
            buffer = buffer + struct.pack("<Q",e) # this is hardcoded 64 bit

        parties[i+1].send(buffer)

    seed = os.urandom(seedSizeInBytes)
    for i in xrange(numOfParties):
        parties[i+1].send(seed)

    if strategy is not None:
        for i in xrange(numOfParties):
            parties[i+1].send(struct.pack("B",strategy))

    # synchronize
    for i in xrange(numOfParties):
        parties[i+1].recv(1)

    for i in xrange(numOfParties):
        parties[i+1].send("a")

    finalResults = {}

    for partyId in xrange(1,numOfParties+1):
        try:
            buffer = parties[partyId].recv(16)
            finalTimeInMilli,bytesSent,intersectionSize = struct.unpack("<dii", buffer)
            finalTime = finalTimeInMilli / 1000

            buffer = parties[partyId].recv(12)
            sendTimeInMilli,bytesSentOnSend = struct.unpack("<di", buffer)
            sendTime = sendTimeInMilli / 1000

            print "party %d with time %f seconds and %d bytes sent" % (partyId,finalTime, bytesSent)

            finalResults[partyId]=(finalTime, bytesSent, sendTime, bytesSentOnSend)
            if partyId == leaderId:
                if intersectionSize != intersectSize:
                    print "Error ! leader published false intersection size (real!=published):(%d!=%d)" % (intersectSize, intersectionSize)
        except:
            print "Error ! party %d doesn't sent back correct data" % partyId

    for process in processes:
        process.wait()
        if process.returncode != 0:
            print "Error ! return code is " + str(process.returncode)
    return finalResults

def getStrategyName(strategy):
    for attr in dir(Strategy):
        if attr is '__doc__' or attr is '__module__':
            continue
        if getattr(Strategy,attr) == strategy:
            return attr

def main(config_filepath = "Config",set_size = None,num_parties=None,key_size = None,old_method = False,strategy = None, num_threads = None):

    if num_parties is not None:
        config.set("General", "numofparties", num_parties)
    if set_size is not None:
        config.set("General", "setsize", set_size)
    if key_size is not None:
        config.set("General", "symsecurityparameter", key_size)
    if num_threads is not None:
        config.set("General", "numcores", num_threads)
    config.write(open(config_filepath, "wb"))

    if strategy is None:
        strategy = DEFAULT_STRATEGY

    def getProtocol():
        if old_method:
            return "Kisnner"
        else:
            return "Ours ({0})".format(getStrategyName(strategy))

    print "Run MPPSI of {0} with {1} parties with set size {2} and key security param {3}".format(getProtocol(), \
            config.get("General", "numofparties"), config.get("General", "setsize"), config.get("General", "symsecurityparameter"))

    if old_method:
        finalResults = runMPPSI(None)
    else:
        finalResults = runMPPSI(strategy)

    return finalResults

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('-c',
                      dest="config_filepath",
                      default="Config"
                      )
    parser.add_option('-m',
                      dest="set_size",
                      type="int",
                      )
    parser.add_option('-n',
                      dest="num_parties",
                      type="int",
                      )
    parser.add_option('-k',
                      dest="key_size",
                      type="int",
                      )
    parser.add_option('-o',
                      dest="old_method",
                      default=False,
                      action="store_true",
                      )
    parser.add_option('-s',
                      dest="strategy",
                      type="int",
                      )
    parser.add_option('-t',
                      dest="num_threads",
                      type="int",
                      )
    options, remainder = parser.parse_args()

    main(options.config_filepath,options.set_size,options.num_parties,options.key_size,options.old_method,options.strategy, options.num_threads)