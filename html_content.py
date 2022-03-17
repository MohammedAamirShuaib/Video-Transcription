import webbrowser

def html_page_download(content,dir_name):
  html_content_download=f"<!DOCTYPE html><html lang='en'><head><link rel='stylesheet' href='/static/completed.css'><title>OSG - Video Transcription Tool</title></head><meta charset='utf-8'><body><div class='logo'><img src='/static/osg_logo.jpg' height='50'></div><br><h3>Transcription Status:</h3><br><p><div class='content' align='center'>{content}</div></p><p><div align ='center'><a href='/download/{dir_name}/' download class='download-btn'>Download Transcribed Documents</a><br/><a href='/logs/{dir_name}/' class='logs-btn'>Logs</a><a href='/' class='homepage'>Back to homepage</a><br></div></p></body></html>"

  return html_content_download


def html_page_logs(content):
  html_content_logs=f"<!DOCTYPE html><html lang='en'><head><link rel='stylesheet' href='/static/logs.css'><title>OSG - Video Transcription Tool</title></head><meta charset='utf-8'><body><div class='logo'><br/><img src='/static/osg_logo.jpg' height='50'></div><p>{content} <br><br><a href='/' class='homepage'>Back to homepage</a></p></body></html>"

  return html_content_logs

def html_background(content):
  html_content_background=f"<!DOCTYPE html><html lang='en'><head><link rel='stylesheet' href='/static/logs.css'><title>OSG - Video Transcription Tool</title></head><meta charset='utf-8'><body><div class='logo'><br/><img src='/static/osg_logo.jpg' height='50'></div><p>{content} <br><br><a href='/' class='homepage'>Back to homepage</a></p></body></html>"

  return html_content_background