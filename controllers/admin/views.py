import json
import random
from functools import lru_cache

from django.contrib.humanize.templatetags.humanize import intcomma
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from unfold.components import BaseComponent, register_component
from django.utils.timezone import now, timedelta


def dashboard_callback(request, context):
    context.update(random_data(request))
    return context


def navigation_component(request):
    return [
        {
            "title": _("Dashboard"),
            "link": reverse_lazy("admin:index"),
            "active": True,
        },
        {"title": _("Analytics"), "link": "#"},
        {"title": _("Settings"), "link": "#"},
    ]


@lru_cache
def cohort_random_data():
    rows = []
    headers = []
    cols = []

    dates = reversed(
        [(now() - timedelta(days=x)).strftime("%B %d, %Y") for x in range(8)]
    )
    groups = range(1, 10)

    for row_index, date in enumerate(dates):
        cols = []

        for col_index, _col in enumerate(groups):
            color_index = 8 - row_index - col_index
            col_classes = []

            if color_index > 0:
                col_classes.append(
                    f"bg-primary-{color_index}00 dark:bg-primary-{9 - color_index}00"
                )

            if color_index >= 4:
                col_classes.append("text-white")

            if color_index >= 6:
                col_classes.append("dark:text-base-800")

            value = random.randint(
                10,
                10000,
            )
            subtitle = ""
            cols.append(
                {
                    "value": value,
                    "color": " ".join(col_classes),
                    "subtitle": subtitle,
                }
            )

        rows.append(
            {
                "header": {
                    "title": date,
                    "subtitle": f"Total {sum(col['value'] for col in cols):,}",
                },
                "cols": cols,
            }
        )

    for index, group in enumerate(groups):
        total = 0
        for row in rows:
            total += row["cols"][index]["value"]
        for row in rows:
            row["cols"][index][
                "subtitle"
            ] = f"{(row['cols'][index]['value'] / total * 100):.0f}%"

        headers.append(
            {
                "title": f"Group #{group}",
                "subtitle": f"Total {total:,}",
            }
        )

    return {
        "headers": headers,
        "rows": rows,
    }


@lru_cache
def tracker_random_data():
    data = []

    for _i in range(1, 64):
        has_value = random.choice([True, True, True, True, False])
        color = None
        tooltip = None

        if has_value:
            value = random.randint(2, 6)
            color = "bg-primary-500"
            tooltip = f"Value {value}"

        data.append(
            {
                "color": color,
                "tooltip": tooltip,
            }
        )

    return data


@register_component
class CohortComponent(BaseComponent):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["data"] = cohort_random_data()
        return context


@register_component
class TrackerComponent(BaseComponent):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["data"] = tracker_random_data()
        return context


