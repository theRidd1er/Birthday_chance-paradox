import time

def log_header_conf(group_size, test_range, path):
    with open(path, 'a') as file:
        file.write(f"\n\n\n\n========== Simulation of Birthday Paradox ==========")
        file.write(f"\n\nConfiguration: \n")
        file.write(f"   - group size: {group_size[0]} -> {group_size[1] - 1};\n")   
        file.write(f"   - test range: {test_range};\n")   
        file.write(f"   - date&time:  {time.strftime('%B %d %Y %H:%M:%S', time.localtime())}\n\n")
        file.write(f"Double : Triple : Quadruple : Simulation time\n\n")

def log_save_execTime(run_time, path):
    with open(path, 'a') as file:
        file.write(f"\nSimulation completed in {run_time:.3f}s\n")
        file.write("\n====================================================")

def log_save_simRes(data, path):
    with open(path, 'a') as file:
        file.write(f"Group of {data[0]:2.0f}; {data[2]:2.2f}% : {data[3]:2.2f}% : {data[4]:2.2f}%\n")

def log_dbInsert(path):
    with open(path, 'a') as file:
        file.write(f"Data inserted to database\n")

def log_dbUpadate(path):
    with open(path, 'a') as file:
        file.write(f"Data updated in database\n")

def log_dbRead(path):
    with open(path, 'a') as file:
        file.write(f"Data read from database\n")