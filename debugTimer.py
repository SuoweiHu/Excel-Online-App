
import time
from app import app

class debugTimer:
    msgStart = ""
    msgEnd   = ""
    ptnTimeStamp  = True
    t_start = 0
    t_end   = 0  

    def __init__(self,\
        start_message = "Start Message",\
        end_message   = "End Message",\
        print_time    = True
        ):
        self.msgStart = start_message
        self.msgEnd   = end_message
        self.ptnTimeStamp = print_time

    def start(self): 
        self.t_start = time.time()
        app.logger.debug(f"\t\t{self.msgStart}")
    def end(self): 
        self.t_end = time.time()
        app.logger.debug(f"\t\t{self.msgEnd}")
        self.print()
    def stop(self): 
        self.t_end = time.time()
        app.logger.debug(f"\t\t{self.msgEnd}")
        self.print()

    def get_interval(self, unit='s'):
        if(unit == 'ms' or unit == 'Ms' or unit == 'MS'):
            return f"{(self.t_end - self.t_start) * 1000} ms"
        elif(unit == 's' or unit == 'S'):
            return f"{(self.t_end - self.t_start)} s"
    def get_startTime(self):
        return  time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.t_start))
    def get_endTime(self):
        return  time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.t_end))

    def print(self):
        app.logger.debug(f"  耗时:\t{self.get_interval()}")
        app.logger.debug(f"开始于:\t{self.get_startTime()}")
        app.logger.debug(f"结束于:\t{self.get_endTime()}")

    