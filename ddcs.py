#!/usr/bin/env python
import os, sys, time
import requests, re
from progress.bar import Bar
import argparse

def helpmsg(name=None):
	return '''Generate a namelist from connect.data.com:
./ddcs.py -i <input file> -o <output file> [-f <#> -d <domain>]

Options: 
-h, --help\tPrint this help menu
-i\tInput file name (see exampleinput.txt for example)
-o\tOutput file name
-f\tEmail output format number. Supported formats: first.last (1), last.first (2), firstlast (3), lastfirst (4), finitlastn (5)(first initial last name)
-d\tEmail domain (ex: domain.com)'''

parser = argparse.ArgumentParser(usage=helpmsg(), add_help=False)
parser.add_argument('-h', '--help', dest='helpbool', action='store_true', required=False)
parser.add_argument('-o', dest='outputf', type=str, required=False)
parser.add_argument('-i', dest='inputf', type=str, required=False)
parser.add_argument('-f', dest='emailf', type=int, required=False)
parser.add_argument('-d', dest='domain', type=str, required=False)
args = vars(parser.parse_args())

if len(sys.argv) == 1 or args['helpbool'] == True:
	print helpmsg()
	sys.exit()
elif args['inputf'] is None:
    print '[-] Error! Missing input file'
    sys.exit()
elif args['outputf'] is None:
    print '[-] Error! Missing output file'
    sys.exit()

#ascii art
banner = ''' ______________
|        ___   |
|       |   |  | data.com scraper
|       |   |  | v2.0
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
    if len(req.split('\n\n')) == 2:
        headers, body = req.split('\n\n')
    elif len(req.split('\n\r\n')) == 2:
        headers, body = req.split('\n\r\n')
    else:
        print '[-] Error reading file'
        sys.exit()
        
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
        try:
            key, value = line.split('=')
        except:
            pass
        payload[key] = value.strip()

def genemail(first,last):
    #args['emailf'] ['domain']
    if args['emailf'] == 1 and args['domain'] is not None:
        email = first+'.'+last+'@'+args['domain']
    elif args['emailf'] == 2 and args['domain'] is not None:
        email = last+'.'+first+'@'+args['domain']
    elif args['emailf'] == 3 and args['domain'] is not None:
        email = first+last+'@'+args['domain']
    elif args['emailf'] == 4 and args['domain'] is not None:
        email = last+first+'@'+args['domain']
    elif args['emailf'] == 5 and args['domain'] is not None:
        email = first[:1]+last+'@'+args['domain']
    else:
        email = 'null'
    
    return email.lower()

def iteratename():
    r = requests.post('https://connect.data.com/dwr/call/plaincall/SearchDWR.findContacts.dwr', data=payload, headers=reqheaders)
    if r.status_code != 200:
        print '[-] Error making initial request...quitting!'
        sys.exit()
    
    #get page numbers
    pages = re.search('count.*?,', r.text, re.DOTALL).group(0)
    pages = int(pages[6:len(pages)-1])/200 +2

    bar = Bar('[+] Processing', max=pages)
    bar.next()
    for i in range(1,pages):
        time.sleep(30)
        bar.next()
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
                email = genemail(first,last)
                names.append(first+','+last+','+email)
    bar.finish() 

#main
if __name__ == '__main__':
    print banner
    print '[+] Reading input file'
    processrequest(args['inputf'])
    print '[+] Requesting names from data.com'
    iteratename()
    
    writeto = open(args['outputf'], 'w+')
    writeto.write('First Name, Last Name, Email\n')
    for name in names:
        writeto.write(name.encode('utf-8'))
        writeto.write('\n')
    writeto.close()
    print '[+] '+ str(len(names))+' names written to: '+args['outputf']