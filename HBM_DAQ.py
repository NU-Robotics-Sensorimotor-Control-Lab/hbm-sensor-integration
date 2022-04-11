# This script will use HBM Common API to get the data from HBM Sensor
import clr
import sys

sys.path.insert(1,"D:\RSC Lab\HBM\HBM Common API\API")

# import HBM Common API 
clr.AddReference("Hbm.Api.Common")
from Hbm.Api.Common import DaqEnvironment
from Hbm.Api.Common import DaqMeasurement
from Hbm.Api.Common.Entities import Device
from Hbm.Api.Common.Entities.Problems import Problem
from Hbm.Api.Common.Entities.Signals import Signal
from Hbm.Api.Common.Enums import DataAcquisitionMode

# import HBM QuantumX API
clr.AddReference("Hbm.Api.QuantumX")
from Hbm.Api.QuantumX import QuantumXDevice
from Hbm.Api.QuantumX import QuantumXDeviceFamily

# import Collections
clr.AddReference("System.Collections")
from System.Collections.Generic import List

# Init
_daqEnv = DaqEnvironment.GetInstance()
_daqSession = DaqMeasurement()
_sessionSignals = List[Signal]()

# Scan for all avaibale devices
scanDevices = _daqEnv.Scan()

if (scanDevices.Count > 0):
    print("Get the device !")
    # Use first device
    measDevice = scanDevices[0]

    # Connect to device
    connect_problems = List[Problem]()
    isConnected = _daqEnv.Connect(measDevice, connect_problems)

    if (isConnected):
        # Use signals form fist 2 connectors
        s1 = measDevice.Connectors[0].Channels[0].Signals[0]
        s2 = measDevice.Connectors[1].Channels[0].Signals[0]

        # set sample rate
        s1.SampleRate = 2400 # Hz
        s2.SampleRate = 2400

        # We don't check problems list here
        measDevice.AssignSignal(s1, connect_problems)
        measDevice.AssignSignal(s2, connect_problems)

        # Register first 2 signals for measurement session
        _sessionSignals.Add(s1)
        _sessionSignals.Add(s2)

        _daqSession.AddSignals(measDevice, _sessionSignals)

        # prepare DAQ session. We only need 1
        # single timestap per block
        _daqSession.PrepareDaq()

        # ----- Start unsyncrhonized DAQ session -----
        _daqSession.StartDaq(DataAcquisitionMode.Unsynchronized)

        # ADD some code right here
        #
        #
        #
        #

        # Disconnect device
        _daqEnv.Disconnect(measDevice)
    
    # Clean up
    _daqSession.Dispose()
    _daqEnv.Dispose() # call this only once at the end of your application



