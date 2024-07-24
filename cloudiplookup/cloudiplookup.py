#!/usr/bin/env python3
# encoding: utf-8
# -*- coding: utf-8 -*-
"""
Cloud IP Lookup v1.0.6 - Public cloud services IP addresses lookup tool

Author: Ricardo Abuchaim - ricardoabuchaim@gmail.com
        https://github.com/rabuchaim/cloudiplookup

License: MIT

""" 
__appid__   = "Cloud IP Lookup"
__version__ = "1.0.6"

import sys, os, json, socket, struct, gzip, pickle, re, ctypes
import urllib.request
from binascii import unhexlify
from time import perf_counter
from pprint import pprint as pp
from timeit import default_timer
from datetime import datetime as dt
from contextlib import contextmanager
from bisect import bisect as binary_search
from argparse import ArgumentParser, HelpFormatter, SUPPRESS
import cloudiplookup as _ 

DATA_DIR = os.path.dirname(_.__file__) if os.name == 'nt' else '/var/lib/cloudiplookup/'

PROVIDERS_INFORMATION_FILE_NAME = 'cloudiplookup.json'
OUTPUT_FILE_NAME                = 'cloudiplookup.dat.gz'
LIST_SLICE_SIZE                 = 1000
DOWNLOAD_TIMEOUT                = 30
middot                          = "\xb7"
singleLine                      = "─"
doubleLine                      = "═"
_DEBUG                          = False
os.environ["PYTHONWARNINGS"]    = "ignore"
os.environ["PYTHONIOENCODING"]  = "utf-8"

##──── FUNCTION TO HELP ME WITH DEBUG ────────────────────────────────────────────────────────────────────────────────────────────
def here(msg=""):print(f"HERE! {msg}",flush=True)

##################################################################################################################################

            ######## ##     ## ##    ##  ######  ######## ####  #######  ##    ##  ######
            ##       ##     ## ###   ## ##    ##    ##     ##  ##     ## ###   ## ##    ##
            ##       ##     ## ####  ## ##          ##     ##  ##     ## ####  ## ##
            ######   ##     ## ## ## ## ##          ##     ##  ##     ## ## ## ##  ######
            ##       ##     ## ##  #### ##          ##     ##  ##     ## ##  ####       ##
            ##       ##     ## ##   ### ##    ##    ##     ##  ##     ## ##   ### ##    ##
            ##        #######  ##    ##  ######     ##    ####  #######  ##    ##  ######

##################################################################################################################################

##──── IP MANIPULATION FUNCTIONS ─────────────────────────────────────────────────────────────────────────────────────────────────
ipv4_to_int = lambda ipv4_address: struct.unpack('!I', socket.inet_aton(ipv4_address))[0]
int_to_ipv4 = lambda num: socket.inet_ntoa(struct.pack('!I', num))
ipv6_to_int = lambda ipv6_address: int.from_bytes(socket.inet_pton(socket.AF_INET6, ipv6_address), byteorder='big')
int_to_ipv6 = lambda num: socket.inet_ntop(socket.AF_INET6, unhexlify(hex(num)[2:].zfill(32)))
##──── Number os possible IPs in a network range. (/0, /1 .. /8 .. /24 .. /30, /31, /32) ─────────────────────────────────────────
##──── Call the index of a list. Ex. numIPs[24] (is the number os IPs of a network range class C /24) ────────────────────────────
numIPsv4 = sorted([2**num for num in range(0,33)],reverse=True) # from 0 to 32
numIPsv6 = sorted([2**num for num in range(0,129)],reverse=True) # from 0 to 128
##──── numHosts is the numIPs - 2 ────────────────────────────────────────────────────────────────────────────────────────────────
numHostsv4 = sorted([(2**num)-2 for num in range(0,33)],reverse=True) # from 0 to 32
numHostsv6 = sorted([(2**num)-2 for num in range(0,129)],reverse=True) # from 0 to 128
##────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

##──── ANSI colors ───────────────────────────────────────────────────────────────────────────────────────────────────────────────
def cRed(msg): return '\033[91m'+msg+'\033[0m'
def cGrey(msg): return '\033[90m'+msg+'\033[0m'
def cBlue(msg): return '\033[94m'+msg+'\033[0m'
def cYellow(msg): return '\033[93m'+msg+'\033[0m'
def cWhite(msg): return '\033[97m'+str(msg)+'\033[0m'
def cDarkYellow(msg): return '\033[33m'+str(msg)+'\033[0m'

##──── Functions to print to stdout ─────────────────────────────────────────────────────────────────────────────────────────────────
def _logEmpty(msg,end=""):return
def log(msg,end="\n"):
    print(msg,end=end,flush=True)
def logVerbose(msg,end="\n"):
    print(msg,end=end,flush=True)
def logDebug(msg,end="\n"):return
def _logDebug(msg,end="\n"):
    print(cDarkYellow(get_date()+" [DEBUG] "+msg),end=end,flush=True)
def logError(msg,end="\n"):
    print(cRed("[ERROR] "+msg),end=end,flush=True)

##──── Return date with no spaces to use with filenames ──────────────────────────────────────────────────────────────────────────
def get_date(no_spaces=False):
    A='%Y%m%d%H%M%S' if no_spaces else '%Y%m%d@%H%M%S'
    B=dt.now()
    return B.strftime(A)

##──── ELAPSED TIMER FUNCTIONS ───────────────────────────────────────────────────────────────────────────────────────────────────
@contextmanager
def elapsed_timer():
    start = default_timer()
    elapsed = lambda: default_timer() - start
    yield lambda: elapsed()
    end = default_timer()
    elapsed = lambda: end-start

##──── FUNCTION TO HELP PRINT elapsed_timer() ────────────────────────────────────────────────────────────────────────────────────
def timer(elapsed_timer_name,decimal_places=9): 
    try:
        return f"[%.{decimal_places}f sec]"%elapsed_timer_name
    except:
        try:
            return f"[%.{decimal_places}f sec]"%elapsed_timer_name()
        except:
            return "[elapsed timer error]"

##──── DECORATOR TO EXEC SOMETHING BEFORE AND AFTER A METHOD CALL. FOR TESTING AND DEBUG PURPOSES ──────────────────────────────
def print_elapsed_time(method):
    def decorated_method(*args, **kwargs):
        startTime = perf_counter()
        result = method(*args, **kwargs)  
        logDebug(str(method)+" ("+str(*args)+") [%.9f sec]"%(perf_counter()-startTime))
        return result
    return decorated_method

