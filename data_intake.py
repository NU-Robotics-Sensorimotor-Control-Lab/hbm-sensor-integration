from random import sample
import nidaqmx as daq
from nidaqmx.constants import READ_ALL_AVAILABLE, AcquisitionType
import time
import warnings
from multiprocessing import Queue

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
    def __init__(self, stream_rate=1000):
        self.intended_stream_rate = 1 / stream_rate
        self.prev_time = time.perf_counter()   

    def Scan(self):
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

    def start_daq(self):
        
        Connector = Int32(0)
        Channel = Int32(0)
        Signal = Int32(0)
        UserSignalID = Int32(1)
        nBuffer = Int32(20000)

        # Connect QuantumX with Computer
        QX_IPadd = self.Scan()
        UUID = UInt64(QXSystem.Connect(QX_IPadd))

        # read signal
        signal_0 = QXSystem.ReadSyncSignal(UUID, Connector, Signal)

        # modify the output rate
        # print(signal_0.OutputRate)
        signal_0.OutputRate = Double(4800.0)
        # print(signal_0.OutputRate)
        # print(signal_0)
        # assign
        QXSystem.AssignSyncSignal(UUID, Connector, signal_0)

        # re-read
        signal_0 = QXSystem.ReadSyncSignal(UUID, Connector, Signal)

        # setup the DAQ
        QXSimpleDAQ.SubscribeSignal(UUID, signal_0.Output.SignalReference, UserSignalID, nBuffer)

        # Start DAQ
        QXSimpleDAQ.StartDAQ()
        return UserSignalID, UUID, signal_0.Output.SignalReference


    def package(self, result):
        result_1 = []
        result_1.append(result-28.219445650110993)
        result_2 = []
        result_2.append(result-28.219445650110993)
        result = []
        result.append(result_1)
        result.append(result_2)

        return result 

    def read_samples(self, samples):
        """Reads in the samples from the daqtask

        NOTE: This is using interpolation to figure out the timesteps, so I
        can't promise that the times are *exactly* accurate

        Returns:
            List of samples
        """

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
        print(1/time_delta)

        return transposed

    def Exit(self, QX_IPadd):
        QXSimpleDAQ.StopDAQ()
        QXSystem.Disconnect(QX_IPadd)
        print("Stop DAQ")

# def main():
#     ni = NI_Interface()
#     QX_IPadd = ni.Scan()
#     UUID, Connector, Channel, Signal = ni.start_daq(QX_IPadd)

#     running = True

#     while running:
#         start = time.perf_counter()
#         samples = ni.Read(UUID, Connector, Channel, Signal)
#         end = time.perf_counter()
#         print(1/(end-start))

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

    UserSignalID, UUID, SignalReference = ni_interface.start_daq()
    QX_IPadd = ni_interface.Scan()

    matrix = []

    while running:
        # Method 1
        # Get Data
        # QXSimpleDAQ.GetDataBlock()
        # values = QXSimpleDAQ.GetSignalData(UserSignalID, None)
        # System.Threading.Thread.Sleep(30)
        # for j in list(values[1].Values):
        #     matrix.append(j)
        # k = matrix.pop(0)
        # result = ni_interface.package(k)
        # samples = ni_interface.read_samples(result)
        # if values[0] != 0:
        #     for j in list(values[1].Values):
        #         result = ni_interface.package(j)
        #         samples = ni_interface.read_samples(result)
        # print(k)

        # Method 2
        k = QXSimpleDAQ.GetSinglePoint(UUID, SignalReference, Double(0.0))
        result = ni_interface.package(k)
        samples = ni_interface.read_samples(result)
        # time.sleep(0.1)
            
        # System.Threading.Thread.Sleep(20)
                
        if samples:
            sample_cache.extend(samples)

            prev_time += sample_delay

        if not send_queue.full() and sample_cache:
            send_queue.put_nowait(sample_cache)
            sample_cache = []

        while not communication_queue.empty():
            val = communication_queue.get_nowait()

            if val == "EXIT":
                ni_interface.Exit(QX_IPadd)
                running = False

