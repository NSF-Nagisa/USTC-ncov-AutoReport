# encoding=utf8
import requests
import json
import time
import datetime
import pytz
import re
import sys
import argparse
from bs4 import BeautifulSoup

url = "https://passport.ustc.edu.cn/login"
data = {
    'model': 'uplogin.jsp',
    'service': 'https://weixine.ustc.edu.cn/2020/caslogin',
    'username': 'PB18151858',
    'password': 'wkp20001013',
    #'warn': '',
    'showCode': '',
    #'button': '',
    }
userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
header = {
    # "origin": "ttps://passport.ustc.edu.cn",
    'Content-Type':  'application/x-www-form-urlencoded',
    "Referer": 'https://passport.ustc.edu.cn/login?service=https://weixine.ustc.edu.cn/2020/caslogin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
}
session = requests.Session()
routeUrl = "https://weixine.ustc.edu.cn/2020/login"
r = session.post(url=url, data=data)#, headers=header
res = session.get(routeUrl)
print(res.url)
print(f"isLoginStatus = {res.status_code}")
print(f"statusCode = {r.status_code}")


