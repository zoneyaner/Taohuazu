#! ./Administrator/AppData/Local/Programs/Python/Python37-32
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
        name="Taohuazu",
        version="2.0",
        keywords=("porn", "download"),
        description="spider of download",
        long_description="a spider on Taohuazu.com which can use for download or do more",
        license="Apache License 2.0",

        url="https://github.com/zhong-yan/Taohuazu",
        author="kawkeye",
        author_email="zhongygg@gmail.com",

        packages=find_packages(),
        include_package_data=True,
        platforms="any",
        install_requires=[
            'bs4>=0.0.1',
            'requests>=2.19.1',
            'beautifulsoup4>=4.6.3',
            'lxml>=4.2.4',
            'urllib3>=1.23'
        ],
        zip_safe=False
)