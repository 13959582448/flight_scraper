import json
import requests
import psycopg2
import time
#实现安装好这些库

conn = psycopg2.connect(database="flight", user="postgres", password="password", host="127.0.0.1", port="5432")
#连接的数据库参数需要自己改
print("Opened database successfully" + "\n")
cur = conn.cursor()

url = 'https://flights.ctrip.com/itinerary/api/12808/products'
#api

header = {}
header[
    'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'
header[
    'Cookie'] = ''
#这里的cookie自己通过chrome的检查功能找自己的

header['content-type'] = 'application/json'
	#格式是json
#构造请求头

cityCode = {"BJS": "北京", "CAN": "广州", "CGO": "郑州", "CGQ": "长春", "TYN": "太原", "URC": "乌鲁木齐", "KHN": "南昌"
    , "KWE": "贵阳", "KWL": "桂林", "LXA": "拉萨", "KMG": "昆明", "HKG": "香港", "HGH": "杭州", "HRB": "哈尔滨", "SHA": "上海",
            "SHE": "沈阳", "SIA": "西安", "SJW": "石家庄",
            "NKG": "南京", "FOC": "福州", "XMN": "厦门", "CKG": "重庆", "CSX": "长沙", "CTU": "成都", "INC": "银川", "HFE": "合肥",
            "SZX": "深圳", "WUH": "武汉"}
type = {"Y": '经济舱', "CF": '商务舱/头等舱', "false": '无', "true": '有', "ALL": '不限'}
city = ['SIA', 'CKG', 'SHE', 'CAN', 'FOC', 'SZX', 'HGH', 'NKG', 'SJW', 'XMN', 'CGO', 'KMG', 'SHA', 'KWL', 'HRB', 'LXA',
        'HKG', 'HFE', 'BJS', 'KWE', 'URC', 'INC', 'CTU', 'KHN', 'TYN', 'CSX', 'WUH', 'CGQ']
#主要城市


def get_info(classType, hasChild, hasBaby, dcity, date):
    for acity in city:
        time.sleep(1)
	#防止过快被检测频繁
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
	#填写表单
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
                                Child = '不包含'
                                flight_info["childPrice"] = '无'
                            else:
                                Child = '包含'
                            if flight_info["babyPrice"] is None:
                                Baby = '不包含'
                                flight_info["babyPrice"] = '无'
                            else:
                                Baby = '包含'

                            if flight_info["price"] is None:
                                flight_info["price"] = 999999  # 异常
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

		#注意这里需要用repr()转换成真正意义上的引号，python中的引号和双引号没有区别

                            except psycopg2.IntegrityError:
                                pass
                            conn.commit()
                            # repr()
                        else:
                            pass


# 出发城市为香港的记录暂无


if __name__ == '__main__':
    create = False
    # 更改
    delete = False
    # 更改
    date = '2019-07-10'
    # 更改
    for dcity in city:
        # 更改
        if delete == True:
            cur.execute('''drop table {}'''.format(cityCode[dcity]))
            conn.commit()
	#事务提交
        else:
            pass

        if create == True:
            cur.execute('''CREATE TABLE {}
                        (航班号 varchar(10)  not null,
                         航空公司 varchar(10) not null,
                         舱位 varchar(10) not null,
                         出发城市 text not null,
                         到达城市 text not null,
                         出发时间 varchar(30) not null,
                         到达时间 varchar(30) not null,
                         成人票价 int ,
                         儿童票价 varchar(6),
                         婴儿票价 varchar(6),
                         准时率 varchar(5),
                         儿童 varchar(5),
                         婴儿 varchar(5),
                         constraint {}flightID_pk primary key(航班号,出发时间,到达时间,舱位)
                        );
                        '''.format(cityCode[dcity], dcity))
            conn.commit()
        else:
            pass

        print("数据库正在录入{}-{}-{}的航班信息 index={}\n".format(cityCode[dcity], dcity, date, city.index(dcity)))
        for classType in ("Y", "CF"):
            get_info(classType, 'false', 'false', dcity, date)
    conn.close()
