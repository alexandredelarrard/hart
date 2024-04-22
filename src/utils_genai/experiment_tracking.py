from datetime import datetime
from uuid import uuid4
from zoneinfo import ZoneInfo

CONFIG__TIMEZONE = "Europe/Paris"


def now_as_a_number(timezone: str):
    """
    This helps for querying: for example if you called this function
    the 16th of April 2024 at 1:35:32PM it would return the following number:
    `20240416133532`
    Then you could query numbers between 20240416 and 20240417 to get the experiments
    of the day etc...

    This allows to implement "datetime" filtering even on engines that don't support it.
    (as long as they implement "int" filtering, of course.

    WARNING: this is fine when you are working alone on remote machines, for your convenience.
    If you are working with a distributed team, you might want to do differently.
    """
    timezone: ZoneInfo = ZoneInfo(timezone)
    now = datetime.now()
    paris_time = now.astimezone(timezone)
    formatted_number = paris_time.strftime("%Y%m%d%H%M%S")
    return formatted_number


def make_experiment_tracking_metadata(experiment_name, timezone=None):
    timezone = timezone or CONFIG__TIMEZONE
    return {
        "experiment": experiment_name,
        "experiment_uuid": str(uuid4()),
        "experiment_ts": datetime.now().timestamp(),
        "experiment_datetime": now_as_a_number(timezone),
        "experiment_timezone": timezone,
    }
