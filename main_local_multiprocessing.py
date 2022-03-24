import multiprocessing
from transcribe import *
from assemblyai_data_extraction import json_data_extraction
from transcribing import *
from os import access
import os
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import base64
import shutil
import sys
from datetime import datetime
import time
import requests
from typing import List
import uuid
from html_content import *
import boto3

app = FastAPI()

# Global variables
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
s3 = boto3.client('s3', aws_access_key_id="AKIAWFPZMNZHUGEYWIIS", aws_secret_access_key="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", region_name='us-east-1')

@app.get('/', response_class=HTMLResponse)
async def file_temp(request: Request):
  dir_name = str(uuid.uuid4())
  return templates.TemplateResponse("webpage.html", {'request': request , 'dir_name': dir_name,"start_time": str(time.time())})

@app.post("/{start_time}/{dir_name}/", response_class=HTMLResponse)
async def create_upload_files(*,files: List[UploadFile] = File(...), request: Request,dir_name,start_time):
  log_list = ""
  log_list+="Please find the logs for your transcription below:<br><br>"
  log_list+="Start_time:&nbsp;"+datetime.now().strftime("%I:%M:%S")+"<br><br>"

  for file in files:
    if file.filename == "":
      wc = "No Files Uploaded"
      log_list+="No files were uploaded"
      logs_text = open("documents/"+dir_name+".txt","w+")
      logs_text.write(log_list)
      logs_text.close()
      s3.upload_file("documents/"+dir_name+".txt","transcription-documents","logs/"+dir_name+".txt")
      os.remove("documents/"+dir_name+".txt")
      return HTMLResponse(content=html_page_download(wc,dir_name), status_code=200)

  os.makedirs("documents/"+dir_name, exist_ok=True)
  log_list+="Files Uploaded: <br>"

  for i in files:
    log_list+=i.filename+"<br>"

  upload_finish_time= round(time.time(),2)
  upload_time = str(round(upload_finish_time - float(start_time),2))
  status = open("documents/"+dir_name+"/status.txt","w+")
  status.close()
  log_list+="<br>Time took to upload files to Ec2:&nbsp;&nbsp;"+upload_time+"<br><br>"
  logs_text = open("documents/"+dir_name+".txt","w+")
  logs_text.write(log_list)
  logs_text.close()
  process = []
  a=1
  for file in files:
    if a%6==1:
      token = "c5df2367fcdc47ae9d8a68b5e9b1a62e"
    if a%6==2:
      token = "a788369fef274a0393624e2fc7a9a70a"
    if a%6==3:
      token = "a2b89c113dc54485abe2692fc8e9ab30"
    if a%6==4:
      token = "d3b6f15c585b4a1bbf43f20f60535185"
    if a%6==5:
      token = "10c3286baa1e4429b0095eabd6480582"
    if a%6==6:
      token = "d807c86bec5e4c80b9460472524189ec"
    fname = file.filename
    avfile = file.file
    p1 = multiprocessing.Process(target=transcribe_request, args=[token, avfile, dir_name,fname])
    p1.start()
    process.append(p1)
    a=a+1

  for p in process:
    p.join()

  shutil.make_archive("documents/"+dir_name,"zip","documents/"+dir_name)
  process_finish_time= round(time.time(),2)
  complete_time = str(round(process_finish_time - float(start_time),2))
  log_list = open("documents/"+dir_name+".txt","a")
  log_list.write("completed transcription in :&nbsp;&nbsp;  "+complete_time+"<br><br>")
  log_list.close()
  s3.upload_file("documents/"+dir_name+".zip","transcription-documents","transcriptions/"+dir_name+".zip")
  s3.upload_file("documents/"+dir_name+".txt","transcription-documents","logs/"+dir_name+".txt")
  with open("documents/"+dir_name+"/status.txt") as f:
    wc_doc = f.readlines()
    wc_doc = wc_doc[0]
  os.remove("documents/"+dir_name+".zip")
  os.remove("documents/"+dir_name+".txt")
  shutil.rmtree("documents/"+dir_name)
  return HTMLResponse(content=html_page_download(wc_doc,dir_name), status_code=200)

@app.get('/download/{dir_name}/')
async def download(dir_name):
  zip_url = s3.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': 'transcription-documents', 'Key': "transcriptions/"+dir_name+".zip"},ExpiresIn=43200)
  return RedirectResponse(zip_url)

@app.get('/logs/{dir_name}/')
async def logs(dir_name):
  logobj = s3.get_object(Bucket = "transcription-documents", Key = "logs/"+dir_name+".txt")
  log_content = logobj["Body"].read().decode("utf-8")
  return HTMLResponse(content=html_page_logs(log_content), status_code=200)