import os
import yaml
import logging
import pymysql
import time
from common import common_config

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class MysqlEnv(object):

    def __init__(self):
        self.mysql_ip = None
        self.mysql_port = None
        self.mysql_user = None
        self.mysql_password = None
        self.db = None
        pass

    def connect_to_mysql_env(self):
        self.mysql_ip = "10.1.19.19"
        self.mysql_port = 3306
        self.mysql_user = "root"
        self.mysql_password = "deepflow"

        db = pymysql.connect(
            host=self.mysql_ip, port=self.mysql_port, user='root',
            passwd=self.mysql_password, db='autotest_environment',
            charset='utf8'
        )
        self.db = db

    def exec_sql(self, sql=""):
        if sql == "":
            assert False

        if self.db is None:
            self.connect_to_mysql_env()
        db = self.db

        cursor = db.cursor()
        result = None
        try:
            # Execute sql statement
            cursor.execute(sql)
            # Returns all information from a database query
            result = cursor.fetchall()
            # save changes made to the firm to the database.
            db.commit()
        except Exception as err:
            #Rollback on Error
            db.rollback()
            logging.error("exec_sql_cmd:exec cmd failed, err:{}".format(err))
        cursor.close()
        return result

    def change_database(self, databases=None):
        if databases is None:
            assert False

        sql = "use {};".format(databases)
        self.exec_sql(sql=sql)

    def exec_sql_in_database_autotest_environment(self, sql=""):
        if sql == "":
            assert False
        logging.info(
            "exec_sql_in_database_autotest_environment::sql ==> {}"
            .format(sql)
        )
        self.change_database(databases="autotest_environment")
        return self.exec_sql(sql=sql)

    def exec_sql_in_transaction(self, database="", sql_list=[]):
        if database == "":
            database = "autotest_environment"
        if sql_list == []:
            assert False

        self.exec_sql()


