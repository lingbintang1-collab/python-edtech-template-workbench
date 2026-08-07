"""Publish the course mail set and render each template with sample data."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from course_mail_templates import publish_and_preview  # noqa: E402
from infrai_email import InfraiEmail  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--namespace",
        default="academy-storefront",
        help="Prefix used to organize this application's templates",
    )
    args = parser.parse_args()
    results = publish_and_preview(InfraiEmail(), args.namespace)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
