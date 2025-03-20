# About This Website 

### 关于html中的论文格式
- 所有论文统一保存在div id = publicationsList中
- 每篇论文均要使用data属性增设dic class = card mb-3，方便javascript筛选
- 论文前端主题展示为<div class="card-body">
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

### 关于publication_tool程序性进行论文转为html以及新增论文的说明
1. publication_tool文件夹模式
```
    ---publication_tool
        // 存储了所有论文的json格式，新增论文请在此新增
        ---final_all_papers.json 
        // 附带将上述json转为html-card的功能函数
        ---publications_to_html.py 
        // 是王老师之前收集的金山文档中的html，之后统一使用final_all_papers.json
        ---wang_html_publications.txt 
```

2. 关于王老师的金山文档wang_html_publications.txt的解析
```
    (1) publication_tool/publications_to_html.py中的wang_to_json()函数解析金山文档中所有html并将其转为json存储。
``` 

3. 关于所有论文json格式转为html
```
    总体运行：python publications_to_html.py


    (1) publication_tool/publications_to_html.py中的json_to_html()函数首先解析所有筛选条件；
    (2) 之后将所有筛选条件组合成filter html；
    (3) 之后组合论文的html；
    (最后尤其重要) 进行牛牛index.html的更新。
```
**非常重要！！！ 注意当进行"牛牛_index.html"的更新时，会定向更新以'<!-- wby: 增设筛选下拉框 -->'开始并以'<!-- “Show All” 按钮 -->'结束的部分，因此不要随意删减牛牛_index.html中的注释**

### Questions
- btn btn-secondary btn-sm这玩意儿在哪定义的？