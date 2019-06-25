import json
import requests
import psycopg2
import time
#ʵ�ְ�װ����Щ��

conn = psycopg2.connect(database="flight", user="postgres", password="password", host="127.0.0.1", port="5432")
#���ӵ����ݿ������Ҫ�Լ���
print("Opened database successfully" + "\n")
cur = conn.cursor()

url = 'https://flights.ctrip.com/itinerary/api/12808/products'
#api

header = {}
header[
    'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'
header[
    'Cookie'] = ''
#�����cookie�Լ�ͨ��chrome�ļ�鹦�����Լ���

header['content-type'] = 'application/json'
	#��ʽ��json
#��������ͷ

cityCode = {"BJS": "����", "CAN": "����", "CGO": "֣��", "CGQ": "����", "TYN": "̫ԭ", "URC": "��³ľ��", "KHN": "�ϲ�"
    , "KWE": "����", "KWL": "����", "LXA": "����", "KMG": "����", "HKG": "���", "HGH": "����", "HRB": "������", "SHA": "�Ϻ�",
            "SHE": "����", "SIA": "����", "SJW": "ʯ��ׯ",
            "NKG": "�Ͼ�", "FOC": "����", "XMN": "����", "CKG": "����", "CSX": "��ɳ", "CTU": "�ɶ�", "INC": "����", "HFE": "�Ϸ�",
            "SZX": "����", "WUH": "�人"}
type = {"Y": '���ò�', "CF": '�����/ͷ�Ȳ�', "false": '��', "true": '��', "ALL": '����'}
city = ['SIA', 'CKG', 'SHE', 'CAN', 'FOC', 'SZX', 'HGH', 'NKG', 'SJW', 'XMN', 'CGO', 'KMG', 'SHA', 'KWL', 'HRB', 'LXA',
        'HKG', 'HFE', 'BJS', 'KWE', 'URC', 'INC', 'CTU', 'KHN', 'TYN', 'CSX', 'WUH', 'CGQ']
#��Ҫ����


def get_info(classType, hasChild, hasBaby, dcity, date):
    for acity in city:
        time.sleep(1)
	#��ֹ���챻���Ƶ��
        if not acity == dcity:
            data = {
                "flightWay": "Oneway",
                "classType": classType,
                "hasChild": hasChild,
                "hasBaby": hasBaby,
                "searchIndex": 1,
                "airportParams": [
                    {"dcity": dcity, "acity": acity, "dcityname": cityCode[dcity], "acityname": cityCode[acity],
                     "date": date}]
            }
	#��д��
            s = json.dumps(data)
            response = requests.post(url, data=s, headers=header).text
            routeList = json.loads(response)["data"].get('routeList')

            if routeList is not None:
                for route in routeList:
                    legs = route.get("legs")
                    for leg in legs:
                        flight = leg.get("flight")
                        characteristic = leg.get("characteristic")
                        flight_info = {}
                        if flight is not None and characteristic is not None:
                            flight_info["arrivalDate"] = flight["arrivalDate"]
                            flight_info["airlineName"] = flight["airlineName"]
                            flight_info["departureDate"] = flight["departureDate"]
                            flight_info["flightNumber"] = flight["flightNumber"]
                            flight_info["punctualityRate"] = flight["punctualityRate"]
                            flight_info["childPrice"] = characteristic["lowestChildPrice"] if classType == "Y" else \
                            characteristic["lowestChildCfPrice"]
                            flight_info["babyPrice"] = characteristic["lowestBabyPrice"]
                            flight_info["price"] = characteristic["lowestPrice"] if classType == "Y" else \
                            characteristic["lowestCfPrice"]
                            if flight_info["childPrice"] is None:
                                Child = '������'
                                flight_info["childPrice"] = '��'
                            else:
                                Child = '����'
                            if flight_info["babyPrice"] is None:
                                Baby = '������'
                                flight_info["babyPrice"] = '��'
                            else:
                                Baby = '����'

                            if flight_info["price"] is None:
                                flight_info["price"] = 999999  # �쳣
                            if flight_info["punctualityRate"] is None:
                                flight_info["punctualityRate"] = ""
                            try:
                                if not flight_info["price"] == 999999:
                                    cur.execute('''insert into {} values({},{},{},{},{},{},{},{},{},{},{},{},{})
                                                                                                                 '''.format(
                                        cityCode[dcity], repr(
                                            flight_info["flightNumber"]), repr(flight_info["airlineName"]),
                                        repr(type[classType]),
                                        repr(cityCode[dcity]),
                                        repr(cityCode[acity]), repr(
                                            flight_info["departureDate"]), repr(flight_info["arrivalDate"]),
                                        flight_info["price"], repr(flight_info["childPrice"]),
                                        repr(flight_info["babyPrice"]), repr(
                                            flight_info["punctualityRate"]), repr(Child), repr(Baby)))

		#ע��������Ҫ��repr()ת�������������ϵ����ţ�python�е����ź�˫����û������

                            except psycopg2.IntegrityError:
                                pass
                            conn.commit()
                            # repr()
                        else:
                            pass


# ��������Ϊ��۵ļ�¼����


if __name__ == '__main__':
    create = False
    # ����
    delete = False
    # ����
    date = '2019-07-10'
    # ����
    for dcity in city:
        # ����
        if delete == True:
            cur.execute('''drop table {}'''.format(cityCode[dcity]))
            conn.commit()
	#�����ύ
        else:
            pass

        if create == True:
            cur.execute('''CREATE TABLE {}
                        (����� varchar(10)  not null,
                         ���չ�˾ varchar(10) not null,
                         ��λ varchar(10) not null,
                         �������� text not null,
                         ������� text not null,
                         ����ʱ�� varchar(30) not null,
                         ����ʱ�� varchar(30) not null,
                         ����Ʊ�� int ,
                         ��ͯƱ�� varchar(6),
                         Ӥ��Ʊ�� varchar(6),
                         ׼ʱ�� varchar(5),
                         ��ͯ varchar(5),
                         Ӥ�� varchar(5),
                         constraint {}flightID_pk primary key(�����,����ʱ��,����ʱ��,��λ)
                        );
                        '''.format(cityCode[dcity], dcity))
            conn.commit()
        else:
            pass

        print("���ݿ�����¼��{}-{}-{}�ĺ�����Ϣ index={}\n".format(cityCode[dcity], dcity, date, city.index(dcity)))
        for classType in ("Y", "CF"):
            get_info(classType, 'false', 'false', dcity, date)
    conn.close()
