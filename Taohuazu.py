#! ./Administrator/AppData/Local/Programs/Python/Python37-32
# -*- coding: utf-8 -*-
import os
import random
import re
import time
from multiprocessing.pool import Pool

import requests
from bs4 import BeautifulSoup
from requests import RequestException
from urllib3.exceptions import ReadTimeoutError
from config import domain, testWebsite

def freeproxy():
    ipadress = []
    IP = []
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
        IP.append(dic_ip)
    return IP
def test_IP():
    ALLIPS = []
    ips = freeproxy()
    pool = Pool(32)
    useIP = pool.map(connect_IP, ips)
    for item in useIP:
        if item:
            ALLIPS.append(item)
    return ALLIPS

def connect_IP(_item):
    useIP = []
    try:
        html = requests.get(testWebsite, proxies=_item, timeout=2)

        if html.status_code == 200:
            print('WELL THIS IS GOOD IPADDERSS')
            print(_item)
            useIP.append(_item)
        return useIP
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

# 测试域名的可访问
def connect(_domain):
    """
    create the main domain which is most important things at first
    :param _domain: http://thz6.com
    :return: a dns which can get the code 200
    """
    try:
        html = requests.get(_domain, timeout=5)
        if html.status_code == 200:
            return _domain
    except RequestException:
        print('Wrong IP Adress!!')
        new_domain = str(input('Enter a new Domain\n')).strip()
        new_html = requests.get(new_domain)
        new_html.raise_for_status()
        return new_domain
    except TimeoutError:
        print('TimeOut')
        pass

# 最大页面数
def maxnums(_url):
    html = requests.get(_url)
    response = BeautifulSoup(html.text, 'lxml')
    lastnums = response.select('#fd_page_top > div > a.last')
    max_num = lastnums[0].get('href').split('-')[-1].replace('.html', '')
    return int(max_num) + 1


# 构建页面列表
def mainpages(_domain):
    asnocode, ascode, usnocode = [], [], []
    _ip = connect(_domain)
    # 亚洲無碼原創
    asnocode_ip = _ip + 'forum-181-1.html'
    # 亚洲有碼原創
    ascode_ip = _ip + 'forum-220-1.html'
    # 欧美無碼
    usnocode_ip = _ip + 'forum-182-1.html'

    for item_asnocode in range(1, maxnums(asnocode_ip)):
        next_asnocode = _ip + 'forum-181-{}.html'.format(item_asnocode)
        asnocode.append(next_asnocode)

    for item_ascode in range(1, 5):
        next_ascode = _ip + 'forum-220-{}.html'.format(item_ascode)
        ascode.append(next_ascode)

    for item_usnocode in range(1, maxnums(usnocode_ip)):
        next_usnocode = _ip + 'forum-182-{}.html'.format(item_usnocode)
        usnocode.append(next_usnocode)
    return asnocode, ascode, usnocode


# 所有等待下载的页面的url
def allpages(_url) -> list:
    """
    亚洲有码
    :param _url: like http://thz6.com/forum-220-1.html
    :return: a list about all page's urls
    """
    # stroe mian page
    urls = []
    try:
        speed = random.randint(40, 80)
        print(_url)
        page = requests.get(_url, timeout=5)
        # 位于哪个页面下的列表
        listnums = _url.split('-')[-1]
        # www头部
        header = _url.split('forum')[0] + 'thread-'

        #  http://thz6.com/thread-1875265-1-2.html
        if page.status_code == 200:
            responses = BeautifulSoup(page.text, 'lxml')

            pattern = re.compile(r'_(\d+)')

            ids = responses.select('tbody')
            for id in ids:
                result = re.search(pattern, str(id.get('id')))
                if result:
                    # url: hader + id + '-1-'+listNums
                    url = header + result.group(1) + '-1-' + listnums
                    urls.append(url)
        if speed >= 50:
            time.sleep(random.randint(1, 10))
        return urls
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


def parse(_url):
    sign_title = 'Taohuazu_桃花族 -  thz.la'
    sign_bt = "http://thz6.com/forum.php?mod=attachment&"
    pictrues = []

    _dir  = 'D:/Home/Pictures/'

    print("\nSource Root:{}\n".format(_url))

    html_next = requests.get(_url, timeout=5)
    if html_next.status_code == 200:
        responses = BeautifulSoup(html_next.text, 'lxml')
        title = responses.findAll('title')[0].get_text().replace(sign_title, '')
        # BT files
        torrents = responses.select('p.attnm > a')
        # pictures
        _img = re.compile(r'^aimg_.*')

        for _bt in torrents:
            url_bt = sign_bt + _bt.get('href').split('?')[1]
            path_bt = _dir + str(title) + '.torrent'
            download(_url=url_bt, _root=_dir, _path=path_bt)

        for pic in responses.find_all(id=_img):
            if pic.get('file'):
                pic_url = pic.get('file')
                pictrues.append(pic_url)
        if pictrues:
            for url_img, num in zip(set(pictrues), [nums for nums in range(0, len(set(pictrues)))]):
                path_img = _dir + str(title) + '-' + str(num) + '.jpg'
                download(_url=url_img, _root=_dir, _path=path_img)


def download(_url:str, _root, _path):
    """
    use for download url, need 3 params
    :param _url: needing url
    :param _root: os.makedirs
    :param _path: whole path in os include root and format
    :return:
    """
    # IP = test_IP()
    # ip = [{'http': '191.253.63.49:20183'},{'http': '222.88.147.104:8060'},{'http': '212.98.150.50:80'},{'http': '46.10.157.115:8080'},
    #       {'http': '201.147.242.186:8080'},{'http': '112.90.50.60:80'},{'http': '103.85.92.221:8080'},{'http': '217.219.25.19:8080'},
    #       {'http': '82.198.187.135:8081'},{'http': '118.24.157.22:3128'},{'http': '47.74.129.59:3128'},{'http': '177.47.63.202:3128'},
    #       {'http': '222.73.68.144:8090'},{'http': '177.69.83.11:80'},{'http': '46.225.248.13:53281'},{'http': '177.54.110.14:20183'}]
    # _proxy = random.sample(ip, 1)
    try:
        response = requests.get(_url, timeout=5)
        if response.status_code == 200:
            response.encoding = response.apparent_encoding
            if not os.path.exists(_root):
                os.makedirs(_root)
            if not os.path.exists(_path):
                print('Address : {}'.format(_path.split('/')[-1]))
                with open(_path, 'wb') as i:
                    i.write(response.content)
        time.sleep(random.randint(0,3))
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


def download_pages(_domain):
    urls = []
    as_nocode, as_code, usnocode = mainpages(_domain)
    # pool_page = Pool(5)
    # as_no_urls = pool_page.map(allpages, as_nocode)
    # as_urls = pool_page.map(allpages, as_code)
    # us_no_urls = pool_page.map(allpages, usnocode)
    for item in as_code:
        urls = urls + allpages(_url=item)
    return urls
    # pool_page.close()
    # pool_page.join()
    # return urls

def spider(_domain):
    ASCODE = download_pages(_domain)
    pool_ascode = Pool(5)
    pool_ascode.map(parse, ASCODE)
    pool_ascode.close()
    pool_ascode.join()

def run(_domain):
    URLS = spider(_domain)
    pool_download = Pool(10)
    pool_download.map(parse, URLS)

if __name__ == "__main__":
    # ip = test_IP()
    # for i in ip:
    #     print(i)
    # run(_domain=domain)
    spider(_domain=domain)
    # download_pages(_domain=domain)