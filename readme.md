# About This Website 

### 关于html中的publications格式
- 所有论文统一保存在div id = publicationsList中
- 每篇论文均要使用data属性增设dic class = card mb-3，方便javascript筛选
- 论文前端主题卡片类为"div class="card-body""
- 所有论文元素最初应当均设置为display=none，统一由function.js调度显示

### 关于增设的function.js功能函数
- function.js包含javascript中的过滤、排序函数，详细注释请参阅该文件
- 论文的card的card.style.display = 'none'时就隐藏，为'block'时显示
- inline block会将元素显示在更内层，block是直接显示，而对于'Show All'按钮，必须将其设置为inline-block才能居中显示

### 关于筛选过滤Publications功能模块的说明

1. 网页初始化后，会先执行function.js的最后一行filterAndSort()函数

2. 下拉框id="xxxFilterDropdown"
```
    (1) 在下拉框中的<option value="xxx">中的value中填写用于程序筛选的值；
    (2) 下拉框中的文本值无关紧要；
    (3) 初始时下拉框的value设置为空值""，方便function.js中进行判断。
```

3. 论文展示条目class="card mb-3"
```
    (1) 在未经筛选时，首先将所有的论文均不显示，即设置style="display: none"；
    (2) 根据下拉框设置对应的data-xxx值，例如设置data-year="2025"代表当前论文的发表是2025年。
```

4. filterAndSort()函数运行机制
```
    (1) 首先获得每个下拉框的具体选择的value(这里与第2点中的value对应上)；
    (2) 对所有card进行筛选(与第3点的论文card对应上)；
    (3) 设置showMoreBtn、thatAllBtn、noPaperBtn的显示方式。
```

5. **特别注意：注意function.js筛选时对王老师多重名称的处理，并且均应转为小写**

### 关于tools程序性进行论文转为html以及新增论文、新增成员的说明
1. tools文件夹模式
```
    ---tools
        // 存储了所有论文的json格式，新增论文请在此新增
        ---final_all_papers.json 
        // 附带将上述json转为html-card的功能函数
        ---publications_to_html.py 
        // 是王老师之前收集的金山文档中的html，之后统一使用final_all_papers.json
        ---wang_html_publications.txt 
```

2. 关于王老师的金山文档wang_html_publications.txt的解析
```
    (1) tools/publications_to_html.py中的wang_to_json()函数解析金山文档中所有html并将其转为json存储。
``` 

3. 关于所有论文json格式转为html
```
    总体运行：python publications_to_html.py 函数为json_to_html()


    (1) tools/publications_to_html.py中的json_to_html()函数首先解析所有筛选条件；
    (2) 之后将所有筛选条件组合成filter html；
    (3) 之后组合论文的html；
    (最后尤其重要) 进行牛牛index.html的更新。
```

4. 关于所有团队成员json格式转为html
```
    总体运行：python publications_to_html.py 函数为member_json_to_html()


    (1) tools/publications_to_html.py中的member_json_to_html()函数首先解析所有筛选条件；
    (2) 之后将所有筛选条件组合成filter html；
    (3) 之后组合成员卡片card的html；
    (最后尤其重要) 进行牛牛index.html的更新。
```

**非常重要！！！ 注意当进行"牛牛_index.html"的更新时，会定向更新以'<!-- wby: 注意，切勿删除，程序代码识别xxx开始部分 -->'开始并以'<!-- wby: 注意，切勿删除，程序代码识别xxx开始部分 -->'结束的部分，因此不要随意删减牛牛_index.html中的注释**

### 关于增设美观流动项

1. 本节术语
```
    (1) 屏幕百分比：指我们人在前端可视化网页时看到的百分比，屏幕100%指的就是整个屏幕，取值区间为[0, 100%]；
    (2) 画布百分比：指我们设定流动时定义的画布，可以为任何值，取值区间为[0, +∞)
```

2. 首先在style中引入动画的定义：
```
    @keyframes gradient-flow {
      0% { background-position: 0% 50%; }
      100% { background-position: 100% 50%; }
    }
```
**注意！！！这里的百分数不是前端的屏幕尺寸，而是你定义的画布尺寸，比如你定义了background-size: 300% 100%;，那么这里的100%就是300%！！！**

3. 在主组件中设置三项
```
    (1) 设置背景渐变 background: linear-gradient(xxxdeg[角度], 颜色 xx%, 颜色 xx%)；
    (2) 设置background-position: 0% 50%; 表示起始在x轴0% y轴50%的位置；
    (3) 设置background-size: 300% 100%; 表示画布尺寸x轴为300%，y轴为100%。
    注意！上述三个必须按顺序设置！
```
**注意！！linear-gradient中的百分数不是前端的屏幕尺寸，而是你定义的画布尺寸，比如你定义了background-size: 300% 100%;，那么这里的100%就是300%！！！**

4. 设定循环流动
```
    .组件名称:hover {
      animation: gradient-flow 1.5s linear infinite;
    }
```

5. 可视化无限循环不跳变的技巧(一句话总结为开始与结束一致，且将结束的所有颜色定为屏幕的100%)
```
    (1) 设置linear-gradient：确保视野开始与结束画面的重合，即设定linear-gradient确保开始帧与结束帧颜色渐变一致；
    (2) 计算background-size：确保结束时显示为屏幕的100%，即假如设定为[颜色1，颜色2]作为结束，那么[颜色1，颜色2]之间的间隔将为屏幕的100%，整体画布x轴尺寸计算为 100% / (最终颜色之间的间隔数) * 总间隔数；
    (3) 补加：可做可不做，由于比如你设定 颜色a 25%, 颜色b 50%, 颜色a 75%, 颜色b 100%。由于一开始的画面其实50%后面还会被75%的影响，因此昨晚上述(1)(2)后建议在尾部超出100%的位置补加一个颜色（比如此example补加一个颜色a）。这样操作起来更复杂，要先补加，然后重新计算background-size，然后还要设定gradient-flow结束时并不是100%。
``` 