import re


class JsonVerify:
    increase_key = []
    lost_key = []
    correct_key = []
    error_set = set()
    error = {}

    def __init__(
            self,
            verify_json=None,
            check_func=None,
            check_value_only=False
    ):
        self.check_func = check_func
        self.check_value_only = check_value_only
        if verify_json:
            self.expect_dict = self.contract_json(verify_json, expect_dict={})

    def contract_json(self, raw_data, path="", expect_dict=None):
        if isinstance(raw_data, dict):

            for key, value in raw_data.items():

                if key.startswith('_') and key.endswith('_'):
                    path = path + '.' + key.strip("_")
                    expect_dict[path.strip(".")] = value

                else:
                    path = path + '.' + key
                    self.add_rules(expect_dict, path, value)
                    self.contract_json(value, path, expect_dict)

                path = path.rsplit('.', 1)[0]

        elif isinstance(raw_data, list):

            for index, value in enumerate(raw_data):
                path = path + '.' + "<int>"
                self.add_rules(expect_dict, path, value)
                self.contract_json(value, path, expect_dict)
                path = path.rsplit('.', 1)[0]

        return expect_dict

    @staticmethod
    def add_rules(expect_dict, path, value):

        if path.strip('.') in expect_dict:
            expect_dict[path.strip('.')]["type"].append(type(value).__name__)

            if value not in expect_dict[path.strip('.')]["value_rules"]:
                expect_dict[path.strip('.')]["value_rules"].append(value)

        else:
            expect_dict[path.strip('.')] = {"type": [type(value).__name__], "value_rules": [value]}

    def verify(self, check_json, path="", real_path=""):

        if isinstance(check_json, dict):

            for key, value in check_json.items():
                path = path + '.' + key
                real_path = real_path + '.' + key
                self.check_rules(value, path, real_path)
                self.verify(value, path, real_path)
                path = path.rsplit('.', 1)[0]
                real_path = real_path.rsplit('.', 1)[0]

        elif isinstance(check_json, list):

            for index, value in enumerate(check_json):
                path = path + '.' + "<int>"
                real_path = f"{real_path}.{index}"
                self.check_rules(value, path, real_path)
                self.verify(value, path, real_path)
                path = path.rsplit('.', 1)[0]
                real_path = real_path.rsplit('.', 1)[0]

    def check_rules(self, check, path, real_path):
        check_rules = self.expect_dict.get(path.strip('.'))
        if isinstance(check_rules, dict):

            if self.check_value_only:
                rules_value = check_rules.get("value_rules")
                msg = {"rulesValue": rules_value, "checkValue": check, "detail": "期望值与结果值不同"}
                self.judge(check in rules_value, path, real_path, msg)

            else:
                if check_rules.get("value"):
                    rules_value = check_rules.get("value")
                    msg = {"rulesValue": rules_value, "checkValue": check, "detail": "期望值与结果值不同"}
                    self.judge(check in rules_value, path, real_path, msg)

                elif check_rules.get("func_rules"):
                    func_name = check_rules.get("func_rules")
                    rules_func = getattr(self.check_func, func_name)
                    msg = {"rulesFunc": func_name, "checkValue": check, "detail": "值不符合函数校验规则"}
                    self.judge(rules_func(check), path, real_path, msg)

                elif check_rules.get("regular_rules"):
                    rules_value = check_rules.get("regular_rules")
                    msg = {"rulesValue": rules_value, "checkValue": check, "detail": "正则匹配错误"}
                    self.judge(re.findall(rules_value, check), path, real_path, msg)

                else:
                    rules_value = check_rules.get("type")
                    msg = {"rulesType": rules_value, "checkValue": check, "detail": "数据类型错误"}
                    self.judge(type(check).__name__ in check_rules.get("type"), path, real_path, msg)

        elif check_rules is None:
            self.increase_key.append(real_path.strip('.'))

    def judge(self, condition, path, real_path, msg):
        real_path = real_path.strip('.')
        path = path.strip('.')

        if condition:
            self.correct_key.append(path)

        else:
            self.error[real_path] = msg
            self.error_set.add(path)

    @property
    def info(self):
        expect_key = set(self.expect_dict.keys())
        correct_key = set(self.correct_key) - self.error_set
        result = {
            "loseKey": list(expect_key-set(self.correct_key)-set(self.error_set)),
            "increaseKey": self.increase_key,
            "keyError": self.error,
            "patchRate": "%.2f" % (len(correct_key) / (len(expect_key) or 1) * 100) + "%"
        }
        return result

    def diff_json(self, verify_json, check_json):
        self.expect_dict = self.contract_json(verify_json, expect_dict={})
        self.verify(check_json)
