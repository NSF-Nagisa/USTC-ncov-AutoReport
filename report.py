# -*- coding: utf-8 -*-
import requests
import json
import time
import datetime
import pytz
import random
import os
import re
import sys
import argparse
from bs4 import BeautifulSoup
from aip import AipOcr

#aip argument
APP_ID = '24730410'
API_KEY = 'Z5gLsAgL3NTVmBTRMCrQ517m'
SECRET_KEY = 'dCaVEOKwzot3lLFDbFjOyXqNoBDQkuG8'
REPORT = True
ACROSS_CAMPUS = True

class Report(object):
    def __init__(self, stuid, password, data_path):
        self.stuid = stuid
        self.password = password
        self.data_path = data_path

    def report(self):
        loginsuccess = False
        retrycount = 5
        while (not loginsuccess) and retrycount:
            session = self.login()
            cookies = session.cookies
            getform = session.get("https://weixine.ustc.edu.cn/2020")
            retrycount = retrycount - 1
            if getform.url != "https://weixine.ustc.edu.cn/2020/home":
                print("Login Failed! Retrying...")
            else:
                print("Login Successful!")
                loginsuccess = True
        if not loginsuccess:
            return False
        flag, across_flag = False, False
        if REPORT:
            data = getform.text
            data = data.encode('ascii','ignore').decode('utf-8','ignore')
            soup = BeautifulSoup(data, 'html.parser')
            token = soup.find("input", {"name": "_token"})['value']

            with open(self.data_path, "rb") as f:
                data = f.read()
                data = json.loads(data)
                data["_token"] = token
                data["jinji_lxr"] = os.environ["CONTACTNAME"]
                data["jinji_guanxi"] = os.environ["CONTACTRALASHIP"]
                data["jiji_mobile"] = os.environ["CONTACTPHONE"]
                # data["jinji_lxr"] = "kk"
                # data["jinji_guanxi"] = "kk"
                # data["jiji_mobile"] = "18189700666"
            
            headers = {
                'authority': 'weixine.ustc.edu.cn',
                'origin': 'https://weixine.ustc.edu.cn',
                'upgrade-insecure-requests': '1',
                'content-type': 'application/x-www-form-urlencoded',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'referer': 'https://weixine.ustc.edu.cn/2020/home',
                'accept-language': 'zh-CN,zh;q=0.9',
                'Connection': 'close',
                'cookie': "PHPSESSID=" + cookies.get("PHPSESSID") + ";XSRF-TOKEN=" + cookies.get("XSRF-TOKEN") + ";laravel_session="+cookies.get("laravel_session"),
            }

            url = "https://weixine.ustc.edu.cn/2020/daliy_report"
            resp=session.post(url, data=data, headers=headers)
            # print(resp.status_code)
            data = session.get("https://weixine.ustc.edu.cn/2020").text
            soup = BeautifulSoup(data, 'html.parser')
            pattern = re.compile("202[0-9]-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}")
            token = soup.find(
                "span", {"style": "position: relative; top: 5px; color: #666;"})
            flag = False
            if pattern.search(token.text) is not None:
                date = pattern.search(token.text).group()
                print("Latest report: " + date)
                date = date + " +0800"
                reporttime = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S %z")
                timenow = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
                delta = timenow - reporttime
                print("{} second(s) before.".format(delta.seconds))
                if delta.seconds < 120:
                    flag = True
        if ACROSS_CAMPUS:
            across_flag = self.across_campus_report(cookies, session)
        print("Health report: ", flag, " across report: ", across_flag)
        return flag and across_flag
        # flag= flag and across_flag
        # if flag == False:
        #     print("Report FAILED!")
        # else:
        #     print("Report SUCCESSFUL!")

        # return flag

    def across_campus_report(self, cookies, session):
        headers = {
                'host': 'weixine.ustc.edu.cn',
                'origin': 'https://weixine.ustc.edu.cn',
                'upgrade-insecure-requests': '1',
                'content-type': 'application/x-www-form-urlencoded',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'referer': 'https://weixine.ustc.edu.cn/2020/apply/daliy/i?t=3',
                'accept-language': 'zh-CN,zh;q=0.9',
                'Connection': 'keep-alive',
                'cookie': "PHPSESSID=" + cookies.get("PHPSESSID") + ";XSRF-TOKEN=" + cookies.get("XSRF-TOKEN") + ";laravel_session="+cookies.get("laravel_session"),
            }
        url = 'https://weixine.ustc.edu.cn/2020/apply/daliy/i?t=3'
        getform = session.get(url=url)
        data = getform.text
        data = data.encode('ascii', 'ignore').decode('utf-8', 'ignore')
        soup = BeautifulSoup(data, 'html.parser')
        token = soup.find("input", {"name": "_token"})['value']
        start_date = soup.find("input", {"name": "start_date"})['value']
        end_date = soup.find("input", {"name": "end_date"})['value']
        
        form = {
            '_token': token,
            'start_date': start_date,
            'end_date': end_date,
            'return_college[]': '中校区',
            't': '23'
        }
        resp = session.post('https://weixine.ustc.edu.cn/2020/apply/daliy/post', data=form, headers=headers)
        flag = False
        if resp.url=='https://weixine.ustc.edu.cn/2020/apply_total?t=d':
            flag=True
        else:
            flag=False
        return flag

    def login(self):
        url = "https://passport.ustc.edu.cn/login?service=http%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin"
        data = {
            'model': 'uplogin.jsp',
            'service': 'https://weixine.ustc.edu.cn/2020/caslogin',
            'CAS_LT': '',
            'username': self.stuid,
            'password': str(self.password),
            'warn': '',
            'showCode': '1',
            'button': '',
            'LT':''
        }
        session = requests.Session()
        
        # get validateCode
        header = {'user-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}
        code = session.get('https://passport.ustc.edu.cn/validatecode.jsp?type=login',headers=header)
        

        # with open('code.jpg','wb') as file:
        #     file.write(code.content)
        #     file.close

        client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
        res = client.basicGeneral(code.content)
        
        for item in res['words_result']:
           validate_code = item['words']
        

        # get CAS_LT
        form = session.get(url).text
        form = form.encode('ascii','ignore').decode('utf-8','ignore')
        soup = BeautifulSoup(form, 'html.parser')
        cas_lt = soup.find('input', {'name':'CAS_LT'})['value']


        # login
        data['LT'] = validate_code
        data['CAS_LT'] = cas_lt
        session.post(url, data=data)
        

        print("login...")
        return session


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='URC nCov auto report script.')
    parser.add_argument('data_path', help='path to your own data used for post method', type=str)
    parser.add_argument('stuid', help='your student number', type=str)
    parser.add_argument('password', help='your CAS password', type=str)
    args = parser.parse_args()
    autorepoter = Report(stuid=args.stuid, password=args.password, data_path=args.data_path)
    count = 5
    while count != 0:
        ret = autorepoter.report()
        if ret != False:
            break
        print("Report Failed, retry...")
        count = count - 1
    if count != 0:
        exit(0)
    else:
        exit(-1)
