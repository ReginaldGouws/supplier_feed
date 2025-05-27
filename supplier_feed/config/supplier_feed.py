from frappe import _

def get_data():
    return [
        {
            "label": _("Supplier Feed"),
            "icon": "fa fa-rss",
            "items": [
                {
                    "type": "page",
                    "name": "feed-dashboard",
                    "label": _("Feed Dashboard"),
                    "description": _("Overview of all supplier feeds"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Feed Setup",
                    "description": _("Configure supplier feeds"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Supplier Feed Record",
                    "description": _("Temporary storage for supplier feed data"),
                    "onboard": 1,
                },
            ]
        },
        {
            "label": _("Settings"),
            "icon": "fa fa-cog",
            "items": [
                {
                    "type": "doctype",
                    "name": "Feed Field Mapping",
                    "description": _("Map supplier fields to internal fields"),
                },
            ]
        },
    ]