# Cloud IP Lookup v1.0.6
Cloud IP Lookup is a Pure Python application and library for Python 3 to verify which cloud platform a given IP address belongs to. Its supports IPv4 and IPv6, and have its own database that can be updated whenever you want with a simple command: ```cloudiplookup --update [--verbose]```

**Cloud IP Lookup does not connect to your cloud services account**. All data is collected from the websites of the most popular cloud service providers. Sometimes these databases are updated several times a day. We recommend that you put the update command in your crontab, at least once a day.

This version has data from AWS, Azure, Cloudflare, Digital Ocean, Google Services (Google Bot, Special Crawlers and User Fetchers), Google Cloud, JD Cloud China and Oracle Cloud providers. Some of them provide the names of services and regions, others don´t, like Cloudflare that only provides the network ranges.

We can add other cloud providers, just open an issue at https://github.com/rabuchaim/cloudiplookup/issues. The requirement for addition is that the cloud provider must have a page where its network ranges are published in json, txt or csv format. For example, AWS: https://ip-ranges.amazonaws.com/ip-ranges.json.


## Installation

```bash
pip install cloudiplookup
```
Or cloning from Github
```bash
git clone https://github.com/rabuchaim/cloudiplookup.git
```

## How to use it as a Python library

```bash
# python3
Python 3.11.6 (main, Oct 23 2023, 22:48:54) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from cloudiplookup import CloudIPLookup
>>> myLookup = CloudIPLookup(verbose=True)
Cloud IP Lookup v1.0.5 is ready! loaded with 48526 networks in 0.00633 seconds and using 4.16 MiB of RAM.
>>> print(myLookup.lookup('52.94.7.24').pp_json())
{
   "ip": "52.94.7.24",
   "cidr": "52.94.7.0/24",
   "region": "sa-east-1",
   "cloud_provider": "AWS",
   "service": "DYNAMODB",
   "elapsed_time": "0.000128607 sec"
}
>>>
>>> result = myLookup.lookup('52.94.7.24')
>>> print(result.cloud_provider)
AWS
>>> print(result.region)
sa-east-1
>>>
>>> result.to_dict()['cloud_provider']
'AWS'
>>> result.to_dict()['region']
'sa-east-1'
>>>
>>> myLookup.get_database_info()
{
   "AWS": {
      "last_updated": "2024-07-24 21:33:10",
      "total_networks": 7632,
      "total_ipv4": 145103465,
      "total_ipv6": 2340885926027723825138381094922
   },
   "Azure": {
      "last_updated": "2024-07-23 10:15:04",
      "total_networks": 44388,
      "total_ipv4": 85522162,
      "total_ipv6": 2787683180039384255618424539
   },
   "Cloudflare": {
      "last_updated": "2024-07-24 23:21:45",
      "total_networks": 22,
      "total_ipv4": 1524736,
      "total_ipv6": 1109194275199700726309615304704
   },
   "Digital Ocean": {
      "last_updated": "2024-07-24 23:04:48",
      "total_networks": 1141,
      "total_ipv4": 2943360,
      "total_ipv6": 2637884402540465881088
   },
   "Google Cloud": {
      "last_updated": "2024-07-24 13:06:03",
      "total_networks": 670,
      "total_ipv4": 13074688,
      "total_ipv6": 832949889714479501372555264
   },
   "Google Services": {
      "last_updated": "2024-07-24 13:06:03",
      "total_networks": 73,
      "total_ipv4": 18049280,
      "total_ipv6": 2060551195390515467569592270848
   },
   "Google Bot": {
      "last_updated": "2024-07-23 22:00:20",
      "total_networks": 229,
      "total_ipv4": 3712,
      "total_ipv6": 1918461383665793368064
   },
   "Google Special Crawlers": {
      "last_updated": "2024-07-23 22:00:20",
      "total_networks": 208,
      "total_ipv4": 3328,
      "total_ipv6": 1918461383665793368064
   },
   "Google User Triggered Fetchers": {
      "last_updated": "2024-07-23 22:00:20",
      "total_networks": 729,
      "total_ipv4": 11680,
      "total_ipv6": 6733061586903986339840
   },
   "JD Cloud": {
      "last_updated": "2024-07-24 23:21:48",
      "total_networks": 91,
      "total_ipv4": 1568,
      "total_ipv6": 121056757983718932480
   },
   "Oracle Cloud": {
      "last_updated": "2024-07-15 09:52:55",
      "total_networks": 745,
      "total_ipv4": 2643530,
      "total_ipv6": 0
   }
}
>>>
>>> from cloudiplookup import update_ip_ranges
>>> update_ip_ranges(verbose=True,debug=False)
Updating AWS - Downloading IP ranges file [0.194571811 sec]
Updating AWS - Parsing IPv4 and IPv6 ranges updated at 2023-11-14 14:13:09 [0.008731522 sec]
Updating AZURE - Downloading IP ranges file [9.597737358 sec]
Updating AZURE - Parsing IPv4 and IPv6 ranges updated at 2023-11-14 12:29:44 [0.064075109 sec]
Updating CLOUDFLARE - Downloading IP ranges file [0.109633796 sec]
Updating CLOUDFLARE - Parsing IPv4 and IPv6 ranges updated at 2023-11-15 05:23:41 [0.000105514 sec]
Updating DIGITAL OCEAN - Downloading IP ranges file [0.447540575 sec]
Updating DIGITAL OCEAN - Parsing IPv4 and IPv6 ranges updated at 2023-11-14 17:43:11 [0.004395924 sec]
Updating GCP - Downloading IP ranges file [0.197874399 sec]
Updating GCP - Parsing IPv4 and IPv6 ranges updated at 2023-11-14 18:04:10 [0.001701975 sec]
Updating GOOGLE SERVICES - Downloading IP ranges file [0.294104148 sec]
Updating GOOGLE SERVICES - Parsing IPv4 and IPv6 ranges updated at 2023-11-14 18:04:10 [0.000351157 sec]
Updating GOOGLE BOT - Downloading IP ranges file [0.396489796 sec]
Updating GOOGLE BOT - Parsing IPv4 and IPv6 ranges updated at 2023-11-14 23:00:21 [0.000692362 sec]
Updating GOOGLE SPECIAL CRAWLERS - Downloading IP ranges file [0.350542481 sec]
Updating GOOGLE SPECIAL CRAWLERS - Parsing IPv4 and IPv6 ranges updated at 2023-11-14 23:00:25 [0.000751040 sec]
Updating GOOGLE USER TRIGGERED FETCHERS - Downloading IP ranges file [0.564765383 sec]
Updating GOOGLE USER TRIGGERED FETCHERS - Parsing IPv4 and IPv6 ranges updated at 2023-11-14 23:00:22 [0.001925866 sec]
Updating JD CLOUD - Downloading IP ranges file [0.375312087 sec]
Updating JD CLOUD - Parsing IPv4 and IPv6 ranges updated at 2023-11-15 05:23:44 [0.000438635 sec]
Updating ORACLE - Downloading IP ranges file [1.007827670 sec]
Updating ORACLE - Parsing IPv4 and IPv6 ranges updated at 2023-10-10 04:47:03 [0.001333245 sec]
Sorting IPv4 and IPv6 data [0.019742529 sec]
Updating all lists... Done! [0.042858025 sec]
Saved file /var/lib/cloudiplookup/cloudiplookup.dat.gz [0.200645894 sec]
Cloud IP Lookup updated with success! [13.629677833 sec]
>>>
```

