#import libraries
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
from flask import Flask,render_template, request, jsonify
from flask_cors import CORS,cross_origin
from selenium import webdriver
import requests
import json
import smtplib
import jinja2
import fpdf
import logging


#creating the lists
course_list=[]
main_course_keys=[]
final_details=[]

#Open text file to enter the course detaisl in delimited format
#initialize text file object
textfile = open("course_details.txt", "w")
#Giving a header to the txt file
line = 'Main_Course|Sub_Course|Training|Description|Mentors' 
textfile.writelines(line+"\n")
#initialize logging
logging.basicConfig(filename="scrapper.log", format='%(asctime)s %(message)s', filemode='w', level=logging.DEBUG)

#initiate a flask application
application=Flask(__name__)


#routing to the home page
@application.route('/')
def welcome():
	return render_template("index.html")


@application.route('/courses',methods=['POST'])
#Once the iNeuron course button is submitted in web page this function will be called
#This function will find the main course lists and calls sub_courses function
def main_course():
 try:
   url = 'https://ineuron.ai/'
   uclient = uReq(url)
   iNeuron_page = uclient.read()
   uclient.close()
   iNeuron_beautify=bs(iNeuron_page,"html.parser")
   main_page_info=json.loads(iNeuron_beautify.find('script',{"id": "__NEXT_DATA__"}).get_text())
   main_course_keys=list(main_page_info['props']['pageProps']['initialState']['init']['categories'].keys())
   #sub_courses(url,main_page_info,list([main_course_keys[0]]))
   sub_courses(url,main_page_info,main_course_keys)
   pdf_writer(final_details)
   return render_template("results.html", len = len(final_details), d2 = final_details)
 except:
  logging.error(f'Unable to open url and fetch the details,{url}')

#This function will fetch the details of main course name and sub course_keys
def sub_courses(url,main_page_info,main_course_keys):
  try:  
    for i in main_course_keys:
        main_course_name=main_page_info['props']['pageProps']['initialState']['init']['categories'][str(i)]['title']
        sub_course_key=list(main_page_info['props']['pageProps']['initialState']['init']['categories'][str(i)]['subCategories'])
        training(url,main_page_info,main_course_name,i,sub_course_key)
    return 
  except:
    logging.error(f'error occured at fetching sub_course deatils. Function sub_courses. main_course_name:{main_course_name}')
#This function will fetch the details of sub course name and the rainining url to navigate through
def training(url,main_page_info,main_course_name,i,sub_course_key):
 try: 
    for m in sub_course_key:
            sub_course_name=main_page_info['props']['pageProps']['initialState']['init']['categories'][str(i)]['subCategories'][str(m)]['title']
            sub_course_name_url=str(sub_course_name).replace(" ","-")
            sub_course_url=url+'category/'+str(sub_course_name_url)
            training_url(sub_course_url,main_course_name,sub_course_name)
    return print(f'The details of the main course {main_course_name} are fetched')
 except:
    logging.error('error at fetching training details, function name: sub_course_name:{sub_course_name}')
#This function will fectch training keys under sub_course of a main course
def training_url(sub_course_url,main_course_name,sub_course_name):
  try:
    training_uclient = uReq(str(sub_course_url))
    training_page = training_uclient.read()
    training_uclient.close()
    training_beautify=bs(training_page,"html.parser")
    training_info_json=json.loads(training_beautify.find('script',{"id": "__NEXT_DATA__"}).get_text())
    training_keys=list(training_info_json['props']['pageProps']['initialState']['filter']['initCourses'])
    training_details(training_info_json,training_keys,main_course_name,sub_course_name)
    return
  except:
    logging.error(f'unable to open training_url, training_url:{sub_course_url}')

#This function will fetch all the details of a Training under sub_course of a main_course
def training_details(training_info_json,training_keys,main_course_name,sub_course_name):
  try:
    number_of_trainings=len(training_keys)
    for q in range(number_of_trainings):
       training_name=training_info_json['props']['pageProps']['initialState']['filter']['initCourses'][q]['title']
       training_description=training_info_json['props']['pageProps']['initialState']['filter']['initCourses'][q]['description']
       number_of_mentors=len(training_info_json['props']['pageProps']['initialState']['filter']['initCourses'][q]['instructorsDetails'])
       mentor_details(training_info_json,q,number_of_mentors,main_course_name,sub_course_name,training_name,training_description)
    return 
  except:
    logging.error(f'error in fetching the training details : {training_name}')

#This function will fetch the mentor names of every training
def mentor_details(training_info_json,q,number_of_mentors,main_course_name,sub_course_name,training_name,training_description):
  try :
    mentor_name=str()
    for l in range(number_of_mentors):
        mentor_name1=training_info_json['props']['pageProps']['initialState']['filter']['initCourses'][q]['instructorsDetails'][l]['name']
        mentor_name=mentor_name1+', '+mentor_name
    mentor_names=mentor_name[:-2]
    final_details.append([main_course_name,sub_course_name,training_name,training_description,mentor_names])
    line_str=main_course_name+'|'+sub_course_name+'|'+training_name+'|'+training_description+'|'+mentor_names
    textfile.writelines(line_str+"\n")
    return 
  except:
    logging.error(f'error in fetching the mentor details of the training {training_name}')

def pdf_writer(final_details):
  try:
    pdf = fpdf.FPDF(format='letter')
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for i in range(len(final_details)):
        try:
          pdf.cell(200, 10, final_details[i][0],ln=1, align = 'l')
          pdf.cell(200, 10, final_details[i][1],ln=1, align = 'l')
          pdf.cell(200, 10, final_details[i][2],ln=1, align = 'l')
          #pdf.cell(200, 10, final_details[i][3],ln=1, align = 'l')
          pdf.cell(200, 10, final_details[i][4],ln=1, align = 'l')
          pdf.ln()
        except:
            pass
    return pdf.output("course_details.pdf")
  except:
    logging.error("pdf writer error occured")

#create a main to connect to the host
if __name__=="__main__":
	application.run(host="0.0.0.0",port=5000)
