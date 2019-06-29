# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from datetime import timedelta, datetime
import psycopg2
from prettytable import from_db_cursor

# ���ӵ����ݿ�
conn = psycopg2.connect(database="flight", user="postgres", password="hch17396", host="127.0.0.1", port="5432")
cur = conn.cursor()
cityCode = {'����': 'BJS', '����': 'CAN', '֣��': 'CGO', '����': 'CGQ', '̫ԭ': 'TYN', '��³ľ��': 'URC', '�ϲ�': 'KHN', '����': 'KWE',
            '����': 'KWL',
            '����': 'LXA', '����': 'KMG', '���': 'HKG', '����': 'HGH', '������': 'HRB', '�Ϻ�': 'SHA', '����': 'SHE', '����': 'SIA',
            'ʯ��ׯ': 'SJW',
            '�Ͼ�': 'NKG', '����': 'FOC', '����': 'XMN', '����': 'CKG', '��ɳ': 'CSX', '�ɶ�': 'CTU', '����': 'INC', '�Ϸ�': 'HFE',
            '����': 'SZX',
            '�人': 'WUH'}
# ���������������
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


# ���������������

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
            '''select avg(����Ʊ��) from {} where �������={} and position({} in ����ʱ��)>0 '''.format(dcity, repr(acity),
                                                                                            repr(x[i])))
        y.append(cur.fetchall())
        # cur.fetchall()���з�������
    y = [y[i][0] for i in range(0, 5)]
    plt.xlabel("����")
    plt.ylabel("ƽ���۸�")
    plt.title("�۸�����")
    plt.plot(x, y)
    plt.show()


def showTickets(dcity, acity, date, classType=None, child=None, baby=None, company=None, order=None):
    haschild = ''' and ��ͯ!='f' ''' if child is None else ''' and ��ͯ='����' '''
    hasbaby = ''' and Ӥ��!='1' ''' if baby is None else ''' and Ӥ��='����' '''
    order = '''''' if order is None else ''' order by ����Ʊ��'''
    company = '''  and ���չ�˾!='JOJO!' ''' if company is None else ''' and ���չ�˾={}'''.format(repr(company))
    classType='''''' if classType is None else ''' and ��λ={}'''.format(repr(classType))
    #ֻ����''''''  ������NoneȻ��ת����repr()
    cur.execute(
            '''select * from {} where �������={} and position({} in ����ʱ��)>0'''.format(dcity, repr(acity),
                                                                                              repr(date))+haschild+hasbaby+classType+company+order)
    x = from_db_cursor(cur)
    x.padding_width = 10
    # �������
    print(x)


showTickets("�ɶ�", '����', '2019-07-08',classType=None,child='2',order='1',company='�Ĵ�����')