## The database file

Cloud IP Lookup uses a pickle database that is a bunch of lists of integers. Everything is located at ```/var/lib/cloudiplookup/```. 

> *On Windows systems, these files are located in the same directory as the library files*.

```bash
root@tucupi:/var/lib/cloudiplookup# ll
total 184
drwxr-xr-x  2 root root   4096 Nov  6 00:21 ./
drwxr-xr-x 47 root root   4096 Oct 11 21:11 ../
-rw-r--r--  1 root root 172158 Nov  6 00:15 cloudiplookup.dat.gz
-rw-r--r--  1 root root    942 Sep 29 10:53 cloudiplookup.json
```

There is a file ```/var/lib/cloudiplookup/cloudiplookup.json``` with all cloud providers information and an another file ```/var/lib/cloudiplookup/cloudiplookup.dat.gz``` that is the database created by function ```update_ip_ranges()```.

```bash
root@tambaqui:/var/lib/cloudiplookup# cat cloudiplookup.json
{
    "AWS": {
        "info_page": "https://docs.aws.amazon.com/vpc/latest/userguide/aws-ip-ranges.html",
        "download_url": "https://ip-ranges.amazonaws.com/ip-ranges.json"
    },
    "AZURE": {
        "info_page": "https://www.microsoft.com/en-us/download/details.aspx?id=56519",
        "download_url": "https://download.microsoft.com/download/(...)/ServiceTags_Public_XXXXXXXX.json"
    },
    "CLOUDFLARE": {
        "info_page": "https://www.cloudflare.com/ips/",
        "download_url": "https://api.cloudflare.com/client/v4/ips"
    },
    "DIGITALOCEAN": {
        "info_page": "https://docs.digitalocean.com/products/platform/",
        "download_url": "https://www.digitalocean.com/geo/google.csv"
    },
    "GOOGLECLOUD": {
        "info_page": "https://support.google.com/a/answer/10026322?hl=en",
        "download_url": "https://www.gstatic.com/ipranges/cloud.json"
    },
    "GOOGLESERVICES": {
        "info_page": "https://support.google.com/a/answer/10026322?hl=en",
        "download_url": "https://www.gstatic.com/ipranges/goog.json"
    },    
    "JDCLOUD": {
        "info_page": "https://www.cloudflare.com/ips/",
        "download_url": "https://api.cloudflare.com/client/v4/ips?networks=jdcloud"
    },
    "ORACLE": {
        "info_page": "https://docs.oracle.com/pt-br/iaas/Content/General/Concepts/addressranges.htm",
        "download_url": "https://docs.oracle.com/iaas/tools/public_ip_ranges.json"
    }
}
```

