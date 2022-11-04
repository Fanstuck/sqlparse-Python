from MainDef import *

if __name__ == '__main__':
    sql=get_sqlstr('read_sql.txt')
    stmt_tuple=analysis_statements(sql)
    for each_stmt in stmt_tuple:
        type_name = get_main_functionsql(each_stmt)
        blood_table(each_stmt)
        blood_column(each_stmt)
        get_aliasnames()
