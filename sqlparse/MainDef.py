#Autor fanstuck
# the BSD License: https://opensource.org/licenses/BSD-3-Clause
from pyecharts import options as opts
from pyecharts.charts import Tree
from pyecharts.charts import Sankey
import sqlparse
import textwrap
from sqlparse.sql import Parenthesis,Function,Identifier, IdentifierList
from sqlparse.tokens import Keyword, Name


COLUMN_OPERATIONS={'SELECT','FROM'}
FUNCTION_OPERATIONS={'SELECT','DROP','INSERT','UPDATE','CREATE'}
RESULT_OPERATIONS = {'UNION', 'INTERSECT', 'EXCEPT', 'SELECT'}
ON_KEYWORD = 'ON'
PRECEDES_TABLE_NAME = {'FROM', 'JOIN', 'DESC', 'DESCRIBE', 'WITH'}
global table_names
global column_names
global columns_rank
global function_names
global alias_names
table_names = []
column_names = []
function_names = []
alias_names = []
columns_rank = 0


def __is_identifier(token):
    return isinstance(token, (IdentifierList, Identifier))


def __is_identifiers(token):
    return isinstance(token, Identifier)


def __is_identifiersList(token):
    return isinstance(token, IdentifierList)


def __is_Function(token):
    return isinstance(token, Function)


def __is_Parenthesis(token):
    return isinstance(token, Parenthesis)


def __precedes_function_name(token_value):
    for keyword in FUNCTION_OPERATIONS:
        if keyword in token_value:
            return True
    return False
#字段血缘可视化
def column_visus():
    list_table=[]
    list_columns=[]
    table_link_list=[]
    for i in range(len(table_names)):
        children_dict={"name":table_names[i]}
        list_table.append(children_dict)
    for i in range(1,len(column_names)):
        for j in range(len(column_names[i])):
            children_dict={"name":column_names[i][j]}
            list_columns.append(children_dict)
    nodes_list=list_table+list_columns
    leaf_num=len(nodes_list)-len(table_names)
    table_link_list=[]
    columns_link_list=[]
    for i in range(1,len(table_names)):
        table_link_dict={'source':table_names[0],'target':table_names[i],'value':10}
        table_link_list.append(table_link_dict)
    for i in range(1,len(table_names)):
        for j in range(len(column_names[i])):
            columns_link_dict={'source':table_names[i],'target':column_names[i][j],'value':5}
            columns_link_list.append(columns_link_dict)
    links_list=table_link_list+columns_link_list
    res = [i for n, i in enumerate(nodes_list) if i not in nodes_list[:n]]
    pic = (
        Sankey()
        .add(
            "表与字段",   #设置图例名称
            nodes=res,   #传入节点数据
            links=links_list,   #传入边和流量数据
            linestyle_opt = opts.LineStyleOpts(opacity = 0.5, curve = 0.5, color = "source"),   #设置透明度、弯曲度、颜色，color可以是"source"或"target"
            label_opts = opts.LabelOpts(position = "right"),   #设置标签位置，position可以是"top"、"left"、"right"、"bottom"等
            node_width = 20,    #设置节点矩形的宽度
            node_gap = 10,   #设置节点矩形的距离
        )
        .set_global_opts(title_opts=opts.TitleOpts(title="字段血缘"))   #设置图表标题
    )
    
    return pic.render_notebook()
#表数据可视化
def Tree_visus(table_names,type_name):
    if type_name != 'SELECT':
        table_names=list(set(table_names))
        list_children=[]
        for i in range(len(table_names)-1):
            children_dict={"name":table_names[i+1]}
            list_children.append(children_dict)
        dict_children={"children":list_children,"name": table_names[0]}
        data=[dict_children]
        c = (
        Tree()
        .add("", data)
        .set_global_opts(title_opts=opts.TitleOpts(title="血缘-{}".format(type_name)))
        .render_notebook()
        )
        return c
    else :
        table_names=list(set(table_names))
        list_children=[]
        for i in range(len(table_names)):
            children_dict={"name":table_names[i]}
            list_children.append(children_dict)
        dict_children={"children":list_children,"name": 'SELECT'}
        data=[dict_children]
        c = (
        Tree()
        .add("", data)
        .set_global_opts(title_opts=opts.TitleOpts(title="查询-{}".format(type_name)))
        .render_notebook()
        )
        return c