##──── A pretty print for json ───────────────────────────────────────────────────────────────────────────────────────────────────
def pp_json(json_to_output,indent=3,sort_keys=False,print_result=True):
    try:
        dump = json.dumps(json_to_output,sort_keys=sort_keys,indent=indent,ensure_ascii=False,default=json_default_formatter)
        if print_result == True:
            print(dump)
        return dump
    except Exception as ERR:
        raise Exception("Failed pp_json() %a"%(str(ERR)))

##──── JSON default formatter for dates ──────────────────────────────────────────────────────────────────────────────────────────
def json_default_formatter(o):
    import datetime
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.__str__

##──── DOWNLOAD A FILE FROM INTERNET. IF IT´S A JSON, RETURNS JSON OTHERWISE RETURNS A LIST OF STRINGS ───────────────────────────
##──── A real browser User agent is needed to download Digital Ocean files because it does not accept empty/curl user agent ──────
def download_file(url, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36", max_redirects=5):
    global last_modified
    redirects = 0
    while redirects < max_redirects:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': user_agent} if user_agent else {})
            with urllib.request.urlopen(req,timeout=DOWNLOAD_TIMEOUT) as response:
                if response.getcode() == 302:
                    url = response.headers['Location']
                    redirects += 1
                    continue
                last_modified = response.headers['Last-Modified'] if 'Last-Modified' in response.headers else None
                if last_modified is None:
                    try:
                        last_modified = response.headers['date'] if 'date' in response.headers else None
                    except:
                        last_modified = dt.now()
                data = response.read().decode('utf-8')                
                try:
                    json_data = json.loads(data)
                    return json_data
                except json.JSONDecodeError:
                    return data.split("\n")
        except urllib.error.URLError as ERR:
            logVerbose(f"Unable to download file ({url}): {str(ERR)}")
            return False
    logVerbose(f"Exceeded maximum redirects. {url}")
    return False

##──── SPLIT A LIST IN CHUNKS OF "n" ───────────────────────────────────────────────────────────────────────────────────────────
def split_list(lista, n):
    for i in range(0, len(lista), n):
        yield lista[i:i + n]

##──── GET MEMORY USAGE ───────────────────────────────────────────────────────────────────────────────────────────────────────
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010

class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
    _fields_ = [("cb", ctypes.c_ulong),
                ("PageFaultCount", ctypes.c_ulong),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t)]

def get_mem_usage()->float:
    ''' Memory usage in MiB '''
    try:
        with open('/proc/self/status') as f:
            memory_usage = f.read().split('VmRSS:')[1].split('\n')[0][:-3]
        return float(memory_usage.strip()) / 1024
    except:
        try:
            pid = ctypes.windll.kernel32.GetCurrentProcessId()
            process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
            counters = PROCESS_MEMORY_COUNTERS()
            counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
            if ctypes.windll.psapi.GetProcessMemoryInfo(process_handle, ctypes.byref(counters), ctypes.sizeof(counters)):
                memory_usage = counters.WorkingSetSize
                return float((int(memory_usage) / 1024) / 1024)
        except:
            return 0.0

##################################################################################################################################

             ######  ##          ###     ######   ######  ########  ######
            ##    ## ##         ## ##   ##    ## ##    ## ##       ##    ##
            ##       ##        ##   ##  ##       ##       ##       ##
            ##       ##       ##     ##  ######   ######  ######    ######
            ##       ##       #########       ##       ## ##             ##
            ##    ## ##       ##     ## ##    ## ##    ## ##       ##    ##
             ######  ######## ##     ##  ######   ######  ########  ######

##################################################################################################################################
##──── CLASS FOR DETAILS OF LOOKUP ───────────────────────────────────────────────────────────────────────────────────────────────        
class CloudIPDetail(object):
    """Object to store the information obtained by searching an IP address
    """    
    def __init__(self, ip, cidr="", region="", cloud_provider="", service="", elapsed_time=""):
        self.ip = ip
        self.cidr = cidr
        self.region = region
        self.cloud_provider = cloud_provider
        self.service = service
        self.elapsed_time = elapsed_time
    def __str__(self):
        return f"{self.__dict__}"
    def __repr__(self):
        return f"{self.to_dict()}"    
    def to_dict(self):
        """To use the result as a dict

        Returns:
            dict: a dictionary with result's properties 
        """
        try:
            d = {
                "ip": self.ip,
                "cidr": self.cidr,
                "region": self.region,
                "cloud_provider": self.cloud_provider,
                "service": self.service,
                "elapsed_time": self.elapsed_time,
                }
            return d
        except Exception as ERR:
            raise Exception("Failed to_dict() %a"%(str(ERR)))
    def pp_json(self,indent=3,sort_keys=False,print_result=False):
        """ A pretty print for json

        If *indent* is a non-negative integer, then JSON array elements and object members will be pretty-printed with that indent level. An indent level of 0 will only insert newlines. None is the most compact representation.

        If *sort_keys* is true (default: False), then the output of dictionaries will be sorted by key.

        If *print_result* is True (default: False), then the output of dictionaries will be printed to stdout, otherwise a one-line string will be silently returned.

        Returns:
            string: returns a string to print.            
        """
        try:
            dump = json.dumps(self.to_dict(),sort_keys=sort_keys,indent=indent,ensure_ascii=False,default=json_default_formatter)
            if print_result == True:
                print(dump,flush=True)
            return dump
        except Exception as ERR:
            raise Exception("Failed pp_json() %a"%(str(ERR)))
    def pp_csv(self):
        """ Print output in CSV format
        """
        try:
            return f"{self.to_dict()['ip']},{self.to_dict()['cidr']},{self.to_dict()['region']},{self.to_dict()['cloud_provider']},{self.to_dict()['service']},{self.to_dict()['elapsed_time'].split(' ')[0]}"
        except Exception as ERR:
            raise Exception("Failed pp_csv() %a"%(str(ERR)))
            
        
