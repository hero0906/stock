# Stock
终端实时获取股票价格
====================
给有需要的朋友,投资需谨慎。

用途:
----
    实时查询股票价格，默认查询了沪指、深指
    结果输出到终端

使用:
----
    需要安装requests库
    支持命令行多参数，如果需要帮助：
        python stock_terminal.py -h
    设置查询代码（必传）   -c   
    设置查询时间间隔（默认6秒）   -s   
    设置线程数（默认3）（如果有需要）   -t    
    
    查询 智慧农业 sz000816
    例如:
        python stock_terminal.py -c sz000816 -t 4 -s 3
    
    支持查询多个股票
    例如:
        python stock_terminal.py -c sh601003,sz000816,sz000778,ss600221

实现:
----
    通过调用新浪股票API，实时查询股票价格
    支持查询多支股票，通过threading多线程同时查询结果
    通过Queue实现线程池
    requests请求接口
    optparse实现命令行参数处理
