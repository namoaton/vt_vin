import datetime
import pymysql as sql
import configparser
# from Kassa import comm

# Create conf file in  Kassa_tools/kassa.conf
# with  such content

# [CONFIG]
# DATABASE = db_name
# USER = db_username
# PASSWORD= db_password
# HOST = ip address of db

configParser = configparser.RawConfigParser()
configFilePath = "Kassa_tools/kassa.conf"
configParser.read(configFilePath)
database = configParser.get('CONFIG', 'DATABASE')
user = configParser.get('CONFIG', 'USER')
password = configParser.get('CONFIG', 'PASSWORD')
host = configParser.get('CONFIG', 'HOST')

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


def get_period(i):
    if i == 1:
        return 0
    if i == 2:
        return 7
    if i == 3:
        return 31


def make_request(query):
    db = sql.connect(
        host, user, password, database, use_unicode=True, charset="utf8")
    cur = db.cursor()
    cur.execute(query)
    result = cur.fetchall()
    cur.close()
    db.close()
    return result


def make_weight_request(doc_number):
    db = sql.connect(
        host, user, password, "vasy", use_unicode=True, charset="utf8")
    cur = db.cursor()
    query = "SELECT * FROM records WHERE id = %s" % doc_number
    cur.execute(query)
    result = cur.fetchall()
    cur.close()
    db.close()
    return result


def write_to_db(query):
    db = sql.connect(
        host, user, password, database, use_unicode=True, charset="utf8")
    cur = db.cursor()
    cur.execute(query)
    cur_id = cur.lastrowid
    db.commit()
    cur.close()
    db.close()
    return cur_id


def get_last_money():
    result = make_request("SELECT * FROM v_kasse")
    print(result[0][0])
    return result[0][0]


def get_summ_vydacha():
    result = make_request("SELECT * FROM v_kasse")
    print(result[0][0])
    return result[0][0]


def get_summ_req(period, table, op_type):
    period = get_period(period_list[2])
    now = datetime.datetime.now() - datetime.timedelta(days=period)
    formatted_date = now.strftime('%Y-%m-%d')
    if op_type == 0:
        rq = make_request("SELECT sum(summa) FROM %s WHERE data<'%s'" %
                          (table, formatted_date))
    else:
        rq = make_request(
            "SELECT sum(summa) FROM %s WHERE op_type=%d and  data<'%s'" %
            (table, op_type, formatted_date))
    # print(rq_nadhod)
    if rq[0][0]:
        return rq[0][0]
    return 0


def get_summ_cur_req(period, table, op_type):
    period = get_period(period_list[2])
    now = datetime.datetime.now() - datetime.timedelta(days=period)
    formatted_date = now.strftime('%Y-%m-%d')
    if op_type == 0:
        rq = make_request("SELECT sum(summa) FROM %s WHERE data>='%s'" %
                          (table, formatted_date))
    else:
        rq = make_request(
            "SELECT sum(summa) FROM %s WHERE op_type=%d and  data>='%s'" %
            (table, op_type, formatted_date))
    # print(rq_nadhod)
    if rq[0][0]:
        return rq[0][0]
    return 0


def get_summ_period():
    # nadhodjennya
    global summ_before_period
    rq_nadhod = get_summ_req(period_list[2], 'nadhodjennya', 0)
    # do vydachy
    rq_vydacha = get_summ_req(period_list[0], 'vydacha', 5)
    # vydacha_za tovar
    rq_vyd_tov = get_summ_req(period_list[3], 'vydacha', 2)
    # vydacha za tovar pid zvit
    rq_vyd_tov_z = get_summ_req(period_list[3], 'vydacha', 3)
    # vydacha pid zvit
    rq_vyd_z = get_summ_req(period_list[1], 'vydacha', 4)
    # vydacha
    rq_vyd = get_summ_req(period_list[1], 'vydacha', 1)
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
    # nadhodjennya
    global summ_cur_period
    rq_nadhod = get_summ_cur_req(period_list[2], 'nadhodjennya', 0)
    # do vydachy
    rq_vydacha = get_summ_cur_req(period_list[0], 'vydacha', 5)
    # vydacha_za tovar
    rq_vyd_tov = get_summ_cur_req(period_list[3], 'vydacha', 2)
    # vydacha za tovar pid zvit
    rq_vyd_tov_z = get_summ_cur_req(period_list[3], 'vydacha', 3)
    # vydacha pid zvit
    rq_vyd_z = get_summ_cur_req(period_list[1], 'vydacha', 4)
    # vydacha
    rq_vyd = get_summ_cur_req(period_list[1], 'vydacha', 1)
    summ_cur_period = {
        "nadhodjennya": rq_nadhod,
        "vydacha": rq_vydacha,
        "vytraty_za_tovar": rq_vyd_tov,
        "vytraty_za_tovar_pid_zvit": rq_vyd_tov_z,
        "vytraty_pid_zvit": rq_vyd_z,
        "vytraty": rq_vyd
    }
    print(summ_cur_period)
    return  summ_cur_period


def add_transaction(transaction):
    db_name = "vydacha"
    if transaction.op_type == 0:
        db_name = "nadhodjennya"
    query = "INSERT INTO %s(data,kontragent, summa, pid_zvit, annot, op_type, stattya_vytrat) VALUES('%s','%s',%.2f,%d," \
            "'%s',%d,'%s')" % (
                db_name, transaction.data, transaction.kontragent, transaction.summa,
                transaction.zvit, transaction.annot, transaction.op_type, transaction.stattya_vytrat)
    print(query)
    write_to_db(query)
    transaction.comm.reload_all.emit()


def edit_transaction(transaction, id, summa, op_type, annot, data, stattya_vytrat):
    db_name = "vydacha"
    data_str = data.strftime('%Y-%m-%d')
    if transaction.op_type == 0:
        db_name = "nadhodjennya"
    query = "UPDATE %s SET summa=%s, pid_zvit=0,annot='%s',op_type=%d, data='%s', stattya_vytrat='%s' WHERE id=%s" % (
        db_name, summa, annot, op_type, data_str, stattya_vytrat, id)
    print(query)
    write_to_db(query)
    transaction.comm.reload_all.emit()

def get_kontragents():
    query = "SELECT kontragent FROM vydacha"
    rq = make_request(query)
    kontragents  = set()
    for elem in rq:
        kontragents.add(elem[0])
    print (kontragents)
    return kontragents

def get_stattya_vytrat():
    query = "SELECT stattya_vytrat FROM vydacha"
    rq = make_request(query)
    vytraty = set()
    for elem in rq:
        vytraty.add(elem[0])
        print(elem)
    query = "SELECT stattya_vytrat FROM  nadhodjennya"
    rq = make_request(query)
    for elem in rq:
        vytraty.add(elem[0])
        # print(elem)
    print(vytraty)
    return  vytraty