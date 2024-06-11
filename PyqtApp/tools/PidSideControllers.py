def temperatureCorrector(temperature, tempDelta = 10):
    print(f'\n\n\ntemperature corrector: {temperature} + {tempDelta} = {temperature + tempDelta}\n\n\n')
    return temperature + tempDelta# updated
    delta = -0.081325*temperature + 9.7987 #12.7987
    print('temperature', temperature, 'updated temperature', temperature - delta)
    return temperature + delta

def maxPowerCorrector(temperature):
    if temperature < 200:
        return 55   
    elif 200 <= temperature < 300:
        return 70 
    elif 300 <= temperature < 500:
        return 85
    elif 500 <= temperature < 1100:
        return 95
    else:
        return 0
    
def getTemperatureUpscale(t):
    # t = 2.20364585e-14*t**5 +  -1.35450975e-10*t**4 + 3.22201667e-07*t**3 + -3.72054524e-04*t**2 + 2.14210916e-01*t -3.09947717e+00
    return 2.27 + t*0.0048
    