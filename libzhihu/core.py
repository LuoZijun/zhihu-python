#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Build-in / Std
import os, sys, time, platform, random
import re, json, cookielib

# requirements
import requests, termcolor, html2text
try:
    from bs4 import BeautifulSoup
except:
    import BeautifulSoup



"""
    Note:
        1. 身份验证由 `auth.py` 完成。
        2. 身份信息保存在当前目录的 `cookies` 文件中。
        3. `requests` 对象可以直接使用，身份信息已经自动加载。

    By Luozijun (https://github.com/LuoZijun), 09/09 2015

"""
requests = requests.Session()
requests.cookies = cookielib.LWPCookieJar('cookies')
try:
    requests.cookies.load(ignore_discard=True)
except:
    Logging.error(u"你还没有登录知乎哦 ...")
    Logging.info(u"执行 `python auth.py` 即可以完成登录。")
    raise Exception("无权限(403)")


class People:
    """
        people:
            name
            domain
            avatar
            profile
                location
                    name
                sex
                job
                    industry
                    organization
                    job
                education
                    organization
                    major
                SNS
                about
            detail:
                chengjiu
                    agree, thx, favor, share
                zhiyejingli

            questions

            answers

            articles

            favors

            edit

            forces
            follows

    """
    def __init__(self, name=None, domain=None):
        self.name = name
        self.domain = domain
    def pull(self):
        pass
    def sync(self):
        pass
    def parser(self):
        pass
    @staticmethod
    def search(keywords):
        return search.people(keywords)
        

class Question:
    def __init__(self, token=None):
        self.token = str(token)
        self.html  = "" 
    def pull(self):
        if self.token == None:
            raise ValueError("token required.")
        url = "http://www.zhihu.com/question/%s" % self.token
        res = requests.get(url)
        if res.status_code in [302, 301]:
            raise IOError("network error.")
        elif res.status_code != 200:
            raise IOError("unknow error.")
        else:
            self.html = res.text

    def sync(self):
        pass

    @classmethod
    def parser(self, html):
        DOM = BeautifulSoup(html, 'html.parser')

        title = DOM.find("h2", class_="zm-item-title").string.replace("\n", "")
        detail = DOM.find("div", id="zh-question-detail").div.get_text()
        # answers
        el = DOM.find("h3", id="zh-question-answer-num")
        try:
            answers_num = int(el["data-num"])
        except:
            answers_num = 0
        # followers
        el = DOM.find("div", class_="zg-gray-normal")
        try:
            followers_num = int(el.a.strong.string)
        except:
            followers_num = 0
        # topics
        topics = []
        elems = DOM.find_all("a", class_="zm-item-tag")
        if elems == None: elems = []
        for el in elems:
            try:
                topics.append(el.contents[0].replace("\n", ""))
            except:
                pass
        # 浏览次数 ?
        try:
            visit_times = int(DOM.find("meta", itemprop="visitsCount")["content"])
        except:
            visit_times = 0

        def fetch_all_answers(DOM):
            # fetch all answers
            answers = []
            elem = DOM.find("div", id="zh-question-answer-wrap")
            if elem == None: return []
            elems = elem.find_all("div", class_="zm-item-answer")
            if elems == None: return []
            for answer_el in elems:
                # 这是什么统计？
                count = answer_el.find("span", class_="count")
                answer = answer_el.find("div", class_=" zm-editable-content clearfix")

                people = {"token": None, "name": None, "avatar": None, "descp": None}
                people_el = answer_el.find("h3", class_="zm-item-answer-author-wrap")
                if people_el == None: return people
                if people_el.string != u"匿名用户":
                    el = people_el.find_all("a")[0]
                    people['token'] = el['href'].split("/")[-1]
                    people['avatar'] = el.find("img", class_="zm-list-avatar")['src']
                    people['name'] = people_el.find_all("a")[1].string
                    # 用户你简介信息应该只有一条吧
                    people['descp'] = map( lambda el: el.string, people_el.find_all("strong") )
                    if len(people['descp']) == 1: people['descp'] = people['descp'][0]
                    elif len(people['descp']) < 1: people['descp'] = ""
                    elif len(people['descp']) > 1: people['descp'] = "\n".join(people['descp'])
                else:
                    # 匿名用户
                    pass
                answers.append({"count": count, "answer": answer, "people": people})
            return answers

        answers = fetch_all_answers(DOM)

        print "title: %s" % title
        print "detail: %s" % detail
        print "topics: %s " % " ".join(topics)

        print "浏览次数: ", visit_times
        print "答案列表: "
        for answer in answers:
            print "\tcount: %s" % answer['count']
            print "\tanswer: %s" % answer['answer']
            print "\tpeople: "
            for k in answer['people'].keys():
                print "\t\t%s: %s" %( k, answer['people'][k] )

    @staticmethod
    def search(keywords):
        return search.question(keywords)


class Answer:
    def __init__(self, question_token=None, answer_token=None):
        self.question_token = question_token
        self.answer_token = answer_token
    def pull(self):
        pass
    def sync(self):
        pass
    @classmethod
    def parser(self, html):
        DOM = BeautifulSoup(html)

    @staticmethod
    def search(keywords):
        return []


class Search:
    def __init__(self, source="question", keywords=None):
        pass
    @staticmethod
    def people(keywords):
        pass
    @staticmethod
    def question(keywords):
        """
            curl 'http://www.zhihu.com/r/search?q=%E9%A3%9E%E6%9C%BA&range=&type=question&offset=0' \
                -H 'Pragma: no-cache' -H 'Accept-Encoding: gzip, deflate, sdch' \
                -H 'Accept-Language: zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4' \
                -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36' \
                -H 'Accept: */*' -H 'Referer: http://www.zhihu.com/search?q=%E9%A3%9E%E6%9C%BA&type=question' \
                -H 'X-Requested-With: XMLHttpRequest' \
                -H 'Cookie: xxx=asds\
                -H 'Connection: keep-alive' \
                -H 'Cache-Control: no-cache' \
                --compressed
        """
        url = "http://www.zhihu.com/r/search"
        res = requests.get(url, params={"q": keywords, "range": None, "type": "question", "offset": 0})
    @staticmethod
    def topic(keywords):
        pass




if __name__ == '__main__':
    q = Question(token="31852176")
    q.pull()
    q.parser(q.html)