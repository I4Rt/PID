
from flask import Flask, render_template, request, make_response, jsonify
from random import randint

# from threading import Thread
# from modules.crc16module import *
# from modules.sender import *
# from modules.reciever import *
# from modules.pid_temperature_set import *
# import modules.PID 

from modules.PIDControllerTools import *

from modules.PIDModels import *

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='')

data = [{'x':i, 'y':randint(5, 20)} for i in range(100000)]
i = 0




heater = Heater(p = 10,i = 2,d = 12,target=25, needPID=True)
heater.startThread()





@app.route('/main', methods=['get'])
def getMain():
    return render_template('main.html', 
                           pidding=heater.needPID, 
                           targetTemperature = heater.targetTemperature,
                           PValue=heater.P,
                           IValue=heater.I,
                           DValue=heater.D)
@app.route('/getData', methods=['POST'])
def getChartData():
    global i
    i += 10
    count = request.args.get('count')
    data1 = heater.realTemperatureList[-int(count):]
    data2 = heater.targetTemperatureList[-int(count):]
    agregated1 = [{'x': i, 'y':data1[i]} for i in range(len(data1))]
    agregated2 = [{'x': i, 'y':data2[i]} for i in range(len(data2))]
    return {'data':[agregated1, agregated2]}, 200

@app.route('/setTargetTemperature', methods=['GET'])
def setTargetTemperature():
    temperature = request.args.get('temperature')
    heater.targetTemperature = float(temperature)
    return {'setTargetTemperature':True, 'temperature': temperature}, 200
    
    
@app.route('/changePidStatus', methods=['GET'])
def changePidStatus():
    print
    needPid = True if request.args.get('status') == 'true' else False
    heater.setNeedPID(needPid)
    return {'changePidStatus':True, 'needPid': needPid}, 200


@app.route('/setPIDParams', methods=['GET'])
def setPIDParams():
    
    P = float(request.args.get('P'))
    I = float(request.args.get('I'))
    D = float(request.args.get('D'))
    if P and I and D:
        heater.P = P
        heater.I = I
        heater.D = D
    return {'setPIDParams':True, 'PID': {'P':P, 'I':I, 'D':D}}, 200


app.run('0.0.0.0', 5340, debug = False)