# 字段血缘
def blood_column(statment):
    global function_names
    global alias_names
    global column_names
    _create_column_list(column_names)
    _extract_column_from_token(statment)
    function_names = distinct_list(function_names)
    alias_names = distinct_list(alias_names)
    distinct_delect_alias_columns()
    zipped = zip(table_names, column_names)
    zipped = list(zipped)
    inherit_columns = zipped[0]
    root_columns = zipped[1:]
    if get_main_functionsql(statment) != 'SELECT':
        columns_Bloodcurse = '{}->{}'.format(inherit_columns, root_columns)
        return columns_Bloodcurse
    else:
        columns_Bloodcurse = column_names
        return columns_Bloodcurse


# 表血缘
def blood_table(statment):
    if __precedes_function_name(get_main_functionsql(statment)):
        idfr_list = _get_one_Identifier(statment)
        get_Identifier_keywords_tables(idfr_list[0])
    type_name = get_main_functionsql(statment)
    _extract_table_from_token(statment)
    inherit_table = table_names[0]
    root_table = set(table_names[1:])
    if get_main_functionsql(statment) != 'SELECT':
        table_Bloodcurse = '{}->{}'.format(inherit_table, root_table)
        return table_Bloodcurse
    else:
        table_Bloodcurse = set(table_names)
        return table_Bloodcurse


def __precedes_table_name(token_value):
    for keyword in PRECEDES_TABLE_NAME:
        if keyword in token_value:
            return True
    return False


def __precedes_column_name(token_value):
    for keyword in COLUMN_OPERATIONS:
        if keyword in token_value:
            return True


def __is_result_operation(keyword):
    for operation in RESULT_OPERATIONS:
        if operation in keyword.upper():
            return True
    return False


def __process_identifier(identifier):
    # 如果有嵌套那么一定存在()
    if '(' not in '{}'.format(identifier):
        get_Identifier_keywords_tables(identifier)
        return
    _extract_table_from_token(identifier)


# 获取所有字段存在
def __process_column_identifier(identifier):
    get_Identifier_keywords_column(identifier)
    _extract_column_from_token(identifier)


# 创建column_names
def _create_column_list(columns_rank):
    global column_names
    #print(column_names)
    #print(len(table_names))
    for i in range(len(table_names)):
        #print(i)
        column_names.append([])
    #print(column_names)
    #print(len(table_names))
    return column_names


# 提出该SQL涉及到的功能关键字
def __process_Function_Identifier(Function):
    for item in Function.tokens:
        if __is_identifiers(item):
            function_names.append(item.value)
        _extract_column_from_token(item)


# 获取字段名
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


# 字段去重
def distinct_delect_alias_columns():
    global column_names
    for i in range(len(table_names)):
        column_names[i] = list(set(column_names[i]))
    column_names_true = []
    for i in column_names:
        column_names_true.append(list(set(i) - set(alias_names)))
    column_names = column_names_true


# 列表去重
def distinct_list(list_qr):
    list_qr = list(set(list_qr))
    return list_qr


# 提底表字段名
def _extract_column_from_token(statment):
    global columns_rank
    if not hasattr(statment, 'tokens'):
        return
    for item in statment.tokens:
        # 除Identifier/IdentifierList以外还有Parenthesis和Function有group，这些需要递归
        if item.is_group and not __is_identifier(item):
            _extract_column_from_token(item)
        if item.ttype in Keyword and item.value == 'SELECT':
            columns_rank = columns_rank + 1
        # 只有identifiers和IdentifierList会有字段
        if isinstance(item, Identifier):
            __process_column_identifier(item)
        if isinstance(item, IdentifierList):
            for token in item.tokens:
                if __is_Function(token):
                    __process_Function_Identifier(token)
                if __is_identifier(token):
                    __process_column_identifier(token)



