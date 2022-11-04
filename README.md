# SQLblood-relationship
This project is based on [sqlparse](https://github.com/andialbrecht/sqlparse/tree/9f44d54c07180b826a6276d3acf5e1458b507c3f) conduct experiments.
SQL blood relationship analysis tool based on Python sqlparse
The research on SQL parsing and blood tracking can almost come to an end now. Since August 22, when I wrote the article "Parsing the syntax, morphology, and compiler files of HiveSQL source code" to explain this article in detail, I have studied SQL syntax parsing intermittently. Today, I have finally made some achievements. Generally, such research projects are supported by data governance and data middle office services, which play a great role in data security. I have covered a lot of content in the previous article, so I won't mention it here:

We can see this article based on Python sqlparse's implementation of blood relationship tracking and parsing in SQL tables. Next, we will add the improvement of this function, that is, the implementation of blood relationship parsing in SQL fields. This is a function that must be completed for Hive blood relationship or MySQL. Of course, the implementation is also troublesome. Here we mainly talk about the ideas and implementation steps.
![图片](https://user-images.githubusercontent.com/62112487/198919776-500df560-226d-486d-a8c9-9a3287e122ca.png)
![图片](https://user-images.githubusercontent.com/62112487/198919770-f6c03b37-a524-489d-a8d0-a128bc9ebfe5.png)

## Implementation process
### Format Output
```
def get_sqlstr(file_path):
    with open(file_path, encoding='utf-8') as file:
        content = file.read()
        str_sql = sqlparse.format(content, reindent=True, keyword_case='upper')
        str_sql = str_sql.strip(' \t\n;')
        indent_str = textwrap.indent(str_sql, "  ")
    return indent_str
```
### Operation identification
This function must also be implemented. We need to understand what the SQL is mainly for. If INSERT or CREATE is inserted, blood relationship analysis is necessary. If SELECT is selected, simple SQL analysis is required. With the research results of sqlparse source code, we can call the corresponding functions:
```
# Get the main functions of the SQL
def get_main_functionsql(statment):
    return statment.get_type()
```
###  AST_tree
```
# 获得树形结构
def get_ASTTree(statment):
    return statment._pprint_tree()
```
### Get Field Name
```
def get_Identifier_keywords_column(identifier):
    if len(identifier.tokens) == 1:
        if not isinstance(identifier.parent, Function):
            for i in range(1, len(table_names) + 1):
                if columns_rank == i:
                    a = identifier.tokens[0].value
                    column_names[columns_rank - 1].append(a)
                    break
        else:
            function_names.append(identifier.value)

    if len(identifier.tokens) == 5:
        if (identifier.tokens[0]._get_repr_name() == 'Name'):
            for i in range(1, len(table_names) + 1):
                if columns_rank == i:
                    a = identifier.tokens[0].value
                    column_names[columns_rank - 1].append(a)
                    break

    if len(identifier.tokens) == 7:
        alias_names.append(identifier.tokens[0].value)
```
Based on the above basic methods
# 基于Python-sqlparse的SQL字段与表血缘追踪解析实现
SQL解析和血缘追踪的研究现在差不多可以告一段落了，从8月22日写[HiveSQL源码之语法词法编译文件解析一文详解](https://blog.csdn.net/master_hunter/article/details/126462698) ，这篇文章以来便断断续续的对SQL语法解析研究，到了今天终于是有了一番成果。一般做此类研究的项目都是在数据治理和数据中台方面的服务作支撑，对于数据安全作用挺大的，多的内容我在上篇文章里面已经讲述了很多了，这里不再多提，基于下面测试的成果：[基于Python-sqlparse的SQL表血缘追踪解析实现](https://jxnuxwt.blog.csdn.net/article/details/127387722) ，大家可以看这篇文章，接下来是接着上篇内容补充一下该功能的完善，也就是实现SQL字段血缘的解析，这是做Hive血缘或者mysql必须完成的功能，当然实现起来也是比较麻烦的。这里主要讲一下思路和实现的步骤。
![图片](https://user-images.githubusercontent.com/62112487/198917778-12ddda26-c205-4fb5-a3c2-492599cda0e7.png)
## 实现过程
### 格式化输出
算是格式化清洗所有的SQL了：
```
def get_sqlstr(file_path):
    with open(file_path, encoding='utf-8') as file:
        content = file.read()
        str_sql = sqlparse.format(content, reindent=True, keyword_case='upper')
        str_sql = str_sql.strip(' \t\n;')
        indent_str = textwrap.indent(str_sql, "  ")
    return indent_str
```
### 操作识别
该功能也是必须要实现的功能，我们需要明白这个SQL主要是干什么事情的。如果是插入INSERT或者是CREATE就有血缘分析的必要，如果是SELECT的话那么做简单的SQL解析即可。有了研究sqlparse源码的成果我们调用相应的函数即可：
```
# 获得该SQL主要功能函数
def get_main_functionsql(statment):
    return statment.get_type()
```
### 树形解构
```
# 获得树形结构
def get_ASTTree(statment):
    return statment._pprint_tree()
```
### 获取字段
```
def get_Identifier_keywords_column(identifier):
    if len(identifier.tokens) == 1:
        if not isinstance(identifier.parent, Function):
            for i in range(1, len(table_names) + 1):
                if columns_rank == i:
                    a = identifier.tokens[0].value
                    column_names[columns_rank - 1].append(a)
                    break
        else:
            function_names.append(identifier.value)

    if len(identifier.tokens) == 5:
        if (identifier.tokens[0]._get_repr_name() == 'Name'):
            for i in range(1, len(table_names) + 1):
                if columns_rank == i:
                    a = identifier.tokens[0].value
                    column_names[columns_rank - 1].append(a)
                    break

    if len(identifier.tokens) == 7:
        alias_names.append(identifier.tokens[0].value)
```      

