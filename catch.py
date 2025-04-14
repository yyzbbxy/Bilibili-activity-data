import requests
import pandas as pd
import time
import re
import datetime
from configparser import RawConfigParser

#读取ini文件
def read_ini():
    conf = RawConfigParser()
    conf.read('header.ini')
    cookie = conf.get('header', 'cookie')
    user_agent = conf.get('header', 'user-agent')
    return cookie, user_agent

#链接网页
def getResponse(url,data,cookie,user_agent):
    headers = {
            "Cookie":cookie,
            "User-Agent":user_agent
        }
    response = requests.get(url=url, params = data, headers = headers)
    return response

#输出数据
def getList(url, params,cookie,user_agent):
    response = getResponse(url,params,cookie,user_agent)
    data = response.json()
    return data['data']

#整理数据
def collect_data():
    #读取配置
    cookie, user_agent = read_ini()
    #设置列名
    columns = ['活动','起始时间','截止时间','tag要求','单稿播放量','累计播放量','打卡天数','稿件数','综合要求','瓜分','其他','tag']
    #创建表格
    data = pd.DataFrame(columns=columns)
    #活动页面参数
    url = "https://member.bilibili.com/x2/creative/h5/clock/v4/activity/list"
    params = {"act_type": "0",
            "csrf": "72965465d9656b906b42f29fdd0be26e",
            "s_locale": "zh_CN"}
    #获取活动列表
    data_list = getList(url, params,cookie,user_agent)['list']
    count = 0
    for i in range(len(data_list)):
        print('loading: '+str(i+1)+'/'+str(len(data_list)))
        #链接页面参数
        url = "https://member.bilibili.com/x2/creative/h5/clock/v4/act/detail"
        params = {"act_id": str(data_list[i]['act_id']),
                "csrf": "72965465d9656b906b42f29fdd0be26e",
                "s_locale": "zh_CN"}
        #读取链接内内容
        time.sleep(1)
        inner_data_list = getList(url, params,cookie,user_agent)
        #周任务
        if ('weeks' in inner_data_list['task_data']):
            desc = inner_data_list['task_data']['main']['desc']
            for week in inner_data_list['task_data']['weeks']:
                stime = week['stime']
                etime = week['etime']
                #活动任务数量
                act_num = len(week['tasks'])
                numbers = []
                act_type = []
                act_value = []
                for act in week['tasks']:
                    number = re.findall(r'\d+', act['award_name'])
                    numbers.append(int(number[0]))
                    act_type.append(act['target_type'])
                    act_value.append(act['target_value'])
                if week['now_week']:
                    stime = week['stime']
                    etime = week['etime']
                    #活动任务数量
                    act_num = len(week['tasks'])
                    numbers = []
                    act_type = []
                    act_value = []
                    for act in week['tasks']:
                        number = re.findall(r'\d+', act['award_name'])
                        numbers.append(int(number[0]))
                        act_type.append(act['target_type'])
                        act_value.append(act['target_value'])

        #非周任务    
        else:
            desc = inner_data_list['task_data']['desc']
            stime = inner_data_list['stime']
            etime = inner_data_list['etime']
            #活动任务数量
            act_num = len(inner_data_list['task_data']['tasks'])
            numbers = []
            act_type = []
            act_value = []
            for act in inner_data_list['task_data']['tasks']:
                number = re.findall(r'\d+', act['award_name'])
                numbers.append(int(number[0]))
                act_type.append(act['target_type'])
                act_value.append(act['target_value'])

        #时间序列转年月日
        stime = time.localtime(stime)
        stime = time.strftime("%Y/%m/%d", stime)
        etime = time.localtime(etime)
        etime = time.strftime("%Y/%m/%d", etime)
        rule_text = inner_data_list['rule_text']
        #按照每个活动任务数量拓展
        for act in range(act_num):
            #获取活动标题
            data.loc[act+count,'活动'] = data_list[i]['title']
            #获取开始时间
            data.loc[act+count,'起始时间'] = stime
            #获取截止时间
            data.loc[act+count,'截止时间'] = etime
            #获取活动tag要求
            task_tag = ''
            for j in range(len(inner_data_list['act_rule']['topic'])):
                #末尾不换行
                if j != len(inner_data_list['act_rule']['topic'])-1:
                    task_tag += ('#'+inner_data_list['act_rule']['topic'][j]['name']+'\n')
                else:
                    task_tag += ('#'+inner_data_list['act_rule']['topic'][j]['name'])
                data.loc[act+count,'tag要求'] = task_tag
            #单稿播放量
            
            #累计播放量
            if act_type[act] == "view":
                data.loc[act+count,'累计播放量'] = act_value[act]
            #打卡天数
            if act_type[act] == "av_day":
                data.loc[act+count,'打卡天数'] = act_value[act]
            #稿件数
            if act_type[act] == "av_num":
                data.loc[act+count,'稿件数'] = act_value[act]
            #获取任务说明
            data.loc[act+count,'综合要求'] = desc
            #瓜分奖励
            data.loc[act+count,'瓜分'] = numbers[act]
            #获取详细规则
            data.loc[act+count,'其他'] = rule_text
            #获取活动tag
            data.loc[act+count,'tag'] = ""
            for j in range(len(data_list[i]['act_tags'])):
                #去除末尾\t
                if data_list[i]['act_tags'][j][-2:].endswith("\t"):
                    data_list[i]['act_tags'][j] = data_list[i]['act_tags'][j].rstrip("\t")
                #去除首尾#
                if data_list[i]['act_tags'][j][-1:] == "#" and data_list[i]['act_tags'][j][0] == "#":
                    data_list[i]['act_tags'][j] = data_list[i]['act_tags'][j][1:-1]
                #以；作为间隔
                if j != len(data_list[i]['act_tags'])-1:
                    data_list[i]['act_tags'][j] = data_list[i]['act_tags'][j] + "；"
                data.loc[act+count,'tag'] = data.loc[act+count,'tag']  + data_list[i]['act_tags'][j]
        count += act_num
    
    #填充缺省
    data.fillna("无", inplace=True)
    print(data)
    return data

def save(data):
    date = datetime.datetime.now().strftime('%Y.%m.%d')
    title = './data/' + str(date) + '.xlsx'
    data.to_excel(title, index=False)
    print("输出完成")

if __name__ == '__main__':
    data = collect_data()
    save(data)