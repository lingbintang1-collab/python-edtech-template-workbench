"""Lifecycle copy kept together like storefront receipt templates."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from infrai_email import InfraiEmail


@dataclass(frozen=True)
class CourseTemplate:
    slug: str
    subject: str
    html: str
    sample_vars: dict[str, str]


COURSE_TEMPLATES = (
    CourseTemplate(
        slug="enrollment-confirmed",
        subject="Your place in {{course_name}} is confirmed",
        html=(
            "<h1>Welcome, {{student_name}}</h1>"
            "<p>Your first lesson starts on {{start_date}}.</p>"
        ),
        sample_vars={
            "student_name": "Mina",
            "course_name": "Storefront Analytics",
            "start_date": "September 8",
        },
    ),
    CourseTemplate(
        slug="lesson-reminder",
        subject="{{course_name}} continues tomorrow",
        html=(
            "<p>Hi {{student_name}}, your next lesson is {{lesson_name}}.</p>"
            "<p>Open your classroom when you are ready.</p>"
        ),
        sample_vars={
            "student_name": "Mina",
            "course_name": "Storefront Analytics",
            "lesson_name": "Reading checkout events",
        },
    ),
)


def publish_and_preview(
    client: InfraiEmail, namespace: str
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    run_id = uuid.uuid4().hex[:10]

    for template in COURSE_TEMPLATES:
        name = f"{namespace}-{template.slug}-{run_id}"
        idempotency_key = f"template:{name}"
        created = client.create_template(
            name=name,
            subject=template.subject,
            html=template.html,
            idempotency_key=idempotency_key,
        )
        template_id = str(created["template_id"])
        preview = client.preview_template(template_id, template.sample_vars)
        results.append(
            {"name": name, "template_id": template_id, "preview": preview}
        )

    return results
