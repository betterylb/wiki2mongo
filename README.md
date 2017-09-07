# wiki2mongo

导入维基镜像数据到MongoDB数据库

使用python下的 xml.etree.cElementTree 这个包好像并不是像SAX一样流式解析xml文件的，所以目前只能解析分成小文件的enwiki的dump文件，下载是在：http://dumps.wikimedia.your.org/backup-index.html

解析一个350M的文件在峰值时占用内存4G左右，效率好低，但是不太会用SAX把XML的标签按结构解析，有时间再研究吧。