class CloudIPLookup(object):
    """Locate if IP Address belongs to a pulic cloud service
    """
    def __init__(self, verbose=False):
        global startMem  # declared as global to be used at function _load_data()
        startMem = get_mem_usage()
        self.verbose = verbose
        self._load_data_text = "" 
        ##──── Swap functions code at __init__ to avoid "if verbose=True" and save time ──────────────────────────────────────────────────
        if verbose == False:
            self._print_verbose = self.__print_verbose_empty
        ##────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────        
        self.is_loaded = False
        self._load_data(self.verbose)
    ##──── Function used to avoid "if verbose == True". The code is swaped at __init__ ───────────────────────────────────────────────────
    def __print_verbose_empty(self,msg):return
    def _print_verbose(self,msg):
        print(msg,flush=True)
    ##────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    def _load_data(self, verbose=False)->bool:        
        global indexMain, indexProvider, indexServices, indexRegions, indexNetworkFeatures, \
                listFirstIP, listNetLength, listProvider, listServices, listRegions, listFeatures, databaseInfo
        if self.is_loaded == True:
            return True   
        startLoadData = perf_counter()
        ##──── Open the dat.gz file ──────────────────────────────────────────────────────────────────────────────────────────────────────
        try:
            f = gzip.open(os.path.join(DATA_DIR,OUTPUT_FILE_NAME),'rb')
        except Exception as ERR:
            raise Exception(f"Failed to 'load' CloudIPLookup dat file! the data file {str(os.path.join(DATA_DIR,OUTPUT_FILE_NAME))} appears to be invalid or does not exist! Run an update (--update) or call the function update_ip_ranges() to create this file.\n\n{str(ERR)}\n")
        try:
            indexMain, indexProvider, indexServices, indexRegions, indexNetworkFeatures, \
                listFirstIP, listNetLength, listProvider, listServices, listRegions, listFeatures, databaseInfo = pickle.load(f)
        except Exception as ERR:
            raise Exception(f"Failed to pickle the data file {str(os.path.join(DATA_DIR,OUTPUT_FILE_NAME))} {str(ERR)}\n")
        ##──── Warming-up ────────────────────────────────────────────────────────────────────────────────────────────────────────────────
        try:
            [self.lookup(iplong) for iplong in [4294967295]]
        except Exception as ERR:
            raise Exception("Failed at warming-up... exiting... %s"%(str(ERR)))
        ##────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
        ##──── Load Time Info ────────────────────────────────────────────────────────────────────────────────────────────────────────────
        try:
            totalLoadTime = (perf_counter() - startLoadData)
            totalMemUsage = (get_mem_usage() - startMem)
            self._load_data_text = f"Cloud IP Lookup v{__version__} is ready! "+ \
                "loaded with %s networks in %.5f seconds and using %.2f MiB of RAM."%(str(self._total_networks()),totalLoadTime,totalMemUsage)
            self._print_verbose(self._load_data_text)
        except Exception as ERR:
            raise Exception("Failed at the end of load data %s"%(str(ERR)))
        ##────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
        self.is_loaded = True
        return True
    @property
    def startup_line_text(self):
        """
        Returns the text of _load_data() in case you want to know without set verbose=True 
        
        Like: Cloud IP Lookup v1.x.x is ready! cloudiplookup.dat.gz loaded with 40217 networks in 0.00564 seconds and using 3.57 MiB.
        """    
        return self._load_data_text
    def _total_networks(self):
        """
        Returns the number of all networks included in cloudiplookup.dat.gz file
        """
        total = 0
        for a_list in listFirstIP:
            total += len(a_list)
        return total        
    def get_database_info(self,print_result=True):
        """Returns or print the current database info"""
        if print_result == True:
            pp_json(databaseInfo)
        else:
            return databaseInfo
    def update_database(self,verbose=True):
        """Update current database"""
        if (verbose == False):
            logVerbose = _logEmpty
        update_ip_ranges(verbose)
        
    def lookup(self,ipaddr:str)->CloudIPDetail:
        """
        Performs a search for the given IP address in the in-memory database

        - Usage:

            from cloudiplookip import CloudIPLookup
    
            myLookup = CloudIPLookup()
            
            result = myLookup.lookup("8.8.8.8")
            
            print(result)
        """                    
        startTime = perf_counter()
        try:
            try:
                iplong = ipv4_to_int(ipaddr)
            except:
                iplong = ipv6_to_int(ipaddr)
        except:
            return CloudIPDetail(ip=ipaddr,cloud_provider="<invalid ip address>",elapsed_time='%.9f sec'%(perf_counter()-startTime))
        try:
            matchRoot = binary_search(indexMain,iplong)-1
            if matchRoot < 0:
                return CloudIPDetail(ip=ipaddr,cloud_provider="<not found in database>",elapsed_time='%.9f sec'%(perf_counter()-startTime))
            matchChunk = binary_search(listFirstIP[matchRoot],iplong)-1
            try:
                cidr = int_to_ipv4(listFirstIP[matchRoot][matchChunk])+"/"+str(listNetLength[matchRoot][matchChunk])
                last_ip = listFirstIP[matchRoot][matchChunk] + numHostsv4[listNetLength[matchRoot][matchChunk]] - 1
            except:
                cidr = int_to_ipv6(int(listFirstIP[matchRoot][matchChunk]))+"/"+str(listNetLength[matchRoot][matchChunk])
                last_ip = listFirstIP[matchRoot][matchChunk] + numHostsv6[listNetLength[matchRoot][matchChunk]] - 1
            if iplong > last_ip:
                return CloudIPDetail(ip=ipaddr,cloud_provider="<not found in database>",elapsed_time='%.9f sec'%(perf_counter()-startTime))
            region = indexRegions[listRegions[matchRoot][matchChunk]-1]
            service = indexServices[listServices[matchRoot][matchChunk]-1]
            cloud_provider = indexProvider[listProvider[matchRoot][matchChunk]-1]
            ##──── SUCCESS! ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
            return CloudIPDetail(ipaddr,cidr,region,cloud_provider,service,elapsed_time='%.9f sec'%((perf_counter()-startTime)))
            ##────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
        except Exception as ERR:
            return CloudIPDetail(ip=ipaddr,region=str(ERR),cloud_provider="<internal lookup error>",elapsed_time='%.9f sec'%(perf_counter()-startTime))
             