## Use as a command line application

```bash
# cloudiplookup
root@pirarara:/var/lib/cloudiplookup# ./cloudiplookup.py
Usage: cloudiplookup.py [--csv] [--info] [--pretty] [--update] [--show-config-file] [--verbose] [--debug] [--help] [--version] [ipaddr,ipaddrN...]

Cloud IP Lookup v1.0.5 - Public cloud services IP addresses lookup tool

Lookup Parameters:
  ipaddr,ipaddrN...   Supply one or more IP address separated by comma.

Output Options:
  --csv, -c           Print output in csv format (ip,cidr,region,cloud_provider,service,elapsed_time).

Database Options:
  --update, -u        Updates IP ranges directly from cloud service providers. Use -v to see updating progress.
  --info, -i          Shows information about the current database file in json format.
  --pretty, -p        Shows information about the current database file in a table format.
  --show-config-file  Displays the available settings for downloading information about network ranges.

More Options:
  --verbose, -v       Shows useful messages about each step that application is doing.
  --debug, -d         Save all data from cloud providers in the data directory. Debug is not verbose!
  --help, -h, -?      Shows this help message about the allowed commands.
  --version           Shows the application version.
```

```bash
# cloudiplookup 3.2.35.65,5.101.104.55,66.249.66.193,2600:9000:21e8:2600:1:5a19:8b40:93a1,104.198.16.10,13.71.199.112
{
   "ip": "3.2.35.65",
   "cidr": "3.2.35.64/26",
   "region": "sa-east-1",
   "cloud_provider": "AWS",
   "service": "EC2",
   "elapsed_time": "0.000016832 sec"
}
{
   "ip": "5.101.104.55",
   "cidr": "5.101.104.0/22",
   "region": "NL-NH Amsterdam",
   "cloud_provider": "Digital Ocean",
   "service": "",
   "elapsed_time": "0.000002593 sec"
}
{
   "ip": "66.249.66.193",
   "cidr": "66.249.66.192/27",
   "region": "",
   "cloud_provider": "Google",
   "service": "Bot",
   "elapsed_time": "0.000031584 sec"
}
{
   "ip": "2600:9000:21e8:2600:1:5a19:8b40:93a1",
   "cidr": "2600:9000:2000::/36",
   "region": "GLOBAL",
   "cloud_provider": "AWS",
   "service": "CLOUDFRONT",
   "elapsed_time": "0.000024586 sec"
}
{
   "ip": "104.198.16.10",
   "cidr": "104.198.16.0/20",
   "region": "us-central1",
   "cloud_provider": "Google Cloud",
   "service": "Google Cloud",
   "elapsed_time": "0.000026428 sec"
}
{
   "ip": "13.71.199.112",
   "cidr": "13.71.199.112/30",
   "region": "westcentralus",
   "cloud_provider": "Azure",
   "service": "ActionGroup",
   "elapsed_time": "0.000004339 sec"
}
 ```
