from pixivapi import Size
from pixivapi import Client
from pixivapi import errors
import pathlib
import time

class DowPixiv():
  __page_data = ""
  __files = []
  name = "Pixiv"
  def __init__(self, download_dir, token):
    self.__download_dir = download_dir
    self.__token = token
    if not self.__authenticate():
      raise errors.LoginError()

    pathlib.Path(self.__download_dir).mkdir(parents=True, exist_ok=True)
    self.__download_dir = pathlib.Path(self.__download_dir)

  def __authenticate(self):
    it = 0
    while it < 20:
      try:
        self.__client = Client()
        self.__client.authenticate(self.__token)
        return True
      except:
        print("Auth failed. Retry...")
      
      it += 1
      time.sleep(5)

    return False
  
  def __load_page(self):
    if self.__page_data == "":
      self.__page_data = self.__client.fetch_user_bookmarks(self.__client.account.id)
    else:
      try:
        self.__page_data = self.__client.fetch_user_bookmarks(self.__client.account.id, max_bookmark_id=int (self.__page_data['next']))
      except errors.BadApiResponse:
        print("errors.BadApiResponse: trying to recover")
        if not self.__authenticate():
          self.__page_data = {
            'next': None
          }
          return

    
    self.__files = []
    for ill in self.__page_data['illustrations']:
      tags = str(ill.user.name).replace("'","''").replace(' ', '_')
      tags += " " + str(ill.user.account).replace("'","''").replace(' ', '_')
      for tag in ill.tags:
        if tag['translated_name'] is not None:
          tags += " " + str (tag['translated_name']).replace(' ', '_').replace("'", "''")

      file_name = []
      if ill.page_count == 1:
        ec = str (ill.image_urls[Size.ORIGINAL]).split('/')[-1].split(".")[-1]
        file_name.append(str (ill.image_urls[Size.ORIGINAL]).split('/')[-1].split("_")[0] + "." + ec)

      for p in ill.meta_pages:
        name = str (p[Size.ORIGINAL]).split('/')[-1]
        file_name.append(name)
      
      self.__files.append([ill, file_name, tags])

  def __download_request(self, ill):
    ill.download(directory=self.__download_dir, size=Size.ORIGINAL)

  def GetFilesLen(self):
    return len(self.__files)
  
  def GetNextPage(self):
    self.__load_page()
    return self.__page_data['next'] is not None

  def DownloadFile(self, file):
    ill = file[0]
    print("Download File: %d" % ill.id)
    self.__download_request(ill)
    result = True
    for s in file[1]:
      dow_dir = pathlib.Path(self.__download_dir)
      if len (file[1]) > 1:
        dow_dir = dow_dir.joinpath(str (ill.id))

      if not dow_dir.joinpath(s).exists():
        result = False
        break
    return result

  def GetFile(self, index):  # url, list of names, tags
    if index > len(self.__files):
      return None
    else:
      return self.__files[index]
  
  def GetShortFileName(self, file):
    return str (file[0].id)
