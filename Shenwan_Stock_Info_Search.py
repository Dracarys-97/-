#!/usr/bin/env python
# coding: utf-8

# In[1]:


print('初始化中…大约需要5s时间')
# 导入模块
try:
    import numpy as np
except ModuleNotFoundError:
    print('找不到numpy模块，请安装numpy模块后再试')

try:
    import pandas as pd
except ModuleNotFoundError:
    print('找不到pandas模块，请安装pandas模块后再试')

    
# 加载索引文件
try:
    fund_reference = pd.read_excel('./原始数据/索引.xlsx', sheet_name = '基金索引')
    stock_reference = pd.read_excel('./原始数据/索引.xlsx', sheet_name = '股票索引')
except FileNotFoundError:
    print('初始化失败。请检查索引文件是否在文件夹下')
else:
    print('初始化成功！')
    
# 这个代码是关掉一个警告
# 虽然有警告，但是实际不影响使用
# 不得已而为之……还是要找到原因，解决警告
pd.set_option('mode.chained_assignment', None)


# In[18]:


# 基础查询功能

def stock_code(): # 股票名 → 股票代码
    try:
        name = input('请输入准确的股票名')
        print('您查找的名为' + name + '的股票代码为：' + stock_reference.loc[stock_reference['证券简称'] == name]['证券代码'].values[0])
    except IndexError:
        print('您查找的股票名不存在，请检查后再试')

def stock_name(): # 股票代码 → 股票名
    try:
        code = input('请输入准确的股票名')
        print('您查找的代码为' + code + '的股票名为：' + stock_reference.loc[stock_reference['证券代码'] == code]['证券简称'].values[0])
    except IndexError:
        print('您查找的股票代码不存在，请检查后再试')
    
def fund_name(): # 基金代码 → 基金名
    try:
        code = input('请输入准确的基金代码')
        print('您查找的代码为' + code + '的基金名为：' + fund_reference.loc[fund_reference['基金代码'] == code]['基金简称'].values[0])
    except IndexError:
        print('您查找的基金代码不存在，请检查后再试')

year = input('请输入报告期')

def load_data(year=year):
    try:
        data = pd.read_csv('./原始数据/' + year + '.csv')
    except FileNotFoundError:
        print('不存在此文件，请检查后再次输入')
    else:
        print('请稍等，正在导入数据。大约需要30s')
        pieces = dict(list(data.groupby(['stock_code', 'fund_code'])))
        return data, pieces

if year == '2018':
    data, pieces = load_data()
else:
    data = pd.read_csv('./原始数据/' + year + '.csv')
print('导入数据成功！')


# In[20]:


