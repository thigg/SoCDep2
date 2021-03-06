# Copyright (C) 2015 Siavoosh Payandeh Azad
import sys
import os
from Utilities import misc

if '--help' in sys.argv[1:] or '-help' in sys.argv[1:]:
    pass
else:
    misc.check_for_dependencies()

import copy
import time
import logging
from ConfigAndPackages import Config, PackageFile, Check_Config
from Utilities import Logger, Benchmark_Alg_Downloader, misc
import SystemInitialization
from GUI_Util import GUI
from pympler import tracker
from Simulator import Simulator
from RoutingAlgorithms.turn_model_evaluation import list_all_turn_models, turn_model_viz, turn_mode_classifier
from RoutingAlgorithms.turn_model_evaluation import odd_even_evaluation
from RoutingAlgorithms.mixed_critical_routing import *
from multiprocessing import Pool


tr = None
if Config.MemoryProfiler:
    tr = tracker.SummaryTracker()

if '--help' in sys.argv[1:] or '-help' in sys.argv[1:]:
    misc.print_help_man()
    sys.exit()
elif '-GUI' in sys.argv[1:]:
    main_window = GUI.MainView(None)
    main_window.title("Schedule and Depend Configuration GUI")
    main_window.mainloop()
    if not main_window.apply_button:
        sys.exit()
elif '-EvTM_odd_even' in sys.argv[1:]:
    misc.generate_file_directories()

    for size in range(4, 8):
        for routing_type in ["MinimalPath", "NonMinimalPath"]:
            odd_even_evaluation.enumerate_all_odd_even_turn_models(size, routing_type)
            print

    odd_even_evaluation.evaluate_robustness_links(3)
    odd_even_evaluation.evaluate_robustness_routers(3)
    #odd_even_evaluation.viz_all_turn_models_against_each_other()
    sys.exit()

elif '-odd_even_viz' in sys.argv[1:]:
    turn_model_viz.viz_2d_odd_even_turn_model()
    sys.exit()

elif '-ETM' in sys.argv[1:]:     # Enumerate turn model
    misc.generate_file_directories()
    if __name__ == '__main__':
        p = Pool(6)
        if sys.argv[sys.argv.index('-ETM') + 1] == '3D':
            args = list(range(0, len(PackageFile.FULL_TurnModel_3D)+1))
            p.map(list_all_turn_models.enumerate_all_3d_turn_models, args)
            p.terminate()
        if sys.argv[sys.argv.index('-ETM') + 1] == '2D':
            args = list(range(0, len(PackageFile.FULL_TurnModel_2D)+1))
            p.map(list_all_turn_models.enumerate_all_2d_turn_models, args)
            p.terminate()
        del p
    sys.exit()
elif '-ETMD' in sys.argv[1:]:     # Enumerate turn model based on deadlock
    misc.generate_file_directories()
    if __name__ == '__main__':
        routing_type = sys.argv[sys.argv.index('-ETMD') + 2]
        if routing_type == "M":
            Config.RotingType = 'MinimalPath'
        elif routing_type == "NM":
            Config.RotingType = 'NonMinimalPath'
        else:
            print "ARGUMENT ERROR:: Routing type should be either M or NM..."
        number_of_multi_threads = int(sys.argv[sys.argv.index('-ETMD') + 3])
        p = Pool(number_of_multi_threads)
        if sys.argv[sys.argv.index('-ETMD') + 1] == '3D':
            args = list(range(0, len(PackageFile.FULL_TurnModel_3D)+1))
            p.map(list_all_turn_models.enumerate_all_3d_turn_models_based_on_df, args)
            p.terminate()
        elif sys.argv[sys.argv.index('-ETMD') + 1] == '2D':
            args = list(range(0, len(PackageFile.FULL_TurnModel_2D)+1))
            p.map(list_all_turn_models.enumerate_all_2d_turn_models_based_on_df, args)
            p.terminate()
        else:
            print "ARGUMENT ERROR:: Dimension should be specified as 2D or 3D..."
    sys.exit()
elif '-TMFT' in sys.argv[1:]:     # check All turn model's fault tolerance
    misc.generate_file_directories()
    Config.ag.x_size = 3
    Config.ag.y_size = 3
    routing_type = sys.argv[sys.argv.index('-TMFT') + 2]
    if routing_type == "M":
        Config.RotingType = 'MinimalPath'
    elif routing_type == "NM":
        Config.RotingType = 'NonMinimalPath'
    else:
        print "ARGUMENT ERROR:: Routing type should be either M or NM..."

    number_of_multi_threads = int(sys.argv[sys.argv.index('-TMFT') + 3])
    if "2D" in sys.argv[1:] or "3D" in sys.argv[1:]:
        pass
    else:
        print "MISSING ARGUMENT:: A dimension value is required for this command"
        sys.exit()
    dimension = sys.argv[sys.argv.index('-TMFT') + 1]
    if "-V" in sys.argv[1:]:
        viz = True
    else:
        viz = False
    list_all_turn_models.check_fault_tolerance_of_routing_algs(dimension, number_of_multi_threads, viz)
    sys.exit()
elif '-VIZTM' in sys.argv[1:]:     # visualizes the turn models in 2D or 3D
    misc.generate_file_directories()
    if "2D" in sys.argv[1:] or "3D" in sys.argv[1:]:
        pass
    else:
        print "MISSING ARGUMENT:: A dimension value is required for this command"
        sys.exit()
    dimension = sys.argv[sys.argv.index('-VIZTM') + 1]
    routing_type = sys.argv[sys.argv.index('-VIZTM') + 2]
    turn_model_viz.viz_all_turn_models(dimension, routing_type)
    sys.exit()
