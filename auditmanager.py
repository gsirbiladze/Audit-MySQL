
from sqlstorage import *
from dbmanager  import DBManager
from datetime   import datetime
import sys
import pprint
import base64 as mask


class AuditManager(DBManager):



    def init_repo_schema(self):
        self.execute_ddl("create database {0} default character set 'utf8'".format(self.current_database),
                          on_fail_exit=True,
                          message="Creating  '{0}' database... ".format(self.current_database),
                          additional_fail_msg="Initialization failed during creating '{0}' database... ".format(self.current_database),
                          additional_ok_msg="OK")

        self.use_database()

        for name, ddl in schema_tables.iteritems():
            self.execute_ddl(ddl,
                             message="Creating table {0}: ".format(name),
                             additional_ok_msg="OK")


    def get_env_type(self, host):
        env = ''
        # try to identify ENV type
        if host:
            host_1st_letter = host[0].upper()
            if host_1st_letter == 'P':
                env = 'PROD'
            elif  host_1st_letter == 'S':
                env = 'STG'
            elif  host_1st_letter == 'Q':
                env = 'QA'
            elif  host_1st_letter == 'D':
                env = 'DEV'
        return env



    def add_aud_target(self, env='', user='', password='', host='localhost', port='3306', dbname='', description=''):
        
        if env == '':
            env = self.get_env_type(host)

        cmd = "insert into `audit_targets_list`(`envtype`,`user`,`password`,`host`,`port`,`dbname`,`description`) values('{0}','{1}','{2}','{3}','{4}','{5}','{6}')"
        cmd = cmd.format(env, user, mask.encodestring(password), host, port, dbname, description)
        self.execute_ddl(cmd)



    def delete_aud_target(self, target_id):
        cmd = 'delete from `audit_targets_list` where `id`={0}'.format(target_id)
        self.execute_ddl(cmd)



    def list_aud_targets(self):
        cmd = 'select * from `audit_targets_list`'
        self.execute_query(cmd)


    
    def get_conn_conf_by_id(self, target_id):
        cmd = 'select `envtype`, `user`,`password`,`host`,`port`,`dbname` as `database` from `audit_targets_list` where `id`={0}'.format(target_id)
        result = self.execute_query(cmd, True)
        
        if result:
            db_conn = dict(result[0])
            try:
                db_conn['password'] = mask.decodestring(db_conn['password'])
            except:
                db_conn['password'] = ''

            #remove  empty fields
            db_conn = dict((key, value) for key, value in db_conn.iteritems() if value)
            return db_conn
        else:
            return result


    def test_aud_target(self, target_id):
        db_conn = self.get_conn_conf_by_id(target_id)
        # make a connection to database
        if db_conn:
            if 'envtype' in db_conn.keys():
                del db_conn['envtype']
            target_db = DBManager(True, True, **db_conn)
            target_db.execute_query(sqls4mysql['dblist'])
            target_db.close()




    def audit_target(self, target_id, snapshot_id='',save_audit=False, envtype='', additional_info=''):
        def calculate_max_memory(**mem_param_rec):
            try:
                max_memory = mem_param_rec['key_buffer_size']  + \
                             mem_param_rec['query_cache_size'] + \
                             mem_param_rec['tmp_table_size']   + \
                             mem_param_rec['innodb_buffer_pool_size'] + \
                             mem_param_rec['innodb_additional_mem_pool_size'] + \
                             mem_param_rec['innodb_log_buffer_size'] + \
                            (mem_param_rec['max_connections'] * (mem_param_rec['sort_buffer_size'] + \
                                                  mem_param_rec['read_buffer_size'] + \
                                                  mem_param_rec['read_rnd_buffer_size'] + \
                                                  mem_param_rec['join_buffer_size'] + \
                                                  mem_param_rec['thread_stack'] + \
                                                  mem_param_rec['binlog_cache_size']))
                return str(max_memory)
            except:
                return '0'
        
        db_conn = self.get_conn_conf_by_id(target_id)
        audit_rec = {}
        if db_conn:
            # first time when we check 'envtype' is provided or not and trying to get it from target's record
            if 'envtype' in db_conn.keys():
                if not envtype:
                    envtype = str(list(db_conn['envtype'])[0])
                del db_conn['envtype']

            db_conn_4disply = db_conn.copy()
            # hide the password and then print
            if 'password' in db_conn_4disply.keys():
                db_conn_4disply['password'] = '******'
            print("\nAuditing ID={1}, connecting to [{0}]...".format(db_conn_4disply, target_id))

            try:
                target_db = DBManager(True, False, **db_conn)
            except Exception as err:
                print("For ID={0}, audit  failed ...".format(target_id))
                print(err)
                return
            
            additional_info += 'connected to: {0}'.format(db_conn_4disply['host']) if 'host' in db_conn_4disply.keys() else 'connected to: {0}'.format('localhost')
    
            audit_rec['snapshot_id'] = snapshot_id if snapshot_id else datetime.now().strftime('%S%M%H%d%m%Y%f')

            audit_rec['host'] = dict(target_db.execute_query(sqls4mysql['host'], True)[0])['host']
            audit_rec['osversion'] = dict(target_db.execute_query(sqls4mysql['osversion'], True)[0])['osversion']

            envtype = envtype.upper()
            audit_rec['envtype'] = self.get_env_type(audit_rec['host']) if not envtype or envtype not in ('PROD','STG','QA','DEV') else envtype

            audit_rec['dbversion'] = dict(target_db.execute_query(sqls4mysql['dbversion'], True)[0])['dbversion']


            # checking if INNODB is enabled
            innodb = str(target_db.get_global_variable('have_innodb')).upper()
            additional_info += ', Have_InnoDB is set to ({0})'.format(innodb)
                
            # calculating MAX memory
            memory_params = dict([(row[0][1],long(row[1][1])) for row in target_db.execute_query(sqls4mysql['memory_params'],True)])
            audit_rec['max_req_memory'] = calculate_max_memory(**memory_params)
          
            audit_rec['additional_info'] = additional_info
           
            for dblist in target_db.execute_query(sqls4mysql['dblist'], True):
                dbname = dict(dblist)['Database']
                audit_rec['dbname'] = dbname
                audit_rec['dbsize'] = dict(target_db.execute_query(sqls4mysql['dbsize'].format(dbname), True)[0])['dbsize']
                audit_rec['free_space'] = dict(target_db.execute_query(sqls4mysql['free_space'].format(dict(dblist)['Database']), True)[0])['free_space']
                 
                if save_audit:
                    cmd = sqls4mysql['insert_aud_rec'].format(audit_rec['snapshot_id'],
                                                              audit_rec['host'],
                                                              audit_rec['osversion'],
                                                              audit_rec['envtype'],
                                                              audit_rec['dbversion'],
                                                              audit_rec['dbname'],
                                                              audit_rec['dbsize'],
                                                              audit_rec['free_space'],
                                                              audit_rec['max_req_memory'],
                                                              audit_rec['additional_info'])
                    self.execute_dml(cmd, False, message='', additional_fail_msg='', additional_ok_msg='')
                else:
                    print(audit_rec)

            target_db.close()
            print('OK')
        else:
            print("Couldn't find record with id={0} ...".format(target_id))



