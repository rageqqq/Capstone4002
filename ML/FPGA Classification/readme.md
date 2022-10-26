To use the run python scripts that utilize PYNQ Overlays run the following code:

```
sudo -s
export XILINX_XRT=/usr
```

Run the python script using python [script name].py

Files:<br />
activity_detect.py - Action detection & fifo sliding window script<br />
features.py - Feature extraction script<br />
main_simulated.py - Simulated action sequence implementing FPGA classificationa and action detection<br />
main.py - FPGA classificationa and action detection test script<br />
overlay.py - PYNQ overlay functions script<br />
predict.py - Classification & benchmarking test based on WISDM dataset<br />
simple_bench.py - Classification & benchmarking test based on Chester dataset<br />
