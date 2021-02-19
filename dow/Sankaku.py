import requests
import time
import os
import sys
import AdvancedHTMLParser

class DowSankaku():
  __url = "https://chan.sankakucomplex.com"
  __http_headers = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 Edg/84.0.522.40"
  __is_connected = False
  __page = 1
  __page_data = ""
  __files = []

  def __init__(self, user, passwd, download_dir, sort_tag):
    self.__user = user
    self.__sort_tag = sort_tag
    self.__passwd = passwd
    self.__download_dir = download_dir
    self.__values = {
        'url': "/user/home",
        'user[name]': self.__user,
        'user[password]': self.__passwd,
        'commit': "Login"
    }
    os.makedirs(self.__download_dir, exist_ok=True)
    self.__conn = requests.Session()
    self.__conn.headers['User-Agent'] = self.__http_headers
    response = self.__get_request('/user/login')
    response = self.__conn.post(self.__url + '/user/authenticate', data=self.__values)
    self.__is_connected = "My Account" in response.text
    self.__parser = AdvancedHTMLParser.AdvancedHTMLParser()
  
  def IsConnected(self):
    return self.__is_connected
  
  def __get_request(self, uri):
    text = self.__url + uri
    resp = ""
    try:
      resp = self.__conn.get(text, stream=False)
      while resp.status_code == 500 or resp.status_code == 429:
        print("Wait 500 or 429")
        time.sleep(120)
        resp = self.__conn.get(text, stream=False)
    except:
      print("Send Request Error")
    return resp

  def __download_request(self, uri):
    text = "https:" + uri
    resp = ""
    try:
      resp = self.__conn.get(text, stream=True)
      while resp.status_code == 500 or resp.status_code == 429:
        print("Wait 500 or 429")
        time.sleep(120)
        resp = self.__conn.get(text, stream=True)
    except:
      print("Send Request Error")
    return resp

  def __load_next_page(self):
    self.__page_data = self.__get_request("/?tags=fav" + "%3A" + self.__sort_tag + "&" + "page=%s" % str(self.__page))
    if self.__page_data.status_code != 200:
      self.__page_data = ""
    else:
      self.__parser.parseStr(self.__page_data.text)
      self.__files = []
      spans = self.__parser.getElementsByTagName('span').getElementsByClassName('thumb')
      for sp in spans:
        item = sp[0][0]
        if 'plus' in sp[0].href:
          continue
        self.__files.append([sp[0].href, 
                            [str(item.src).split("/")[-1]], 
                            " ".join(str(item.title).replace("'", "''").split(" ")[:-4])])

    if len(self.__files) == 0:
      print("no data")
      self.__page_data = ""
    if self.__page_data != "":
      print("Page: %i" % self.__page)
      self.__page += 1

  def GetNextPage(self):
    self.__load_next_page()
    if self.__page_data != "":
      return True
    else:
      return False

  def GetFilesLen(self):
    return len(self.__files)

  def GetFile(self, index): # url, list of names, tags
    if self.__page_data != "" and len(self.__files) > index:
      return self.__files[index]
    else:
      return None

  def DownloadFile(self, file):
    resp = self.__get_request(file[0])
    ps = AdvancedHTMLParser.AdvancedHTMLParser()
    ps.parseStr(resp.text)
    link = ps.getElementsByTagName('a').getElementById('highres')
    name = os.path.join(self.__download_dir, file[1][0])
    data = self.__download_request(link.href)
    if data.status_code == 200:
      open(name, "bw").write(data.content)
      print("Download file:%s" % name)
      return True
    else:
      return False
