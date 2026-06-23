from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_provider: str = "mock"

    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-v4-pro"
    deepseek_api_url: str = "https://api.deepseek.com/chat/completions"

    spark_app_id: str = ""
    spark_api_key: str = ""
    spark_api_secret: str = ""
    spark_model: str = "4.0Ultra"
    spark_api_url: str = "https://spark-api-open.xf-yun.com/v1/chat/completions"

    database_url: str = "sqlite:///./edupath.db"
    jwt_secret_key: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

