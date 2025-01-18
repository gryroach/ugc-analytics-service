from logging import config as logging_config

from dotenv import find_dotenv, load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)
DOTENV_PATH = find_dotenv(".env")
load_dotenv(DOTENV_PATH)


class AppSettings(BaseSettings):
    project_name: str = Field(default="Event API")
    api_production: bool = Field(default=True)

    # Kafka
    # https://kafka.apache.org/documentation.html#producerconfigs
    kafka_bootstrap_server: str = Field(default="kafka-0:9092")
    kafka_topic_name: str = Field(default="user_events")
    kafka_batch_sleep: int = Field(default=1, description="Задержка при отправке сообщений пакетами")
    kafka_batch_size: int = Field(default=100, description="Количество сообщений, отправляемых в пакете")
    kafka_retry_backoff_ms: int = Field(default=100)

    # Настройки Redis
    redis_host: str = Field(default="redis")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=1)
    test_redis_host: str = Field(default="redis")
    test_redis_port: int = Field(default=6379)
    test_redis_db: int = Field(default=0)

    # Работа с токенами
    jwt_algorithm: str = Field(default="RS256")
    jwt_public_key_path: str = Field(default="/app/keys/example_public_key.pem")

    # Другие настройки
    test_mode: bool = Field(default=False)

    model_config = SettingsConfigDict(
        env_file=DOTENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="ugc_",
    )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def jwt_public_key(self) -> str:
        try:
            with open(self.jwt_public_key_path, "r") as key_file:
                return key_file.read()
        except FileNotFoundError:
            raise ValueError(
                f"Public key file not found at: {self.jwt_public_key_path}"
            )
        except Exception as e:
            raise ValueError(f"Error reading public key: {str(e)}")


settings = AppSettings()
