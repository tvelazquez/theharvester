#!/usr/bin/env python

import string
import httplib, sys
from socket import *
import re
import getopt
from discovery import *
from lib import htmlExport
from lib import hostchecker

print "\n*************************************"
print "*TheHarvester Ver. 2.2              *"
print "*Coded by Christian Martorella      *"
print "*Edge-Security Research             *"
print "*cmartorella@edge-security.com      *"
print "*************************************\n\n"

def usage():

 print "Usage: theharvester options \n"
 print "       -d: Domain to search or company name"
 print "       -b: Data source (google,bing,bingapi,pgp,linkedin,google-profiles,people123,jigsaw,all)"
 print "       -s: Start in result number X (default 0)"
 print "       -v: Verify host name via dns resolution and search for virtual hosts"
 print "       -f: Save the results into an HTML and XML file"
 print "       -n: Perform a DNS reverse query on all ranges discovered"
 print "       -c: Perform a DNS brute force for the domain name"
 print "       -t: Perform a DNS TLD expansion discovery"
 print "       -e: Use this DNS server"
 print "       -l: Limit the number of results to work with(bing goes from 50 to 50 results,"
 print "	   -h: use SHODAN database to query discovered hosts"
 print "            google 100 to 100, and pgp doesn't use this option)"
 print "\nExamples:./theharvester.py -d microsoft.com -l 500 -b google"
 print "         ./theharvester.py -d microsoft.com -b pgp"
 print "         ./theharvester.py -d microsoft -l 200 -b linkedin\n"


