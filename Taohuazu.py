#! ./Administrator/AppData/Local/Programs/Python/Python37-32
# -*- coding: utf-8 -*-
import os
import re
import time

import requests
import threading
from bs4 import BeautifulSoup
from requests import RequestException
from urllib3.exceptions import ReadTimeoutError




def connect(_domain):
    """
    create the main domain which is most important things at first
    :param _domain: 2018-09-09 http://thz6.com
    :return: a dns which can get the code 200
    """
    url = _domain + '/forum.php'
    try:
        html = requests.get(url, timeout=5)
        if html.status_code == 200:
            return _domain
    except RequestException:
        print('please check the IP Adress, it is wrong!!')
        new_domain = str(input('Enter a new Domain\n')).strip()
        new_html = requests.get(new_domain)
        new_html.raise_for_status()
        return new_domain
    except TimeoutError:
        print('TimeOut')
        pass


def maxnums(_basicurl):
    html = requests.get(_basicurl)
    response = BeautifulSoup(html.text, 'lxml')
    lastnums = response.select('#fd_page_top > div > a.last')
    max_num = lastnums[0].get('href').split('-')[-1].replace('.html', '')
    return int(max_num) + 1


def mainpages(_url):
    asnocode, ascode, usnocode = [], [], []
    _ip = connect(_domain=_url)
    # 亚洲無碼原創
    asnocode_ip = _ip + '/forum-181-1.html'
    # 亚洲有碼原創
    ascode_ip = _ip + '/forum-220-1.html'
    # 欧美無碼
    usnocode_ip = _ip + '/forum-182-1.html'

    for item_asnocode in range(1, maxnums(asnocode_ip)):
        next_asnocode = _ip + '/forum-181-{}.html'.format(item_asnocode)
        asnocode.append(next_asnocode)

    for item_ascode in range(1, maxnums(ascode_ip)):
        next_ascode = _ip + '/forum-220-{}.html'.format(item_ascode)
        ascode.append(next_ascode)

    for item_usnocode in range(1, maxnums(usnocode_ip)):
        next_usnocode = _ip + '/forum-182-{}.html'.format(item_usnocode)
        usnocode.append(next_usnocode)
    return asnocode, ascode, usnocode



def spider(_url, _dir):
    """
    亚洲有码
    :param _url: like http://thz6.com/forum-220-1.html
    :param _dir: path for download
    :return: no
    """
    # stroe mian page
    link = []
    pictrues = []
    speed = 1
    try:
        page = requests.get(_url, timeout=5)
        if page.status_code == 200:
            content = BeautifulSoup(page.text, 'lxml')
            links = content.select('a')
            pattern = re.compile(r'^thread-\d+-1-1.html$')

            for item in links:
                if re.search(pattern, str(item.get('href'))):
                    result = re.search(pattern, str(item.get('href')))
                    oneurl = "http://thz6.com/" + result.group(0)
                    if oneurl not in link:
                        link.append(oneurl)

            sign_title = 'Taohuazu_桃花族 -  thz.la'
            sign_bt = "http://thz6.com/forum.php?mod=attachment&"
            for _link in link:
                speed = speed + 1
                print("\nSource Root:{}\n".format(_link))
                html_next = requests.get(_link, timeout=5)
                if html_next.status_code == 200:
                    responses = BeautifulSoup(html_next.text, 'lxml')
                    title = responses.findAll('title')[0].get_text().replace(sign_title, '')
                    torrents = responses.select('p.attnm > a')
                    _img = re.compile(r'^aimg_.*')

                    for _file in torrents:
                        bt_url = sign_bt + _file.get('href').split('?')[1]
                        path_bt = _dir + str(title) + '.torrent'
                        download(_url=bt_url, _root=_dir, _path=path_bt)

                    for pic in responses.find_all(id=_img):
                        if pic.get('file'):
                            pic_url = pic.get('file')
                            pictrues.append(pic_url)
                    if pictrues:
                        for item, num in zip(set(pictrues), [nums for nums in range(0, len(set(pictrues)))]):
                            path_img = _dir + str(title) + '-' + str(num) + '.jpg'
                            download(_url=item, _root=_dir, _path=path_img)
                        # clean th cache!!
                        pictrues = []
                if speed == 10:
                    time.sleep(10)
                    speed = 1
    except ReadTimeoutError:
        pass
    except TimeoutError:
        pass
    except RequestException:
        pass
    except ConnectionError:
        pass
    except TypeError:
        pass


def download(_url:str, _root, _path):
    """
    use for download url, need 3 params
    :param _url: needing url
    :param _root: os.makedirs
    :param _path: whole path in os include root and format
    :return:
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
                    # time.sleep(1)
    except RequestException:
        pass
    except TimeoutError:
        pass
    except ReadTimeoutError:
        pass
    except ConnectionError:
        pass
    except TypeError:
        pass


def as_code(dir_):
    as_nocode, as_code, us_nocode = mainpages('http://thz6.com')
    for item_code in as_code:
        spider(_url=item_code, _dir=dir_)


def as_nocode(dir_):
    as_nocode, as_code, us_nocode = mainpages('http://thz6.com')
    for item_nocode in as_nocode:
        spider(_url=item_nocode, _dir=dir_)


def us_nocode(dir_):
    as_nocode, as_code, us_nocode = mainpages('http://thz6.com')
    for item_us in us_nocode:
        spider(_url=item_us, _dir=dir_)

if __name__ == "__main__":
    dirs = ['asnocode', 'ascode', 'usnocode']
    # 亚洲無碼原創
    _dir_asnocode = "D:/Home/Pictures/{}/".format(dirs[0])
    # 亚洲有碼原創
    _dir_ascode = "D:/Home/Pictures/{}/".format(dirs[1])
    # 欧美無碼
    _dir_usnocode = "D:/Home/Pictures/{}/".format(dirs[2])
    # zip three list of differrent types

    task_ascode = threading.Thread(target=as_code(dir_=_dir_ascode))
    task_ascode.start()
    task_ascode.join()
    task_nocode = threading.Thread(target=as_nocode(dir_=_dir_asnocode))
    task_nocode.start()
    task_nocode.join()
    task_usnocode = threading.Thread(target=us_nocode(dir_=_dir_usnocode))
    task_usnocode.start()
    task_usnocode.join()
