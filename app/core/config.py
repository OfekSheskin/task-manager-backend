from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App configuration, loaded from the .env file (or from real environment
    variables, which is how a deployment supplies them)."""

    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    # The origins a browser is allowed to call the API from, comma-separated.
    # The default is the local Vite dev server; a deployment sets its own site.
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def sqlalchemy_url(self) -> str:
        """The database URL in the form SQLAlchemy accepts.

        Hosted Postgres providers hand out URLs on the `postgres://` scheme,
        which SQLAlchemy 2 dropped; it only recognises `postgresql://`.
        """
        prefix = "postgres://"
        if self.database_url.startswith(prefix):
            return "postgresql://" + self.database_url[len(prefix):]
        return self.database_url


settings = Settings()
