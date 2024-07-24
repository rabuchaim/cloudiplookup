```
Cloud IP Lookup v1.0.6 - Public cloud services IP addresses lookup tool

Author: Ricardo Abuchaim - ricardoabuchaim@gmail.com
        https://github.com/rabuchaim/cloudiplookup

License: MIT

  ###  #  #   ##   #  #   ###  ####  #      ##    ###
 #     #  #  #  #  ## #  #     #     #     #  #  #
 #     ####  #  #  # ##  # ##  ###   #     #  #  # ##
 #     #  #  ####  #  #  #  #  #     #     #  #  #  #
  ###  #  #  #  #  #  #   ###  ####  ####   ##    ###

What's new in v1.0.6 - 24/Jul/2024
- Database included in this package was updated on 24/Jul/2024.
- Put some flowers in database info function
- Moved the line sys.tracebacklimit from begginning to the main_function() 
  because it was causing problems in Django.
- Changed the regex to identify the download URL from Azure. Some devs are using
  this library with AWS Lambdas and AWS was throwing some Warnings about the 
  scape "\" sequence. No impact.

What's new in v1.0.5 - 15/Nov/2023
- Updated Google Services (Google Bot, Special Crawlers and User Fetchers), 
  Cloudflare and JD Cloud China.

What's new in v1.0.4 - 08/Nov/2023
- Created a debug option in function update_ip_ranges(). The debug option save all files
  downloaded from cloud providers into the data directory. Debug is not verbose!

  def update_ip_ranges(verbose=False,debug=False):

- The "verbose" option in the update_ip_ranges(verbose=False) function was not 
  working. This problem only occurs if you are using as a library and try to 
  update cloudiplookup while a program is running. Verbose log messages 
  were displayed even if enabled with the "verbose=False" option. It is now 
  working correctly. It did not affect the search or the update itself.

    >>> from cloudiplookup import CloudIPLookup, update_ip_ranges
    >>> update_ip_ranges(verbose=False,debug=False)
    0
    >>> update_ip_ranges(Verbose=True,debug=False)
    Updating AWS - Downloading IP ranges file [0.342903962 sec]
    Updating AWS - Parsing IPv4 and IPv6 ranges updated at 2023-11-07 22:43:10 [0.009359716 sec]
    (.......)

What's new in v1.0.2 - 06/Nov/2023
- Cloud providers' update dates have been normalized. Aesthetic change.

What's new in v1.0.1 - 06/Nov/2023
- Changed Digital Ocean URL (just added www to the hostname)
- Collected last modified date from Digital Ocean via http header (previously 
  last modified date was not collected)
- Print output in csv format (ip,cidr,region,cloud_provider,service,elapsed_time)
- Fixed an issue in the function that adjusts the terminal window. This problem 
  prevented the cloudiplookup.py script from being executed by crontab.
- Fixed the function that checks the memory used in Windows
- You can run "cloudiplookup" from any path on windows
- Fully tested in Python 3.11, 3.12 and 3.13
- Put some flowers

What's new in v1.0.0 - 30/Sep/2023
- INITIAL PUBLIC RELEASE

```