
sqls4mysql = {}

sqls4mysql['global_variable'] = "select @@{}"

sqls4mysql['dblist'] = """show databases"""


sqls4mysql['dbversion'] = """select concat(@@VERSION_COMMENT,' ',@@VERSION) as dbversion"""

sqls4mysql['osversion'] = """select concat(@@VERSION_COMPILE_OS,' ',@@VERSION_COMPILE_MACHINE) as osversion"""

sqls4mysql['host'] = """select @@HOSTNAME as host"""


sqls4mysql['dbsize'] = """select ifnull(sum(data_length + index_length),0) as dbsize from information_schema.tables where table_schema='{0}'"""


sqls4mysql['free_space'] = """ select ifnull(sum(data_free),0) as free_space from information_schema.tables where table_schema='{0}'"""


sqls4mysql['get_targets_id_list'] = """select `id` from audit_targets_list"""


sqls4mysql['memory_params'] = """show global variables
                                    where
                                  variable_name in ('key_buffer_size',
                                                    'query_cache_size',
                                                    'tmp_table_size',
                                                    'innodb_buffer_pool_size',
                                                    'innodb_additional_mem_pool_size',
                                                    'innodb_log_buffer_size',
                                                    'max_connections',
                                                    'sort_buffer_size',
                                                    'read_buffer_size',
                                                    'read_rnd_buffer_size',
                                                    'join_buffer_size',
                                                    'thread_stack',
                                                    'binlog_cache_size')"""


sqls4mysql['max_req_memory'] = """select   @@key_buffer_size + 
				           @@query_cache_size +
				           @@tmp_table_size +
                                           @@innodb_buffer_pool_size +
				           @@innodb_additional_mem_pool_size +
				           @@innodb_log_buffer_size +
				           (@@max_connections * (@@sort_buffer_size +
							         @@read_buffer_size +
								 @@read_rnd_buffer_size +
								 @@join_buffer_size +
							         @@thread_stack +
							         @@binlog_cache_size)) as max_req_memory"""





sqls4mysql['insert_aud_rec'] = """ insert 
                                        into audit_storage(`snapshot_id`,`host`,`osversion`,`envtype`,`dbversion`,`dbname`,`dbsize`,`free_space`,`max_req_memory`,`gathering_date`,`additional_info`)
                                   values("{0}","{1}","{2}","{3}","{4}","{5}",{6},{7},{8}, now(), "{9}")"""




schema_tables = {}

schema_tables['audit_targets_list'] = ("create table `audit_targets_list`("
                                     "`id` int auto_increment,"
                                     "`envtype`  set('PROD','STG','QA','DEV'),"
                                     "`user`     varchar(60),"
                                     "`password` varchar(60),"
                                     "`host`     varchar(120),"
                                     "`port`     varchar(10) default '3306',"
                                     "`dbname`   varchar(60),"
                                     "`description` text,"
                                     " constraint `aud_db_connections_pk` primary key (`id`)"
                                     ") ENGINE=InnoDB")

schema_tables['audit_storage'] = ("create table `audit_storage`("
                                "`snapshot_id` varchar(22)," 
                                "`host`       varchar(120),"
                                "`osversion`  varchar(120),"
                                "`envtype`    set('PROD','STG','QA','DEV'),"
                                "`dbversion`  varchar(60),"
                                "`dbname`     varchar(60),"
                                "`dbsize`     bigint(21) unsigned,"
                                "`free_space` bigint(21) unsigned,"
                                "`max_req_memory` bigint(21) unsigned,"
                                "`gathering_date` datetime,"
                                "`additional_info` text,"
                                " index `aud_strg_hde_idx` (`host`,`dbname`,`envtype`),"
                                " index `aud_strg_snpid_idx` (`snapshot_id`),"
                                " index `aud_strg_gd_idx` (`gathering_date`)"
                                ") ENGINE=InnoDB")


