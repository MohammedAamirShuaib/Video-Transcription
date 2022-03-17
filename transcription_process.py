def tanscribing_files(files, dir_name, start_time):
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
      s3.upload_file("documents/"+dir_name+".txt","video-transcription-file-sharing","logs/"+dir_name+".txt")
      os.remove("documents/"+dir_name+".txt")

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
        s3.upload_file("documents/"+dir_name+".zip","video-transcription-file-sharing","transcriptions/"+dir_name+".zip")
        s3.upload_file("documents/"+dir_name+".txt","video-transcription-file-sharing","logs/"+dir_name+".txt")
        os.remove("documents/"+dir_name+".zip")
        os.remove("documents/"+dir_name+".txt")
        shutil.rmtree("documents/"+dir_name)

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
  s3.upload_file("documents/"+dir_name+".zip","video-transcription-file-sharing","transcriptions/"+dir_name+".zip")
  s3.upload_file("documents/"+dir_name+".txt","video-transcription-file-sharing","logs/"+dir_name+".txt")
  os.remove("documents/"+dir_name+".zip")
  os.remove("documents/"+dir_name+".txt")
  shutil.rmtree("documents/"+dir_name)
  print("Process Completed!")