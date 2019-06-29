# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from datetime import timedelta, datetime
import psycopg2
from prettytable import from_db_cursor

# 连接到数据库
conn = psycopg2.connect(database="flight", user="postgres", password="hch17396", host="127.0.0.1", port="5432")
cur = conn.cursor()
cityCode = {'北京': 'BJS', '广州': 'CAN', '郑州': 'CGO', '长春': 'CGQ', '太原': 'TYN', '乌鲁木齐': 'URC', '南昌': 'KHN', '贵阳': 'KWE',
            '桂林': 'KWL',
            '拉萨': 'LXA', '昆明': 'KMG', '香港': 'HKG', '杭州': 'HGH', '哈尔滨': 'HRB', '上海': 'SHA', '沈阳': 'SHE', '西安': 'SIA',
            '石家庄': 'SJW',
            '南京': 'NKG', '福州': 'FOC', '厦门': 'XMN', '重庆': 'CKG', '长沙': 'CSX', '成都': 'CTU', '银川': 'INC', '合肥': 'HFE',
            '深圳': 'SZX',
            '武汉': 'WUH'}
# 解决中文乱码问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


# 解决中文乱码问题

def get_days_after_today(n):
    now = datetime.now()
    if (n < 0):
        return datetime(now.year, now.month, now.day)
    else:
        n_days_after = now + timedelta(days=n)
        return datetime(n_days_after.year, n_days_after.month, n_days_after.day)


def draw_analysis(dcity, acity):
    date_list = list(str(get_days_after_today(n))[:-9] for n in range(7, 12))
    x = date_list.copy()
    y = []
    for i in range(0, 5):
        temp = cur.execute(
            '''select avg(成人票价) from {} where 到达城市={} and position({} in 出发时间)>0 '''.format(dcity, repr(acity),
                                                                                            repr(x[i])))
        y.append(cur.fetchall())
        # cur.fetchall()所有返回数据
    y = [y[i][0] for i in range(0, 5)]
    plt.xlabel("日期")
    plt.ylabel("平均价格")
    plt.title("价格走势")
    plt.plot(x, y)
    plt.show()


def showTickets(dcity, acity, date, classType=None, child=None, baby=None, company=None, order=None):
    haschild = ''' and 儿童!='f' ''' if child is None else ''' and 儿童='包含' '''
    hasbaby = ''' and 婴儿!='1' ''' if baby is None else ''' and 婴儿='包含' '''
    order = '''''' if order is None else ''' order by 成人票价'''
    company = '''  and 航空公司!='JOJO!' ''' if company is None else ''' and 航空公司={}'''.format(repr(company))
    classType='''''' if classType is None else ''' and 舱位={}'''.format(repr(classType))
    #只能用''''''  不能用None然后转换成repr()
    cur.execute(
            '''select * from {} where 到达城市={} and position({} in 出发时间)>0'''.format(dcity, repr(acity),
                                                                                              repr(date))+haschild+hasbaby+classType+company+order)
    x = from_db_cursor(cur)
    x.padding_width = 10
    # 调整宽度
    print(x)


showTickets("成都", '北京', '2019-07-08',classType=None,child='2',order='1',company='四川航空')
