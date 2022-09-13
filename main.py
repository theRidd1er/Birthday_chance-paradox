
import time
import multiprocessing as mlp
import random
import pandas as pd
from read_write import log_header_conf, log_save_execTime, log_save_simRes
from db_operations import db_conn_inf, db_results, db_done_sims

paths = {
        "log" : ".\\Projects_git\\Birthday_Paradox_Simulation\\BirthdayParadox_Simulations.txt",
        "dba" : ".\\Projects_git\\Birthday_Paradox_Simulation\\BirthdayParadox_DataBase.db"
}

# simulation configuration and start menu
def conf_menu_display(test_range, path):

    while True:

        group_size = [None, None]
        req_sims_sizes = []

        print("------------------------------------")
        print("Hello in Birthday Paradox simulation")
        print("------------------------------------\n")

        print("Simulation parameters configuration:")

        while not (group_size[0] or group_size[1]):
            try:
                group_size[0] = int(input("Enter group start size to test: "))
                group_size[1] = int(input("Enter group end size to test: ")) + 1

            except ValueError:
                print("Enter only numbers")
            except Exception:
                print("Error")
            except group_size[1] - group_size[0] < 1:
                print("Group size must be larger or equal to 1")
            else:

                print("\nYour configuration: ")
                print(f"Group size: {group_size[0]} to {group_size[1] - 1}")
                print(f"Test range: {test_range}")
                print(f"Simulations: {group_size[1] - group_size[0]}")

        req_sims_sizes = db_done_sims(group_size, path)

        options = ["Do you want to re-simulate for all groups?",
                    "Do you want to display results for all groups?",
                    "Do you want to run simulations only for the missing groups?",
                    "Do you want to change groups sizes?"
        ]

        if len(req_sims_sizes) != 0:
            print("------------------------------------")
            print(f"The database does not contain simulation results for the groups consisting of:  ")
            for i, val in enumerate(req_sims_sizes):
                print(val, end = ", ")
            print("------------------------------------")

            print(f"{options[0]} (Enter '1')")
            print(f"{options[2]} (Enter '2')")
            print(f"{options[3]} (Enter '3')")

            acceptance = int(input("\n: "))
            if acceptance == 2:
                acceptance = 3
        else:
            print("------------------------------------")
            print(f"  The database contains simulation \n    results for all the groups.")
            print("------------------------------------")
            print(f"{options[0]} (Enter '1')")
            print(f"{options[1]} (Enter '2')")
            print(f"{options[3]} (Enter '3')")

            acceptance = int(input("\n: "))
            if acceptance == 3:
                acceptance = 4

        if acceptance == 1:
            req_sims_sizes = []
            for i in range(group_size[0], group_size[1]):
                req_sims_sizes.append(i)
            break
        elif acceptance == 2:
            req_sims_sizes = 0
            break
        elif acceptance == 3:
            break
        else:
            continue
    
    return group_size, req_sims_sizes

def simulation(group_size, test_range, simulation_number):
    
    global paths
    single_sim_results = []
    complete_simulation_results = [0, 0, 0]
    trial = 0

    # print(f"\nSimulation number {simulation_number}")

    for i in range(test_range):
        trial = i + 1

        single_sim_results = generate_and_check_birthdays(group_size)
        
        for i, val in enumerate(single_sim_results):
            if val == True:
                complete_simulation_results[i] += 1
                val = False
                
        # if trial % (round(test_range/10)) == 0:
        #     print(f"\n{trial} trials were carried out")

    results = [percentage_calculation(complete_simulation_results[0], test_range),
                percentage_calculation(complete_simulation_results[1], test_range),
                percentage_calculation(complete_simulation_results[2], test_range)
    ]

    data = [group_size, test_range, results[0], results[1], results[2]]

    #saving sim results to log file
    log_save_simRes(data, paths.get("log"))

    #connecting and upadating/interting results to database
    db_conn_inf(data, paths.get("dba"), paths.get("log"))
    
def generate_and_check_birthdays(group_size):

    birthday_list = [random.randint(1, 366) for i in range(group_size)]
    checklist = [False, False, False] # [double birthday, triple birthday, quadruple birthday]

    for i in birthday_list:
        repeats = birthday_list.count(i)
        if repeats == 2:
            checklist[0] = True
        elif repeats == 3:
            checklist[1] = True
        elif repeats == 4:
            checklist[2] = True
    
    return checklist

def percentage_calculation(value, test_range):
    temp = float(round((value/test_range) * 100, 2))
    return temp if temp < 100 else 100

def display_results(group_size, path, path_log):

    results_data = db_results(group_size, path, path_log)
    
    df = pd.DataFrame(results_data, columns = ['Group size', 'Test range', 'Double birthday chance in %', 'Triple birthday chance in %', 'Quadruple birthday chance in %'])
    print(df)

def main():

    global paths
    test_range = 100_000

    # displaying configuration menu and taking a group range
    group_size, req_groupSizes_sim = conf_menu_display(test_range, paths.get("dba"))

    # writing in log file conf of simulation
    log_header_conf(group_size, test_range, paths.get("log"))

    apk_start_time = time.time()

    if req_groupSizes_sim != 0:

        # determining the optimum number of processes required
        # max usage = half of total cpu cores

        cores = mlp.cpu_count()  
        indicator_cores = round(int(len(req_groupSizes_sim) / 2)) 

        if indicator_cores <= (cores / 2):
            use_cores = indicator_cores
        else:
            use_cores = int(cores / 2)

        # main loop for simulations in group x -> y
        # creating processes for each simulation in the number specified to perform the scope of the program's operation

        processes = []
       
        
        for i, val in enumerate(req_groupSizes_sim):

            x = mlp.Process(target = simulation, args=(val, test_range, i + 1))
            processes.append(x)
            x.start()

            # blocking the opening of countless processes at once
            # waiting for processes to join before opening new processes
            if (i + 1) % use_cores == 0 and i > 0:
                elem = i - use_cores
                for _ in range(i - use_cores, i):
                    processes[elem].join()
                    elem += 1
                progress = (i / len(req_groupSizes_sim)) * 100
                print(f"Simulation progres {progress:2.2f}%...")
            elif (i + 1) == (group_size[1] - group_size[0]):
                elem = i - (i % use_cores)
                for _ in range(i - (i % use_cores), i + 1):
                    processes[elem].join()
                    elem += 1
                progress = (i / len(req_groupSizes_sim)) * 100
                print(f"Simulation progres {progress:2.2f}%...")

        print(f"Simulation progres 100%...")    
    
    #displaying results
    display_results(group_size, paths.get("dba"), paths.get("log"))

    # ending apk exec, saving time of exec. 
    run_time = time.time() - apk_start_time
    print(f"\nAplication completed task in {run_time:.3f}s")
    log_save_execTime(run_time,paths.get("log"))

if __name__ == '__main__':
    main()