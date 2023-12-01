import matplotlib.pyplot as plt
class Exchange:
    
    def __init__(self, k1:float, k2:float, curT = None):
        
        self.k1 = k1 # значение максимума
        self.curT = k1 
        if curT:
            self.curT = curT
            
        self.k2  = k2 # обобщенный коеффициент инертности
        
    def calculate(self, time, curTargetTemp = None):
        if curTargetTemp:
            self.k1 = curTargetTemp
        diff = self.k1 - self.curT
        delta = diff/(self.k2 * time)
        if abs(diff) > abs(delta):
            self.curT = self.curT + delta
        else:
            self.curT = self.curT + diff
        
        # print(delta)
        return self.curT
    
class Linear:
    
    def __init__(self, k1:float, k2:float):
        
        self.curT = k1 
        if self.curT:
            self.curT = self.curT
        self.k2  = k2 # скорости нагрева
        
    def calculate(self, time, power = None):
        if power:
            self.k2 = power
    
        delta = self.k2 * time
        self.curT = self.curT + delta
        return self.curT
    

class Heater():
    def __init__(self, power, outerT, curT, inert, target: Exchange):
        
        self.outerT = outerT
        
        
        
        self.curT = curT
        self.freazeFoo = Exchange(outerT, inert, curT)
        self.heatFoo = Linear(curT, power)
        
        self.target = target
        
        self.heaterTrack = [self.curT]
        self.targetTrack = [self.target.curT]
        
        
    def heat(self, time, swithcOn = True, curTargetTemp = None):
        
        
        
        if swithcOn:
            self.heatFoo.curT = self.curT
            self.curT = self.heatFoo.calculate(time)
        else:
            self.freazeFoo.curT = self.curT
            self.curT = self.freazeFoo.calculate(time, max(self.outerT, self.target.curT))
        
        self.target.k1 = self.curT
        if self.curT > self.target.curT:
            t = self.curT
        else:
            t = self.outerT
        temp = self.target.calculate(time, t)
        
        self.heaterTrack.append(self.curT)
        self.targetTrack.append(temp)
        
    
    def plot(self, target = None):
        plt.figure()
        plt.plot(self.heaterTrack, label='негреватель')
        plt.plot(self.targetTrack, label='объект')
        if target:
            plt.plot(target)
        plt.show()
            
        
        
 
if __name__ == '__main__':
    
    mainK2 = 30
    exchanger1 = Exchange(20, mainK2, 15)
    points1 = [15]
    
    exchanger2 = Exchange(20, mainK2, 30)
    points2 = [30]
    
    exchanger1_copy1 = Exchange(20, mainK2, 15)
    points3 = [15]
    
    linear = Linear(15, 0.3)
    points4 = [15]
    
    exchanger1_copy2 = Exchange(20, mainK2, 15)
    points5 = [15]
    
    
    
    for i in range(1, 101):
        p1 = exchanger1.calculate(1)
        points1.append(p1)
        p2 = exchanger2.calculate(1)
        points2.append(p2)
        
        exchanger1_copy1.k1 = p2
        p3 = exchanger1_copy1.calculate(1)
        points3.append(p3)
        
        p4 = linear.calculate(1)
        points4.append(p4)
        
        exchanger1_copy2.k1 = p4
        p5 = exchanger1_copy2.calculate(1)
        points5.append(p5)
        
    # plt.plot(points1)
    # plt.plot(points2)
    
    
    figure, axis = plt.subplots(2, 2)

    axis[0, 0].plot(points1)
    axis[0, 0].plot(points2)

    axis[0, 1].plot(points3)
    axis[0, 1].plot(points2)

    axis[1, 0].plot(points5)
    axis[1, 0].plot(points4)


    exchanger2.curT = linear.curT

    for i in range(101, 201):
        
        p2 = exchanger2.calculate(1)
        points4.append(p2)
        
        exchanger1_copy2.k1 = p2
        p5 = exchanger1_copy2.calculate(1)
        points5.append(p5)
        
    axis[1, 1].plot(points5)
    axis[1, 1].plot(points4)

    figure.show()
    
    ##################################################
    heater = Heater(0.3, 23, 23, 30, Exchange(23, 44))
    
    setting = [True for i in range(20)]
    target = [50 for i in range(600)]
    target += [80 for i in range(400)]
    target += [40 for i in range(400)]
    target += [120 for i in range(100)]
    target += [80 for i in range(100)]
    target += [120 for i in range(100)]
    target += [80 for i in range(100)]
    target += [120 for i in range(100)]
    target += [80 for i in range(100)]
    
    
    for val in target:
        heater.heat(1, True if heater.curT < val else False )


    heater.plot(target)
    
          
