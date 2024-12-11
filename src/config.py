from dataclasses import dataclass


@dataclass
class Settings:
    db_name: str = "db.sqlite3"
    db_echo: bool = False
    bot_token: str = "7861877518:AAHH_Lwp3R_Qo4dylxR13foQFrjDWR9MMQg"


settings = Settings()
