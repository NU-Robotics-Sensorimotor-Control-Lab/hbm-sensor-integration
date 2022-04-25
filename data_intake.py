from random import sample
import nidaqmx as daq
from nidaqmx.constants import READ_ALL_AVAILABLE, AcquisitionType
import time
import warnings
from multiprocessing import Queue

import clr
import sys
from System import *

sys.path.insert(1,"C:\Program Files (x86)\HBM\QuantumX API 4\DLLs")

# import HBM Common API 
clr.AddReference("HBM.QuantumX")
from HBM.QuantumX import QXSystem
from HBM.QuantumX import QXSimpleDAQ
from HBM.QuantumX import eDAQValueState

def Scan():
    result = QXSystem.ScanForQXDevices()
    if result: 
        result_str = ''
        result_str = str(result[0])
        name = result_str[:29]
        QX_IPadd = result_str[29:result_str.index(':')]
        # print("Found the decie: " + name + ". The IP adress: " + QX_IPadd)
    else:
        print("Did not find any useful device")
        return False
    return QX_IPadd

def Read(QX_IPadd):
    UUID = QXSystem.Connect(QX_IPadd)
    data = QXSimpleDAQ.GetSingleShot(UInt64(UUID), Boolean(False), None, None)
    values = list(data[1])
    result_1 = []
    result_1.append(values[0])
    result_2 = []
    result_2.append(values[1])
    result = []
    result.append(result_1)
    result.append(result_2)

    return result

def Exit(QX_IPadd):
    QXSystem.Disconnect(QX_IPadd)

def read_samples():

    QX_IPadd = Scan()
    samples = Read(QX_IPadd)
    return samples


class NI_Interface:
    def __init__(self, stream_rate=1000) -> None:
        self.intended_stream_rate = 1 / stream_rate
        self.prev_time = time.perf_counter()

    def read_samples(self):
        """Reads in the samples from the daqtask

        NOTE: This is using interpolation to figure out the timesteps, so I
        can't promise that the times are *exactly* accurate

        Returns:
            List of samples
        """
        samples = read_samples()

        if len(samples[0]) == 0:
            return None

        next_time = time.perf_counter()

        time_delta = (time.perf_counter() - self.prev_time) / len(samples[0])

        if (abs(1 - (time_delta / self.intended_stream_rate)) > 0.1 and self.prev_time > 5):
            warnings.warn(f"Data intake is not running smoothly")

        samples.append(
            [self.prev_time + (time_delta * i) for i in range(len(samples[0]))]
        )

        transposed = [[C[i] for C in samples] for i in range(len(samples[0]))]

        self.prev_time = next_time

        return transposed

    def Exit(self, QX_IPadd):
        QXSystem.Disconnect(QX_IPadd)


def data_sender(
    sample_delay, send_queue: Queue = None, communication_queue: Queue = None
):
    """
        Runs in a separate process and constantly fills the send_queue with
        datapoints
    """
    ni_interface = NI_Interface()

    running = True

    sample_cache = []

    prev_time = time.perf_counter()

    while running:
        samples = ni_interface.read_samples()

        if samples:
            sample_cache.extend(samples)

            prev_time += sample_delay

        if not send_queue.full() and sample_cache:
            send_queue.put_nowait(sample_cache)
            sample_cache = []

        while not communication_queue.empty():
            val = communication_queue.get_nowait()

            if val == "EXIT":
                ni_interface.safe_exit()
                running = False
