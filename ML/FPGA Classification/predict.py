import pynq.lib.dma
import pandas as pd
from pynq import allocate
from pynq import Overlay
import numpy as np


ol = Overlay("/home/xilinx/mlp_test.bit")


dma = ol.axi_dma_0


in_data = pd.read_csv("/home/xilinx/x_test.csv").to_numpy(dtype=np.float32)
in_label = pd.read_csv("/home/xilinx/y_test.csv").to_numpy(dtype=np.int64)


input_buffer = allocate(shape=(206,), dtype=np.float32)
output_buffer = allocate(shape=(1,), dtype=np.float32)
test_batch = len(in_data)
flat_data = in_data.flatten()

count = 0
result = ""




print("Start Testing")
import time
start_time = time.time()
for i in range(test_batch):
    input_buffer[:] = flat_data[i*206:206+i*206]
    dma.sendchannel.transfer(input_buffer)
    dma.recvchannel.transfer(output_buffer)
    dma.sendchannel.wait()
    dma.recvchannel.wait()
    if (in_label[i][int(output_buffer[0])] == 1):
        count += 1

    '''
    if (in_label[i][int(output_buffer[0])] == 1):
        count += 1
        passed = "Passed"
    else:
        passed = "Failed"
    '''

    expected = 0
    for t in range(4):
        if (in_label[i][t] == 1):
            expected = t

    #print("Test {0}: pred: {1}  expect: {2} --> {3}".format(i+1, int(output_buffer[0]), expected, passed))

time_taken = time.time() - start_time
print("%s seconds" % (time_taken))
print("Time Taken per input: %s ms" % ((time_taken)/test_batch*1000))

print("accuracy: " + str(count/test_batch))