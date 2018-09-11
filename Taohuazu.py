#! ./Administrator/AppData/Local/Programs/Python/Python37-32
# -*- coding: utf-8 -*-
import os
import random
import re
import time
from multiprocessing.pool import Pool

import requests
from bs4 import BeautifulSoup
from requests import RequestException, ConnectTimeout
from urllib3.exceptions import ReadTimeoutError

from libs.config import domain, Asia_nocode, Asia_code, US_nocode


def connect(_domain):
    """
    测试域名的可访问
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
    except ConnectTimeout:
        print('ConnectTimeout')
        pass


def maxnums(_url):
    """
    最大页面数
    :param _url: 主要类型下第一个页面
    :return: 最大值
    """
    html = requests.get(_url)
    response = BeautifulSoup(html.text, 'lxml')
    lastnums = response.select('#fd_page_top > div > a.last')
    max_num = lastnums[0].get('href').split('-')[-1].replace('.html', '')
    return int(max_num) + 1


def pages(_domain):
    """
    检查域名正确性并且构造所有主页面,得到所有待下载的页面总表
    :param _domain: 传入域名
    :return: 返回构造的主页面
    """
    asnocode, ascode, usnocode, urls = [], [], [], []
    _ip = connect(_domain)
    # 亚洲無碼原創特征
    asnocode_ip = _ip + 'forum-181-1.html'
    # 亚洲有碼原創特征
    ascode_ip = _ip + 'forum-220-1.html'
    # 欧美無碼特征
    usnocode_ip = _ip + 'forum-182-1.html'

    # 为避免下载任务沉重,可直接修改爬取页面的范围,例如1到20即可,约莫需要半小时
    #  1-10
    for item_asnocode in range(1, maxnums(asnocode_ip)):
        next_asnocode = _ip + 'forum-181-{}.html'.format(item_asnocode)
        asnocode += onepage(_urls=next_asnocode)
    # 10-20
    for item_ascode in range(1, maxnums(ascode_ip)):
        next_ascode = _ip + 'forum-220-{}.html'.format(item_ascode)
        ascode += onepage(_urls=next_ascode)
    # 1-10
    for item_usnocode in range(1, maxnums(usnocode_ip)):
        next_usnocode = _ip + 'forum-182-{}.html'.format(item_usnocode)
        usnocode += onepage(_urls=next_usnocode)
    urls = asnocode + ascode + usnocode
    return urls


def onepage(_urls) -> list:
    """
    一个主页面下的待下载的URLs
    :param _urls: like http://thz6.com/forum-220-1.html
    :return: a list about all page's urls
    """
    # stroe mian page
    urls = []
    try:
        speed = random.randint(40, 80)
        print(_urls)
        page = requests.get(_urls, timeout=5)
        # 页码
        listnums = _urls.split('-')[-1]
        # www头部
        header = _urls.split('forum')[0] + 'thread-'

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
            time.sleep(random.randint(1, 5))
        return urls
    except RequestException:
        print('Request Error')
        pass
    except TimeoutError:
        print('TimeoutError')
        pass
    except ReadTimeoutError:
        print('ReadTimeoutError')
        pass
    except ConnectionError:
        print('ConnectionError')
        pass
    except ConnectTimeout:
        print('ConnectTimeout')
        pass


# 用于更新的,可定制爬取页数的三大功能类似方法:
def pages_as_nocode(_domain,_min, _max) -> list:
    """
    亚洲无码
    :param _domain: 网站域名
    :param _min: 最小值
    :param _max: 最大值
    :return: 该区间内所有的等待下载的页面总表
    """
    asnocode = []
    _min = min(_min, _max)
    _max = max(_min, _max)
    for item_asnocode in range( _min, _max):
        next_asnocode = _domain + 'forum-181-{}.html'.format(item_asnocode)
        asnocode += onepage(_urls=next_asnocode)
    return asnocode


def pages_as_code(_domain, _min, _max) -> list:
    """
    亚洲有码
    :param _domain: 网站域名
    :param _min: 最小值
    :param _max: 最大值
    :return: 该区间内所有的等待下载的页面总表
    """
    ascode = []
    _min = min(_min, _max)
    _max = max(_min, _max)
    for item_ascode in range( _min,  _max):
        next_ascode = _domain + 'forum-220-{}.html'.format(item_ascode)
        ascode += onepage(_urls=next_ascode)
    return ascode


def pages_us_nocode(_domain, _min, _max) -> list:
    """
    欧美无码
    :param _domain: 网站域名
    :param _min: 最小值
    :param _max: 最大值
    :return: 该区间内所有的等待下载的页面总表
    """
    usnocode = []
    _min = min(_min, _max)
    _max = max(_min, _max)
    for item_usnocode in range(_min, _max):
        next_usnocode = _domain + 'forum-182-{}.html'.format(item_usnocode)
        usnocode += onepage(_urls=next_usnocode)
    return usnocode


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
    下载功能
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
        time.sleep(random.randint(1,3))
    except RequestException:
        print('Request Error')
        pass
    except TimeoutError:
        print('TimeoutError')
        pass
    except ReadTimeoutError:
        print('ReadTimeoutError')
        pass
    except ConnectionError:
        print('ConnectionError')
        pass
    except ConnectTimeout:
        print('ConnectTimeout')
        pass
    except OSError:
        print('OSError')
        pass


def run( _urls, _cores):
    """
    多线程
    :param _urls: 待下载的URL列表
    :param _cores:  开启的核心数(四核)
    :return: 0
    """
    pool_ = Pool(_cores)
    pool_.map(parse, _urls)
    pool_.close()
    pool_.join()
    return


def choice():
    """
    判断某类型下是否更新或者全部爬取的逻辑
    :return:
    """
    _judge = input('是否更新该类型下的所有页面?(yes/no)\n').lower()
    _range = str(input("请输入更新范围:(以','隔开)\n"))
    range_ = _range.split(',')
    if range_:
        range_01 = range_[0]
        range_02 = range_[-1]
        return _judge, int(range_01), int(range_02)
    else:
        print(_range)
        print('输入错误!!!!')
        return


def spider(_domain):
    """
    更新
    :param _domain: 网站域名
    :return: 0
    """
    # 1-10
    print('\t1:亚洲无码\n')
    # 1-30-35
    print('\t2:亚洲有码\n')
    # 1-10
    print('\t3:欧美无码\n')

    print('\t4:全部内容\n')

    choices = int(input('请输入你要爬取的类型编号:\n'))
    if choices == 1:
        _judge,range_01,range_02 = choice()
        if _judge == 'no':
            run(_urls=pages_as_nocode(_domain=_domain, _min=range_01, _max=range_02), _cores=8)
        elif _judge == 'yes':
            run(_urls=pages_as_nocode(_domain=_domain, _min=1, _max=maxnums(_url=Asia_nocode)), _cores=32)
        else:
            return

    elif choices == 2:
        _judge, range_01, range_02 = choice()
        if _judge == 'no':
            run(_urls=pages_as_code(_domain=_domain, _min=range_01, _max=range_02), _cores=16)
        elif _judge == 'yes':
            run(_urls=pages_as_code(_domain=_domain, _min=1, _max=maxnums(_url=Asia_code)), _cores=32)
        else:
            return

    elif choices == 3:
        _judge, range_01, range_02 = choice()
        if _judge == 'no':
            run(_urls=pages_us_nocode(_domain=_domain, _min=range_01, _max=range_02), _cores=8)
        elif _judge == 'yes':
            run(_urls=pages_us_nocode(_domain=_domain, _min=1, _max=maxnums(_url=US_nocode)), _cores=32)
        else:
            return
    elif choices == 4:
        run(_urls=pages(_domain=_domain), _cores=8)
        return
    else:
        print('输入错误,请核实信息')
        return


if __name__ == "__main__":
    spider(_domain=domain)
