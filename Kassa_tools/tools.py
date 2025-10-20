# Kassa_tools/tools.py

import datetime
import pymysql as sql
import configparser

# ---------- CONFIG ----------
configParser = configparser.RawConfigParser()
configFilePath = "Kassa_tools/kassa.conf"
configParser.read(configFilePath)

DB_NAME = configParser.get('CONFIG', 'DATABASE')
DB_USER = configParser.get('CONFIG', 'USER')
DB_PASS = configParser.get('CONFIG', 'PASSWORD')
DB_HOST = configParser.get('CONFIG', 'HOST')

# ---------- DB HELPERS (single source of truth) ----------
def get_conn(database=None, autocommit=False):
    """Create a PyMySQL connection using keyword-only args."""
    return sql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=(database or DB_NAME),
        charset="utf8mb4",
        autocommit=autocommit
    )

def make_request(query, params=None, database=None):
    """SELECT helper with optional params and db override."""
    with get_conn(database=database, autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            return cur.fetchall()

def write_to_db(query, params=None, database=None, autocommit=True):
    """INSERT/UPDATE/DELETE helper with params; returns lastrowid if any."""
    with get_conn(database=database, autocommit=autocommit) as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            last_id = cur.lastrowid
        if not autocommit:
            conn.commit()
    return last_id

# ---------- CONSTANTS / STATE ----------
period_list = [1, 1, 1, 1]

summ_before_period = {
    "nadhodjennya": 0,
    "vydacha": 0,
    "vytraty_za_tovar": 0,
    "vytraty_za_tovar_pid_zvit": 0,
    "vytraty_pid_zvit": 0,
    "vytraty": 0
}

summ_cur_period = {
    "nadhodjennya": 0,
    "vydacha": 0,
    "vytraty_za_tovar": 0,
    "vytraty_za_tovar_pid_zvit": 0,
    "vytraty_pid_zvit": 0,
    "vytraty": 0
}

transaction_type = {
    0: "надходження",
    1: "видача",
    2: "видача за товар",
    3: "видача за товар під звіт",
    4: "видача під звіт",
    5: "гроші до видачі в кассі",
    6: ""
}

polymer = [
    "пе-бн", "ящик-бн", "стр-бн", "пет-бн", "пет-преформа-бн", "пет-пробка-бн",
    "етикетка", "лента-пет-бн", "пп-беги-бн", "пет-пр-бн", "пе-цв-бн",
    "пет-мікс-бн", "пе-сіp"
]

makulatura = ["5б-бн", "лоток-бн", "гільза-бн", "8в-бн"]

# ---------- UTIL FUNCS ----------
def get_period(i: int) -> int:
    """Map UI period index to days back."""
    return {1: 0, 2: 7, 3: 31}.get(i, 0)

def _date_cutoff(days_back: int) -> str:
    now = datetime.datetime.now() - datetime.timedelta(days=days_back or 0)
    return now.strftime('%Y-%m-%d')

# ---------- PUBLIC DB OPS ----------
def make_weight_request(doc_number):
    """Read from 'vasy' DB."""
    return make_request(
        "SELECT * FROM records WHERE id = %s",
        params=(doc_number,),
        database="vasy"
    )

def get_last_money():
    result = make_request("SELECT * FROM v_kasse")
    print(result[0][0])
    return result[0][0]

def get_summ_vydacha():
    result = make_request("SELECT * FROM v_kasse")
    print(result[0][0])
    return result[0][0]

def get_summ_req(period, table, op_type):
    """Sum strictly BEFORE the cutoff date."""
    days = get_period(period)
    cutoff = _date_cutoff(days)
    if op_type == 0:
        rq = make_request(f"SELECT SUM(summa) FROM {table} WHERE data < %s", (cutoff,))
    else:
        rq = make_request(
            f"SELECT SUM(summa) FROM {table} WHERE op_type = %s AND data < %s",
            (op_type, cutoff)
        )
    return rq[0][0] or 0

def get_summ_cur_req(period, table, op_type):
    """Sum ON/AFTER the cutoff date."""
    days = get_period(period)
    cutoff = _date_cutoff(days)
    if op_type == 0:
        rq = make_request(f"SELECT SUM(summa) FROM {table} WHERE data >= %s", (cutoff,))
    else:
        rq = make_request(
            f"SELECT SUM(summa) FROM {table} WHERE op_type = %s AND data >= %s",
            (op_type, cutoff)
        )
    return rq[0][0] or 0

def get_summ_period():
    global summ_before_period
    rq_nadhod     = get_summ_req(period_list[2], 'nadhodjennya', 0)
    rq_vydacha    = get_summ_req(period_list[0], 'vydacha',      5)
    rq_vyd_tov    = get_summ_req(period_list[3], 'vydacha',      2)
    rq_vyd_tov_z  = get_summ_req(period_list[3], 'vydacha',      3)
    rq_vyd_z      = get_summ_req(period_list[1], 'vydacha',      4)
    rq_vyd        = get_summ_req(period_list[1], 'vydacha',      1)
    summ_before_period = {
        "nadhodjennya": rq_nadhod,
        "vydacha": rq_vydacha,
        "vytraty_za_tovar": rq_vyd_tov,
        "vytraty_za_tovar_pid_zvit": rq_vyd_tov_z,
        "vytraty_pid_zvit": rq_vyd_z,
        "vytraty": rq_vyd
    }
    print(summ_before_period)
    return summ_before_period

def get_summ_cur():
    global summ_cur_period
    rq_nadhod     = get_summ_cur_req(period_list[2], 'nadhodjennya', 0)
    rq_vydacha    = get_summ_cur_req(period_list[0], 'vydacha',      5)
    rq_vyd_tov    = get_summ_cur_req(period_list[3], 'vydacha',      2)
    rq_vyd_tov_z  = get_summ_cur_req(period_list[3], 'vydacha',      3)
    rq_vyd_z      = get_summ_cur_req(period_list[1], 'vydacha',      4)
    rq_vyd        = get_summ_cur_req(period_list[1], 'vydacha',      1)
    summ_cur_period = {
        "nadhodjennya": rq_nadhod,
        "vydacha": rq_vydacha,
        "vytraty_za_tovar": rq_vyd_tov,
        "vytraty_za_tovar_pid_zvit": rq_vyd_tov_z,
        "vytraty_pid_zvit": rq_vyd_z,
        "vytraty": rq_vyd
    }
    print(summ_cur_period)
    return summ_cur_period

def add_transaction(transaction):
    db_name = "nadhodjennya" if transaction.op_type == 0 else "vydacha"
    query = f"""
        INSERT INTO {db_name}
        (data, kontragent, summa, pid_zvit, annot, op_type, stattya_vytrat)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        transaction.data,
        transaction.kontragent,
        float(transaction.summa),
        int(transaction.zvit),
        transaction.annot,
        int(transaction.op_type),
        transaction.stattya_vytrat or ""
    )
    print(query, params)
    write_to_db(query, params=params)

    # Emit only if set
    if getattr(transaction, "comm", None):
        transaction.comm.reload_all.emit()

def edit_transaction(transaction, id, summa, op_type, annot, data, stattya_vytrat):
    """Edit and keep row in correct table based on *new* op_type."""
    db_name = "nadhodjennya" if int(op_type) == 0 else "vydacha"
    data_str = data.strftime('%Y-%m-%d') if hasattr(data, "strftime") else str(data)
    query = f"""
        UPDATE {db_name}
        SET summa=%s, pid_zvit=%s, annot=%s, op_type=%s, data=%s, stattya_vytrat=%s
        WHERE id=%s
    """
    params = (
        float(summa),
        0,
        annot,
        int(op_type),
        data_str,
        (stattya_vytrat or ""),
        int(id)
    )
    print(query, params)
    write_to_db(query, params=params)

    if getattr(transaction, "comm", None):
        transaction.comm.reload_all.emit()

def get_kontragents():
    rq = make_request("SELECT kontragent FROM vydacha")
    kontragents = {row[0] for row in rq if row and row[0]}
    print(kontragents)
    return kontragents

def get_stattya_vytrat():
    vytraty = set()
    for table in ("vydacha", "nadhodjennya"):
        rq = make_request(f"SELECT stattya_vytrat FROM {table}")
        for elem in rq:
            if elem and elem[0]:
                vytraty.add(elem[0])
    print(vytraty)
    return vytraty
