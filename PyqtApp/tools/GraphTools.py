from data.FSTargetDataMeasurement import *

def getYinX(curX, pairs:list[FSTargetDataMeasurement]):
    print('pairs', len(pairs))
    print('curX', curX)
    
    
    for i in range(1, len(pairs)):
        x = pairs[i].time
        if curX < x:
            x2 = x
            x1 = pairs[i-1].time
            y2 = pairs[i].value
            y1 = pairs[i-1].value
            if x1 == x2:
                print('1. x, y =', curX, y1)
                return y1
            print('2. x, y =', curX, y1 + (y2 - y1)*(curX - x1)/(x2-x1))
            return y1 + (y2 - y1)*(curX - x1)/(x2-x1)
        print('3. x, y =', curX, pairs[-1].value)
    return pairs[-1].value
            
    