import tensorflow as tf
import torch
import multiprocessing
import time

print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

for item in tf.config.list_physical_devices():
  print(item)

x = torch.rand(5, 3)
print(x)
print(torch.cuda.is_available())

def test(data, core):
  data[core] = ["teesa"]
  time.sleep(5)

procs = []
manager = multiprocessing.Manager()
dict_data = manager.dict()

for i in range(4):
  procs.append(multiprocessing.Process(target=test, args=(dict_data, i,)))
  procs[-1].start()

for i in range(4):
  procs[i].join()

print(dict_data)