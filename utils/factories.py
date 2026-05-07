import factory
from faker import Faker

# 实例化 Faker，指定生成中文/英文的假数据
fake = Faker(["zh_CN", "en_US"])


class UserPayloadFactory(factory.DictFactory):
    """
    User 接口请求体造数工厂
    继承 DictFactory，意味着它产出的是一个字典（直接拿去传给 API）
    """
    # 每次调用，自动生成一个逼真的人名
    name = factory.LazyFunction(lambda: fake.name())

    # 每次调用，自动生成一个绝不重复的企业邮箱
    email = factory.LazyFunction(lambda: fake.unique.company_email())

    # 默认角色是 member
    role = "member"

    class Params:
        """定义一些可以快速切换的特性（Traits）"""
        is_admin = factory.Trait(
            role="admin"
        )
        is_guest = factory.Trait(
            role="guest"
        )

class TodoPayloadFactory(factory.DictFactory):
    """Todo 接口请求体造数工厂"""
    # 自动生成一句简短的假句子作为标题
    title = factory.LazyFunction(lambda: fake.sentence(nb_words=3)[:-1])

    # user_id 默认给个占位符，实际测试时我们会动态覆盖它
    user_id = 1
    completed = False