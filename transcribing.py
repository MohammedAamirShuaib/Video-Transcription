from transcribe import *
from assemblyai_data_extraction import json_data_extraction
import docx
import time

def transcribe_request(token,files, dir_name, fname):
  transcription_start_time = time.time()
  log_list = open("documents/"+dir_name+".txt","a")
  status = open("documents/"+dir_name+"/status.txt","a")
  tid = upload_file(token,files)
  result = {}
  print('starting to transcribe the file: [ {} ]'.format(fname))
  while result.get("status") != 'completed':
      print(result.get("status"))
      result = get_text(token, tid)
      # Handeling Errors
      if result.get("status") == 'error':
          log_list.write("Error occured while transcribing the file :&nbsp;&nbsp;"+fname+"<br>")
          status.write("<img src='/static/error.jpg' height='20'>&nbsp;&nbsp;Error &nbsp;:&nbsp;"+fname+"<br><br>")

  transcription_finish_time = time.time()
  transcribe_time= str(round(transcription_finish_time-transcription_start_time,2))
  log_list.write(fname+"&nbsp; :&nbsp;&nbsp; transcription complete in "+transcribe_time+"<br><br>")
  df = json_data_extraction(result,fname)
  print('saving transcript...')
  df = df[['spcode','utter']]
  print('Converting files')
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
  doc.save("documents/"+dir_name+"/"+fname+".docx")
  log_list.close()
  status.write("<img src='/static/success.jpg' height='20'>&nbsp;&nbsp;Completed &nbsp;:&nbsp;"+fname+"<br><br>")
  status.close()