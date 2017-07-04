#!/usr/bin/env python
import os, sys, time
import requests
import re

if len(sys.argv) != 3:
    print '[-] Too few or too many arguments. Please refer to the README.'
    sys.exit()

#ascii art
banner = ''' ______________
|        ___   |
|       |   |  | data.com scraper
|       |   |  | v1.0
|   ____|   |  | 
|  |        |  | 
|  |  [ ]   |  | by:
|  |________|  | https://github.com/generaltesler
|______________|
'''

#global vars
cwd = os.getcwd()
names = []
payload = {}
reqheaders = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}
specialchars = ['!','?','.','_','@','#','$','%','^','&','*','(',')','+','=','/','\\','<','>','`','~','|','{','}','[',']',';',':',',','\"']

def processrequest(filename):
    with open(cwd+'/'+filename, 'r') as f:
        req = f.read()
    headers, body = req.split('\n\n')
    
    #get session data from headers
    jsessionid = re.search('JSESSIONID=.*?(;|\n)',headers).group(0)
    #jsessionid = jsessionid[11:len(jsessionid)-1]
    dwrsessionid = re.search('DWRSESSIONID=.*?(;|\n)',headers).group(0)
    #dwrsessionid = dwrsessionid[13:len(dwrsessionid)-1]
    cookies = jsessionid+' '+dwrsessionid.strip()
    reqheaders['Cookie'] = cookies

    #construct post body
    for line in body.split('\n'):
        if line[:8] == 'c0-param':
            #if page number isnt in body -> add it (required for iteration)
            #change number of names on page to max (200)
            if 'curentPage' not in line:
                line = re.sub(r'%22totalRecordsOnPage%22%3A.*?%7D',r'%22currentPage%22%3A1%2C%22totalRecordsOnPage%22%3A200%7D',line)
            else:
                line = re.sub(r'%22totalRecordsOnPage%22%3A.*?%7D',r'%22totalRecordsOnPage%22%3A200%7D',line)
        key, value = line.split('=')
        payload[key] = value.strip()


def iteratename():
    r = requests.post('https://connect.data.com/dwr/call/plaincall/SearchDWR.findContacts.dwr', data=payload, headers=reqheaders)
    if r.status_code != 200:
        print '[-] Error making initial request...quitting!'
        sys.exit()
    
    #get page numbers
    pages = re.search('count.*?,', r.text, re.DOTALL).group(0)
    pages = int(pages[6:len(pages)-1])/200 +2

    for i in range(1,pages):
        time.sleep(30)
        payload['c0-param0'] = re.sub(r'%22currentPage%22%3A.*?%2C', r'%22currentPage%22%3A'+str(i)+r'%2C', payload['c0-param0'], re.DOTALL)
        r = requests.post('https://connect.data.com/dwr/call/plaincall/SearchDWR.findContacts.dwr', data=payload, headers=reqheaders)
        if r.status_code != 200:
            print '[-] Error requesting names on page '+i
            pass
        
        #extract names
        for each in re.findall('inactive.*?name.*?\".*?\"',r.text, re.DOTALL):
            name = re.search('name:\".*?\"',each).group(0)
            name = name[6:len(name)-1]
            if len(name.split(', ')) == 2:
                last, first = name.split(', ')
            else:
                pass
            #dont append any names containing special characters
            if not any(char in last for char in specialchars) and not any(char in first for char in specialchars): 
                names.append(first+' '+last)

#main
if __name__ == '__main__':
    print banner
    print '[+] Reading input file'
    processrequest(sys.argv[1])
    print '[+] Requesting names from data.com'
    iteratename()
    
    writeto = open(sys.argv[2], 'w+')
    for name in names:
        writeto.write(name.encode('utf-8'))
        writeto.write('\n')
    writeto.close()
    print '[+] '+ str(len(names))+' names written to: '+sys.argv[2]
