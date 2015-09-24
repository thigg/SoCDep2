# Copyright (C) 2015 Siavoosh Payandeh Azad
from Utilities import misc
misc.CheckForDependencies()


import threading
import sys, os, time
import numpy
import logging
from ConfigAndPackages import Config
from Utilities import Logger, Benchmark_Alg_Downloader
from SystemHealthMonitoring import SHM_Functions
import SystemInitialization
from GUI_Util import GUI
from pympler import tracker

tr = tracker.SummaryTracker()

Start_Program = True
if '--help' in sys.argv[1:] or '-help' in sys.argv[1:]:
    print("Usage:    python Main.py [option1]")
    print("Options and arguments:")
    print("-GUI\t:Graphical User Interface for Configuration")
    print("-UTEST\t:Runs Unit Tests")
    print("")
    sys.exit()
elif '-GUI' in sys.argv[1:]:
    app = GUI.ConfigAppp(None)
    app.title('Schedule And Depend')
    app.mainloop()
    if not app.Apply_Button:
        sys.exit()
elif '-UTEST' in sys.argv[1:]:
    os.system('python UnitTest/UnitTests.py')
    sys.exit()
elif '-BENCHMARK' in sys.argv[1:]:
    Benchmark = sys.argv[sys.argv.index('-BENCHMARK') + 1]
    if Benchmark_Alg_Downloader.Download_Benchmark_Algorithms(str(Benchmark)):
        pass
    else:
        sys.exit()


ProgramStartTime = time.time()
##############################
# Just for getting a copy of the current console
sys.stdout = Logger.Logger()

# preparing to setup Logging
logging.basicConfig(filename=os.path.join(os.path.join(os.path.curdir, Config.LoGDirectory),
                    'Logging_Log_'+str(time.time())+'.log'), level=logging.DEBUG)
logging.info('Starting logging...')
####################################################################
misc.GenerateFileDirectories()
misc.DrawLogo()
####################################################################
# Initialization of the system
TG, AG, SHM, NoCRG, CriticalRG, NonCriticalRG, PMCG = SystemInitialization.InitializeSystem(logging)

# just to have a sense of how much time we are spending in each section
print ("===========================================")
SystemStartingTime = time.time()
print ("\033[92mTIME::\033[0m SYSTEM STARTS AT:"+str(round(SystemStartingTime-ProgramStartTime))+
       " SECONDS AFTER PROGRAM START...")

####################################################################
#
#                   Fault event handler
#
####################################################################

def FaultEvent():
    global timer
    TimeAfterSystemStart = time.time() - SystemStartingTime
    print ("\033[92mTIME::\033[0m FAULT OCCURRED"+str("%.2f" % TimeAfterSystemStart)+" SECONDS AFTER SYSTEM START...")
    # Should we reset the timer or the next fault falls out of the program run time?
    TimeUntilNextFault = numpy.random.normal(Config.MTBF,Config.SD4MTBF)
    if TimeAfterSystemStart + TimeUntilNextFault <= Config.ProgramRunTime:
        print ("TIME UNTIL NEXT FAULT:"+str("%.2f" % TimeUntilNextFault)+" Sec")
        # reset the timer
        timer = threading.Timer(TimeUntilNextFault, FaultEvent)
        timer.start()

    # we generate some random fault to be inserted in the system
    FaultLocation, FaultType = SHM_Functions.RandomFaultGeneration(SHM)
    # here we actually insert the fault in the system
    SHM_Functions.ApplyFaultEvent(AG, SHM, NoCRG, FaultLocation, FaultType)

if Config.EventDrivenFaultInjection:
    TimeUntilNextFault = numpy.random.normal(Config.MTBF, Config.SD4MTBF)
    print ("TIME UNTIL NEXT FAULT:"+str("%.2f" % TimeUntilNextFault)+" Sec")
    timer = threading.Timer(TimeUntilNextFault, FaultEvent)
    timer.start()

    while True:
        if time.time() - SystemStartingTime > Config.ProgramRunTime:
            break

    timer.cancel()
    timer.join()

logging.info('Logging finished...')

print("===========================================")
print("         Reporting Memory Usage")
print("===========================================")
tr.print_diff()
print("===========================================")