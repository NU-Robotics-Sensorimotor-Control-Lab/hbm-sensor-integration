function a = read()
HBM_API_path='C:\Program Files (x86)\HBM\QuantumX API 4\';
QX = NET.addAssembly(...
[HBM_API_path 'DLLs\HBM.QuantumX.dll']);
QX_DC = NET.addAssembly(...
[HBM_API_path ,'DLLs\HBM.DeviceComponents.dll']);

QX_IPadd=System.String('169.254.173.36'); 
UUID   = HBM.QuantumX.QXSystem.Connect (QX_IPadd);
[Values,Status]= HBM.QuantumX.QXSimpleDAQ.GetSingleShot(UUID,false);
a = Values(1);
HBM.QuantumX.QXSystem.Disconnect (QX_IPadd);