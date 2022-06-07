import nidaqmx as daq
from nidaqmx.constants import READ_ALL_AVAILABLE, AcquisitionType
import time
import warnings
from multiprocessing import Queue

# This will run in it's own thread

import clr
import sys
from System import *
import System

sys.path.insert(1,"C:\Program Files (x86)\HBM\QuantumX API 4\DLLs")

# import HBM Common API 
clr.AddReference("HBM.QuantumX")
from HBM.QuantumX import QXSystem
from HBM.QuantumX import QXSimpleDAQ
from HBM.QuantumX import eDAQValueState
from HBM.DeviceComponents import eConnectorTypes

class NI_Interface:
    def __init__(self, channels=["Dev1/ai0", "Dev1/ai1", "Dev1/ai2", "Dev1/ai3", "Dev1/ai4", "Dev1/ai5", "Dev1/ai6", "Dev1/ai7"], stream_rate=1000) -> None:
        self.daqtask = daq.Task()
        self.intended_stream_rate = 1 / stream_rate

        for chn in channels:
            self.daqtask.ai_channels.add_ai_voltage_chan(chn)

        self.daqtask.timing.cfg_samp_clk_timing(
            stream_rate, sample_mode=AcquisitionType.CONTINUOUS
        )

        self.daqtask.start()
        self.prev_time = time.perf_counter()

    def read_samples(self):
        """Reads in the samples from the daqtask

        NOTE: This is using interpolation to figure out the timesteps, so I
        can't promise that the times are *exactly* accurate

        Returns:
            List of samples
        """
        samples = self.daqtask.read(
            number_of_samples_per_channel=READ_ALL_AVAILABLE)
        # print(samples)

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

    def safe_exit(self, QX_IPadd):
        self.daqtask.stop()
        self.daqtask.close()
        QXSimpleDAQ.StopDAQ()
        QXSystem.Disconnect(QX_IPadd)
        print("Closed DAQ")

    def HBM_Scan(self):
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

    hbm_cache = []
    QX_IPadd = ni_interface.HBM_Scan()
    UUID = QXSystem.Connect(QX_IPadd)

    i = 0
    sum_Fx = 0
    sum_Fy = 0
    sum_Fz = 0
    sum_Mx = 0
    sum_My = 0
    sum_Mz = 0

    while running:
        samples = ni_interface.read_samples()
        

        Hbm_data = list(QXSimpleDAQ.GetSingleShot(UInt64(UUID), Boolean(False), None, None)[1])

        Fz = (Hbm_data[0]+Hbm_data[1])/2
        Fy = (Hbm_data[2]+Hbm_data[3])/2
        Fx = (Hbm_data[4]+Hbm_data[5])/2


        Mz = (Hbm_data[6]+Hbm_data[7])/2
        My = (Hbm_data[8]+Hbm_data[9])/2
        Mx = (Hbm_data[10]+Hbm_data[11])/2

        if i < 100:
            sum_Fx += Fx
            sum_Fy += Fy
            sum_Fz += Fz
            sum_Mx += Mx
            sum_My += My
            sum_Mz += Mz
        i += 1
        
        if i >= 105:
            Fx = Fx - sum_Fx/100
            Fy = Fy - sum_Fy/100
            Fz = Fz - sum_Fz/100
            Mx = Mx - sum_Mx/100
            My = My - sum_My/100
            Mz = Mz - sum_Mz/100


        if Fz and samples:
            for sample_list in samples:
                sample_list.insert(0, Fz)
                sample_list.insert(1, Fy)
                sample_list.insert(2, Fx)

                sample_list.insert(3, Mz)
                sample_list.insert(4, My)
                sample_list.insert(5, Mx)
    
                sample_cache.append(sample_list)
                prev_time += sample_delay

        if not send_queue.full() and sample_cache:
            send_queue.put_nowait(sample_cache)
            sample_cache = []

        while not communication_queue.empty():
            val = communication_queue.get_nowait()

            if val == "EXIT":
                ni_interface.safe_exit(QX_IPadd)
                running = False