elif '-TMC' in sys.argv[1:]:
    turn_mode_classifier.classify_3d_turn_models()
    sys.exit()
elif '-CONF' in sys.argv[1:]:
    if len(sys.argv) == 2:
        misc.update_config("ConfigAndPackages/ConfigFile.txt")
    else:
        path_to_config_file = sys.argv[sys.argv.index('-CONF') + 1]
        misc.update_config(path_to_config_file)
elif '-BENCHMARK' in sys.argv[1:]:
    benchmark = sys.argv[sys.argv.index('-BENCHMARK') + 1]
    print benchmark
    if Benchmark_Alg_Downloader.download_benchmark_algorithms(str(benchmark)):
        pass
    else:
        sys.exit()
elif "-MC" in sys.argv[1:]:
    routing_type = "MinimalPath"
    scenario = 1

    if scenario == 1:       # L Scenario
        critical_nodes = [0, 15]
        critical_path = [0, 1, 2, 3, 7, 11, 15]
        critical_rg_nodes = ["0LI", "0EO", "1WI", "1EO", "2WI", "2EO", "3WI", "3NO", "7SI", "7NO", "11SI", "11NO", "15SI", "15LO",
                             "15LI", "15SO", "11NI", "11SO", "7NI", "7SO", "3NI", "3WO", "2EI", "2WO", "1EI", "1WO", "0EI", "0LO"]
        forced_turns = ["W2N"]

    elif scenario == 2:
        critical_nodes = [0, 15]
        critical_path = [0, 1, 5, 9, 10, 14, 15]
        critical_rg_nodes = ["0LI", "0EO", "1WI", "1NO", "5SI", "5NO", "9SI", "9EO", "10WI", "10NO", "14SI", "14EO", "15WI", "15LO",
                             "15LI", "15WO", "14EI", "14SO", "10NI", "10WO", "9EI", "9SO", "5NI", "5SO", "1NI", "1WO", "0EI", "0LO"]
        forced_turns = ["E2N", "S2E"]

    elif scenario == 3:
        critical_nodes = [0, 15]
        critical_path = [0, 1, 5, 9, 13, 14, 15]
        critical_rg_nodes = ["0LI", "0EO", "1WI", "1NO", "5SI", "5NO", "9SI", "9NO", "13SI", "13EO", "14WI", "14EO", "15WI", "15LO",
                             "15LI", "15WO", "14EI", "14WO", "13EI", "13SO", "9NI", "9SO", "5NI", "5SO", "1NI", "1WO", "0EI", "0LO"]
        forced_turns = ["E2N", "S2E"]

    elif scenario == 4: # ISLAND
        critical_nodes = [0, 1]
        critical_path = [0, 1]
        critical_rg_nodes = ["0LI", "0EO", "1WI", "1LO"]
        forced_turns = []

    elif scenario == 5: # BASELINE
        critical_nodes = []
        critical_path = []
        critical_rg_nodes = []
        forced_turns = []

    misc.generate_file_directories()

    max_connectivity = 0
    best_turn_model = None

    for turn_model in all_2d_turn_models:
        discard = False
        for turn in forced_turns:
            if turn not in turn_model:
                discard = True
        if not discard:
            connectivity, noc_rg = mixed_critical_rg(4, routing_type, critical_nodes, critical_rg_nodes,
                                                     turn_model, False, False)
            if connectivity > max_connectivity:
                max_connectivity = connectivity
                best_turn_model = turn_model

    
    print "==="*6
    print "max connectivity:", max_connectivity
    print "best turn model", best_turn_model
    connectivity, noc_rg = mixed_critical_rg(4, routing_type, critical_nodes, critical_rg_nodes,
                                             best_turn_model, True, True)
    report_router_links(4, noc_rg)
    generate_routing_table(4, noc_rg, routing_type)
    sys.exit()

Check_Config.check_config_file()
program_start_time = time.time()
##############################
# Just for getting a copy of the current console
sys.stdout = Logger.Logger()

# preparing to setup Logging
logging.basicConfig(filename=os.path.join(os.path.join(os.path.curdir, PackageFile.LoGDirectory),
                    'Logging_Log_'+str(time.time())+'.log'), level=logging.DEBUG)
logging.info('Starting logging...')
####################################################################
misc.generate_file_directories()
misc.draw_logo()
misc.generate_configfile()
####################################################################
# Initialization of the system

tg, ag, shmu, noc_rg, CriticalRG, NonCriticalRG, pmcg = SystemInitialization.initialize_system(logging)

# just to have a sense of how much time we are spending in each section
print ("===========================================")
system_starting_time = time.time()
print ("\033[92mTIME::\033[0m SYSTEM STARTS AT:"+str(round(system_starting_time-program_start_time)) +
       " SECONDS AFTER PROGRAM START...")

if Config.enable_simulator:
    Simulator.run_simulator(Config.ProgramRunTime, tg, ag, shmu, noc_rg, CriticalRG, NonCriticalRG, logging)
logging.info('Logging finished...')

if Config.MemoryProfiler:
    print("===========================================")
    print("         Reporting Memory Usage")
    print("===========================================")
    tr.print_diff()
    print("===========================================")
