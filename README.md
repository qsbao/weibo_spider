# 微博评论爬虫

核心逻辑在[rmrb_spider/spiders/rmrb.py](rmrb_spider/spiders/rmrb.py)

## 安装
1. 安装Python3
2. 安装Python依赖
```
pip3 install -r requirements.txt 
```

## 启动
1. 进入rmrb_spider/spiders文件夹
2. 执行命令，微博评论内容输出到了out.xml内
```
scrapy runspider rmrb.py -o out.xml
```