# 股票类
class Stock():
    def __init__(self):
        try:
            self.code = input('请输入证券代码')
            self.name = stock_reference.loc[stock_reference['证券代码'] == self.code]['证券简称'].values[0]
        except IndexError:
            print('不存在此证券代码，请重试')
            return
        self.year = year
        print('成功实例化' + self.name + '!')
        
    def search_section(self): # 查询截面数据
        if not data[(data['stock_code'] == self.code)].isnull().any().any():
            try:
                name_1 = stock_reference.loc[stock_reference['证券代码'] == self.code]['证券简称'].values[0]
            except IndexError:
                print("查询失败，可能是以下两种情况：")
                print('1. 股票代码不存在。请重新输入股票代码self.code = "正确的代码" 以纠正该错误。')
                print('2. 该季度无公募基金持仓该股票')
                return
        data1 = data[(data['stock_code'] == self.code)].copy()
        data1.sort_values(by='stock_value', inplace=True, ascending=False)
        data2 = data[(data['stock_code'] == self.code)&(data['season'] == 1)].copy()
        data3 = data[(data['stock_code'] == self.code)&(data['season'] == 2)].copy()
        data4 = data[(data['stock_code'] == self.code)&(data['season'] == 3)].copy()
        data5 = data[(data['stock_code'] == self.code)&(data['season'] == 4)].copy()
        # 写入
        with pd.ExcelWriter(r'./生成的查询数据/'+ self.year + '年各' + self.name + '公募基金持仓截面数据.xlsx') as writer:
            data1.to_excel(writer,index = False, sheet_name='总表')
            data2.to_excel(writer,index = False, sheet_name='一季度')
            data3.to_excel(writer,index = False, sheet_name='二季度')
            data4.to_excel(writer,index = False, sheet_name='三季度')
            data5.to_excel(writer,index = False, sheet_name='四季度')
        print('结果已保存至程序文件夹下，结果按持仓市值排序。')
    
    def search_change(self): # 查询变化
        global data
        global pieces
        # 要改成第一年和其他年不一样，跨年的地方要修缮
        data1 = pd.DataFrame(np.random.randn(1, 8), 
                            columns=['fund_code', '基金名', 'season', 'stock_code', 'stock_value', 'stock_num',
                                    '加仓市值', '加仓数量'
                                    ])
                            
        # 辅助函数
        def calculate_change(value):
            for i in range(4):
                if i == 0:
                    continue
                else:
                    value['加仓数量'][i] = value['stock_num'][i] - value['stock_num'][i-1]
                    value['加仓市值'][i] = value['stock_value'][i] - value['stock_value'][i-1]
            value.drop(value[value['加仓市值'] == 0].index, inplace=True)

            
            
        '''-------主函数--------'''
        print('正在查询中，请稍等片刻')
        # 如果是第一年，则不需要2018年第一季度
        if self.year == '2018':
            for key, value in pieces.items():
                if key[0] != self.code: # 查找的数据不是这只股票就跳过
                    continue
                # 填充不存在的季度为0
                for i in range(1, 5): # 一年四季
                    if i not in list(value['season']):
                        now = value.iloc[[0]].copy()
                        now['season'] = i
                        now['stock_num'] = 0
                        now['stock_value'] = 0
                        value = pd.concat([value, now], ignore_index=True)
                value.sort_values(by='season', inplace=True)
                value.index = [0,1,2,3]
                value['加仓数量'] = 0
                value['加仓市值'] = 0
                for i in range(4):
                    if i == 0:
                        continue
                    else:
                        value['加仓数量'][i] = value['stock_num'][i] - value['stock_num'][i-1]
                        value['加仓市值'][i] = value['stock_value'][i] - value['stock_value'][i-1]
                value.drop(value[value['加仓市值'] == 0].index, inplace=True)

                # 缝合
                data1 = pd.concat([data1, value], ignore_index=True) 

            data1.drop(0, inplace=True)# 把一开始创建的第一行删掉
            data1.drop(data1[data1['season'] == 1].index, inplace=True) # 把第一季度删掉
            # 排序
            data1.sort_values(by=['season','加仓数量'], ascending=False, inplace=True) 
            data2 = data1[data1['season'] == 2].copy().sort_values(by='加仓数量', ascending=False)
            data3 = data1[data1['season'] == 3].copy().sort_values(by='加仓数量', ascending=False)
            data4 = data1[data1['season'] == 4].copy().sort_values(by='加仓数量', ascending=False)
            # 写入文件中
            with pd.ExcelWriter(r'./生成的查询数据/'+ self.year + '年各季度' + self.name + '公募基金持仓变化情况.xlsx') as writer:
                data1.to_excel(writer, index = False, sheet_name='总表')
                data2.to_excel(writer, index=False, sheet_name='二季度')
                data3.to_excel(writer, index=False, sheet_name='三季度')
                data4.to_excel(writer, index=False, sheet_name='四季度')

            print('结果已保存至程序文件夹下')
        
        # 查询的若不是第一年，则需要加上前一年第四季度的数据来计算
        else:
            prev_year = str(int(year)-1)
            prev_data = pd.read_csv('./原始数据/' + prev_year + '.csv')
            prev = prev_data[prev_data['season'] == 4].copy()
            prev['season'] = 0
            data = pd.concat([data,prev], ignore_index=True)
            pieces = dict(list(data.groupby(['stock_code', 'fund_code'])))
            for key, value in pieces.items():
                if key[0] != self.code: # 查找的数据不是这只股票就跳过
                    continue
                # 填充不存在的季度为0
                for i in range(0, 5): # 非第一年的有点特殊，我的处理方法是，在2019年加入了第0季，表示2018年第4季度
                    if i not in list(value['season']): # 如果有季度没有持仓，则创建一条为0的记录
                        now = value.iloc[[0]].copy()
                        now['season'] = i
                        now['stock_num'] = 0
                        now['stock_value'] = 0
                        value = pd.concat([value, now], ignore_index=True)
                value.sort_values(by='season', inplace=True)
                value.index = [0,1,2,3,4]
                value['加仓数量'] = 0
                value['加仓市值'] = 0
                for i in range(5):
                    if i == 0:
                        continue
                    else:
                        value['加仓数量'][i] = value['stock_num'][i] - value['stock_num'][i-1]
                        value['加仓市值'][i] = value['stock_value'][i] - value['stock_value'][i-1]
                value.drop(value[value['加仓市值'] == 0].index, inplace=True)

                # 缝合
                data1 = pd.concat([data1, value], ignore_index=True) 

            data1.drop(0, inplace=True)# 把一开始创建的第一行删掉
            data1.drop(data1[data1['season'] == 0].index, inplace=True) # 把上一年的第四季度删掉
            # 排序
            data1.sort_values(by=['season','加仓数量'], ascending=False, inplace=True) 
            data5 = data1[data1['season'] == 1].copy().sort_values(by='加仓数量', ascending=False)
            data2 = data1[data1['season'] == 2].copy().sort_values(by='加仓数量', ascending=False)
            data3 = data1[data1['season'] == 3].copy().sort_values(by='加仓数量', ascending=False)
            data4 = data1[data1['season'] == 4].copy().sort_values(by='加仓数量', ascending=False)

            # 写入文件中
            with pd.ExcelWriter(r'./生成的查询数据/'+ self.year + '年各季度' + self.name + '公募基金持仓变化情况.xlsx') as writer:
                data1.to_excel(writer, index = False, sheet_name='总表')
                data5.to_excel(writer, index = False, sheet_name='一季度')
                data2.to_excel(writer, index=False, sheet_name='二季度')
                data3.to_excel(writer, index=False, sheet_name='三季度')
                data4.to_excel(writer, index=False, sheet_name='四季度')

            print('结果已保存至程序文件夹下')
        '''------主函数结束------'''


# In[21]:


stock = Stock()


# In[16]:


stock.search_section()


# In[29]:


stock.search_change()


# In[46]:


# 修改报告期的模板代码
''' 模板开始-------------------------

# 引号不能省略
year = '2018'
# 载入新数据集
#data = pd.read_csv('./原始数据/' + year + '.csv') # 切换至2019、2020年，请使用这行代码
data, pieces = load_data()                        # 切换至2018年，请使用这行代码
# 重新创建股票实例
stock = Stock()

模板结束------------------------- '''


# In[ ]:




