
from functools import wraps

def exec_params(sql_snippets,params):
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

    return ("".join(sql_query),sql_params)
class Relation(str):
    """Relation is indetented well parenthesated string formuala"""
    pass
def AND(*snippets,indent=2):
    return REL("AND",*snippets,indent=indent)
def OR(*snippets,indent=2):
    return REL("OR",*snippets,indent=indent)
def REL(rel,*snippets,indent=2):
    indent = " "*indent
    result =[]
    result.append('(')

    for i,snippet in enumerate(snippets):

        if i != 0:
            result.append(indent+rel)
        if isinstance(snippet,Relation):
            for s in snippet.split("\n"):
                result.append(indent+s)
        else:
            result.append(indent+'('+snippet+")")



    r = ("\n").join(result)+"\n)"
    #print("RESULT",rel,":")
    #print(r)
    #print("END")

    return Relation(r)
class SqlQueryBuffer():
    def __init__(self):
        self.snippets = []
    def __call__(self,snippet):
        self.snippets.append(snippet)

    def freeze(self,**params):
        return exec_params("\n".join(self.snippets),params)


if __name__ == "__main__":


    def query_users(users,query,registred):
        q = SqlQueryBuffer()
        q("SELECT name, email FROM")
        if users == True:
            q("users")
        else:
            q("admin")
        q("WHERE")
        q(OR(
            AND("name LIKE {query} OR registred={registred}",
                "address LIKE '%@gmail.com'"),
            "1=0")
        )
        return q.freeze(registred=registred,
                        query=query)
    expected ="""SELECT name, email FROM
users
WHERE
(
  (
    (name LIKE ? OR registred=?)
    AND
    (address LIKE '%@gmail.com')
  )
  OR
  (1=0)
)"""
    r= query_users(users=True,query="% Dupont",registred=1)
    print(r[0])
    print("comparing")
    print(r)

    print(repr(expected))

    assert query_users(users=True,query="% Dupont",registred=1) == (
        (expected,["% Dupont",1]))
