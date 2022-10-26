from asyncio.windows_events import NULL
from overlay import fpga
from features import extract_features
from activity_detect import activity

classifier = fpga( "/home/xilinx/mlp_test.bit",432 )

reading_buffer = activity()

input_data = [1,2,3,4,5,6]

data = activity.update(input_data)
if data != None:
    data = extract_features(data)
    action = classifier.classify(data)

