from transcribe import *
from assemblyai_data_extraction import json_data_extraction
import docx
import time

def transcribe_request(token,files, dir_name, log_list, wc):
  for file in files:
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
            wc.append("<img src='/static/error.jpg' height='20'>&nbsp;&nbsp;Error &nbsp;:&nbsp;"+fname+"<br><br>")
            return wc

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
      wc.append("<img src='/static/success.jpg' height='20'>&nbsp;&nbsp;Completed &nbsp;:&nbsp;"+fname+"<br><br>")