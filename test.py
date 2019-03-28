

def connecttodb(sqlquery1, sqlquery2):
    cnxn = pypyodbc.connect(driver='{SQL Server}', server = 'HQSQLPTranP', database = 'PublicTransGrant_Test')