if __name__ == "__main__":



    def print_usage():
        print("""Available arguments

                       --init : Initialize database schema
                       --drop : Drop database schema

                       --list : List targets
                      
                       --add  : Add target database

                                -env: set of ('PROD','STG','QA','DEV','')
                                -user:
                                -password:
                                -host:
                                -port:
                                -database:
                                -description:
 
                                Usage:
                                      -argument=value

                       --del  : remove target database

                       --test : test connection to target database

                       --audit: Audit target (takes target's id number)

                                -env (optional)
                                -additional_info (optional)

                                Usage:
                                      -argument=value
            
                      --audit-all : audit all existing targets

                 """)



    def parse_arguments(skip_arguments, clean_arguments, wrong_arg_error,  *arguments, **arg_template):
        arguments = list(arguments[i] for i in range(skip_arguments,len(arguments)))
        if arguments:
            for i in range(len(arguments)):
                arg = arguments[i][0: arguments[i].find('=')]
                if arg in arg_template.keys():
                    arg_template[arg] = arguments[i].replace(arg + '=', '')
                elif wrong_arg_error:
                   print("\nError: unknow argument '{}' ...\n".format(arg))
                   exit(1)
        
        if clean_arguments:
            # clean template and return 
            return dict({(key,value) for key,value in arg_template.iteritems() if value})
        else:
            return arg_template
            



    args = sys.argv
    if len(args) > 1:
        if args[1] == "--init":
            schema_create = AuditManager(use_db=False)
            schema_create.init_repo_schema()
            schema_create.close()

        elif args[1] == "--drop":
            print("\nWHY WOULD YOU???\n\nif you really need to drop repository, go into the database and drop it by YOURSELF!!!! \n")

        elif args[1] == "--list":
            tlist = AuditManager()            
            tlist.list_aud_targets()
            tlist.close()

        elif args[1] == "--add":
            a = AuditManager()
            target_template = {'-env': "",'-user': "",'-password': "",'-host': "localhost",'-port': "3306",'-database': "",'-description': ""}

            target_template = parse_arguments(2, False, True,  *args, **target_template)

            a.add_aud_target(target_template['-env'],
                             target_template['-user'],
                             target_template['-password'],
                             target_template['-host'],
                             target_template['-port'],
                             target_template['-database'],
                             target_template['-description'])
            a.close()

        elif args[1] == "--del":
            if not len(args) == 3:
                print("\nOne numerical Agument is required for '--del'...\n")
            elif not args[2].isdigit():
                print("\nNumerical Agument is required for '--del' and NOT like '{}' or something...\n".format(args[2]))
            else:
                d = AuditManager()
                d.delete_aud_target(args[2])            
                d.close()

        elif args[1] == "--test":
            if not len(args) == 3:
                print("\nPlease provide target id number '--test'...\n")
            elif not args[2].isdigit():
                print("\nNumerical Agument is required for '--test' and NOT like '{}' or something...\n".format(args[2]))
            else:
                t = AuditManager()
                t.test_aud_target(args[2])            
                t.close()

        elif args[1] == "--audit":
            if not len(args) >= 3:
                print("\nError: Incorrect arguments ...\n")
                print_usage()
            elif not args[2].isdigit():
                print("\nNumerical Agument is required for '--audit' and NOT like '{}' or something...\n".format(args[2]))
            else:
                a = AuditManager()
                arg_templ = {'-env':'', '-additional_info':''}
                arg_templ = parse_arguments(3, False, True, *args, **arg_templ)
                a.audit_target(args[2],  '', True, arg_templ['-env'], arg_templ['-additional_info'])
                a.close()

        elif args[1] == "--audit-all":
            if not len(args) == 2 :
                print("\nError: Incorrect arguments ...\n")
                print_usage()
            else:
                a = AuditManager()
                snapshotid = datetime.now().strftime('%S%M%H%d%m%Y%f')
                for ids in a.execute_query(sqls4mysql['get_targets_id_list'], True):
                    a.audit_target(dict(ids)['id'], str(snapshotid),  True, '', '')
                a.close()

        else:
             print_usage()
    else:
         print_usage()

        
