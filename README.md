# data.com Scraper

This script will scrape connect.data.com for employee names. The output list of names is useful for generating a list of emails and/or usernames for a password spray.

## Usage

**Requirements**: requests (pip install requests)

**Input**: a file containing the initial contact listing request on connect.data.com (https://connect.data.com/dwr/call/plaincall/SearchDWR.findContacts.dwr). This contains the three pieces of information needed for gathering the names: two session cookies and the target domain. I have included an example input file for reference.

**Output**: a file containing a newline delimited list of names

**Syntax**

```
./ddcs.py <input file> <output file>
```

## Notes

- The script will filter out names containing special characters.

- The script will wait 30 seconds between requesting pages to help prevent triggering a CAPTCHA. If you are still getting CAPTCHA'd, consider increasing the sleep time and/or considering making a new account (it appears that CAPTCHAs are per-user, not per-source)

## Changelog

- 7/1/2017 - inital commit