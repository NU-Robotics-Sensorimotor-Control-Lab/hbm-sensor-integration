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

    def start_hbm(self):
        
        Connector = Int32(0)
        Channel = Int32(0)
        Signal = Int32(0)
        UserSignalID = Int32(1)
        nBuffer = Int32(20000)

        # Connect QuantumX with Computer
        QX_IPadd = self.HBM_Scan()
        UUID = UInt64(QXSystem.Connect(QX_IPadd))

        # read signal
        signal_0 = QXSystem.ReadSyncSignal(UUID, Connector, Signal)

        # modify the output rate
        signal_0.OutputRate = Double(1200.0)

        # assign
        QXSystem.AssignSyncSignal(UUID, Connector, signal_0)

        # re-read
        signal_0 = QXSystem.ReadSyncSignal(UUID, Connector, Signal)

        # setup the DAQ
        QXSimpleDAQ.SubscribeSignal(UUID, signal_0.Output.SignalReference, UserSignalID, nBuffer)

        # Start DAQ
        QXSimpleDAQ.StartDAQ()
        return UserSignalID, UUID, signal_0.Output.SignalReference


# def main():
#     sample_delay = 1/1000
#     ni_interface = NI_Interface()
#     sample_cache = []
#     prev_time = time.perf_counter()

#     UserSignalID, UUID, SignalReference = ni_interface.start_hbm()
#     QX_IPadd = ni_interface.HBM_Scan()

#     hbm_cache = []

#     for i in range(20):
#         samples = ni_interface.read_samples()

#         # HBM_data = QXSimpleDAQ.GetSinglePoint(UUID, SignalReference, Double(0.0))
#         QXSimpleDAQ.GetDataBlock()
#         result = QXSimpleDAQ.GetSignalData(UserSignalID, None)
#         if result[0] != 0:
#             value = list(result[1].Values)

#         # if samples:
#         #     sample_cache.extend(samples)

#             # prev_time += sample_delay
#         # print(samples)
#         if value:
#             hbm_cache.extend(value)
#         System.Threading.Thread.Sleep(1)
#         for sample_list in samples:
#             if hbm_cache:
#                 print(sample_list)
#                 Fz = hbm_cache.pop(0)
#                 sample_list.insert(0, Fz)
#                 sample_list.insert(1, 0.0)
#                 print(sample_list)
#                 sample_cache.append(sample_list)
#                 prev_time += sample_delay
            
#     print(sample_cache)

    # samples = ni_interface.read_samples()

    # if samples:
    #     sample_cache.extend(samples)

    #     prev_time += sample_delay
    # print(samples)
    # print(sample_cache)
    # print(prev_time)

# if __name__ == "__main__":
#     main()


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
    UserSignalID, UUID, SignalReference = ni_interface.start_hbm()
    QX_IPadd = ni_interface.HBM_Scan()

    while running:
        samples = ni_interface.read_samples()
        
        # # read HBM sensor data
        # QXSimpleDAQ.GetDataBlock()
        # result = QXSimpleDAQ.GetSignalData(UserSignalID, None)

        # if result[0] != 0:
        #     value = list(result[1].Values)

        value = QXSimpleDAQ.GetSinglePoint(UUID, SignalReference, Double(0)) - 28.219445650110993
        # System.Threading.Thread.Sleep(10)
        #sample list [10 vales ,time]
        # 1000 Hz 1000 date 
        if value and samples:
            for sample_list in samples:
                sample_list.insert(0, value)
                sample_list.insert(1, 0.0)
    
                sample_cache.append(sample_list)
                prev_time += sample_delay

        # if samples:
        #     sample_cache.extend(samples)

        #     prev_time += sample_delay

        if not send_queue.full() and sample_cache:
            send_queue.put_nowait(sample_cache)
            sample_cache = []

        while not communication_queue.empty():
            val = communication_queue.get_nowait()

            if val == "EXIT":
                ni_interface.safe_exit(QX_IPadd)
                running = False