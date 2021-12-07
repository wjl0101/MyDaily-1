# 😈自动打卡平安复旦脚本

## 简介📖
这个项目是Follow这个[工作](https://github.com/ZiYang-xie/Hello_Fudan)，做了一点小小的改动。
主要做了一下几个改动:
* 重构了文档结构，将connection和ocr分离方便之后扩展
* 增加了推送微信功能，打卡成功可被通知

github配置和uid、密码配置见这个[教程](https://github.com/ZiYang-xie/pafd-automated/tree/master/docs).

对于主要更新的微信推送功能，教程如下:

微信推送使用的Server酱提供的工具, 链接看[这里](https://sct.ftqq.com/login).

![image](https://user-images.githubusercontent.com/53508777/144698842-ee1aaae3-f0a8-403e-852e-2845c4cb19ec.png)

通过这个获取sendkey, 获取后在GitHub中建立uid和密码secret的地方建立一个名为 SENDKEY 的新secret, value即为上面复制的sendkey.
