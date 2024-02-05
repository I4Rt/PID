from data.FSTargetDataMeasurement import *

def getYinX(curX, pairs:list[FSTargetDataMeasurement]):
    for i in range(1, len(pairs)):
        x = pairs[i].time
        if curX < x:
            x2 = x
            x1 = pairs[i-1].time
            y2 = pairs[i].value
            y1 = pairs[i-1].value
            if x1 == x2:
                print('x, y =', curX, y1)
                return y1
            print('x, y =', curX, y1 + (y2 - y1)*(curX - x1)/(x2-x1))
            return y1 + (y2 - y1)*(curX - x1)/(x2-x1)
    return pairs[-1].value
            
    