def start(argv):
	if len(sys.argv) < 4:
		usage()
		sys.exit()
	try :
	       opts, args = getopt.getopt(argv, "l:d:b:s:vf:nhcte:")
	except getopt.GetoptError:
  	     	usage()
		sys.exit()
	start=0
	host_ip=[]
	filename=""
	bingapi="yes"
	dnslookup=False
	dnsbrute=False
	dnstld=False
	shodan=False
	vhost=[]
	virtual=False
	limit = 100
	dnsserver=False
	for opt, arg in opts:
		if opt == '-l' :
			limit = int(arg)
		elif opt == '-d':
			word = arg	
		elif opt == '-s':
			start = int(arg)
		elif opt == '-v':
			virtual = "basic"
		elif opt == '-f':
			filename= arg
		elif opt == '-n':
			dnslookup=True
		elif opt == '-c':
			dnsbrute=True
		elif opt == '-h':
			shodan=True
		elif opt == '-e':
			dnsserver=arg
		elif opt == '-t':
			dnstld=True
		elif opt == '-b':
			engine = arg
			if engine not in ("google", "linkedin", "pgp", "all","google-profiles","bing","bing_api","yandex","people123","jigsaw"):
				usage()
				print "Invalid search engine, try with: bing, google, linkedin, pgp, exalead, jigsaw, bing_api, people123, google-profiles"
				sys.exit()
			else:
				pass
	if engine == "google":
		print "[-] Searching in Google:"
		search=googlesearch.search_google(word,limit,start)
		search.process()
		all_emails=search.get_emails()
		all_hosts=search.get_hostnames()
	if engine == "exalead":
		print "[-] Searching in Exalead:"
		search=exaleadsearch.search_exalead(word,limit,start)
		search.process()
		all_emails=search.get_emails()
		all_hosts=search.get_hostnames()
	elif engine == "bing" or engine =="bingapi":	
		print "[-] Searching in Bing:"
		search=bingsearch.search_bing(word,limit,start)
		if engine =="bingapi":
			bingapi="yes"
		else:
			bingapi="no"
		search.process(bingapi)
		all_emails=search.get_emails()
		all_hosts=search.get_hostnames()
	elif engine == "yandex":# Not working yet
		print "[-] Searching in Yandex:"
		search=yandexsearch.search_yandex(word,limit,start)
		search.process()
		all_emails=search.get_emails()
		all_hosts=search.get_hostnames()
	elif engine == "pgp":
		print "[-] Searching in PGP key server.."
		search=pgpsearch.search_pgp(word)
		search.process()
		all_emails=search.get_emails()
		all_hosts=search.get_hostnames()
	elif engine == "people123":
		print "[-] Searching in 123People.."
		search = people123.search_123people(word,limit)
		search.process()
		people = search.get_people()
		print "Users from 123People:"
		print "====================="
		for user in people:
			print user
		sys.exit()
	elif engine == "jigsaw":
		print "[-] Searching in Jigsaw.."
		search = jigsaw.search_jigsaw(word,limit)
		search.process()
		people = search.get_people()
		print "Users from Jigsaw:"
		print "====================="
		for user in people:
			print user
		sys.exit()


	elif engine == "linkedin":
		print "[-] Searching in Linkedin.."
		search=linkedinsearch.search_linkedin(word,limit)
		search.process()
		people=search.get_people()
		print "Users from Linkedin:"
		print "===================="
		for user in people:
			print user
		sys.exit()
	elif engine == "google-profiles":
		print "[-] Searching in Google profiles.."
		search=googlesearch.search_google(word,limit,start)
		search.process_profiles()
		people=search.get_profiles()
		print "Users from Google profiles:"
		print "---------------------------"
		for users in people:
			print users
		sys.exit()
	elif engine == "all":
		print "Full harvest.."
		all_emails=[]
		all_hosts=[]
		virtual = "basic"
		print "[-] Searching in Google.."
		search=googlesearch.search_google(word,limit,start)
		search.process()
		emails=search.get_emails()
		hosts=search.get_hostnames()
		all_emails.extend(emails)
		all_hosts.extend(hosts)
		print "[-] Searching in PGP Key server.."
		search=pgpsearch.search_pgp(word)
		search.process()
		emails=search.get_emails()
		hosts=search.get_hostnames()
		all_hosts.extend(hosts)
		all_emails.extend(emails)
		print "[-] Searching in Bing.."
		bingapi="no"
		search=bingsearch.search_bing(word,limit,start)
		search.process(bingapi)
		emails=search.get_emails()
		hosts=search.get_hostnames()
		all_hosts.extend(hosts)
		all_emails.extend(emails)
		print "[-] Searching in Exalead.."
		search=exaleadsearch.search_exalead(word,limit,start)
		search.process()
		emails=search.get_emails()
		hosts=search.get_hostnames()
		all_hosts.extend(hosts)
		all_emails.extend(emails)
	#Results############################################################
	print "\n[+] Emails found:"
	print "------------------"
	if all_emails ==[]:
		print "No emails found"
	else:
		for emails in all_emails:
			print emails 

	print "\n[+] Hosts found in search engines:"
	print "------------------------------------"
	if all_hosts == []:
		print "No hosts found"
		full=[]
	else:
		full_host=hostchecker.Checker(all_hosts)
		full=full_host.check()
		for host in full:
			ip=host.split(':')[0]
			print host
			if host_ip.count(ip.lower()):
				pass
			else:
				host_ip.append(ip.lower())
	
	#DNS reverse lookup#################################################
	dnsrev=[]
	if dnslookup==True:
		print "\n[+] Starting active queries:"
		analyzed_ranges=[]
		for x in full:
			ip=x.split(":")[0]
			range=ip.split(".")
			range[3]="0/24"
			range=string.join(range,'.')
			if not analyzed_ranges.count(range):
				print "[-]Performing reverse lookup in :" + range
				a=dnssearch.dns_reverse(range,True)
				a.list()
				res=a.process()
				analyzed_ranges.append(range)
			else:
				continue
			for x in res:
				if x.count(word):
					dnsrev.append(x)
					if x not in full:
						full.append(x)
		print "Hosts found after reverse lookup:"
		print "---------------------------------"
		for xh in dnsrev:
			print xh
	#DNS Brute force####################################################
	dnsres=[]
	if dnsbrute==True:
		print "[-] Starting DNS brute force:"
		a=dnssearch.dns_force(word,dnsserver,verbose=True)
		res=a.process()
		print "[+] Hosts found after DNS brute force:"
		for y in res:
			print y
			dnsres.append(y)
			if y not in full:
				full.append(y)
	#DNS TLD expansion###################################################
	dnstldres=[]
	if dnstld==True:
		print "[-] Starting DNS TLD expansion:"
		a=dnssearch.dns_tld(word,dnsserver,verbose=True)
		res=a.process()
		print "\n[+] Hosts found after DNS TLD expansion:"
		print "=========================================="
		for y in res:
			print y
			dnstldres.append(y)
			if y not in full:
				full.append(y)
	
	#Virtual hosts search###############################################
	if virtual == "basic":
		print "[+] Virtual hosts:"
		print "=================="
		for l in host_ip:
			search=bingsearch.search_bing(l,limit,start)
 			search.process_vhost()
 			res=search.get_allhostnames()
			for x in res:
				print l+"\t"+x
				vhost.append(l+":"+x)
				full.append(l+":"+x)
	else:
		pass
	shodanres=[]
	shodanvisited=[]
	if shodan == True:
		print "[+] Shodan Database search:"
		for x in full:
			print x
			try:
				ip=x.split(":")[0]
				if not shodanvisited.count(ip):
					print "\tSearching for: " + x 
					a=shodansearch.search_shodan(ip)
					shodanvisited.append(ip)
					results=a.run()
					for res in results:
						shodanres.append(x+"SAPO"+str(res['banner'])+"SAPO"+str(res['port']))
			except:
				pass
		print "[+] Shodan results:"
		print "==================="
		for x in shodanres:
			print x.split("SAPO")[0] +":"+ x.split("SAPO")[1]
	else:
		pass

	###################################################################
	#Here i need to add explosion mode.
	#Tengo que sacar los TLD para hacer esto.
	recursion= None	
	if recursion:
		start=0
		for word in vhost:
			search=googlesearch.search_google(word,limit,start)
			search.process()
			emails=search.get_emails()
			hosts=search.get_hostnames()
			print emails
			print hosts
	else:
		pass
	
	if filename!="":	
		try:
			print "Saving file"
			html = htmlExport.htmlExport(all_emails,full,vhost,dnsres,dnsrev,filename,word,shodanres,dnstldres)
			save = html.writehtml()
			sys.exit()
		except Exception,e:
			print e	
			print "Error creating the file"
	filename = filename.split(".")[0]+".xml"
	file = open(filename,'w')
	file.write('<theHarvester>')
	for x in all_emails:
		file.write('<email>'+x+'</email>')
	for x in all_hosts:
		file.write('<host>'+x+'</host>')
	for x in vhost:
		file.write('<vhost>'+x+'</vhost>')
	file.write('</theHarvester>')
	file.close

		
if __name__ == "__main__":
        try: start(sys.argv[1:])
	except KeyboardInterrupt:
		print "Search interrupted by user.."
	except:
		sys.exit()

