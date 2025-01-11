# 写在开始的声明

自用的程序，因为使用obsidian需要个人的本地图床，所以使用这个程序，发现一些不舒服的地方。此前因为自己不是程序员搞不定所以就凑合着用，但是现在有了AI加持，我只要会提要求就行。然后用cursor尝试发现效果不错，所以发上来，如果有类似需求的人则正好帮助到别人，也算没白折腾。
再次强调我不是程序员，所以肯定有一些什么协议什么东西，或者告知不到位的地方，请程序员团体多包涵。以上所有修改内容都是利用cursor完成的，任何人都能做到类似效果，这里面没有我的原创内容，任何人都可以直接fork我现在维护的这个库。

## 使用细节
我的这个库其他内容都没有什么改变，只是强化了原本程序没有做的图片管理内容，在默认的127.0.0.1:8888端口浏览器打开后，页面最上方左侧有一个图片管理入口，进入之后就可以管理，删除你已经放在pics的图片文件，你可以直接用网页的上传功能，也可以用picgo，piclist等软件上传，但是本人能力有限，目前没有找到兼容piclist删除的方法，所以无法做到piclist删除管理的功能。别的功能都可以正常使用。

## 基本教程

可以参考https://www.bilibili.com/video/BV16S4y1v7Kb/?vd_source=7fdb60e4077f3e4b6c6dda4a44a3dcc7 的内容进行设置，我这个软件只是简化了一些内容，不需要执行教程提到的文件替换操作，解压即算是准备好。其他设置可以照搬视频的内容进行操作。

## 最后，优化内容

1. 分页功能
每页显示20条记录
添加页码导航
支持页面跳转功能
2. 搜索优化
支持文件名和日期搜索
移除实时搜索，改为点击或回车触发
搜索结果支持分页
3. 界面美化
添加深色主题
优化表格样式和对比度
美化滚动条
改进表单控件样式
4. 性能优化
异步执行文件检查
优化数据库查询
添加错误处理和日志记录
5. 代码优化
改进数据库操作的事务处理
优化文件检查逻辑
统一返回值格式
这些优化提升了系统的可用性、性能和用户体验
内容来自cursor，再次声明，我不是程序员，我不知道这个程序到底使用了哪些人的原创，如果有侵权问题请告知。


