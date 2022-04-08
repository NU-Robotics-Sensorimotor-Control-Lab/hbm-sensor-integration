import clr
import time
clr.AddReference("dlls/HBM.QuantumX")
clr.AddReference("dlls/HBM.DeviceComponents")

from HBM.QuantumX import QXSystem
from HBM.QuantumX import QXSimpleDAQ
from HBM.DeviceComponents import eConnectorTypes

# connect IP-Adress
Qx_IPadd = 'XXX.xx.xxx.221'
UUID = QXSystem().Connect()

# subscribe signal
Kanaele = [1, 2, 3, 4]
Connector = [0, 1, 2, 3]
Channel = 0
Signal = 0
UserSignalID = Connector
nBuffer = 20000

for ik in range(1, len(Connector)):
    QXSimpleDAQ().SubscribeSignal(UUID, Connector(ik), Channel,
                                Signal, eConnectorTypes().ANALOG_IN_CHANNEL, 
                                UserSignalID(ik), nBuffer)
# pause, wait for the data
measure_time = 0.600

# Start DAQ

QXSimpleDAQ().StartDAQ(False)

# pause?
time.sleep(measure_time)

QXSimpleDAQ().GetDataBlock()

for ik in range(1, len(UserSignalID)):
    Retmess(ik), MValue{ik} = QXSimpleDAQ().GetSignalData(UserSignalID(ik))

# Stop DAQ and disconnect
QXSimpleDAQ().StopDAQ()
QXSystem().Disconnect(Qx_IPadd)

# read the data
for ik in range(1, len(UserSignalID)):
    M_wert{ik} = float(MValue{ik}.Values)
    T_wert{ik} = float(MValue{ik}.TimeStamps)






