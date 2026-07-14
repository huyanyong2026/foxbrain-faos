"""VAFOX OS UX 2.0 information architecture contract."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class NavigationLayer:
    key: str
    name: str
    route: str
    purpose: str
    max_entries: int


UX_NAVIGATION_LAYERS = (
    NavigationLayer("business", "Business", "/os/business", "Business objects and operations", 8),
    NavigationLayer("ai", "AI", "/os/ai", "Central AI assistant, knowledge, agents and tasks", 4),
    NavigationLayer("messages", "Messages", "/os/messages", "Daily reports, approvals, notifications and todos", 4),
    NavigationLayer("me", "Me", "/os/me", "Profile, permissions, theme, settings and system", 5),
)


UX_PRINCIPLES = {
    "home_first_layer_is_minimal": True,
    "home_has_no_explanatory_small_text": True,
    "one_page_one_subject": True,
    "one_layer_max_entries": 8,
    "find_anything_within_three_steps": True,
    "ai_is_independent_center": True,
    "global_search_is_fixed": True,
    "ai_entry_is_fixed": True,
    "mobile_bottom_navigation": True,
    "details_only_after_click_through": True,
    "apple_hig_inspired": True,
}


def build_ux_information_architecture_contract() -> dict:
    return {
        "ok": True,
        "version": "VAFOX OS UX 2.0",
        "codename": "Apple Experience Edition",
        "module": "ux_information_architecture",
        "goal": "make VAFOX simple enough that employees know where to click on first use",
        "home_policy": "first_layer_four_entries_only_no_repeated_business_content",
        "v8_policy": "fixed_global_search_fixed_ai_entry_mobile_bottom_navigation_and_no_home_small_text",
        "layers": [asdict(layer) for layer in UX_NAVIGATION_LAYERS],
        "principles": dict(UX_PRINCIPLES),
        "fixed_entries": {
            "global_search": "/os/search",
            "ai": "/jarvis",
            "mobile_bottom_nav": ["/os/business", "/os/ai", "/os/messages", "/os/me"],
        },
        "recommended_structure": {
            "home": ["Business", "AI", "Messages", "Me"],
            "business": ["Stores", "Employees", "Products", "Brands", "Customers", "Suppliers", "Finance"],
            "ai": ["AI Assistant", "AI Knowledge", "AI Agents", "AI Tasks"],
            "messages": ["AI Daily Report", "Approvals", "Notifications", "Todos"],
            "me": ["Profile", "Permissions", "Theme", "Settings", "System"],
        },
    }
