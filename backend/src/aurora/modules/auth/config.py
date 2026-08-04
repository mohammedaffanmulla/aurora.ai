from aurora.core.config import settings

# JWT
JWT_SECRET_KEY = settings.auth_jwt_secret_key
JWT_ALGORITHM = settings.auth_jwt_algorithm

ACCESS_TOKEN_EXPIRE_MINUTES = (
    settings.auth_access_token_expire_minutes
)

REFRESH_TOKEN_EXPIRE_DAYS = (
    settings.auth_refresh_token_expire_days
)

# Password
BCRYPT_ROUNDS = settings.auth_bcrypt_rounds

# Email
SMTP_HOST = settings.auth_smtp_host
SMTP_PORT = settings.auth_smtp_port
SMTP_USER = settings.auth_smtp_user
SMTP_PASSWORD = settings.auth_smtp_password
SMTP_FROM_ADDRESS = settings.auth_smtp_from_address
SMTP_USE_TLS = settings.auth_smtp_use_tls

FRONTEND_BASE_URL = settings.auth_frontend_base_url

MAX_ACTIVE_SESSIONS_PER_USER = (
    settings.auth_max_active_sessions_per_user
)

EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS = (
    settings.auth_email_verification_token_expire_hours
)

PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = (
    settings.auth_password_reset_token_expire_minutes
)