# 提底表表名
def _extract_table_from_token(statment):
    if not hasattr(statment, 'tokens'):
        return
    # 可添加多个preceding_token
    table_name_preceding_token = False

    for item in statment.tokens:
        # 除Identifier/IdentifierList以外还有Parenthesis和Function有group，这些需要递归
        if item.is_group and not __is_identifier(item):
            _extract_table_from_token(item)

        # 启动函数，依赖PRECEDES_TABLE_NAME，当为指定Keyword时候启发table_name_preceding_token
        if item.ttype in Keyword:
            # 有关键字的情况下可以判定存在表，那么直接跳到符合的情况下，剩余的token不再判断
            if __precedes_table_name(item.value.upper()):
                table_name_preceding_token = True
                continue
                # 那么直接跳到符合的情况下，剩余的token不再判断
        if not table_name_preceding_token:
            continue
        # 可能From里面也嵌套查询等外表，那么再次设定为False再判断一次
        if item.ttype in Keyword or item.value == ',':
            if (__is_result_operation(item.value) or
                    item.value.upper() == ON_KEYWORD):
                table_name_preceding_token = False
                continue
            # FROM clause is over
            break

        # 只有identifiers和IdentifierList会有库.表
        if isinstance(item, Identifier):
            __process_identifier(item)

        if isinstance(item, IdentifierList):
            for token in item.tokens:
                if __is_identifier(token):
                    __process_identifier(token)

                # 该方法解析IdentifierList


def _extract_IdentifierList_Identifier(IdentifierLists, idfr_list):
    tokens_list = IdentifierLists.tokens
    for each_token in tokens_list:
        if __is_identifiers(each_token):
            identifier = each_token
            idfr_list.append(identifier)
        if __is_identifiersList(each_token):
            idfr_list.extend(_extract_IdentifierList_Identifier(each_token, idfr_list))
    return idfr_list


# 满足库.表形式的identifiers提取即判定为表
def get_Identifier_keywords_tables(identifiers):
    global table_names
    if len(identifiers.tokens) == 3 and identifiers.tokens[1].value == ' ':
        a = identifiers.tokens[0].value
        return table_names.append(a)
    if len(identifiers.tokens) > 1 and identifiers.tokens[1].value == '.':
        a = identifiers.tokens[0].value
        b = identifiers.tokens[2].value
        db_table = (a, b)
        full_tree = '{}.{}'.format(a, b)
        if len(identifiers.tokens) == 3:
            return table_names.append(full_tree)
        else:
            i = identifiers.tokens[3].value
            c = identifiers.tokens[4].value
            if i == ' ':
                return table_names.append(full_tree)
            full_tree = '{}.{}.{}'.format(a, b, c)
            return table_names.append(full_tree)
    if len(identifiers.tokens) == 1:
        a = identifiers.tokens[0].value
        return table_names.append(a)


# 第一层Identifier
def _get_one_Identifier(statment):
    idfr_list = []
    tokens_list = statment.tokens
    for each_token in tokens_list:
        if each_token._get_repr_name() == 'Identifier':
            idfr_list.append(each_token)
    return idfr_list


# 获得该条SQL语句的所有涉及到更新查询写入删除操作功能
def get_functionsql(statment):
    function_list = []
    tokens_list = statment.tokens
    for each_token in tokens_list:
        if each_token.value in RESULT_OPERATIONS:
            function_list.append(each_token.value)
    return function_list


# 获得树形结构
def get_ASTTree(statment):
    return statment._pprint_tree()


# 获得该SQL主要功能函数
def get_main_functionsql(statment):
    return statment.get_type()


def analysis_statements(str_sql):
    return sqlparse.parse(str_sql)


def get_sqlstr(file_path):
    with open(file_path, encoding='utf-8') as file:
        content = file.read()
        str_sql = sqlparse.format(content, reindent=True, keyword_case='upper')
        str_sql = str_sql.strip(' \t\n;')
        indent_str = textwrap.indent(str_sql, "  ")
    return indent_str

def get_function_aggregate():
    print(function_names)

def get_aliasnames():
    print(alias_names)
def get_tablename():
    print(table_names)
def get_columnnames(each_stmt):
    blood_table(each_stmt)
    blood_column(each_stmt)
    print(column_names)
