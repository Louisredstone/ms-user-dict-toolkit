# 简介

本repo是微软拼音输入法的用户自定义短语功能的工具箱，主要包含以下功能：
- 解析导出的.dat文件，提取短语和对应的词组
- 文本 (json/yaml) 转.dat文件
- 批量导入短语的工具

# 批量导入短语的工具

笔者的个人习惯是在中文输入时使用英文标点. 然而, 偶尔要用到中文的标点符号, 如冒号 (windows路径不支持英文冒号, 但支持中文冒号), 书名号, 人名分隔符·等.
同时, 微软输入法平时输入一些特殊符号也很不方便, 如着重号※, 希腊字母等.

为此, 笔者设计了一个脚本, 用于批量添加快捷输入到微软拼音输入法的用户自定义短语中.
例如`ibkm`呼出`《》`, `icdot`呼出`·`等.

## 命名规则

快捷输入的命名规则如下:
1. 为了避免与正常输入起冲突, 所有快捷输入的名字都以`i`开头. 这是为了模仿微软输入法的u/v模式, 汉语拼音几乎没有以i/o/u/v开头的拼写, 而u和v被占用, 我们选择用i代替.
2. **从微软输入法中导出的所有以`i`开头的短语都会被视为由本脚本生成, 因此请不要使用`i`开头的短语作为手动自定义短语.** 如有冲突, 请修改短语名称或直接修改本脚本.
3. 一个符号可能有多个快捷输入.
4. 中文标点符号有一套专门的编码 (笔者自己设定的), 在无冲突的情况下一般取其英文称呼的前三个字母, 然后加上前缀`i`. 如果按此规则两个符号有冲突, 则会特殊对待. 另一套并行的编码规则是无冲突的情况下取其中文拼音的前三个字母, 然后加上前缀. 同样, 冲突的情况单独对待.
5. 成对的符号有特殊的生成规则, 如`《》`对应的快捷输入是`ibkm`, `《`对应的是`ilbkm`, `》`对应的是`irbkm`, 但`《`和`》`也会在输入`ibkm`时出现在候选词中.
6. 一些符号 (或者其中文变体) 可能在 Markdown (LaTeX) 语法中有对应的表示, 这种情况下对应表示也会采用. (当然要加前缀)

## 使用方法

1. 找到对应设置: 右键输入法 - 设置 - 词库和自学习 - 添加或编辑自定义短语. 我们与UI的交互基本都在这个页面完成.
2. 导出用户自定义短语, 保存为.dat结尾的文件, 例如`user.dat`. 这是为了保存手动定义的短语 (不以`i`开头的短语). 如果为空则无需此步.
3. 设置字符表, 详见char.csv和char-pair.csv. 
4. 如果是初次运行, 需要安装一些依赖包, 运行`pip install -r requirements.txt`.
5. 运行`python main.py --input user.dat --output new.dat`
6. 清空原有的自定义短语. (确保你知道自己在做什么!)
7. 导入新生成的.dat文件.
8. Enjoy!