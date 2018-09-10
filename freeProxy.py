#! ./Administrator/AppData/Local/Programs/Python/Python37-32
# -*- coding: utf-8 -*-
import re
from multiprocessing.pool import Pool

import requests
from requests import RequestException
from urllib3.exceptions import ReadTimeoutError

from config import testWebsite


def freeproxy():
    ipadress = []
    ips = []
    pattern = re.compile(r'(\d+\.\d+\.\d+\.\d+:\d+)\n')
    with open('D:/Projects/Taohuazu/IPaddress.txt', encoding='utf-8') as ip:
        lines = ip.readlines()
        for i in lines:
            result = re.search(pattern, str(i))
            if result:
                ipadress.append(result.group(1))
    for item in ipadress:
        dic_ip = {
            'http': item
        }
        ips.append(dic_ip)
    return ips


def test_ip():
    allips = []
    ips = freeproxy()
    pool = Pool(32)
    useip = pool.map(connect_ip, ips)
    for item in useip:
        if item:
            allips.append(item)
    return allips


def connect_ip(_item):
    useip = []
    try:
        html = requests.get(testWebsite, proxies=_item, timeout=2)

        if html.status_code == 200:
            print('WELL THIS IS GOOD IPADDERSS')
            print(_item)
            useip.append(_item)
        return useip
    except RequestException:
        print('请求出错')
        pass
    except TimeoutError:
        print('连接超时')
        pass
    except ReadTimeoutError:
        print('读取超时')
        pass
    except ConnectionError:
        print('连接错误')
        pass
