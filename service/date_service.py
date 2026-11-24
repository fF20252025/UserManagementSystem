
import re
from datetime import date, datetime, time

import jdatetime


class DateService:
    """
    Central service for converting and formatting
    Gregorian and Jalali dates.
    """

    SUPPORTED_CALENDARS = ("jalali", "gregorian")

    @staticmethod
    def gregorian_to_jalali(value):
        if isinstance(value, datetime):
            value = value.date()

        if not isinstance(value, date):
            raise ValueError("Invalid Gregorian date")

        return jdatetime.date.fromgregorian(date=value)

    @staticmethod
    def jalali_to_gregorian(value):
        if isinstance(value, str):
            value = value.strip()

            match = re.fullmatch(
                r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})",
                value
            )

            if not match:
                raise ValueError("Invalid Jalali date format")

            year, month, day = map(int, match.groups())

            value = jdatetime.date(year, month, day)

        if not isinstance(value, jdatetime.date):
            raise ValueError("Invalid Jalali date")

        return value.togregorian()

    @staticmethod
    def parse_date(value, calendar="gregorian"):
        if value is None:
            return None

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        if not isinstance(value, str):
            raise ValueError("Invalid date value")

        value = value.strip()

        if not value:
            return None

        if calendar not in DateService.SUPPORTED_CALENDARS:
            raise ValueError("Unsupported calendar")

        if calendar == "jalali":
            return DateService.jalali_to_gregorian(value)

        try:
            return date.fromisoformat(value)
        except ValueError:
            raise ValueError("Invalid Gregorian date format")

    @staticmethod
    def format_date(value, calendar="jalali", separator="/"):
        if value is None:
            return ""

        if isinstance(value, datetime):
            value = value.date()

        if not isinstance(value, date):
            raise ValueError("Invalid date value")

        if calendar == "gregorian":
            return value.strftime(
                f"%Y{separator}%m{separator}%d"
            )

        if calendar == "jalali":
            jalali_date = DateService.gregorian_to_jalali(value)

            return (
                f"{jalali_date.year:04d}{separator}"
                f"{jalali_date.month:02d}{separator}"
                f"{jalali_date.day:02d}"
            )

        raise ValueError("Unsupported calendar")

    @staticmethod
    def format_datetime(value, calendar="jalali"):
        if value is None:
            return ""

        if not isinstance(value, datetime):
            raise ValueError("Invalid datetime value")

        formatted_date = DateService.format_date(
            value,
            calendar=calendar
        )

        return f"{formatted_date} {value.strftime('%H:%M:%S')}"

    @staticmethod
    def today(calendar="jalali"):
        today = date.today()

        return DateService.format_date(
            today,
            calendar=calendar
        )

    @staticmethod
    def normalize_calendar(value):
        if value is None:
            return "jalali"

        value = value.strip().lower()

        aliases = {
            "jalali": "jalali",
            "shamsi": "jalali",
            "persian": "jalali",
            "gregorian": "gregorian",
            "miladi": "gregorian",
        }

        if value not in aliases:
            raise ValueError("Unsupported calendar")

        return aliases[value]
