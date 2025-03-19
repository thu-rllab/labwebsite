## about this website 

### 关于html中的论文格式
- 所有论文统一保存在div id = publicationsList中
- 每篇论文均要使用data属性增设dic class = card mb-3，方便javascript筛选
- 论文前端主题展示为<div class="card-body">
- 所有论文元素最初应当均设置为display=none，统一由function.js调度显示

### 关于增设的function.js功能函数
- function.js包含javascript中的过滤、排序函数，详细注释请参阅该文件
- 论文的card的card.style.display = 'none'时就隐藏，为'block'时显示
- inline block会将元素显示在更内层，block是直接显示，而对于'Show All'按钮，必须将其设置为inline-block才能居中显示

2. Questions
- btn btn-secondary btn-sm这玩意儿在哪定义的？