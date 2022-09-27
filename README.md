# 项目说明

全新版本分刀器，新名字：pcr-split-box

如果要使用从本地html导入数据的功能，请自行在项目根目录创建 gzlj.html 文件

默认从网页获取数据

数据来源网站：https://www.caimogu.cc/gzlj.html

运行命令：

```
python main.py [BOSS] [ORDER_KEY] [REQUEST_MODE]

e.g.
python main.py A score always
python main.py B damage auto
python main.py C score never
```

## 2022/09/27更新

制作了一个简陋的 gui 界面 app.py

main.py 已经废弃，不再更新，现在主要开发 gui 界面

## 第一版 release 说明

程序入口为 PcrSplitBox.exe 文件

设置禁用角色和缺少的角色，需要手动修改根目录下 config.json 文件 (按照json格式)

"ban_list": 禁用角色，设置禁用角色可以减少搜索的压力，提高搜索的速度，减少内存占用等。设置后，分刀方案中将不会包含禁用的角色

"lack_list": 缺少的角色，设置缺少的角色后，分刀时仍会考虑缺少的角色

* 注意事项：

在方括号[]里填入角色名，注意使用半角双引号(英文输入法的双引号)，每个角色之间用半角逗号(英文输入法)间隔

* 设置案例：

```
{"ban_list": ["圣千", "春女仆"], "lack_list": ["春猫", "圣锤"]}
```

(后续可能会出设置的ui界面，现在...太累了，摸了)