##──── CLASS FOR ARGUMENT PARSER ──────────────────────────────────────────────────────────────────────────────────────────────────────
class class_argparse_formatter(HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = 'Usage: '
        return super(class_argparse_formatter, self).add_usage(usage, actions, groups, prefix)
    def _format_usage(self, usage, actions, groups, prefix):
        return super(class_argparse_formatter, self)._format_usage(usage, actions, groups, prefix)

##################################################################################################################################

                # # ##  ##   #  ### ###     ### ##      ##   #  ###  ## ###  ##
                # # # # # # # #  #  #        #  # #     # # # # # # #   #   #
                # # ##  # # ###  #  ##       #  ##      ##  ### # # # # ##   #
                # # #   # # # #  #  #        #  #       # # # # # # # # #     #
                ### #   ##  # #  #  ###     ### #       # # # # # #  ## ### ##

##################################################################################################################################
#defupdate
@print_elapsed_time
def update_ip_ranges(verbose=False,debug=False):
    global cloudip, databaseInfo, _DEBUG
    cloudip, databaseInfo = {}, {}
    _DEBUG = debug
    logDebug.__code__ = _logDebug.__code__ if (verbose == True and debug == True) else _logEmpty.__code__
    logVerbose.__code__ = _logEmpty.__code__ if (verbose == False) else log.__code__    
    ##──── LOAD CLOUD SERVICE PROVIDERS INFORMATION FILE ─────────────────────────────────────────────────────────────────────────────
    try:
        with open(os.path.join(DATA_DIR,PROVIDERS_INFORMATION_FILE_NAME),"r") as f:
            infoFile = json.load(f)        
    except Exception as ERR:
        logError(f"Failed to open information file \"{str(os.path.join(DATA_DIR,PROVIDERS_INFORMATION_FILE_NAME))}\": {str(ERR)}")
        return 1
    try:
        with elapsed_timer() as elapsed:
            ##──── Each cloud provider has its own file format, so it´s necessary a specific for each one ────────────────────────────────────
            update_ip_ranges_aws(infoFile['AWS']['download_url'])
            update_ip_ranges_azure(infoFile['AZURE']['info_page']) # azure is different
            update_ip_ranges_cloudflare(infoFile['CLOUDFLARE']['download_url']) 
            update_ip_ranges_digital_ocean(infoFile['DIGITALOCEAN']['download_url'])
            update_ip_ranges_google_cloud(infoFile['GOOGLECLOUD']['download_url'])
            update_ip_ranges_google_services(infoFile['GOOGLESERVICES']['download_url'])
            update_ip_ranges_google_services(infoFile['GOOGLEBOT']['download_url'])
            update_ip_ranges_google_services(infoFile['GOOGLESSPECIALCRAWLERS']['download_url'])
            update_ip_ranges_google_services(infoFile['GOOGLESUSERTRIGGERED']['download_url'])
            update_ip_ranges_jdcloud(infoFile['JDCLOUD']['download_url']) # cloudflare jdcloud china
            update_ip_ranges_oracle_cloud(infoFile['ORACLE']['download_url'])
    except Exception as ERR:
        logDebug(f"Failed to update IP ranges - {str(ERR)}")
        return 1
    with elapsed_timer() as elapsed_sort:
        cloudip = dict(sorted(cloudip.items(),key=lambda x:int(x[0]), reverse=False))
    logVerbose(f"Sorting IPv4 and IPv6 data {timer(elapsed_sort())}")
    with elapsed_timer() as elapsed_lists:
        listFirstIP = [int(key) for key,val in cloudip.items()]
        listNetLength = [int(val['netlength']) for key,val in cloudip.items()]
        dictProvider, dictServices, dictRegions, dictFeatures = {}, {}, {}, {}
        listProvider, listServices, listRegions, listFeatures = [], [], [], []
        nextKeyProvider, nextKeyServices, nextKeyRegions, nextKeyFeatures = 0, 0, 0, 0
        for key,val in cloudip.items():
            if dictProvider.get(val['provider'],0) == 0:
                nextKeyProvider += 1
                dictProvider[val['provider']] = nextKeyProvider
            if dictServices.get(val['service'],0) == 0:
                nextKeyServices += 1
                dictServices[val['service']] = nextKeyServices
            if dictRegions.get(val['region'],0) == 0:
                nextKeyRegions += 1
                dictRegions[val['region']] = nextKeyRegions
            if dictFeatures.get(val['network_features'],0) == 0:
                nextKeyFeatures += 1
                dictFeatures[val['network_features']] = nextKeyFeatures
            listProvider.append(dictProvider[val['provider']])
            listServices.append(dictServices[val['service']])
            listRegions.append(dictRegions[val['region']])
            listFeatures.append(dictFeatures[val['network_features']])
        indexProvider = list(dictProvider.keys())
        indexServices = list(dictServices.keys())
        indexRegions = list(dictRegions.keys())
        indexNetworkFeatures = list(dictFeatures.keys())
        listFirstIP = list(split_list(listFirstIP,LIST_SLICE_SIZE))
        listNetLength = list(split_list(listNetLength,LIST_SLICE_SIZE))
        listProvider = list(split_list(listProvider,LIST_SLICE_SIZE))
        listServices = list(split_list(listServices,LIST_SLICE_SIZE))
        listRegions = list(split_list(listRegions,LIST_SLICE_SIZE))
        listFeatures = list(split_list(listFeatures,LIST_SLICE_SIZE))
        indexMain = [item[0] for item in listFirstIP]
        database = [indexMain, indexProvider, indexServices, indexRegions, indexNetworkFeatures, 
                    listFirstIP, listNetLength, listProvider, listServices, listRegions, listFeatures,
                    databaseInfo]
    logVerbose(f"Updating all lists... Done! {timer(elapsed_lists())}")
    if _DEBUG == True:
        with elapsed_timer() as elapsed_savefiles:
            with open(os.path.join(DATA_DIR,"cloudip.json"),"w") as f:
                json.dump(cloudip,f,indent=3,sort_keys=False,ensure_ascii=False,default=json_default_formatter)
            logDebug(f"Saving cloudip.json file {timer(elapsed_savefiles())}")
            with open(os.path.join(DATA_DIR,"cloudiplookup.dat.json"),"w") as f:
                json.dump(database,f,indent=3,sort_keys=False,ensure_ascii=False,default=json_default_formatter)
            logDebug(f"Saving cloudiplookup.dat.json file {timer(elapsed_savefiles())}")
    with elapsed_timer() as elapsed_save_gzip:
        with gzip.GzipFile(filename=os.path.join(DATA_DIR,OUTPUT_FILE_NAME), mode='wb', compresslevel=9) as f:
            pickle.dump(database,f,pickle.HIGHEST_PROTOCOL)
        f.close()
        logVerbose(f"Saved file {os.path.join(DATA_DIR,OUTPUT_FILE_NAME)} {timer(elapsed_save_gzip())}")
    logVerbose(f"Cloud IP Lookup updated with success! {timer(elapsed())}")
    ##──── EXIT WITH SUCCESS ─────────────────────────────────────────────────────────────────────────────────────────────────────────
    return 0

##──── UPDATE AWS IP RANGES ──────────────────────────────────────────────────────────────────────────────────────────────────────
@print_elapsed_time
def update_ip_ranges_aws(download_url):
    global cloudip, databaseInfo, _DEBUG
    initialLen = len(cloudip.keys())
    try:
        with elapsed_timer() as elapsed:
            ipranges = download_file(download_url)
            if ipranges == False:
                logError(f"Updating AWS - FAILED to download IP ranges file from {download_url} {timer(elapsed())}")
                return False
            logVerbose(f"Updating AWS - Downloading IP ranges file {timer(elapsed())}")
            if _DEBUG == True:
                outputFile = os.path.join(DATA_DIR,'ipranges-aws.json')
                logDebug(f"Saving ipranges to {outputFile}")
                with open(outputFile,'w') as f:
                    json.dump(ipranges,f,indent=3,sort_keys=False,ensure_ascii=False,default=json_default_formatter)
        with elapsed_timer() as elapsed:
            total_ipv4 = total_ipv6 = 0
            for item in ipranges['prefixes']:
                cidr, region, service, network_border_group = item.values()
                first_ip, netlen = cidr.split("/")
                total_ipv4 += numIPsv4[int(netlen)]
                first_ip2int = ipv4_to_int(first_ip)
                region = network_border_group if region != network_border_group else region
                cloudip[first_ip2int] = {'provider':'AWS','cidr':cidr,'region':region, 'service':service, 'netlength':int(netlen),'network_features':''}
            for item in ipranges['ipv6_prefixes']:
                cidr, region, service, network_border_group = item.values()
                first_ip, netlen = cidr.split("/")
                total_ipv6 += numIPsv6[int(netlen)]
                first_ip2int = ipv6_to_int(first_ip)
                region = network_border_group if region != network_border_group else region
                cloudip[first_ip2int] = {'provider':'AWS','cidr':cidr,'region':region, 'service':service, 'netlength':int(netlen),'network_features':''}
            try:
                formatedDate = dt.strptime(ipranges['createDate'], "%Y-%m-%d-%H-%M-%S")
                formatedDate = formatedDate.strftime("%Y-%m-%d %H:%M:%S")
            except:
                formatedDate = ipranges['createDate']
            logVerbose(f"Updating AWS - Parsing IPv4 and IPv6 ranges updated at {formatedDate} {timer(elapsed())}")
        databaseInfo["AWS"] = {'last_updated':formatedDate,
                               'total_networks':len(cloudip.keys())-initialLen,
                               'total_ipv4':total_ipv4, 'total_ipv6':total_ipv6}
    except Exception as ERR:
        logVerbose(f"Failed to update AWS IP ranges - {str(ERR)}")
    return
    
##──── UPDATE AZURE IP RANGES ──────────────────────────────────────────────────────────────────────────────────────────────────────
@print_elapsed_time
def update_ip_ranges_azure(info_page):
    global cloudip, databaseInfo, _DEBUG
    initialLen = len(cloudip.keys())
    try:
        with elapsed_timer() as elapsed:
            ##──── Azure changes the name og the file on each version, so is necessary to locate it ──────────────────────────────────────────
            rule = re.compile(r'.*(https://download.microsoft.com.*ServiceTags_Public.*.json)".*')
            ipranges = download_file(info_page)
            url = next((linha for linha in ipranges if (re.match(rule,linha))),False)
            download_url = re.match(rule,url).group(1)
            ipranges = download_file(download_url)
            if ipranges == False:
                logError(f"Updating AZURE - FAILED to download IP ranges file from {download_url} {timer(elapsed())}")
                return False
            logVerbose(f"Updating AZURE - Downloading IP ranges file {timer(elapsed())}")
            if _DEBUG == True:
                outputFile = os.path.join(DATA_DIR,'ipranges-azure.json')
                logDebug(f"Saving ipranges to {outputFile}")
                with open(outputFile,'w') as f:
                    json.dump(ipranges,f,indent=3,sort_keys=False,ensure_ascii=False,default=json_default_formatter)
        with elapsed_timer() as elapsed:
            total_ipv4 = total_ipv6 = 0
            values = ipranges['values']
            for bloco in values:
                service = bloco['properties']['systemService']
                try:
                    networkFeatures = ", ".join(bloco['properties']['networkFeatures'])
                except:
                    networkFeatures = ""
                region = bloco['properties']['region']
                region_id = bloco['properties']['regionId']
                for cidr in bloco['properties']['addressPrefixes']:
                    first_ip, netlen = str(cidr).split("/")
                    if first_ip.find(":") < 0:
                        total_ipv4 += numIPsv4[int(netlen)]
                        first_ip2int = ipv4_to_int(first_ip)
                    else:
                        total_ipv6 += numIPsv6[int(netlen)]
                        first_ip2int = ipv6_to_int(first_ip)
                    cloudip[first_ip2int] = {'provider':'Azure','cidr':str(cidr),'region':region, 'service':service, 'netlength':int(netlen),'network_features':networkFeatures}
        try:
            formatedDate = dt.strptime(last_modified, "%a, %d %b %Y %H:%M:%S %Z")
            formatedDate = formatedDate.strftime("%Y-%m-%d %H:%M:%S")
        except:
            formatedDate = last_modified
        logVerbose(f"Updating AZURE - Parsing IPv4 and IPv6 ranges updated at {formatedDate} {timer(elapsed())}")
        databaseInfo["Azure"] = {'last_updated':formatedDate,
                                 'total_networks':len(cloudip.keys())-initialLen,
                                 'total_ipv4':total_ipv4, 'total_ipv6':total_ipv6}
    except Exception as ERR:
        logVerbose(f"Failed to update AZURE IP ranges {bloco['properties']['networkFeatures']} - {str(ERR)}")
    return

##──── UPDATE GOOGLE CLOUD PLATFORM IP RANGES ──────────────────────────────────────────────────────────────────────────────────────────────────────
@print_elapsed_time
def update_ip_ranges_google_cloud(download_url):
    global cloudip, databaseInfo, _DEBUG
    initialLen = len(cloudip.keys())
    try:
        with elapsed_timer() as elapsed:
            ipranges = download_file(download_url)
            if ipranges == False:
                logError(f"Updating GOOGLE CLOUD - FAILED to download IP ranges file from {download_url} {timer(elapsed())}")
                return False
            logVerbose(f"Updating GOOGLE CLOUD - Downloading IP ranges file {timer(elapsed())}")
            if _DEBUG == True:
                outputFile = os.path.join(DATA_DIR,'ipranges-googlecloud.json')
                logDebug(f"Saving ipranges to {outputFile}")
                with open(outputFile,'w') as f:
                    json.dump(ipranges,f,indent=3,sort_keys=False,ensure_ascii=False,default=json_default_formatter)
        with elapsed_timer() as elapsed:
            total_ipv4 = total_ipv6 = 0
            for item in ipranges['prefixes']:
                service = item['service']
                region = item['scope']
                if item.get('ipv4Prefix',0) != 0:
                    cidr = item['ipv4Prefix']
                    first_ip, netlen = str(cidr).split("/")
                    total_ipv4 += numIPsv4[int(netlen)]
                    first_ip2int = ipv4_to_int(first_ip)
                else:
                    cidr = item['ipv6Prefix']
                    first_ip, netlen = str(cidr).split("/")
                    total_ipv6 += numIPsv6[int(netlen)]
                    first_ip2int = ipv6_to_int(first_ip)
                cloudip[first_ip2int] = {'provider':'Google Cloud Platform','cidr':cidr,'region':region,'service':service,'netlength':int(netlen),'network_features':''}
        try:
            formatedDate = dt.strptime(ipranges['creationTime'], "%Y-%m-%dT%H:%M:%S.%f")
            formatedDate = formatedDate.strftime("%Y-%m-%d %H:%M:%S")
        except:
            formatedDate = ipranges['creationTime']
        logVerbose(f"Updating GOOGLE CLOUD - Parsing IPv4 and IPv6 ranges updated at {formatedDate} {timer(elapsed())}")
        databaseInfo["Google Cloud"] = {'last_updated':formatedDate,
                                        'total_networks':len(cloudip.keys())-initialLen,
                                        'total_ipv4':total_ipv4, 'total_ipv6':total_ipv6}
    except Exception as ERR:
        logVerbose(f"Failed to update GOOGLE CLOUD PLATFORM IP ranges - {str(ERR)}")
        return 1

##──── UPDATE GOOGLE CLOUD SERVICES IP RANGES ──────────────────────────────────────────────────────────────────────────────────────────────────────
@print_elapsed_time
def update_ip_ranges_google_services(download_url):
    global cloudip, databaseInfo, _DEBUG
    initialLen = len(cloudip.keys())
    try:
        service = 'Google Bot' \
                if download_url.find("googlebot") >= 0 else 'Google Special Crawlers' \
                if download_url.find("special-crawlers") >= 0 else 'Google User Triggered Fetchers' \
                if download_url.find("user-triggered") >= 0 else 'Google Services'
        with elapsed_timer() as elapsed:
            ipranges = download_file(download_url)
            if ipranges == False:
                logError(f"Updating GOOGLE {service.upper().replace('GOOGLE ','')} - FAILED to download IP ranges file from {download_url} {timer(elapsed())}")
                return False
            logVerbose(f"Updating GOOGLE {service.upper().replace('GOOGLE ','')} - Downloading IP ranges file {timer(elapsed())}")
            if _DEBUG == True:
                filename = download_url.split("/")[-1]
                outputFile = os.path.join(DATA_DIR,f'ipranges-{filename}.json')
                logDebug(f"Saving ipranges to {outputFile}")
                with open(outputFile,'w') as f:
                    json.dump(ipranges,f,indent=3,sort_keys=False,ensure_ascii=False,default=json_default_formatter)
        with elapsed_timer() as elapsed:
            total_ipv4 = total_ipv6 = 0
            for item in ipranges['prefixes']:
                if item.get('ipv4Prefix',0) != 0:
                    cidr = item['ipv4Prefix']
                    first_ip, netlen = str(cidr).split("/")
                    total_ipv4 += numIPsv4[int(netlen)]
                    first_ip2int = ipv4_to_int(first_ip)
                else:
                    cidr = item['ipv6Prefix']
                    first_ip, netlen = str(cidr).split("/")
                    total_ipv6 += numIPsv6[int(netlen)]
                    first_ip2int = ipv6_to_int(first_ip)
                cloudip[first_ip2int] = {'provider':"Google",'cidr':cidr,'region':'','service':service.replace("Google ",""),'netlength':int(netlen),'network_features':''}
        try:
            formatedDate = dt.strptime(ipranges['creationTime'], "%Y-%m-%dT%H:%M:%S.%f")
            formatedDate = formatedDate.strftime("%Y-%m-%d %H:%M:%S")
        except:
            formatedDate = ipranges['creationTime']
        logVerbose(f"Updating GOOGLE {service.upper().replace('GOOGLE ','')} - Parsing IPv4 and IPv6 ranges updated at {formatedDate} {timer(elapsed())}")
        databaseInfo[service] = {'last_updated':formatedDate,
                                 'total_networks':len(cloudip.keys())-initialLen,
                                 'total_ipv4':total_ipv4, 'total_ipv6':total_ipv6}
    except Exception as ERR:
        logVerbose(f"Failed to update GOOGLE {service.upper().replace('GOOGLE ','')} IP ranges - {str(ERR)}")
        return 1

##──── UPDATE CLOUDFLARE IP RANGES ──────────────────────────────────────────────────────────────────────────────────────────────────────
@print_elapsed_time
def update_ip_ranges_cloudflare(download_url):
    global cloudip, databaseInfo, _DEBUG
    initialLen = len(cloudip.keys())
    try:
        with elapsed_timer() as elapsed:
            ipranges = download_file(download_url)
            if ipranges == False:
                logError(f"Updating CLOUDFLARE - FAILED to download IP ranges file from {download_url} {timer(elapsed())}")
                return False
            logVerbose(f"Updating CLOUDFLARE - Downloading IP ranges file {timer(elapsed())}")
            if _DEBUG == True:
                outputFile = os.path.join(DATA_DIR,'ipranges-cloudflare.json')
                logDebug(f"Saving ipranges to {outputFile}")
                with open(outputFile,'w') as f:
                    json.dump(ipranges,f,indent=3,sort_keys=False,ensure_ascii=False,default=json_default_formatter)
        with elapsed_timer() as elapsed:
            total_ipv4 = total_ipv6 = 0
            for item in ipranges['result']['ipv4_cidrs']:
                cidr = item
                first_ip, netlen = str(cidr).split("/")
                total_ipv4 += numIPsv4[int(netlen)]
                first_ip2int = ipv4_to_int(first_ip)
                cloudip[first_ip2int] = {'provider':'Cloudflare','cidr':cidr,'region':'','service':'','netlength':int(netlen),'network_features':''}
            for item in ipranges['result']['ipv6_cidrs']:
                cidr = item
                first_ip, netlen = str(cidr).split("/")
                total_ipv6 += numIPsv6[int(netlen)]
                first_ip2int = ipv6_to_int(first_ip)
                cloudip[first_ip2int] = {'provider':'Cloudflare','cidr':cidr,'region':'','service':'','netlength':int(netlen),'network_features':''}
        # Cloudflare has an API, so the date in header is always the current date time.
        try:
            formatedDate = dt.strptime(last_modified, "%a, %d %b %Y %H:%M:%S %Z")
            formatedDate = formatedDate.strftime("%Y-%m-%d %H:%M:%S")
        except:
            formatedDate = last_modified
        logVerbose(f"Updating CLOUDFLARE - Parsing IPv4 and IPv6 ranges updated at {formatedDate} {timer(elapsed())}")
        databaseInfo["Cloudflare"] = {'last_updated':formatedDate,
                                      'total_networks':len(cloudip.keys())-initialLen,
                                      'total_ipv4':total_ipv4, 'total_ipv6':total_ipv6}
    except Exception as ERR:
        logVerbose(f"Failed to update CLOUDFLARE IP ranges - {str(ERR)}")
        return 1

##──── UPDATE CLOUDFLARE IP RANGES ──────────────────────────────────────────────────────────────────────────────────────────────────────
@print_elapsed_time
def update_ip_ranges_jdcloud(download_url):
    global cloudip, databaseInfo, _DEBUG
    initialLen = len(cloudip.keys())
    try:
        with elapsed_timer() as elapsed:
            ipranges = download_file(download_url)
            if ipranges == False:
                logError(f"Updating JD CLOUD - FAILED to download IP ranges file from {download_url} {timer(elapsed())}")
                return False
            logVerbose(f"Updating JD CLOUD - Downloading IP ranges file {timer(elapsed())}")
            if _DEBUG == True:
                outputFile = os.path.join(DATA_DIR,'ipranges-jdcloud.json')
                logDebug(f"Saving ipranges to {outputFile}")
                with open(outputFile,'w') as f:
                    json.dump(ipranges,f,indent=3,sort_keys=False,ensure_ascii=False,default=json_default_formatter)
        with elapsed_timer() as elapsed:
            total_ipv4 = total_ipv6 = 0
            for item in ipranges['result']['jdcloud_cidrs']:
                cidr = item
                first_ip, netlen = str(cidr).split("/")
                try:
                    first_ip2int = ipv4_to_int(first_ip)
                    total_ipv4 += numIPsv4[int(netlen)]
                except:
                    first_ip2int = ipv6_to_int(first_ip)
                    total_ipv6 += numIPsv6[int(netlen)]
                cloudip[first_ip2int] = {'provider':'JD Cloud','cidr':cidr,'region':'China','service':'','netlength':int(netlen),'network_features':''}
        # Cloudflare JD Cloud China has an API, so the date in header is always the current date time.
        try:
            formatedDate = dt.strptime(last_modified, "%a, %d %b %Y %H:%M:%S %Z")
            formatedDate = formatedDate.strftime("%Y-%m-%d %H:%M:%S")
        except:
            formatedDate = last_modified
        logVerbose(f"Updating JD CLOUD - Parsing IPv4 and IPv6 ranges updated at {formatedDate} {timer(elapsed())}")
        databaseInfo["JD Cloud"] = {'last_updated':formatedDate,
                                    'total_networks':len(cloudip.keys())-initialLen,
                                    'total_ipv4':total_ipv4, 'total_ipv6':total_ipv6}
    except Exception as ERR:
        logVerbose(f"Failed to update JD CLOUD IP ranges - {str(ERR)}")
        return 1


##──── UPDATE ORACLE CLOUD IP RANGES ──────────────────────────────────────────────────────────────────────────────────────────────────────
@print_elapsed_time
def update_ip_ranges_oracle_cloud(download_url):
    global cloudip, databaseInfo, _DEBUG
    initialLen = len(cloudip.keys())
    try:
        with elapsed_timer() as elapsed:
            ipranges = download_file(download_url)
            if ipranges == False:
                logError(f"Updating ORACLE - FAILED to download IP ranges file from {download_url} {timer(elapsed())}")
                return False
            logVerbose(f"Updating ORACLE - Downloading IP ranges file {timer(elapsed())}")
            if _DEBUG == True:
                outputFile = os.path.join(DATA_DIR,'ipranges-oracle.json')
                logDebug(f"Saving ipranges to {outputFile}")
                with open(outputFile,'w') as f:
                    json.dump(ipranges,f,indent=3,sort_keys=False,ensure_ascii=False,default=json_default_formatter)
        with elapsed_timer() as elapsed:
            total_ipv4 = total_ipv6 = 0
            for region in ipranges['regions']:
                region_name = region['region']
                for item in region['cidrs']:
                    cidr = item['cidr']
                    service = ', '.join(item['tags'])
                    first_ip, netlen = str(cidr).split("/")
                    if cidr.find(":") < 0:
                        first_ip2int = ipv4_to_int(first_ip)                
                        total_ipv4 += numIPsv4[int(netlen)]
                    else:
                        first_ip2int = ipv6_to_int(first_ip)                
                        total_ipv6 += numIPsv6[int(netlen)]
                    cloudip[first_ip2int] = {'provider':'Oracle Cloud','cidr':cidr,'region':region_name,'service':service,'netlength':int(netlen),'network_features':''}
        try:
            formatedDate = dt.strptime(ipranges['last_updated_timestamp'], "%Y-%m-%dT%H:%M:%S.%f")
            formatedDate = formatedDate.strftime("%Y-%m-%d %H:%M:%S")
        except:
            formatedDate = ipranges['last_updated_timestamp']
        logVerbose(f"Updating ORACLE - Parsing IPv4 and IPv6 ranges updated at {formatedDate} {timer(elapsed())}")
        databaseInfo["Oracle Cloud"] = {'last_updated':formatedDate,
                                        'total_networks':len(cloudip.keys())-initialLen,
                                        'total_ipv4':total_ipv4, 'total_ipv6':total_ipv6}
    except Exception as ERR:
        logVerbose(f"Failed to update ORACLE CLOUD IP ranges - {str(ERR)}")
        return 1

##──── UPDATE DIGITAL OCEAN IP RANGES ──────────────────────────────────────────────────────────────────────────────────────────────────────
@print_elapsed_time
def update_ip_ranges_digital_ocean(download_url):
    global cloudip, databaseInfo, last_modified, _DEBUG
    initialLen = len(cloudip.keys())    
    try:
        with elapsed_timer() as elapsed:
            ipranges = download_file(download_url)
            if ipranges == False:
                logError(f"Updating DIGITAL OCEAN - FAILED to download IP ranges file from {download_url} {timer(elapsed())}")
                return False
            logVerbose(f"Updating DIGITAL OCEAN - Downloading IP ranges file {timer(elapsed())}")
            if _DEBUG == True:
                outputFile = os.path.join(DATA_DIR,'ipranges-digitalocean.csv')
                logDebug(f"Saving ipranges to {outputFile}")
                with open(outputFile,'w') as f:
                    for line in ipranges:
                        if line:
                            f.write(line+"\n")
        with elapsed_timer() as elapsed:
            total_ipv4 = total_ipv6 = 0
            for linha in ipranges:
                if linha != "":
                    cidr, country_code, micro_region, city, unknown = linha.split(",")
                    first_ip, netlen = str(cidr).split("/")
                    if cidr.find(":") < 0:
                        first_ip2int = ipv4_to_int(first_ip)
                        total_ipv4 += numIPsv4[int(netlen)]
                    else:
                        first_ip2int = ipv6_to_int(first_ip)
                        total_ipv6 += numIPsv6[int(netlen)]                
                    cloudip[first_ip2int] = {'provider':'Digital Ocean','cidr':cidr,'region':micro_region+" "+city,'service':'','netlength':int(netlen),'network_features':''}
        try:
            formatedDate = dt.strptime(last_modified, "%a, %d %b %Y %H:%M:%S %Z")
            formatedDate = formatedDate.strftime("%Y-%m-%d %H:%M:%S")
        except:
            formatedDate = last_modified
        logVerbose(f"Updating DIGITAL OCEAN - Parsing IPv4 and IPv6 ranges updated at {formatedDate} {timer(elapsed())}")
        databaseInfo["Digital Ocean"] = {'last_updated':formatedDate,
                                        'total_networks':len(cloudip.keys())-initialLen,
                                        'total_ipv4':total_ipv4, 'total_ipv6':total_ipv6}
    except Exception as ERR:
        logVerbose(f"Failed to update DIGITAL OCEAN IP ranges - {str(ERR)}")
        return 1
        

##################################################################################################################################
##################################################################################################################################

                             ##     ##    ###    #### ##    ##                 
                             ###   ###   ## ##    ##  ###   ##                 
                             #### ####  ##   ##   ##  ####  ##                 
                             ## ### ## ##     ##  ##  ## ## ##                 
                             ##     ## #########  ##  ##  ####                 
                             ##     ## ##     ##  ##  ##   ###                 
             ####### ####### ##     ## ##     ## #### ##    ## ####### ####### 
 
##################################################################################################################################
##################################################################################################################################
#defmain
def main_function():
    global args, _DEBUG
    sys.tracebacklimit = 0
    parser = ArgumentParser(formatter_class=class_argparse_formatter,
                            description=__doc__.splitlines()[1],
                            allow_abbrev=True,
                            add_help=False)
    lookup = parser.add_argument_group("Lookup Parameters")
    lookup.add_argument(dest="ipaddr",action="store",nargs='?',metavar="ipaddr,ipaddrN...",help="Supply one or more IP address separated by comma.")
    output = parser.add_argument_group("Output Options") 
    output.add_argument("--csv","-c",dest='csv',action="store_true",default=False,help="Print output in csv format (ip,cidr,region,cloud_provider,service,elapsed_time).")
    update = parser.add_argument_group("Database Options")
    update.add_argument("--update","-u",dest='update',action="store_true",default=False,help="Updates IP ranges directly from cloud service providers. Use -v to see updating progress.")
    update.add_argument("--info","-i",dest='info',action="store_true",default=False,help="Shows information about the current database file in json format.")
    update.add_argument("--pretty","-p",dest='pretty',action="store_true",default=False,help="Shows information about the current database file in a table format.")
    update.add_argument("--show-config-file",dest='showconfigfile',action="store_true",default=False,help="Displays the available settings for downloading information about network ranges.")
    optional = parser.add_argument_group("More Options")
    optional.add_argument('--verbose','-v',dest="verbose",action='store_true',default=False,help='Shows useful messages about each step that application is doing.')
    optional.add_argument('--debug','-d',dest="debug",action='store_true',default=False,help='Save all data from cloud providers in the data directory. Debug is not verbose!')
    optional.add_argument('--help','-h','-?',action='help',help='Shows this help message about the allowed commands.')
    optional.add_argument('--version',action='version',help='Shows the application version.',version="%s v%s"%(__appid__,__version__))
    ##────── do the parse ───────────────────────────────────────────────────────────────────────────────────────────────────
    args = parser.parse_args()
    ##────── Se não houve subcomando, exiba o help ─────────────────────────────────────────────────────────────────────────

    _DEBUG = args.debug
    if (args.debug == True and args.verbose == True):
        logDebug.__code__ = _logDebug.__code__
    if (args.verbose == False):
        logVerbose.__code__ = _logEmpty.__code__
        
    if (args.showconfigfile == True):
        try:
            with open(os.path.join(DATA_DIR,PROVIDERS_INFORMATION_FILE_NAME),"r") as f:
                infoFile = json.load(f)
            logDebug(f"Config file location: {os.path.join(DATA_DIR,PROVIDERS_INFORMATION_FILE_NAME)}")
            pp_json(infoFile)
            sys.exit(0)
        except Exception as ERR:
            logError(f"Failed to open information file \"{str(os.path.join(DATA_DIR,PROVIDERS_INFORMATION_FILE_NAME))}\": {str(ERR)}")
            sys.exit(1)
    
    if (args.update == True):
        sys.exit(update_ip_ranges(verbose=args.verbose,debug=_DEBUG))

    iplookup = CloudIPLookup((args.verbose or args.debug))
    if (args.info == True):
        if args.pretty == True:
            for key,val in databaseInfo.items():
                print(f"{key.ljust(32,'.')}: {(str(val['total_networks'])+' networks ').ljust(15)} - Last update: {val['last_updated']}")
        else:
            pp_json(databaseInfo)
        sys.exit(0)
    
    if (args.ipaddr is None):
        parser.print_help()
        print("")
        sys.exit(0)
    
    iplist = args.ipaddr.replace(' ','').split(",")
    for ipaddr in iplist:
        if args.csv == True:
            print(iplookup.lookup(ipaddr).pp_csv())
        else:
            print(iplookup.lookup(ipaddr).pp_json())

if __name__ == "__main__":
    sys.exit(main_function())