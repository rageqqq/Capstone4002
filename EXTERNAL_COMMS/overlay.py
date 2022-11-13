import pynq.lib.dma
import pandas as pd
from pynq import allocate
from pynq import Overlay
import numpy as np
from features import extract_features, extract_features_v2, extract_features_v3
import statistics



class fpga:
  """Instantiates PYNQ overlay for classification

    fpga class initialises the PYNQ Overlay for the ULTRA96 V2 and the DMA objects for memory access.

    Attributes:
        ol: Initialises the PYNQ overlay contained in the specified .bit file.
        dma: Initialises the DMA object for memory access.
        input_buffer: array of values to be classified of shape (432,).
        output_buffer: array of classified output values of shape(1,).
  """
  def __init__(self, overlay, input_shape):
    self.ol = Overlay(overlay)
    self.input_shape = input_shape
    self.dma = self.ol.axi_dma_0
    self.input_buffer = allocate(shape=(input_shape,), dtype=np.float32)
    self.output_buffer = allocate(shape=(1,), dtype=np.float32)

  def classify(self, data):
    """Classifies input data.

        Classifies the extracted feature array of shape (432,) using the configured FPGA overlay.
        Returns an integer value corresponding to the respective actions
        0 - Grenade
        1 - Quit
        2 - Reload
        3 - Shield

        Args:
            data (list): Extracted time serires data from sliding window (432,)
        Returns:
            int: integer value corresponding to the respective actions

        """
    features = []
    #features = extract_features(data)
    if self.input_shape == 432:
      features = extract_features(data)
    elif self.input_shape == 192:
      features = extract_features_v2(data)
    elif self.input_shape == 372:
      features = extract_features_v3(data)
    # elif self.input_shape == 132:
    #   features = extract_features_v2(data)
    self.input_buffer[:] = features
    self.dma.sendchannel.transfer(self.input_buffer)
    self.dma.recvchannel.transfer(self.output_buffer)
    self.dma.sendchannel.wait()
    self.dma.recvchannel.wait()

    return int(self.output_buffer[0])

  def classify_v2(self, tup_5):
    classifications = []
    for i in range(len(tup_5)):
      classifications.append(self.classify(tup_5[i]))
    return statistics.mode(classifications)


