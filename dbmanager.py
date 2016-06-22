
import mysql.connector as mql
import pprint
from   collections import OrderedDict

class DBManager:



    def __init__(self, use_db=True, exit_on_error=True, **conn_info):
        if not conn_info:
            conn_info  = {'user': "watchdog",
                          'password': "watchdog",
                          'host': "localhost",
                          'port':'3306',
                          'database': "auditor",
                          'raise_on_warnings': True }
        
        # to figure out , do we need to connect to database, or just to instance
        if 'database' in conn_info.keys():
            self.current_database = conn_info['database']
            if not use_db:
                del conn_info['database']
        
        try:
            self.connection = mql.connect(**conn_info)
            self.cursor = self.connection.cursor()
        except Exception as err:
            # prevent from revealing the password
            if exit_on_error:
                if 'password' in conn_info.keys():
                    conn_info['password'] = '*******'
                print("Connection error: {0}".format(conn_info))
                print(err)
                exit(1)
            else:
                raise  
  


    def use_database(self, dbname=''):
        try:
            if not (dbname == ''):
                self.connection.database = dbname
            elif (not self.current_database == ''):
                self.connection.database = self.current_database
            else:
                self.connection.database = ''
        except Exception as err:
            print(err)



    def get_global_variable(self, variable_name):
        try:
            self.cursor.execute("show global variables where variable_name='{0}'".format(variable_name))
            return self.cursor.fetchone()[1]
        except:
            return ''



    def execute_query(self, sql, data_return=False):
        try:
            self.cursor.execute(sql)
            #pprint.pprint(self.cursor.description)
            column_names = self.cursor.column_names
            table = [] 
            row = self.cursor.fetchone()
            while row is not None:
                table.append(zip(column_names, row))
                row = self.cursor.fetchone()
         
            if data_return:
                return table
            else:
                if table:
                    one_line = ''
                    for title in OrderedDict(table[0]).keys():
                        one_line = one_line + ' | ' + str(title)
                    print(one_line)

                    for records in table:
                        one_line = ''
                        for rec in OrderedDict(records).values():
                            one_line = one_line + ' | ' + str(rec).replace('\n','')
                        print(one_line)

        except Exception as err:
            print(err)


    def execute_dml(self, dml, on_fail_exit=False, message='', additional_fail_msg='', additional_ok_msg=''):
        if not message == '':
            print(message)
        try:
            self.cursor.execute(dml)
        except Exception as err:
            if not additional_fail_msg == '':
                print(additional_fail_msg)

            print(err)

            if on_fail_exit:
                exit(1)
        else:
            if not additional_ok_msg == '':
                print(additional_ok_msg)
            self.connection.commit()



    def execute_ddl(self, ddl, on_fail_exit=False, message='', additional_fail_msg='', additional_ok_msg=''):
        if not message == '':
            print(message)
        try:
            self.cursor.execute(ddl)
        except Exception as err:
            if not additional_fail_msg == '':
                print(additional_fail_msg)

            print(err)

            if on_fail_exit:
                exit(1)
        else:
            if not additional_ok_msg == '':
                print(additional_ok_msg)
            self.connection.commit()



    def close(self):
        self.connection.close()



