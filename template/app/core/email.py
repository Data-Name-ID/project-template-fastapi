from email.message import EmailMessage
from typing import Any

import aiosmtplib
import jinja2

from app.core.store import Store


class EmailManager:
    def __init__(self, store: Store) -> None:
        self.store = store

        loader = jinja2.FileSystemLoader(self.store.config.templates_dir)
        self.env = jinja2.Environment(
            loader=loader,
            trim_blocks=True,
            autoescape=True,
        )

    async def send_email(
        self,
        *,
        recipient: str,
        title: str,
        template: str,
        **template_kwargs: Any,
    ) -> None:
        email_message = EmailMessage()
        email_message["From"] = self.store.config.email.smtp_user
        email_message["To"] = recipient
        email_message["Subject"] = title
        email_message.set_content(
            self.env.get_template(template).render(**template_kwargs),
            subtype="html",
        )

        await aiosmtplib.send(
            email_message,
            hostname=self.store.config.email.smtp_server,
            port=self.store.config.email.smtp_port,
            username=self.store.config.email.smtp_user,
            password=self.store.config.email.smtp_password,
            start_tls=self.store.config.email.smtp_use_tls,
        )
