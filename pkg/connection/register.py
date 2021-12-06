import json
from operator import pos
import time
from requests import session, post, adapters
from os import path as os_path, getenv
from sys import exit as sys_exit
from bs4 import BeautifulSoup
from json import loads as json_loads
import os

import requests
from ocr import read_image

from urllib3.util import url

adapters.DEFAULT_RETRIES = 5

class FudanConnection:
    """
    建立与平安复旦的连接
    """
    UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15"
    
    def __init__(self, 
                uid, psw, send_key,
                url_login = "https://uis.fudan.edu.cn/authserver/login",
                url_pingan = "https://zlapp.fudan.edu.cn/site/ncov/fudanDaily",
                url_code = "https://zlapp.fudan.edu.cn/backend/default/code"):
        """初始化一个session, 以及登录信息, 

        Args:
            uid (str): 复旦学号
            psw (str): 信息办密码
            url_login (str, optional): 复旦认证网址. Defaults to "https://uis.fudan.edu.cn/authserver/login".
            url_pingan (str, optional): 平安复旦网址. Defaults to "https://zlapp.fudan.edu.cn/site/ncov/fudanDaily".
            url_code (str, optional): 复旦默认验证码网址. Defaults to "https://zlapp.fudan.edu.cn/backend/default/code".
        """
        self.session = session()
        self.session.keep_alive = False
        self.session.headers["User-Agent"] = self.UA
        self.url_login = url_login
        self.url_pingan = url_pingan
        self.url_code = url_code
        
        self.uid = uid
        self.psw = psw
        self.send_key = send_key
    
    def _page_init(self):
        """登录页面 
        Returns:
            str: 登录页面html文本
        """
        print("*Initiating---", end=" ")
        page_login = self.session.get(self.url_login)
        
        print("\nStatus code ", 
            page_login.status_code)
        
        if page_login.status_code == 200:
            print("*Initiated---", end=" " )
            return page_login.text
        else:
            print("*Failed to open the login page, please check the Internet")
            self.close()
    
    def login(self):
        """登录到平安复旦
        """
        
        page_login = self._page_init()
        
        data = {
            "username": self.uid,
            "password": self.psw,
            "service": self.url_pingan
        }
        
        ##登录的令牌
        soup = BeautifulSoup(page_login, "lxml")
        inputs = soup.find_all("input")

        for i in inputs[2::]:
            data[i.get("name")] = i.get("value")
        
        
        #print(data)
        
        headers = {
            "User-Agent": self.UA,
            "Host": "uis.fudan.edu.cn",
            "Referer": self.url_login
        }
        
        post = self.session.post(
            self.url_login,
            data=data,
            headers=headers,
            allow_redirects=False
        )
        
        if post.status_code == 302:
            print("\n---------------\n"
                  "😄登录成功\n"
                  "---------------\n")
        else:
            print("\n---------------\n"
                  "💔登录失败,请检查账号信息\n"
                  "---------------\n")
            self.close()
    
    def check_status(self):
        """检查是否打卡，如果打卡就结束，如果没有就存一下之前的信息
        """
        
        print("\n❓检查是否已经打卡")
        get_info = self.session.get(
            "https://zlapp.fudan.edu.cn/ncov/wap/fudan/get-info"
        )
        
        #上一次的信息
        old_info = get_info.json()
        #for key in old_info["d"]["oldInfo"]:
        #    print(key,"    ",old_info["d"]["oldInfo"][key])
        #print(old_info["d"]["info"])
        #print("------------")
        print("📅上次打卡的日期是,",old_info["d"]["info"]["date"])
        
        geo_info = old_info["d"]["info"]["geo_api_info"]
        geo_info = json_loads(geo_info)
        
        print("📅上次打卡的地址是,",geo_info["formattedAddress"])
        
        ##设置时区
        os.environ['TZ'] = 'Asia/Shanghai'
        time.tzset()
        today = time.strftime("%Y%m%d", time.localtime())
        print("📅今日日期是, ", today)
        
        if today == old_info["d"]["info"]["date"]:
            self.send_wechat(old_info["d"]["oldInfo"]["area"])
            return True
        else:
            print("😔还没提交, 继续提交吧")
            self.old_info = old_info["d"]["oldInfo"]
            return False
        
        
        
    
    def get_verify_code(self):
        """调用ocr识别验证码

        Returns:
            str: 验证码
        """
        image_byte = self.session.get(self.url_code).content
        #print(image)
        verify_code = read_image(image_byte)
        return verify_code
    
    def send_wechat(self,location):
        """关联微信推送

        Args:
            location (str): 打卡地址
        """
        url = 'https://sc.ftqq.com/{}.send?text=打卡成功,打卡地址是{}'.format(self.send_key,location)
        requests.get(url=url)
        
    
    def check_in(self):
        """打卡主要功能
        """
        if self.check_status():
            print("😉已经打卡了,服务结束")
            
            self.close()
        else:
            headers = {
                "Host": "zlapp.fudan.edu.cn",
                "Referer": "https://zlapp.fudan.edu.cn/site/ncov/fudanDaily?from=history",
                "DNT": "1",
                "TE": "Trailers",
                "User-Agent": self.UA
            }
            
            print("🔋正在提交中------")
            
            geo_api_info = json_loads(self.old_info["geo_api_info"])
            area = self.old_info["area"]
            province = self.old_info["province"]
            city = self.old_info["city"]
            district = geo_api_info["addressComponent"].get("district", "")
            
            print("🔋正在识别验证码中-------")
            while(True):
                code = self.get_verify_code()
                print("验证码为:", code)
                
                data = self.old_info
                data.update(
                    {
                        "tw":"13",
                        "province":province,
                        "city": city,
                        "area": " ".join((province,city,district)),
                        "code": code,
                    }
                )
                
                save_response = self.session.post(
                    url = "https://zlapp.fudan.edu.cn/ncov/wap/fudan/save",
                    data = data,
                    headers = headers,
                    allow_redirects=False 
                )
                save_msg = json_loads(save_response.text)["m"]
                print(save_msg, '\n\n')
                
                time.sleep(0.1)
                print(json_loads(save_response.text)["e"])
                if(json_loads(save_response.text)["e"] != 1):
                    self.send_wechat(area)
                    break
    
        
    def logout(self):
        """登出账号
        """
        exit_url = 'https://uis.fudan.edu.cn/authserver/logout?service=/authserver/login'
        expire = self.session.get(exit_url).headers.get("Set-Cookie")
        # print(expire)
        
        if "01-Jan-1970" in expire:
            print("⭕️登出完毕")
        else:
            print("⭕️登出异常")

    def close(self, exit_code=0):
        """关闭会话
        Args:
            exit_code (int, optional): 退出代码. Defaults to 0.
        """
        self.logout()
        self.session.close()
        print("⭕️关闭会话")
        print("******************")
        sys_exit(exit_code)
        
        
        
        
if __name__ == "__main__":
    uid = getenv("STD_ID")
    psw = getenv("PASSWORD")
    send_key = getenv("SENDKEY")
    
    connection = FudanConnection(uid, psw, send_key)
    connection.login()
    connection.check_in()
    connection.close()
    
        
        
        