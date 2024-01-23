def getYinX(curX, xData, yData):
    for i in range(1, len(xData)):
        x = xData[i]
        if curX < x:
            x2 = x
            x1 = xData[i-1]
            y2 = yData[i]
            y1 = yData[i-1]
            if x1 == x2:
                print('x, y =', curX, y1)
                return y1
            print('x, y =', curX, y1 + (y2 - y1)*(curX - x1)/(x2-x1))
            return y1 + (y2 - y1)*(curX - x1)/(x2-x1)
            
    