import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# 定位根目录
_ROOT = Path(__file__).parent
# 动态计算该读哪个 .env 文件
_ENV = os.getenv("ENV", "test")
_ENV_FILE = _ROOT / f".env.{_ENV}"


class Settings(BaseSettings):
    # 明确告诉 IDE，base_url 必须是个字符串！
    # 如果 .env 里没写 base_url，Pydantic 在启动时就会直接报错拦截，而不是等测试跑了一半才死掉。
    base_url: str
    env: str = "test"  # 给定默认值
    db_url: str

    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = str(_ROOT / "logs" / "test.log")

    # Pydantic 2.x 的核心配置，指定它去读哪个文件
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore"  # 如果 .env 里有类中未定义的变量，直接忽略不报错
    )

# 实例化一个全局单例供整个框架调用
settings = Settings()