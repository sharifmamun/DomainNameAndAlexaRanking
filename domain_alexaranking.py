#!/usr/bin/python
# -*- coding: utf-8 -*-
# Last updated on: March 22, 2013

# All the import stuffs#
# If you don't have anything, please have that or I can help you to get that!

import cookielib
from mechanize import Browser
import mechanize
from bs4 import BeautifulSoup
import re
import subprocess
import time
import sys
import csv
import os
import urllib2
import sys, traceback
import glob
# ----------Import ENDs here-------------

def main():
    # Asking for user input
    input_from_user = raw_input("Enter the search string: ").strip()
    if str(input_from_user).find("."):
        query = input_from_user.split(".")[0]
    else:
        query = input_from_user
    # I am using http://www.namedroppers.com/ for checking domains
    # I had done a handful amount of time to do that research
    # It's better than most of the domain search tools and the Google search
    sample_file = open(query+".csv", "wb")
    csv_output = csv.writer(sample_file, dialect='excel')   # output.csv is the output file name!
    csv_output.writerow(["Domain Name","Admin Info", "Email Address", "Popularity Rank", "Reachability Rank"]) # Setting first row with all column titles
    sample_file.close()
    url = "http://www.namedroppers.com/b/q?k=%s&x=20&y=19&order=0&com=1&net=1&org=1&edu=1&biz=1&us=1&info=1&name=1&display=2"% (query)

    # Beautfying the response from the browser
    get_Response(query, url)

    for i in range(2,3):
        try:
            new_url = "http://www.namedroppers.com/b/q?p=%d&k=%s&order=0&com=1&net=1&org=1&edu=1&biz=1&us=1&info=1&name=1" % (i, query)
            get_Response(query, new_url)
            for files in glob.glob("*.txt"):
                os.remove(files)
        except Exception, e:
            print "Couldn't do it: %s" % e            
            print "DONE"            
            os._exit(1)
        

def get_Response(query, new_url):
    # Opening a browser
    br = Browser()
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
     # Setting browsers
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)
    br.set_handle_robots(False)
    br.set_handle_equiv(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    # Getting response from the Browser and reading that
    new_response = br.open(new_url).read()
    
    new_soup = BeautifulSoup(new_response)
    soup_finder = new_soup.find("pre")
    ## Creating CSV file
    sample_file = open(query+".csv", "ab")
    csv_output = csv.writer(sample_file, dialect='excel')   # output.csv is the output file name!
    
    for a_tr in soup_finder.findAll("a"):
        if str(a_tr).startswith("<a href=\"/who/"):
            start = '<a href=\"/who/'
            end = '\">WHOIS</a>'
            result = re.search('%s(.*)%s' % (start, end), str(a_tr)).group(1)
            print(result)
            f_name = result
            #os.remove('log.txt')
            log_file = open(f_name + '.txt', 'w')
            log_file.seek(0)
            time.sleep(1)
            child = subprocess.Popen(['whois', result], shell = True, stdout=log_file, stderr=log_file)
            log_file.flush()
            time.sleep(1)
            log_file.close()
            #print a_tr
            
            email = email_address_finder(f_name + '.txt')
            
            admin_info = []
            admin_info.append(result)
            time.sleep(1)
            line_file = open(f_name+'.txt', 'r')
            line_file.seek(0)
            time.sleep(1)
            line_string = line_file.readlines()
            admin_name = ""
            checker =0
            if len(line_string)>0:
                if line_string[8].find("The data")!= -1:
                    for i, line in enumerate(line_string):
                        if line.find("Registrant:")!= -1:
                            admin_name = str(line_string[i+1]).strip()
            if admin_name=="":  
                for i, line in enumerate(line_string):
                    if line.find("Registrant")!= -1 or line.find("REGISTRANT")!= -1 or line.find("registrant")!= -1:
                        #print "inside if"
                        for j in range(i+1,i+2):
                            if (str(line_string[j])).find(":") != -1:
                                temp = (str(line_string[j]).strip())                            
                                #print temp
                                #print (str(line_string[j])).find(":")
                                admin_name = temp.split(":")[1]
                            else:
                                admin_name = str(line_string[j]).strip()
                        break
            if admin_name=="":
                for i, line in enumerate(line_string):
                    if line.find("Administrative")!= -1:
                            admin_name = str(line_string[i+1]).strip()
                            r = re.compile(r'(\b[\w.]+@+[\w.]+.+[\w.]\b)')
                            results = r.findall(admin_name)
                            #print results
                            if len(results)> 0:
                                admin_name = admin_name[0:admin_name.find(results[0])]
                                if email == "Null":
                                    email = results[0]                                            
            if admin_name=="":
                admin_name = "Not Found"
            admin_info.append(admin_name)
            admin_info.append(str(email))
            popularity, reach = get_alexa_rank(result)
            #print popularity, reach
            admin_info.extend([popularity, reach])   
            #print "ADMIN INFO", admin_info                    
            csv_output.writerow(admin_info)
            #print "Done"
            line_file.close()
            
    sample_file.close()

def email_address_finder(filename):
    # vars for filenames
    # read file
    time.sleep(1)
    if os.path.exists(filename):
            data = open(filename,'r')
            data.seek(0)
            bulkemails = data.read()
            data.close()
    else:
            print "File not found."
            raise SystemExit

    # regex = whoEver@wHerever.xxx
    r = re.compile(r'(\b[\w.]+@+[\w.]+.+[\w.]\b)')
    results = r.findall(bulkemails)
    
    if len(results) >0 :    
        return results[0]
    else:
        return "Null"


def get_alexa_rank(url):
    try:
        data = urllib2.urlopen('http://data.alexa.com/data?cli=10&dat=snbamz&url=%s' % (url)).read()

        reach_rank = re.findall("REACH[^\d]*(\d+)", data)
        if reach_rank:
            reach_rank = reach_rank[0]
        else:
            reach_rank = 0

        popularity_rank = re.findall("POPULARITY[^\d]*(\d+)", data)
        if popularity_rank:
            popularity_rank = popularity_rank[0]
        else:
            popularity_rank = 0
        return int(popularity_rank), int(reach_rank)

    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        return -1, -1 

if  __name__ =='__main__':
    main()
