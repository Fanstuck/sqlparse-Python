from MainDef import *

if __name__ == '__main__':
    sql=get_sqlstr('read_sql.txt')
    stmt_tuple=analysis_statements(sql)
    for each_stmt in stmt_tuple:
        blood_table(each_stmt)
        get_tablename()
        0000