```bash
# cloudiplookup --csv 3.2.35.65,5.101.104.55,2600:9000:21e8:2600:1:5a19:8b40:93a1,8.35.192.12,13.71.199.112
3.2.35.65,3.2.35.64/26,sa-east-1,AWS,EC2,0.000019659
5.101.104.55,5.101.104.0/22,NL-NH Amsterdam,Digital Ocean,,0.000002078
2600:9000:21e8:2600:1:5a19:8b40:93a1,2600:9000:2000::/36,GLOBAL,AWS,CLOUDFRONT,0.000028556
8.35.192.12,8.35.192.0/20,,Google Cloud,,0.000004661
13.71.199.112,13.71.199.112/30,westcentralus,Azure,ActionGroup,0.000004508
```
```bash
# cloudiplookup --update --verbose
Updating AWS - Downloading IP ranges file [0.247580905 sec]
Updating AWS - Parsing IPv4 and IPv6 ranges updated at 2023-11-14 14:13:09 [0.007899989 sec]
Updating AZURE - Downloading IP ranges file [11.802777994 sec]
Updating AZURE - Parsing IPv4 and IPv6 ranges updated at 2023-11-14 12:29:44 [0.069718062 sec]
Updating CLOUDFLARE - Downloading IP ranges file [0.096246977 sec]
Updating CLOUDFLARE - Parsing IPv4 and IPv6 ranges updated at 2023-11-15 05:24:27 [0.000107779 sec]
Updating DIGITAL OCEAN - Downloading IP ranges file [0.715709110 sec]
Updating DIGITAL OCEAN - Parsing IPv4 and IPv6 ranges updated at 2023-11-14 17:43:11 [0.004408466 sec]
Updating GOOGLE CLOUD - Downloading IP ranges file [0.243777335 sec]
Updating GOOGLE CLOUD - Parsing IPv4 and IPv6 ranges updated at 2023-11-14 18:04:10 [0.000553817 sec]
Updating GOOGLE SERVICES - Downloading IP ranges file [0.219680303 sec]
Updating GOOGLE SERVICES - Parsing IPv4 and IPv6 ranges updated at 2023-11-14 18:04:10 [0.000346342 sec]
Updating GOOGLE BOT - Downloading IP ranges file [0.488023029 sec]
Updating GOOGLE BOT - Parsing IPv4 and IPv6 ranges updated at 2023-11-14 23:00:21 [0.000280338 sec]
Updating GOOGLE SPECIAL CRAWLERS - Downloading IP ranges file [0.362579674 sec]
Updating GOOGLE SPECIAL CRAWLERS - Parsing IPv4 and IPv6 ranges updated at 2023-11-14 23:00:25 [0.000616955 sec]
Updating GOOGLE USER TRIGGERED FETCHERS - Downloading IP ranges file [0.587292662 sec]
Updating GOOGLE USER TRIGGERED FETCHERS - Parsing IPv4 and IPv6 ranges updated at 2023-11-14 23:00:22 [0.001841709 sec]
Updating JD CLOUD - Downloading IP ranges file [0.391410524 sec]
Updating JD CLOUD - Parsing IPv4 and IPv6 ranges updated at 2023-11-15 05:24:30 [0.000430358 sec]
Updating ORACLE - Downloading IP ranges file [0.732044416 sec]
Updating ORACLE - Parsing IPv4 and IPv6 ranges updated at 2023-10-10 04:47:03 [0.001720133 sec]
Sorting IPv4 and IPv6 data [0.021423362 sec]
Updating all lists... Done! [0.028821872 sec]
Saved file /var/lib/cloudiplookup/cloudiplookup.dat.gz [0.203250980 sec]
Cloud IP Lookup updated with success! [15.981186821 sec]
```
```bash
# ./cloudiplookup.py --info --pretty
AWS.............................: 7251 networks   - Last update: 2023-11-14 14:13:09
Azure...........................: 39244 networks  - Last update: 2023-11-14 12:29:44
Cloudflare......................: 22 networks     - Last update: 2023-11-15 05:24:27
Digital Ocean...................: 1683 networks   - Last update: 2023-11-14 17:43:11
Google Cloud....................: 652 networks    - Last update: 2023-11-14 18:04:10
Google Services.................: 61 networks     - Last update: 2023-11-14 18:04:10
Google Bot......................: 231 networks    - Last update: 2023-11-14 23:00:21
Google Special Crawlers.........: 210 networks    - Last update: 2023-11-14 23:00:25
Google User Triggered Fetchers..: 719 networks    - Last update: 2023-11-14 23:00:22
JD Cloud........................: 115 networks    - Last update: 2023-11-15 05:24:30
Oracle Cloud....................: 647 networks    - Last update: 2023-10-10 04:47:03
```
## Debug mode

