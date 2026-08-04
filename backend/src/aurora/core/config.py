from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ==========================================
    # Application
    # ==========================================
    app_name: str = "Aurora"
    app_version: str = "0.1.0"
    debug: bool = True

    # ==========================================
    # Core
    # ==========================================
    secret_key: str
    database_url: str

    # ==========================================
    # Auth
    # ==========================================
    auth_jwt_secret_key: str
    auth_jwt_algorithm: str = "HS256"

    auth_access_token_expire_minutes: int = 15
    auth_refresh_token_expire_days: int = 30

    auth_password_reset_token_expire_minutes: int = 30
    auth_email_verification_token_expire_hours: int = 24

    auth_bcrypt_rounds: int = 12
    auth_max_active_sessions_per_user: int = 10

    auth_frontend_base_url: str

    # ==========================================
    # SMTP
    # ==========================================
    auth_smtp_host: str
    auth_smtp_port: int
    auth_smtp_user: str = ""
    auth_smtp_password: str = ""
    auth_smtp_from_address: str
    auth_smtp_use_tls: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()