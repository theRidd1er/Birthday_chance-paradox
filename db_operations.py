import sqlite3 as sql3
from read_write import log_dbInsert, log_dbUpadate, log_dbRead

def create_connection(path):

    # create a database connection
    conn = None

    try:
        conn = sql3.connect(path)
    except sql3.Error as e:
        print(e)
        return 0
     
    return conn

def db_conn_update(data, conn, path_log):
    with conn:

        upd_data = [round(data[2], 2), round(data[3], 2), round(data[4], 2), data[0], data[1]]

        sql = ''' UPDATE Sim_res 
                    SET Res_double = ?, 
                    Res_triple = ?,
                    Res_quadruple = ?
                    WHERE Group_size = ? AND 
                    Test_range = ?; '''

        cur = conn.cursor()
        cur.execute(sql, upd_data)
        conn.commit

        log_dbUpadate(path_log)

def db_conn_insert(data, conn, path_log):
    sql = ''' INSERT INTO Sim_res (Group_size, Test_range, Res_double, Res_triple, Res_quadruple)
                VALUES (?,?,?,?,?) '''

    cur = conn.cursor()
    cur.execute(sql, data, )
    conn.commit

    log_dbInsert(path_log)

def check_if_exist_record(group_size, test_range, conn):
    
    sql = ''' SELECT ID_sim FROM Sim_res WHERE Group_size = ? AND Test_range = ?'''

    cur = conn.cursor()
    cur.execute(sql, (group_size, test_range, ))
    conn.commit

    data = cur.fetchall()

    if len(data) == 1:
        return 1
    else:
        return 0

def db_conn_inf(data, path, path_log):

    conn = create_connection(path)

    is_exist = check_if_exist_record(data[0], data[1], conn)

    if is_exist == 1:
        db_conn_update(data, conn, path_log)
    else:
        db_conn_insert(data, conn, path_log)

def db_results(group_size, path, path_log):

    conn = create_connection(path)

    sql = ''' SELECT Group_size, Test_range, Res_double, Res_triple, Res_quadruple FROM Sim_res 
                WHERE Group_size > ? AND Group_size <= ?'''

    cur = conn.cursor()
    cur.execute(sql, (group_size[0], group_size[1], ))
    conn.commit

    data = cur.fetchall()

    log_dbRead(path_log)

    return data

def db_done_sims(group_size, path):

    conn = create_connection(path)

    sql = ''' SELECT Group_size FROM Sim_res 
                WHERE Group_size >= ? AND
                Group_size < ?
                ORDER BY Group_size ASC'''

    cur = conn.cursor()
    cur.execute(sql, (group_size[0], group_size[1], ))
    conn.commit

    data = cur.fetchall()
    
    sims = []
    for i in range(group_size[0], group_size[1]):
        sims.append(i)

    sims_to_exec = []
    for i in range(len(data)):
        sims_to_exec.append(data[i][0])

    total_list = sims + sims_to_exec
    req_sims = []

    for i in total_list:
        repeats = total_list.count(i)
        if repeats != 2:
            req_sims.append(i)

    return req_sims
