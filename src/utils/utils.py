from datetime import datetime


class utils:
    @staticmethod
    def parse_time(raw: str) -> str:
        raw = raw.strip()
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%m/%d/%y, %I:%M %p",
            "%m/%d/%y %I:%M %p",
            "%m/%d/%y, %H:%M",
            "%m/%d/%y %H:%M",
            "%Y-%m-%dT%H:%M:%S",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(raw, fmt).strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue

        try:
            year = datetime.now().year
            return datetime.strptime(f"{year}/{raw}", "%Y/%m/%d, %I:%M %p").strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        except ValueError:
            pass

        return raw
