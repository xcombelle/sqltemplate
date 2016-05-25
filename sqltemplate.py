
from functools import wraps
class SqlQuery():
    def __init__(self,sql_snippets,params):
        current_param = None
        sql_query = []
        sql_params = []
        for c in sql_snippets:
            if c == "{":
                current_param = []
            elif c == "}":
                sql_params.append(params["".join(current_param)])
                sql_query.append("?")
                current_param = None
            else:
                if current_param is None:
                    sql_query.append(c)
                else:
                    current_param.append(c)
    
        self.query = "".join(sql_query)
        self.params = sql_params
    def exec_params(self):
        return self.query,self.params
class SqlBuffer():
    def __init__(self):
        self.snippets = []
    def __call__(self,snippet):
        self.snippets.append(snippet)
    def AND(self,*snippets):
        self.REL("AND",*snippets)
    def OR(self,*snippets):
        self.REL("OR",*snippets)
    def REL(self,rel,*snippets):
        self.snippets.append('(')
        for i,snippet in enumerate(snippets):
            if i != 0:
                self.snippets.append(rel)
            self.snippets.append('('+snippet+')')
            
        self.snippets.append(')')
                            
    def freeze(self,params):
        return SqlQuery("\n".join(self.snippets),params)
def sql(query):
    
    @wraps(query)
    def wrapper(**params):
        sql_buffer = SqlBuffer()
        query(sql_buffer,**params)
        return sql_buffer.freeze(params)
    return wrapper


if __name__ == "__main__":

    @sql
    def query1(sql,**params):
        sql("SELECT * FROM")
        if params["table_one"] == True:
            sql("table_one")
        else:
            sql("table_two")
        sql("WHERE")
        sql.AND("name LIKE {query} OR registred={registred}",
                "address LIKE '%@gmail.com'")
    

    expected ="""SELECT * FROM
table_one
WHERE
(
(name LIKE ? OR registred=?)
AND
(address LIKE '%@gmail.com')
)"""
    print( query1(table_one=True,query="% Dupont",registred=1).exec_params(),"\n",repr(expected))
    assert query1(table_one=True,query="% Dupont",registred=1).exec_params() == (
        (expected,["% Dupont",1]))
