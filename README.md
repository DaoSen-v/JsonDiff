### json_verify

说明： 主要用于json数据diff，输出匹配的字段信息、字段匹配准确率

安装方式： 
```shell script
pip install json_verify
```

##### 1、 生成契约校验实例

```python
from json_verify import JsonVerify

demo_json = {
    "msg": "一段文字信息",
    "phone": 13746067836,
    "name": [
        {"age": 12}, 
        {"phone": 213213, "age": 18}
    ]
}
check_json = {
    "msg": None,
    "address": "上海",
    "name": [
        {"age": 12},
        {"phone": 213213, "age": 18},
    ]
}
instance = JsonVerify(demo_json)
instance.verify(check_json)
print(instance.info)
```
\>>>
```json
{'loseKey': ['phone'], 'increaseKey': ['address', 'name.0.language'], 'keyError': {'msg': {'type_rules': ['str'], 'check_value': None, 'detail': '数据类型错误'}}, 'patchRate': '66.67%'}

```

备注：校验规则{key：value}

value:为列表类型时默认校验列表元素，每个元素与锲约列表匹配程度，与元素在列表中顺序无关、与元素长短无关

默认契约校验为值数据类型作为校验规则

- loseKey： 被检验json数据缺少的key
- increaseKey：被检验json增加的key
- keyError：被检验json的key对应value不符合锲约要求
- patchRate：所有key匹配的正确率（increaseKey不参与运算）

##### 2、自定义契约

自定义契约字段需要加上 下划线 前后缀

```json
如锲约json：
{"name": "百里清"}

自定义锲约时：
{"_name_": {"rules_value": ["百里清"]}}
```





###### 2.1 自定义值匹配契约   rules_value

```python
from json_verify import JsonVerify

demo_json = {
    "_msg_": {"rules_value": ["不匹配的文字信息"]},
    "name": [
        {"age": 12}, 
        {"phone": 213213, "age": 18}
    ]
}
check_json = {
    "msg": "错误信息",
    "name": [
        {"age": 12},
        {"phone": 213213, "age": 18},
    ]
}
instance = JsonVerify(demo_json)
instance.verify(check_json)
print(instance.info)
```
\>>>
```json
{'loseKey': [], 'increaseKey': [], 'keyError': {'msg': {'rules_value': ['不匹配的文字信息'], 'check_value': '错误信息', 'detail': '期望值与结果值不同'}}, 'patchRate': '80.00%'}
```



###### 2.2 自定义正则匹配契约  regular_rules

```python
from json_verify import JsonVerify

demo_json = {
    "_msg_": {"regular_rules": "^\d+$"},
    "name": [
        {"age": 12}, 
        {"phone": 213213, "age": 18}
    ]
}
check_json = {
    "msg": "错误信息",
    "name": [
        {"age": 12},
        {"phone": 213213, "age": 18},
    ]
}
instance = JsonVerify(demo_json)
instance.verify(check_json)
print(instance.info)
```
\>>> 
```json
{'loseKey': [], 'increaseKey': [], 'keyError': {'msg': {'regular_rules': '^\\d+$', 'check_value': '错误信息', 'detail': '正则匹配错误'}}, 'patchRate': '80.00%'}
```



###### 2.3 自定义函数契约 func_rules

```python
from json_verify import JsonVerify

demo_json = {
    "_msg_": {"func_rules": "check_msg"}, # func_rules: 函数要存在于check_func对象里
    "name": [
        {"_age_": {"func_rules": "check_age"}}, 
        {"phone": 213213, "_age_": {"func_rules": "check_age"}}
    ]
}
check_json = {
    "msg": "错误信息",
    "name": [
        {"age": 12},
        {"phone": 213213, "age": 18},
    ]
}


class CheckFunction:

    def check_msg(self, msg):
        if msg:
            return True

    def check_age(self, age):

        return True if age>12 else False
        
instance = JsonVerify(demo_json, check_func=CheckFunction())
# check_func: 校验函数存放的包、模块、类实例 可以使用getattr(check_func, func_name) 获取的类型
instance.verify(check_json)

print(instance.info)
```

\>>> 
```json
{'loseKey': [], 'increaseKey': [], 'keyError': {'name.0.age': {'func_rules': 'check_age', 'check_value': 12, 'detail': '值不符合函数校验规则'}}, 'patchRate': '80.00%'}
```
##### 3、 做精确值匹配 check_value_only

注意： 启用此方法时任何自定义契约校验都会失效
```python
from json_verify import JsonVerify

demo_json = {
    "msg": "123", # func_rules: 函数要存在于check_func对象里
    "name": [
        {"age": 18}, 
        {"phone": 213213, "age": 18}
    ]
}
check_json = {
    "msg": "错误信息",
    "name": [
        {"age": 12},
        {"phone": 213213, "age": 18},
    ]
}


class CheckFunction:

    def check_msg(self, msg):
        if msg:
            return True

    def check_age(self, age):
        return True if age>12 else False
        
instance = JsonVerify(demo_json, check_func=CheckFunction(), check_value_only=True)
# check_func: 校验函数存放的包、模块、类实例 可以使用getattr(check_func, func_name) 获取的类型
instance.verify(check_json)

print(instance.info)
```
\>>> 
```json
{'loseKey': [], 'increaseKey': [], 'keyError': {'name': {'rules_value': [[{'age': 18}, {'phone': 213213, 'age': 18}]], 'check_value': [{'age': 12}, {'phone': 213213, 'age': 18}], 'detail': '期望值与结果值不同'}, 'name.0': {'rules_value': [{'age': 18}, {'phone': 213213, 'age': 18}], 'check_value': {'age': 12}, 'detail': '期望值与结果值不同'}, 'name.0.age': {'rules_value': [18], 'check_value': 12, 'detail': '期望值与结果值不同'}}, 'patchRate': '40.00%'}
```