@lru_cache
def random_data(request):
    WEEKDAYS = [
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "Sat",
        "Sun",
    ]

    positive = [[1, random.randrange(8, 28)] for i in range(1, 28)]
    negative = [[-1, -random.randrange(8, 28)] for i in range(1, 28)]
    average = [r[1] - random.randint(3, 5) for r in positive]
    performance_positive = [[1, random.randrange(8, 28)] for i in range(1, 28)]
    performance_negative = [[-1, -random.randrange(8, 28)] for i in range(1, 28)]

    return {
        "navigation": navigation_component(request),
        "filters": [
            {"title": _("All"), "link": "#", "active": True},
            {
                "title": _("New"),
                "link": "#",
            },
        ],
        "kpi": [
            {
                "title": "Product A Performance",
                "metric": f"${intcomma(f'{random.uniform(1000, 9999):.02f}')}",
                "footer": mark_safe(
                    f'<strong class="text-green-700 font-semibold dark:text-green-400">+{intcomma(f"{random.uniform(1, 9):.02f}")
                                                                                         }%</strong>&nbsp;progress from last week'
                ),
                "chart": json.dumps(
                    {
                        "labels": [WEEKDAYS[day % 7] for day in range(1, 28)],
                        "datasets": [{"data": average, "borderColor": "#9333ea"}],
                    }
                ),
            },
            {
                "title": "Product B Performance",
                "metric": f"${intcomma(f'{random.uniform(1000, 9999):.02f}')}",
                "footer": mark_safe(
                    f'<strong class="text-green-700 font-semibold dark:text-green-400">+{intcomma(f"{random.uniform(1, 9):.02f}")
                                                                                         }%</strong>&nbsp;progress from last week'
                ),
            },
            {
                "title": "Product C Performance",
                "metric": f"${intcomma(f'{random.uniform(1000, 9999):.02f}')}",
                "footer": mark_safe(
                    f'<strong class="text-green-700 font-semibold dark:text-green-400">+{intcomma(f"{random.uniform(1, 9):.02f}")
                                                                                         }%</strong>&nbsp;progress from last week'
                ),
            },
            {
                "title": "Product C Performance",
                "metric": f"${intcomma(f'{random.uniform(1000, 9999):.02f}')}",
                "footer": mark_safe(
                    f'<strong class="text-green-700 font-semibold dark:text-green-400">+{intcomma(f"{random.uniform(1, 9):.02f}")
                                                                                         }%</strong>&nbsp;progress from last week'
                ),
            },
        ],
        "progress": [
            {
                "title": "Social marketing e-book",
                "description": f"${intcomma(f'{random.uniform(1000, 9999):.02f}')}",
                "value": random.randint(10, 90),
            },
            {
                "title": "Freelancing tasks",
                "description": f"${intcomma(f'{random.uniform(1000, 9999):.02f}')}",
                "value": random.randint(10, 90),
            },
            {
                "title": "Development coaching",
                "description": f"${intcomma(f'{random.uniform(1000, 9999):.02f}')}",
                "value": random.randint(10, 90),
            },
            {
                "title": "Product consulting",
                "description": f"${intcomma(f'{random.uniform(1000, 9999):.02f}')}",
                "value": random.randint(10, 90),
            },
            {
                "title": "Other income",
                "description": f"${intcomma(f'{random.uniform(1000, 9999):.02f}')}",
                "value": random.randint(10, 90),
            },
            {
                "title": "Course sales",
                "description": f"${intcomma(f'{random.uniform(1000, 9999):.02f}')}",
                "value": random.randint(10, 90),
            },
            {
                "title": "Ads revenue",
                "description": f"${intcomma(f'{random.uniform(1000, 9999):.02f}')}",
                "value": random.randint(10, 90),
            },
            {
                "title": "Customer Retention Rate",
                "description": f"${intcomma(f'{random.uniform(1000, 9999):.02f}')}",
                "value": random.randint(10, 90),
            },
        ],
        "chart": json.dumps(
            {
                "labels": [WEEKDAYS[day % 7] for day in range(1, 28)],
                "datasets": [
                    {
                        "label": "Example 1",
                        "type": "line",
                        "data": average,
                        "borderColor": "var(--color-primary-500)",
                    },
                    {
                        "label": "Example 2",
                        "data": positive,
                        "backgroundColor": "var(--color-primary-700)",
                    },
                    {
                        "label": "Example 3",
                        "data": negative,
                        "backgroundColor": "var(--color-primary-300)",
                    },
                ],
            }
        ),
        "performance": [
            {
                "title": _("Last week revenue"),
                "metric": "$1,234.56",
                "footer": mark_safe(
                    '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
                ),
                "chart": json.dumps(
                    {
                        "labels": [WEEKDAYS[day % 7] for day in range(1, 28)],
                        "datasets": [
                            {
                                "data": performance_positive,
                                "borderColor": "var(--color-primary-700)",
                            }
                        ],
                    }
                ),
            },
            {
                "title": _("Last week expenses"),
                "metric": "$1,234.56",
                "footer": mark_safe(
                    '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
                ),
                "chart": json.dumps(
                    {
                        "labels": [WEEKDAYS[day % 7] for day in range(1, 28)],
                        "datasets": [
                            {
                                "data": performance_negative,
                                "borderColor": "var(--color-primary-300)",
                            }
                        ],
                    }
                ),
            },
        ],
        "table_data": {
            "headers": [_("Day"), _("Income"), _("Expenses")],
            "rows": [
                ["22-10-2025", "$2,341.89", "$1,876.45"],
                ["23-10-2025", "$1,987.23", "$2,109.67"],
                ["24-10-2025", "$3,456.78", "$1,543.21"],
                ["25-10-2025", "$1,765.43", "$2,987.65"],
                ["26-10-2025", "$2,876.54", "$1,234.56"],
                ["27-10-2025", "$1,543.21", "$2,765.43"],
                ["28-10-2025", "$3,210.98", "$1,987.65"],
            ],
        },
    }
