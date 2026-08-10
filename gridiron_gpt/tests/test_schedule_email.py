from email.message import EmailMessage

import pytest
from fastapi.testclient import TestClient

from gridiron_gpt.api.app import create_app
from gridiron_gpt.product.schedule_email import (
    ScheduleEmailRequest,
    ScheduleEmailResult,
    build_schedule_email,
    schedule_csv,
)
from gridiron_gpt.product.schedule_generator import (
    ScheduleConfig,
    ScheduleGenerator,
    ScheduleTeam,
)


def generated():
    teams = tuple(
        ScheduleTeam(
            team_id=f"team-{index + 1}",
            name=f"Team {index + 1}",
            division="East" if index < 5 else "West",
        )
        for index in range(10)
    )
    schedule = ScheduleGenerator().generate(
        ScheduleConfig(
            teams=teams,
            regular_season_weeks=13,
            playoff_start_week=14,
            playoff_weeks=3,
        )
    )
    return schedule, {team.team_id: team.name for team in teams}


def schedule_payload():
    return {
        "teams": [
            {
                "team_id": f"team-{index + 1}",
                "name": f"Team {index + 1}",
                "division": "East" if index < 5 else "West",
            }
            for index in range(10)
        ],
        "regular_season_weeks": 13,
        "playoff_start_week": 14,
        "playoff_weeks": 3,
    }


def test_schedule_csv_contains_all_games():
    schedule, names = generated()
    csv_text = schedule_csv(schedule, names)

    assert csv_text.startswith("Week,Away Team,Home Team,Divisional")
    assert len(csv_text.strip().splitlines()) == 66


def test_email_contains_csv_attachment():
    schedule, names = generated()
    request = ScheduleEmailRequest(
        recipients=("owner@example.com",),
        subject="League Schedule",
        message="Attached.",
    )

    email = build_schedule_email(
        request=request,
        schedule=schedule,
        name_by_id=names,
        sender_email="commissioner@example.com",
    )

    assert isinstance(email, EmailMessage)
    assert email["Subject"] == "League Schedule"
    assert email["To"] == "owner@example.com"
    attachments = list(email.iter_attachments())
    assert len(attachments) == 1
    assert attachments[0].get_filename() == "fantasy_schedule.csv"
    assert "Week,Away Team" in attachments[0].get_content()


def test_multiple_recipients_are_supported():
    request = ScheduleEmailRequest(
        recipients=("one@example.com", "two@example.com"),
        subject="Schedule",
        message="Attached.",
    )
    assert len(request.recipients) == 2


def test_invalid_recipient_is_rejected():
    with pytest.raises(ValueError, match="invalid recipient"):
        ScheduleEmailRequest(
            recipients=("not-an-email",),
            subject="Schedule",
            message="Attached.",
        )


def test_reply_to_is_validated():
    with pytest.raises(ValueError, match="reply_to"):
        ScheduleEmailRequest(
            recipients=("one@example.com",),
            subject="Schedule",
            message="Attached.",
            reply_to="invalid",
        )


class FakeMailer:
    def __init__(self):
        self.calls = []

    def send(self, request, schedule, name_by_id):
        self.calls.append((request, schedule, name_by_id))
        return ScheduleEmailResult(
            sent=True,
            recipient_count=len(request.recipients),
            provider="fake",
            detail="sent",
        )


def test_schedule_email_api_uses_injected_mailer(tmp_path):
    mailer = FakeMailer()
    client = TestClient(create_app(tmp_path, schedule_mailer=mailer))
    response = client.post(
        "/schedules/email",
        json={
            "schedule": schedule_payload(),
            "recipients": ["one@example.com", "two@example.com"],
            "subject": "RRFL Schedule",
            "message": "Here it is.",
            "reply_to": "commissioner@example.com",
        },
    )

    assert response.status_code == 200
    assert response.json()["sent"] is True
    assert response.json()["recipient_count"] == 2
    assert response.json()["provider"] == "fake"
    assert len(mailer.calls) == 1
    assert len(mailer.calls[0][1].matchups) == 65


def test_schedule_email_api_rejects_bad_recipient(tmp_path):
    client = TestClient(create_app(tmp_path, schedule_mailer=FakeMailer()))
    response = client.post(
        "/schedules/email",
        json={
            "schedule": schedule_payload(),
            "recipients": ["bad-address"],
            "subject": "Schedule",
            "message": "Attached.",
        },
    )

    assert response.status_code == 422