[您可以进入项目的官方网站获取更多帮助](http://my-easy-pic-bed.ringotek.cn)
# (For users who speak English, there is an readme.md in English edition, please roll down the page to read)

# 这是啥？

&nbsp;

MY-Easy-Pic-Bed 是一款轻量级的图床服务器软件，采用Apache lincense 2.0开源。它基于Python3.8和Flask框架开发，基本不需要配置，就能在您的电脑上搭建一个图床。当然，您也可以将它移动到您的服务器上，成为可以对外提供服务的图床。

&nbsp;&nbsp;

# 有啥用？

&nbsp;

MY-Easy-Pic-Bed 是专门为喜欢在电脑上使用markdown写博客、写笔记的同学们设计的。有了它，你再也不需要担心你的文章的插图会因为文件路径的改变而需要重新配置链接。

&nbsp;

你只需要把图片放到 MY-Easy-Pic-Bed 之中，就只需要在Markdown文件中插入程序返回的地址即可插入图片！

&nbsp;

你可能会说，我直接把图片统一放置在一个文件夹里不就好了吗？

&nbsp;

的确，但是如果你使用了MY-Easy-Pic-Bed，你就可以很方便地在多台计算机之间移动你的笔记，而无需关心文件存储位置的问题。试想一下，如果把文件放置在一个文件夹里而不是使用 MY-Easy-Pic-Bed ，你在更换电脑的时候，需要重新配置每篇文章的图片链接！这可是极大的工作量！

&nbsp;

没事，现在有了 MY-Easy-Pic-Bed ，这一切都只需要交给它，你只需要专心于写作即可！

&nbsp;



# 怎么在笔记中使用 MY-Easy-Pic-Bed ？

&nbsp;

你只需要把图片传至你的 MY-Easy-Pic-Bed ，然后把它返回的链接填写到Markdown文件之中。

&nbsp;

当更换电脑的时候，你只需要把 MY-Easy-Pic-Bed 的文件目录以及你的笔记复制到新电脑，然后运行 MY-Easy-Pic-Bed 和文本编辑器。你又可以像在之前的电脑上一样使用你的笔记了！

&nbsp;&nbsp;

###### 注意，在您编辑笔记的过程中，需要一直打开 MY-Easy-Pic-Bed 以确保图片能正常显示。不过请你放心，这并不会对你的电脑的流畅度造成丝毫影响！

&nbsp;&nbsp;
---
title: 安装MY-Easy-Pic-Bed
date: 2020-11-16 21:44:27
tags: document

---

# 开始之前

## 环境准备

请您提前在您的计算机上安装python 3.8

然后

在控制台中输入

```
pip install flask
```

# 下载 MY-Easy-Pic-Bed

首先，您需要在github上下载本项目到您的计算机

```
git clone https://github.com/fslongjin/My-Easy-Pic-Bed.git
```

### 中国大陆下载加速

如果您位处中国大陆，您可以通过以下命令来加速您的下载

```
git clone https://gitclone.com/github.com/fslongjin/My-Easy-Pic-Bed.git
```

# 

nbsp;nbsp;


# 开始之前

&nbsp;

## 请您先安装 MY-Easy-Pic-Bed

&nbsp;

# 运行MY-Easy-Pic-Bed

&nbsp;

至此，安装结束了！看来，My-Easy-Pic-Bed真的是有史以来最容易安装的图床软件！

&nbsp;

### 对于Windows平台

您只需要双击 startProgram.exe 即可运行MY-Easy-Pic-Bed ！

&nbsp;

### 对于Linux平台

您需要在MY-Easy-Pic-Bed的根目录下打开终端，然后执行以下命令：

```
python3 app.py
```

于是，程序就成功启动了！


-------------------------------
English Edition

[You can visit the official website of this project for more help](http://my-easy-pic-bed.ringotek.cn)
# What is this?
 
My-Easy-Pic-Bed is a lightweight pic bed server software, which is open source with Apache lincense 2.0. It is based on Python 3.8 and flask framework, basically no configuration, you can build a pic bed on your computer. Of course, you can also move it to your server and become a pic bed for external services.
  
# What is the use?
 
My-Easy-Pic-Bed is designed for students to write notes on their computers. With it, you no longer need to worry that the illustrations of your article will need to be reconfigured due to changes in file paths.
 
You just need to put the picture in my easy pic bed and just insert the address returned by the program in the markdown file to insert the picture!
 
You might say, I just put the pictures in one folder?
 
Yes, but if you use My-Easy-Pic-Bed, you can easily move your notes between multiple computers without having to worry about where the files are stored. Imagine if you put the files in a folder instead of my easy pic bed, you need to reconfigure the image links of each article when you change your computer! It's a lot of work!
 
It's OK, now that you have my easy pic bed, all you need to do is hand it over. You just need to concentrate on your writing!
 
#How to use my easy pic bed in notes?
 
You just need to send the picture to your My-Easy-Pic-Bed and fill in the markdown file with the link it returns.
 
When changing the computer, you just need to copy my easy pic bed file directory and your notes to the new computer, and then run my easy pic bed and text editor. You can use your notes again as you did on your previous computer!
  
######Note that you need to keep my easy pic bed open as you edit your notes to make sure the pictures are displayed properly. However, please rest assured that this will not affect the fluency of your computer at all!
  
---
Title: installing My-Easy-Pic-Bed
date: 2020-11-16 21:44:27
tags: document
---
# Before you start
# Environmental preparation
Please install Python 3.8 on your computer in advance
then
Enter in the console
` ` ` `
pip install flask
` ` ` `
# Download my easy pic bed
First, you need to download the project to your computer on GitHub
` ` ` `
git clone  https://github.com/fslongjin/My-Easy-Pic-Bed.git
` ` ` `
Chinese mainland download and accelerate
If you are in Chinese mainland, you can accelerate your download by following commands.
` ` ` `
git clone  https://gitclone.com/github.com/fslongjin/My-Easy-Pic-Bed.git
` ` ` `

nbsp;
nbsp;
# Before you start
 
# Please install My-Easy-Pic-Bed first
 
##Run My-Easy-Pic-Bed
 
At this point, the installation is over! It seems that My-Easy-Pic-Bed is the easiest pic bed software ever installed!
 
### For Windows platform
You just double-click startProgram.exe to run My-Easy-Pic-Bed!
 
### For Linux platform
You need to open the terminal in the root directory of My-Easy-Pic-Bed and execute the following command:
` ` ` `
python3  app.py
` ` ` `
So, the program started successfully!
