import pathlib
from classes.Config import DowConfig
from classes.Database import DowDatabase

config = DowConfig(pathlib.Path(".").joinpath("config.json"))
db = DowDatabase(config.ROOT_DIR, config.DB_NAME)

sql = "UPDATE files SET features = 'no'"
db.Execute(sql)
print("Done")