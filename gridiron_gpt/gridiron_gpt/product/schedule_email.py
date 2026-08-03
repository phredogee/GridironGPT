from __future__ import annotations

import csv
import io
import os
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import parseaddr
from typing import Protocol

from gridiron_gpt.product.schedule_generator import GeneratedSchedule


@dataclass(frozen=True)
class ScheduleEmailRequest:
    recipients: tuple[str, ...]
    subject: str
    message: str
    sender_name: str = "GridironGPT"
    reply_to: str | None = None
    attachment_name: str = "fantasy_schedule.csv"

    def __post_init__(self) -> None:
        if not self.recipients:
            raise ValueError("at least one recipient is required")
        invalid = [recipient for recipient in self.recipients if not _valid_email(recipient)]
        if invalid:
            raise ValueError(f"invalid recipient email: {invalid[0]}")
        if self.reply_to and not _valid_email(self.reply_to):
            raise ValueError("invalid reply_to email")
        if not self.subject.strip():
            raise ValueError("subject is required")
        if not self.attachment_name.lower().endswith(".csv"):
            raise ValueError("attachment_name must end with .csv")


@dataclass(frozen=True)
class ScheduleEmailResult:
    sent: bool
    recipient_count: int
    provider: str
    detail: str


class ScheduleMailer(Protocol):
    def send(
        self,
        request: ScheduleEmailRequest,
        schedule: GeneratedSchedule,
        name_by_id: dict[str, str],
    ) -> ScheduleEmailResult: ...


class SmtpScheduleMailer:
    """Send generated schedules through any SMTP-compatible provider."""

    def __init__(
        self,
        *,
        host: str,
        port: int,
        username: str,
        password: str,
        sender_email: str,
        use_ssl: bool = False,
        use_starttls: bool = True,
        timeout: float = 20.0,
    ) -> None:
        if not host.strip():
            raise ValueError("SMTP host is required")
        if port <= 0:
            raise ValueError("SMTP port must be positive")
        if not _valid_email(sender_email):
            raise ValueError("valid sender_email is required")
        if use_ssl and use_starttls:
            raise ValueError("use_ssl and use_starttls cannot both be enabled")
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.sender_email = sender_email
        self.use_ssl = use_ssl
        self.use_starttls = use_starttls
        self.timeout = timeout

    @classmethod
    def from_environment(cls) -> "SmtpScheduleMailer":
        required = {
            "GRIDIRON_SMTP_HOST": os.getenv("GRIDIRON_SMTP_HOST", ""),
            "GRIDIRON_SMTP_PORT": os.getenv("GRIDIRON_SMTP_PORT", ""),
            "GRIDIRON_SMTP_SENDER": os.getenv("GRIDIRON_SMTP_SENDER", ""),
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise RuntimeError(
                "schedule email is not configured; missing " + ", ".join(missing)
            )
        return cls(
            host=required["GRIDIRON_SMTP_HOST"],
            port=int(required["GRIDIRON_SMTP_PORT"]),
            username=os.getenv("GRIDIRON_SMTP_USERNAME", ""),
            password=os.getenv("GRIDIRON_SMTP_PASSWORD", ""),
            sender_email=required["GRIDIRON_SMTP_SENDER"],
            use_ssl=_env_bool("GRIDIRON_SMTP_SSL", False),
            use_starttls=_env_bool("GRIDIRON_SMTP_STARTTLS", True),
        )

    def send(
        self,
        request: ScheduleEmailRequest,
        schedule: GeneratedSchedule,
        name_by_id: dict[str, str],
    ) -> ScheduleEmailResult:
        email = build_schedule_email(
            request=request,
            schedule=schedule,
            name_by_id=name_by_id,
            sender_email=self.sender_email,
        )
        smtp_class = smtplib.SMTP_SSL if self.use_ssl else smtplib.SMTP
        with smtp_class(self.host, self.port, timeout=self.timeout) as client:
            if self.use_starttls:
                client.starttls()
            if self.username:
                client.login(self.username, self.password)
            client.send_message(email)
        return ScheduleEmailResult(
            sent=True,
            recipient_count=len(request.recipients),
            provider="smtp",
            detail="schedule email sent",
        )


def build_schedule_email(
    *,
    request: ScheduleEmailRequest,
    schedule: GeneratedSchedule,
    name_by_id: dict[str, str],
    sender_email: str,
) -> EmailMessage:
    email = EmailMessage()
    email["Subject"] = request.subject.strip()
    email["From"] = f"{request.sender_name} <{sender_email}>"
    email["To"] = ", ".join(request.recipients)
    if request.reply_to:
        email["Reply-To"] = request.reply_to
    email.set_content(request.message.strip() or "The league schedule is attached.")
    csv_bytes = schedule_csv(schedule, name_by_id).encode("utf-8")
    email.add_attachment(
        csv_bytes,
        maintype="text",
        subtype="csv",
        filename=request.attachment_name,
    )
    return email


def schedule_csv(schedule: GeneratedSchedule, name_by_id: dict[str, str]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Week", "Away Team", "Home Team", "Divisional"])
    for game in schedule.matchups:
        writer.writerow(
            [
                game.week,
                name_by_id[game.away_team_id],
                name_by_id[game.home_team_id],
                "Yes" if game.divisional else "No",
            ]
        )
    return output.getvalue()


def _valid_email(value: str) -> bool:
    _, address = parseaddr(value.strip())
    return bool(address and "@" in address and "." in address.rsplit("@", 1)[-1])


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}
