import matlab.engine

eng = matlab.engine.start_matlab( )
print("Launch MATLAB engine in Python")
for i in range(200):
    data = eng.read()
    print(data)