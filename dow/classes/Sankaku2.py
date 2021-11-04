import requests
import time
import pathlib

class DowSankaku():
  __url = "https://chan.sankakucomplex.com"
  __http_headers = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 Edg/84.0.522.40"
  __is_connected = False
  __search_tags = ""
  __page = 1
  __files = []
  name = "Sankaku"

  def __init__(self, user, passwd, download_dir, tags):
    self.__conn = requests.Session()
    self.__search_tags = tags
    self.__download_dir = pathlib.Path(download_dir)
    self.__download_dir.mkdir(parents=True, exist_ok=True)
    self.__conn.headers['User-Agent'] = self.__http_headers
    self.__values = {
        'url': "/user/home",
        'user[name]': user,
        'user[password]': passwd,
        'commit': "Login"
    }
    response = self.__get_request('/user/login')
    response = self.__conn.post(self.__url + '/user/authenticate', data=self.__values)
    self.__is_connected = "My Account" in response.text

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
    resp = self.__get_request(f"/?tags={self.__search_tags}&page={self.__page}")
    self.__files = []
    if resp.status_code == 200:
      for line in resp.text.split("\n"):
        if "thumb blacklisted" in line:
          #url, name, tags, mini
          spt = str(line).split('"')
          self.__files.append([spt[3], 
                              [spt[9].split("/")[-1]], 
                              " ".join(spt[11].replace("'", "''").split(" ")[:-4]),
                              spt[9]])
    
    print("Page" + str(self.__page))
    self.__page += 1

  def __load_image_page(self, file):
    resp = self.__get_request(file[0])
    if resp.status_code == 200:
      begin = str(resp.text).find("<div id=stats>")
      end = str(resp.text).find("</div>", begin)
      block = str(resp.text)[begin:end]
      lines = block.split("\n")
      url = ""
      for line in lines:
        name = file[1][0].split(".")[0]
        if "highres" in line and name in line:
          url = line.split('"')[1].replace("amp;", "")
          ext = url.split(".")[-1].split("?")[0]
          file[1][0] = name + "." + ext
          file.append(url)
          break
      return file
  
  def GetNextPage(self):
    self.__load_next_page()
    return True if len(self.__files) > 0 else False

  def GetFilesLen(self):
    return len(self.__files)

  def GetFile(self, index): # url, list of names, tags
    if len(self.__files) > index:
      self.__files[index] = self.__load_image_page(self.__files[index])
      return self.__files[index]
    else:
      return None

  def DownloadFile(self, file):
    name = pathlib.Path(self.__download_dir).joinpath(file[1][0])
    data = self.__download_request(file[4])
    if type(data) != str and data.status_code == 200:
      name.open("bw").write(data.content)
      print("Download file:%s" % name)
      return True
    else:
      return False

  def GetShortFileName(self, file):
    return str(file[1][0].split(".")[0])

  def DeleteBookmark(self, file):
    id_ = str(file[0]).split("/")[-1]
    print(f"Delete bookmark {id_}")
    values = {
      "id" : int(id_)
    }
    response = self.__conn.post(self.__url + "/favorite/destroy.json", data=values)

if __name__ == '__main__':
  pass
