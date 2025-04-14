import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta



class Data:
    def __init__(self):
        data_dir = "./data"
        self.data = self.load_data(data_dir)
    def load_data(self, data_dir):
        data = pd.DataFrame()
        for filename in os.listdir(data_dir):
            if filename.endswith('.xlsx'):
                file_path = os.path.join(data_dir, filename)
                file = pd.read_excel(file_path)
                file['起始时间'] = pd.to_datetime(file['起始时间'])
                file['截止时间'] = pd.to_datetime(file['截止时间'])
                data = pd.concat([data, file], ignore_index=True)
        data = data.drop(['综合要求', '其他'], axis=1)     
        #清理重复项目
        data.drop_duplicates(inplace=True,ignore_index=True)
        print(data)
        
        return data
    def sort(self):
        start = pd.DataFrame(self.data['起始时间'].value_counts().index)
        date = np.array(start['起始时间'].astype(str))
        print(date)
        xs = [(datetime.strptime(d, '%Y-%m-%d').date() + timedelta(days=-1)) for d in date]
        start.columns = ['time']
        start_left = pd.DataFrame(data=None,columns=['time'])
        start_left['time'] = [pd.to_datetime(i) for i in xs]
        start_num = pd.DataFrame(self.data['起始时间'].value_counts().values, columns = ['add'])
        start = pd.concat([start,start_num], axis=1)
        start = pd.concat([start,start_left], axis=0).drop_duplicates(subset=['time']).fillna(0)
        print(start)
        stop = pd.DataFrame(self.data['截止时间'].value_counts().index)
        date = np.array(stop['截止时间'].astype(str))
        xs = [(datetime.strptime(d, '%Y-%m-%d').date() + timedelta(days=-1)) for d in date]
        stop.columns = ['time']
        stop_right = pd.DataFrame(data=None,columns=['time'])
        stop_right['time'] = [pd.to_datetime(i) for i in xs]
        stop_num = pd.DataFrame(self.data['截止时间'].value_counts().values, columns = ['delete'])
        stop = pd.concat([stop,stop_num], axis=1)
        stop = pd.concat([stop,stop_right], axis=0).drop_duplicates(subset=['time']).fillna(0)
        print(start)
        total = pd.merge(start, stop, how='outer', on='time').fillna(0)
        total.insert(loc=len(total.columns), column='total', value=0)

        print(total)
        total = total.sort_values(by='time')
        sum = 0
        for i in range(total.shape[0]):
            sum = sum + total.iloc[i,1] - total.iloc[i,2]
            total.iloc[i,3] = sum
        print(total)
        return total
    def clear(self):
        total = data.sort()
        plt.figure(figsize=(18,6))
        plt.rcParams['font.sans-serif']=['SimHei']
        plt.rcParams['axes.unicode_minus']=False 
        plt.title('B站打卡活动任务数量变化',fontsize=25)  
        plt.xlabel('日期',fontsize=10)   
        plt.ylabel('活动任务数',fontsize=10)  
        plt.plot(total['time'], total['total'], 'o-',label='客流量')
        plt.tick_params(axis='both',which='both',labelsize=10)
 
        # 显示折线图
        plt.gcf().autofmt_xdate()  # 自动旋转日期标记
        plt.show()
if __name__ == "__main__":
    data = Data()
    data.clear()