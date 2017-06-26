# 22/11/2016
# OS Trunk Check v2.2
# Danyal Butt - DRB Dev
# drbdev.com


import requests
import smtplib
import ctypes
import datetime
import string
import time
import os
from lxml import html
from sys import argv
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText



has_run = False
trunk_status = False
mins = 0


def timer():
	global mins

	while mins != 5:
		print ">>>>>>>>>>>>>>>", mins
		time.sleep(60)
		mins += 1

		if mins == 5:
			getData()



def getData():
 
	payload = {
	          'username': 'user',
	          'password': 'password'
	}

	session_request = requests.session()

	login_url = "http://****:********@192.168.0.10/admin/config.php#"
	result = session_request.get(login_url)

	tree = html.fromstring(result.text)

	result = session_request.post(
		login_url, 
		data = payload, 
		headers = dict(referer=login_url)
	)


	url = "http://****:********@192.168.0.10/admin/config.php?&type=tool&display=asteriskinfo&extdisplay=registries"

	result = session_request.get(
		
			url,
			headers = dict(referer = url)

	)

	tree = html.fromstring(result.content)
	data = tree.xpath('.//pre/text()')[0]

	f = open("data.txt", "a")
	f.truncate()
	f.write(data)
	f.close()



	checkData()



def checkData():

	global has_run
	global trunk_status

	if has_run == False:
		has_run = True
		getData()
	else:
		data_array = []
		trunk_array = []

		with open('data.txt') as my_file:
			data_array = my_file.readlines()

		sip = [s for s in data_array if "sip" in s]

		for i in range(len(sip)):
			if "Registered" in sip[i]:
				trunk_array.append(sip[i])
			else:
				trunk_status = True
				trunk_array.append(sip[i])

		sendEmail(trunk_array)

				


def sendEmail(message):

	global trunk_status
	global mins
	now = datetime.datetime.now()

	fp =  "\n".join(message)


	if trunk_status == False:
		subject = "SIP Trunks OK " + now.strftime("%d-%m-%Y %H:%M")
		body = "All SIP trunks are connected and online\n\n\n"
		toaddr = "Trunk.testing@offshore-shipbrokers.co.uk"
	else:
		subject = "SIP Trunks ALERT " + now.strftime("%d-%m-%Y %H:%M")
		body = "One or more of the SIP trunks shown below are offline. Please check.\n\n\n"
		toaddr = ["Trunk.testing@offshore-shipbrokers.co.uk", "Osl.alerts@hotmail.co.uk", "447837680150@textmagic.com"]

	fromaddr = "trunkwarning@gmail.com"
	password = "password"
	

	msg = MIMEMultipart('alternative')
	msg['Subject'] = subject
	msg['From'] = fromaddr
	if trunk_status == False:
		msg['To'] = toaddr
	else:
		msg['To'] = ", ".join(toaddr)

	part1 = MIMEText(body + fp)

	msg.attach(part1)

	f = open("log.txt", "a")
	f.write(str(now.strftime("%d-%m-%Y %H:%M")) + "\n\n" + part1.as_string() + "\n\n")
	f.close()


	s = smtplib.SMTP_SSL('smtp.gmail.com:465')
	s.ehlo()
	s.login(fromaddr, password)

	s.sendmail(fromaddr, toaddr, msg.as_string())
	s.quit()
	mins = 0
	trunk_status = False
	timer()


getData()


