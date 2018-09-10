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

from config import domain


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
    """

    :param _url: 主要类型下第一个页面
    :return: 最大值
    """
    html = requests.get(_url)
    response = BeautifulSoup(html.text, 'lxml')
    lastnums = response.select('#fd_page_top > div > a.last')
    max_num = lastnums[0].get('href').split('-')[-1].replace('.html', '')
    return int(max_num) + 1


# 构建页面列表
def mainpages(_domain):
    """
    检查域名正确性并且构造所有主页面
    :param _domain: 传入域名
    :return: 返回构造的主页面
    """
    asnocode, ascode, usnocode = [], [], []
    _ip = connect(_domain)
    # 亚洲無碼原創特征
    asnocode_ip = _ip + 'forum-181-1.html'
    # 亚洲有碼原創特征
    ascode_ip = _ip + 'forum-220-1.html'
    # 欧美無碼特征
    usnocode_ip = _ip + 'forum-182-1.html'

    # 为避免下载任务沉重,可直接修改爬取页面的范围,例如1到20即可,约莫需要半小时
    for item_asnocode in range(1, maxnums(asnocode_ip)):
        next_asnocode = _ip + 'forum-181-{}.html'.format(item_asnocode)
        asnocode.append(next_asnocode)

    for item_ascode in range(5, maxnums(ascode_ip)):
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
        # 页码
        listnums = _url.split('-')[-1]
        # www头部
        header = _url.split('forum')[0] + 'thread-'

        #  http://thz6.com/thread-1875265-1-2.html
        if page.status_code == 200:
            responses = BeautifulSoup(page.text, 'lxml')

            pattern = re.compile(r'_(\d+)')

            ids = responses.select('tbody')
            for _id in ids:
                result = re.search(pattern, str(_id.get('id')))
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


# 解析每个页面下的图片和种子并且提供下载
def parse(_url):
    """
    解析最终结果页面,并且进行下载
    :param _url:
    :return:
    """
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


# 下载功能
def download(_url:str, _root, _path):
    """
    use for download url, need 3 params
    :param _url: needing url
    :param _root: os.makedirs
    :param _path: whole path in os include root and format
    :return: 0
    """
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


# 得到所有待下载的页面总表,以包的形式返回
def download_pages(_domain):
    """
    所有等待下载的页面
    :param _domain: 域名
    :return: 页面列表
    """
    as_no_code_urls, as_code_urls, us_no_code_urls = [], [],[]
    as_nocode, as_code, usnocode = mainpages(_domain)
    for item_asnocode, item_ascode, item_usnocode in zip(as_nocode, as_code, usnocode):
        as_no_code_urls = as_no_code_urls + allpages(_url=item_asnocode)
        as_code_urls = as_code_urls + allpages(_url=item_ascode)
        us_no_code_urls = us_no_code_urls + allpages(_url=item_usnocode)
    return as_no_code_urls, as_code_urls, us_no_code_urls


# 解压包,开启多线程
def run(_domain):
    """
    开启多线程
    :param _domain: 域名
    :return: 0
    """
    porn = download_pages(_domain)
    pool_ = Pool(16)
    for asnocode, ascode, usnocode in zip(porn):
        pool_.map(parse, asnocode)
        pool_.map(parse, ascode)
        pool_.map(parse, usnocode)
    pool_.close()
    pool_.join()

if __name__ == "__main__":
    run(_domain=domain)
