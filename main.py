from os import access
import os
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import base64
import docx
import shutil
import sys
from datetime import datetime
import time
import requests
from transcribe import *
from assemblyai_data_extraction import json_data_extraction
from typing import List
import uuid
from html_content import *
import boto3

app = FastAPI()

# Global variables
access_id = os.environ['access_id']
secret_id = os.environ['secret_id']
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
s3 = boto3.client('s3', aws_access_key_id=access_id, aws_secret_access_key=secret_id, region_name='us-east-1')

@app.get('/', response_class=HTMLResponse)
async def file_temp(request: Request):
  dir_name = str(uuid.uuid4())
  return templates.TemplateResponse("webpage.html", {'request': request , 'dir_name': dir_name, "start_time": str(time.time())})

@app.post("/{start_time}/{dir_name}/", response_class=HTMLResponse)
async def create_upload_files(*,files: List[UploadFile] = File(...), request: Request,dir_name,start_time):
  log_list = []
  log_list.append("Start_time:&nbsp;"+datetime.now().strftime("%I:%M:%S")+"<br>")

  for file in files:
    if file.filename == "":
      wc = "No Files Uploaded"
      log_list.append("No files were uploaded")
      logs= "".join(log_list)
      logs_text = open("documents/"+dir_name+".txt","w+")
      logs_text.write(logs)
      logs_text.close()
      s3.upload_file("documents/"+dir_name+".txt","transcription-documents","logs/"+dir_name+".txt")
      os.remove("documents/"+dir_name+".txt")
      return HTMLResponse(content=html_page_download(wc,dir_name), status_code=200)

  os.makedirs("documents/"+dir_name, exist_ok=True)
  wc = ""

  log_list.append("Please find the logs for your transcription below:<br><br>")
  log_list.append("Files Uploaded: <br>")

  for i in files:
    log_list.append(i.filename+"<br>")
  
  log_list.append("<br><br>")
  upload_finish_time= round(time.time(),2)
  upload_time = str(round(upload_finish_time - float(start_time),2))
  log_list.append("Time took to upload files to Ec2:&nbsp;&nbsp;"+upload_time+"<br><br>")
  for file in files:
    token = "d3b6f15c585b4a1bbf43f20f60535185"
    fname = file.filename
    transcription_start_time = time.time()
    tid = upload_file(token,file.file)
    result = {}
    log_list.append("starting to transcribe the file: &nbsp;&nbsp;"+fname+"<br>")
    print('starting to transcribe the file: [ {} ]'.format(fname))
    while result.get("status") != 'completed':
        print(result.get("status"))
        result = get_text(token, tid)
        # Handeling Errors
        if result.get("status") == 'error':
          log_list.append("Error occured while transcribing the file :&nbsp;&nbsp;"+fname+"<br>")
          wc = wc+"<img src='/static/error.jpg' height='20'>&nbsp;&nbsp;Error &nbsp;:&nbsp;"+fname+"<br><br>"
          shutil.make_archive("documents/"+dir_name,"zip","documents/"+dir_name)
          logs= "".join(log_list)
          logs_text = open("documents/"+dir_name+".txt","w+")
          logs_text.write(logs)
          logs_text.close()
          s3.upload_file("documents/"+dir_name+".zip","transcription-documents","transcriptions/"+dir_name+".zip")
          s3.upload_file("documents/"+dir_name+".txt","transcription-documents","logs/"+dir_name+".txt")
          os.remove("documents/"+dir_name+".zip")
          os.remove("documents/"+dir_name+".txt")
          shutil.rmtree("documents/"+dir_name)
          return HTMLResponse(content=html_page_download(wc,dir_name), status_code=200)

    transcription_finish_time = time.time()
    transcribe_time= str(round(transcription_finish_time-transcription_start_time,2))
    log_list.append("Transcription Completed for the file:&nbsp;&nbsp;"+fname+"&nbsp; in "+transcribe_time+"<br>")

    df = json_data_extraction(result,fname)
    print('saving transcript...')
    log_list.append("Saving the transcription of the file :&nbsp;&nbsp;"+fname+"<br>")

    df = df[['spcode','utter']]

    print('Converting files')
    log_list.append("Converting into document file:&nbsp;&nbsp;"+fname+"<br>")

    # open an existing document
    doc = docx.Document()

    t = doc.add_table(df.shape[0]+1, df.shape[1])

    # add the header rows.
    for j in range(df.shape[-1]):
        t.cell(0,j).text = df.columns[j]

    # add the rest of the data frame
    for i in range(df.shape[0]):
        for j in range(df.shape[-1]):
            t.cell(i+1,j).text = str(df.values[i,j])

    print('saving transcript...')
    log_list.append("Saving the document file:&nbsp;&nbsp;"+fname+"<br><br><br>")
    doc.save("documents/"+dir_name+"/"+fname+".docx")
    wc = wc+"<img src='/static/success.jpg' height='20'>&nbsp;&nbsp;Completed &nbsp;:&nbsp;"+fname+"<br><br>"

  log_list.append("Zipping all the transcribed documents and preparing to download")
  shutil.make_archive("documents/"+dir_name,"zip","documents/"+dir_name)
  logs= "".join(log_list)
  logs_text = open("documents/"+dir_name+".txt","w+")
  logs_text.write(logs)
  logs_text.close()
  s3.upload_file("documents/"+dir_name+".zip","transcription-documents","transcriptions/"+dir_name+".zip")
  s3.upload_file("documents/"+dir_name+".txt","transcription-documents","logs/"+dir_name+".txt")
  os.remove("documents/"+dir_name+".zip")
  os.remove("documents/"+dir_name+".txt")
  shutil.rmtree("documents/"+dir_name)
  return HTMLResponse(content=html_page_download(wc,dir_name), status_code=200)

@app.get('/download/{dir_name}/')
async def download(dir_name):
  zip_url = s3.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': 'transcription-documents', 'Key': "transcriptions/"+dir_name+".zip"},ExpiresIn=43200)
  return RedirectResponse(zip_url)

@app.get('/logs/{dir_name}/')
async def logs(dir_name):
  logobj = s3.get_object(Bucket = "transcription-documents", Key = "logs/"+dir_name+".txt")
  log_content = logobj["Body"].read().decode("utf-8")
  return HTMLResponse(content=html_page_logs(log_content), status_code=200)