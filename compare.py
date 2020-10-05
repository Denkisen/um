import os
import json

INPUT = ""

f = open("config.json", "r")
conf = json.load(f)
INPUT = os.path.join(conf["DB_PATH"], conf["DUPS"])
f.close()

files = open(INPUT, "r")

for file in files:
  first, second = file.split(" | ", 2)
  if os.path.exists(first) and os.path.exists(second[:-1]):
    os.system("gwenview \"%s\" | gwenview \"%s\"" % (first, second[:-1]))
files.close()