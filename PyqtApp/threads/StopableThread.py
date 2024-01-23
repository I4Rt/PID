from threading import Thread, Event, currentThread
from time import sleep

class StopableThread(Thread):
    
    def __init__(self, looped = False, *args, **kwargs):
        Thread.__init__(self, *args, **kwargs)
        self.__looped = looped
        self.__event = Event()
        self.__pauseEvent = Event()
        
    def stop(self, ):
        self.__event.set()
        
    def pause(self, ):
        self.__pauseEvent.set()
        
    def play(self):
        self.__pauseEvent = Event()
        
        
    def run(self):
        if self.__looped:
            while not self.__event.is_set():
                if not self.__pauseEvent.is_set():
                    self._target(*self._args, **self._kwargs)
                else:
                    sleep(0.05)
        else:
            self._target(self._args, **self._kwargs)
    
    # def __del__(self):
    #     print("deleted StopableThread object", currentThread().ident)
        
    
    

    
    
if __name__ == '__main__':
    from time import sleep
    from datetime import datetime as dt

    def doPrints(text, adder = ''):
        print(str(dt.now()), text, adder)
        sleep(1)
        
    st = StopableThread(target=doPrints, args=('Привет! Я пишу текст!'), kwargs={'adder': 'УРА'}, looped=False)
    st.start()
    
    sleep(7)
    
    st.stop()
    st.join()
    
    print('finished')