If you update the data using the ```--debug``` option, all files downloaded from cloud service providers will be available in the ```/var/lib/cloudiplookup``` directory. 

> *On Windows systems, these files are located in the same directory as the library files*.

```bash
root@pirarara:/var/lib/cloudiplookup# ll
total 20368
drwxr-xr-x 3 ricardo ricardo     4096 Nov 15 01:54 ./
drwxr-xr-x 6 ricardo root        4096 Nov  7 23:58 ../
-rw-r--r-- 1 root    root    10484261 Nov 15 01:54 cloudip.json
-rw-r--r-- 1 root    root      177903 Nov 15 01:54 cloudiplookup.dat.gz
-rw-r--r-- 1 root    root     4479551 Nov 15 01:54 cloudiplookup.dat.json
-rw-r--r-- 1 root    root        1448 Nov 15 01:31 cloudiplookup.json
-rw-r--r-- 1 root    root     1666844 Nov 15 02:22 ipranges-aws.json
-rw-r--r-- 1 root    root     3678383 Nov 15 02:22 ipranges-azure.json
-rw-r--r-- 1 root    root         788 Nov 15 02:22 ipranges-cloudflare.json
-rw-r--r-- 1 root    root       71987 Nov 15 02:22 ipranges-digitalocean.csv
-rw-r--r-- 1 root    root       83122 Nov 15 02:22 ipranges-gcp.json
-rw-r--r-- 1 root    root        4934 Nov 15 02:22 ipranges-goog.json.json
-rw-r--r-- 1 root    root       14358 Nov 15 02:22 ipranges-googlebot.json.json
-rw-r--r-- 1 root    root        4527 Nov 15 02:22 ipranges-jdcloud.json
-rw-r--r-- 1 root    root       93165 Nov 15 02:23 ipranges-oracle.json
-rw-r--r-- 1 root    root       13289 Nov 15 02:22 ipranges-special-crawlers.json.json
-rw-r--r-- 1 root    root       43826 Nov 15 02:22 ipranges-user-triggered-fetchers.json.json
```

## Sugestions, feedbacks, bugs, new cloud service provider requests...
E-mail me: ricardoabuchaim at gmail.com

