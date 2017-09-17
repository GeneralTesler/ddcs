# data.com Scraper

This script will scrape connect.data.com for employee names. If an email format and domain are supplied, it will generate the emails for each name retrieved. 

## Usage

**Requirements**: 

pip install: requests, progress

**Input**: a file containing the initial contact listing request on connect.data.com (https://connect.data.com/dwr/call/plaincall/SearchDWR.findContacts.dwr). This contains the three pieces of information needed for gathering the names: two session cookies and the target domain. I have included an example input file for reference.

**Output**: a file containing a newline delimited list of names. If no email format and domain are supplied, emails are 'null'

**Syntax**

```
./ddcs.py -i <input file> -o <output file> [-f <#> -d <domain>]

Options: 
-h, --help      Print this help menu
-i              Input file name (see exampleinput.txt for example)
-o              Output file name
-f              Email output format number. Supported formats: first.last (1), last.first (2), firstlast (3), lastfirst (4), finitlastn (5)(first initial last name)
-d              Email domain (ex: domain.com)
```

## Notes

- The script will filter out names containing special characters.

- The script will wait 30 seconds between requesting pages to help prevent triggering a CAPTCHA. If you are still getting CAPTCHA'd, consider increasing the sleep time and/or considering making a new account (it appears that CAPTCHAs are per-user, not per-source)

## Changelog

- 9/16/2017 - added better argument parsing; added email generation; changed output to csv
- 7/17/2017 - fixed issue where an empty last line caused an error; added a progress bar
- 7/1/2017 - inital commit