class Environment(object):

    def __init__(self):
        self.case_id = "test_case_001"
        self.case_name = "test_case_001"
        self.user_type = "exclusive"

        self.mysql = MysqlEnv()
        self.users_table_name = "case_users"
        self.environment_table_name = "deepflow"
        pass

    def setter(self, **kwargs):
        for key, value in kwargs.items():
            if key == "case_id":
                self.case_id = value
            elif key == "case_name":
                self.case_name = value
            elif key == "user_type":
                self.user_type = value

    # 创建数据表 deepflow
    # create table deepflow(
    # 	id INT NOT NULL AUTO_INCREMENT,
    # 	df_id VARCHAR(100) NOT NULL,
    # 	df_name VARCHAR(100) NOT NULL,
    #     df_ip VARCHAR(100) NOT NULL,
    #     df_status VARCHAR(100) NOT NULL,
    # 	PRIMARY KEY (id)
    # 	)
    # 	ENGINE=InnoDB DEFAULT CHARSET=utf8;

    def write_one_environment_info(
        self, df_id="", df_name="", df_ip="", df_status=""
    ):
        if df_id == "" or df_name == "" or df_ip == "" or df_status == "":
            logging.error(
                "write_one_environment_inifo::4 variables need to be input at the same time"
            )
            assert False

        table_name = "deepflow"
        sql_list = [
            "INSERT INTO {} ".format(table_name),
            "(df_id, df_name, df_ip, df_status) ", "VALUES ",
            "('{}', '{}', '{}', '{}');".format(
                df_id, df_name, df_ip, df_status
            )
        ]
        sql = "".join(sql_list)
        logging.info("write_one_environment_info::sql ==> {}".format(sql))
        self.mysql.exec_sql_in_database_autotest_environment(sql=sql)
        pass

    def get_all_environment_info(self):
        table_name = "deepflow"
        sql = "select * from {}".format(table_name)
        environment_tuple = self.mysql.exec_sql_in_database_autotest_environment(
            sql=sql
        )
        environment_list = list(environment_tuple)
        environment_dict = {"deepflow": []}

        for item in environment_list:
            one_environment_dict = {}
            id, df_id, df_name, df_ip, df_status = item
            one_environment_dict["df_id"] = df_id
            one_environment_dict["df_name"] = df_name
            one_environment_dict["df_ip"] = df_ip
            one_environment_dict["df_status"] = df_status
            environment_dict["deepflow"].append(one_environment_dict)
        return environment_dict

    # 创建数据表 case_users
    # create table case_users(
    # 	id INT NOT NULL AUTO_INCREMENT,
    # 	case_id VARCHAR(100) NOT NULL,
    # 	case_name VARCHAR(100) NOT NULL,
    #   df_id VARCHAR(100) NOT NULL,
    #   start_use_time VARCHAR(100) NOT NULL,
    #   use_type VARCHAR(100) NOT NULL,
    # 	PRIMARY KEY (id)
    # 	)
    # 	ENGINE=InnoDB DEFAULT CHARSET=utf8;

    def write_one_user_info(
        self, case_id="", case_name="", df_id="", start_use_time="",
        use_type=""
    ):
        if case_id == "" or case_name == "" or df_id == "" or use_type == "":
            logging.error(
                "write_one_user_info::5 variables need to be input at the same time"
            )
            assert False

        if start_use_time == "":
            time_now = int(time.time())
            time_array = time.localtime(time_now)
            time_strift = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
            start_use_time = time_strift

        table_name = self.users_table_name
        sql_list = [
            "INSERT INTO {} ".format(table_name),
            "(case_id, case_name, df_id, start_use_time, use_type) ",
            "VALUES ", "('{}', '{}', '{}', '{}', '{}');".format(
                case_id, case_name, df_id, start_use_time, use_type
            )
        ]
        sql = "".join(sql_list)
        logging.info("write_one_user_info::sql ==> {}".format(sql))
        return self.mysql.exec_sql_in_database_autotest_environment(sql=sql)

    def get_all_user_info(self):
        table_name = self.users_table_name
        sql = "select * from {}".format(table_name)
        user_tuple = self.mysql.exec_sql_in_database_autotest_environment(
            sql=sql
        )
        user_list = list(user_tuple)
        user_dict = {"users": []}

        for item in user_list:
            one_user_dict = {}
            id, case_id, case_name, df_id, start_use_time, use_type = item
            one_user_dict["case_id"] = case_id
            one_user_dict["case_name"] = case_name
            one_user_dict["df_id"] = df_id
            one_user_dict["start_use_time"] = start_use_time
            one_user_dict["use_type"] = use_type
            user_dict["users"].append(one_user_dict)
        return user_dict

    def get_current_user_info(self):
        table_name = self.users_table_name
        sql = "select * from {} where case_id = '{}'".format(
            table_name, self.case_id
        )
        user_tuple = self.mysql.exec_sql_in_database_autotest_environment(
            sql=sql
        )
        user_info = user_tuple[0]
        user_dict = {}
        id, case_id, case_name, df_id, start_use_time, use_type = user_info
        user_dict["case_id"] = case_id
        user_dict["case_name"] = case_name
        user_dict["df_id"] = df_id
        user_dict["start_use_time"] = start_use_time
        user_dict["use_type"] = use_type
        logging.info(
            "get_current_user_info::user_dict ==> {}".format(user_dict)
        )
        return user_dict

    def delete_one_user_info(self, case_id=""):
        if case_id == "":
            case_id = self.case_id

        table_name = self.users_table_name
        sql = "delete from {} where case_id = '{}'".format(table_name, case_id)
        self.mysql.exec_sql_in_database_autotest_environment(sql=sql)

    def renewal_environment(self):
        "Continue to lease the test environment, that is, update the time when the environment starts to be used"
        res = self.get_current_user_info()
        user = res["users"][0]
        case_id = user["case_id"]
        case_name = user["case_name"]
        df_id = user["df_id"]
        use_type = user["use_type"]

        self.delete_one_user_info(case_id=case_id)
        self.write_one_user_info(
            case_id=case_id, case_name=case_name, df_id=df_id,
            use_type=use_type
        )
        pass

    def _apply_environment_for_exclusive(self):

        class ApplyError(Exception):

            def __init__(self, value=""):
                if value == "":
                    self.value = "当前无满足要求的环境"
                else:
                    self.value = value

            def __str__(self):
                return repr(self.value)

        environ_table = "deepflow"
        sql = "select df_id from {} where df_status = 'free';".format(
            environ_table
        )

        try:
            sql_res = self.mysql.exec_sql_in_database_autotest_environment(
                sql=sql
            )
            if sql_res == ():
                print("apply_environment::sql_res ==> {}".format(sql_res))
                print("暂时没有申请到环境")
                raise ApplyError(
                )  # Throws ApplyError exception if the input is not a number
        except ApplyError as e:
            logging.error(e.value)
            return False

        df_id = sql_res[0][0]

        sql = "update deepflow set df_status = 'exclusive' where df_id = '{}' and df_status = 'free';".format(
            df_id
        )
        update_res = self.mysql.exec_sql_in_database_autotest_environment(
            sql=sql
        )
        logging.info("apply_environment::update_res ==> {}".format(update_res))
        sql_res = self.write_one_user_info(
            case_id=self.case_id, case_name=self.case_name, df_id=df_id,
            use_type=self.user_type
        )
        logging.info(
            "_apply_environment_for_exclusive::sql_res ==> {}".format(sql_res)
        )
        # TODO 是否成功写入信息判断

        sql = "select * from case_users"
        res = self.mysql.exec_sql_in_database_autotest_environment(sql=sql)
        logging.info("apply_environment::res ==> {}".format(res))
        return True

    def apply_environment(self):
        environ_table = "deepflow"
        if self.user_type == "exclusive":
            applied_flag = False
            for _ in range(120):
                apply_status = self._apply_environment_for_exclusive()
                if apply_status:
                    applied_flag = True
                    break
                time.sleep(1)
            if applied_flag:
                logging.info("apply_environment::Environment has been applied")
            else:
                logging.info(
                    "apply_environment::Application environment failed"
                )

        elif self.user_type == "share":
            # TODO 这里申请到的环境，有可能是空的，需要做处理
            update_flag = False
            sql = "select df_id from {} where df_status = 'share';".format(
                environ_table
            )
            df_id = self.mysql.exec_sql_in_database_autotest_environment(
                sql=sql
            )
            logging.info(
                "apply_environment_for_user::df_id ==> {}".format(df_id)
            )
            if df_id != None:
                update_flag = True
            else:
                sql = "select df_id from {} where df_status = 'share';"
                df_id = self.mysql.exec_sql_in_database_autotest_environment(
                    sql=sql
                )
                logging.info(
                    "apply_environment_for_user::df_id ==> {}".format(df_id)
                )

            if update_flag:
                sql = "update deepflow set df_status = 'exclusive' where df_id = '{}' and df_status = 'free';".format(
                    df_id
                )
                update_res = self.mysql.exec_sql_in_database_autotest_environment(
                    sql=sql
                )
                logging.info(
                    "apply_environment_for_user:: ==> {}".format(update_res)
                )
        else:
            pass

    def update_environment_to_free(self, df_id=""):
        if df_id == "":
            assert False
            # TODO 这里从类变量中去获取

        table_name = self.environment_table_name
        sql = "update {} set df_status = 'free' where df_id = '{}';".format(
            table_name, df_id
        )
        self.mysql.exec_sql_in_database_autotest_environment(sql=sql)
        pass

    def update_environment_to_share(self):
        pass

    def release_environment(self):
        user_dict = self.get_current_user_info()
        print("release_environment::user_dict ==> {}".format(user_dict))
        if user_dict["use_type"] == "exclusive":
            df_id = user_dict["df_id"]
            self.update_environment_to_free(df_id=df_id)
            self.delete_one_user_info()
            pass
        elif user_dict["user_type"] == "share":
            pass
        else:
            raise KeyError

    def refresh_expired_users(self):
        pass

    def update_common_df_ip(self, df_ip=""):
        common_config.df_ce_mgt_ip = df_ip
        pass

    def regular_update_info_to_resource(self):
        pass


env = Environment()
# environ.write_one_environment_info(df_id="deepflow_002", df_name="deepflow_002", df_ip="2.2.2.2", df_status="share")
# environ.write_one_user_info(case_id="test_case_001", case_name="test_case_001", df_id="deepflow_002", use_type="share")

env.setter(
    case_id="test_case_001", case_name="test_case_001", user_type="exclusive"
)
env.apply_environment()
env.release_environment()
# environ.renewal_environment()
# env.apply_environment()
# env.get_current_user_info()

#########
#转换成时间数组
# timeArray = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
# #转换成时间戳
# timestamp = time.mktime(timeArray)

# #转换成时间戳
# timestamp = int(time.mktime(time_array))
# print("timestamp", timestamp)

# environ = Environment()
# environ.get_resource_from_yaml()
# environ.write_resource_to_yaml()
#
# environ.user_type = "share"
# res = environ.apply_environment()
# print(res)
#
# environ.user_type = "exclusive"
# res = environ.apply_environment()
# print(res)
#
