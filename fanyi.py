import websocket
import difflib
import hashlib
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread
from pyaudio import PyAudio, paInt16
import numpy as np
from datetime import datetime
import wave
import time
import re
import sys
import urllib.parse, urllib.request
import hashlib
import urllib
import random
import json
import time
from urllib import request
from urllib import parse
import json
import js2py
from translate import Translator
import random
import re
import requests
import os

class BaiduFanyi(object):
    """百度翻译"""

    def __init__(self, keywords):
        """
        :param keywords:待检测语言
        """
        self.keywords = keywords
        self.url_root = 'http://fanyi.baidu.com/'  # 翻译根url
        self.url_langdetect = 'https://fanyi.baidu.com/langdetect'  # 检测语言url
        self.url_trans = 'https://fanyi.baidu.com/v2transapi'  # 执行翻译url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
            'origin': 'https://fanyi.baidu.com',
            'referer': 'https://fanyi.baidu.com/?aldtype=16047'
        }
        self.data_langdetect = {
            'query': self.keywords
        }
        self.session = requests.session()
        self.session.headers = self.headers
        # 创建执行js的环境
        self.context = js2py.EvalJs()

    def langdetect(self):
        """
        发送请求,检测输入的语言类型
        :return: 正常:en:英文,zh:中文;异常:None
        """
        try:
            response = self.session.post(self.url_langdetect, data=self.data_langdetect)
            response_dict = response.json()  # {'error': 0, 'msg': 'success', 'lan': 'zh'}
            if response_dict.get('error') == 0:
                return response_dict.get('lan')
        except Exception as e:
            print(e)

    def get_token_gtk(self):
        """
        获取token,gtk(用于合成sign)
        :return:(token, gtk)
        """
        response = self.session.get(self.url_root)
        response_str = response.content.decode()
        # 注意双引号问题
        token = re.findall(r"token: '(.*?)'", response_str)[0]
        gtk = re.findall(r";window.gtk = ('.*?');", response_str)[0]
        return token, gtk

    def trans(self, lan):
        """
        发送请求,开始翻译
        :return: 正常:翻译结果(str);异常:None
        """
        try:
            token, gtk = self.get_token_gtk()
            # print(token, gtk)  # 2d275a77fc7ba0609e7151f57859040d '320305.131321201'

            js = r"""
            function n(r, o) {
                for (var t = 0; t < o.length - 2; t += 3) {
                var a = o.charAt(t + 2);
                a = a >= "a" ? a.charCodeAt(0) - 87 : Number(a), a = "+" === o.charAt(t + 1) ? r >>> a : r << a, r = "+" === o.charAt(t) ? r + a & 4294967295 : r ^ a
                }
                return r
            }
            function e(r) {
                var o = r.match(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g);
                if (null === o) {
                    var t = r.length;
                    t > 30 && (r = "" + r.substr(0, 10) + r.substr(Math.floor(t / 2) - 5, 10) + r.substr(-10, 10))
                } else {
                    for (var e = r.split(/[\uD800-\uDBFF][\uDC00-\uDFFF]/), C = 0, h = e.length, f = []; h > C; C++) "" !== e[C] && f.push.apply(f, a(e[C].split(""))), C !== h - 1 && f.push(o[C]);
                    var g = f.length;
                    g > 30 && (r = f.slice(0, 10).join("") + f.slice(Math.floor(g / 2) - 5, Math.floor(g / 2) + 5).join("") + f.slice(-10).join(""))
                }
                var u = void 0, l = "" + String.fromCharCode(103) + String.fromCharCode(116) + String.fromCharCode(107);
                u = null !== i ? i : (i = window[l] || "") || "";
                for (var d = u.split("."), m = Number(d[0]) || 0, s = Number(d[1]) || 0, S = [], c = 0, v = 0; v < r.length; v++) {
                    var A = r.charCodeAt(v);
                    128 > A ? S[c++] = A : (2048 > A ? S[c++] = A >> 6 | 192 : (55296 === (64512 & A) && v + 1 < r.length && 56320 === (64512 & r.charCodeAt(v + 1)) ? (A = 65536 + ((1023 & A) << 10) + (1023 & r.charCodeAt(++v)), S[c++] = A >> 18 | 240, S[c++] = A >> 12 & 63 | 128) : S[c++] = A >> 12 | 224, S[c++] = A >> 6 & 63 | 128), S[c++] = 63 & A | 128)
                }
                for (var p = m, F = "" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(97) + ("" + String.fromCharCode(94) + String.fromCharCode(43) + String.fromCharCode(54)), D = "" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(51) + ("" + String.fromCharCode(94) + String.fromCharCode(43) + String.fromCharCode(98)) + ("" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(102)), b = 0; b < S.length; b++) p += S[b], p = n(p, F);
                return p = n(p, D), p ^= s, 0 > p && (p = (2147483647 & p) + 2147483648), p %= 1e6, p.toString() + "." + (p ^ m)
            }
            """
            # js中替换gtk
            js = js.replace(r'null !== i ? i : (i = window[l] || "") || ""', gtk)
            # print(js)

            # 执行js,定义加密函数e(r)
            self.context.execute(js)
            # 执行加密函数e(r),对keywords进行加密
            sign = self.context.e(self.keywords)
            # print(sign)  # 477811.239938

            data = {
                'from': lan,
                'to': 'en' if lan == 'zh' else 'zh',
                'query': self.keywords,
                'transtype': 'translang',
                'simple_means_flag': 3,
                'sign': sign,  # 此参数需破解
                'token': token  # 此参数需破解

            }
            response = self.session.post(self.url_trans, data=data)
            response_dict = response.json()
            ret = response_dict['trans_result']['data'][0]['dst']
            return ret
        except Exception as e:
            print(e)

    def run(self):
        # 1.检测输入的语言类型
        lan = self.langdetect()
        if lan is None:
            return
        # 2.翻译
        ret = self.trans(lan)
        print('%s' % (ret))  # 中国-->China


def main():
    ffstr = ''
    while True:
        f1 = open(r'test.txt', 'r')
        f1str = f1.read()
        if ffstr != f1str:
            baidu_fanyi = BaiduFanyi(f1str)
            baidu_fanyi.run()
            ffstr = f1str
        f1.close()



