# scenario_library.py
# Defines automotive domains and their combinational fields

AUTOMOTIVE_SCENARIOS = {
    "bluetooth": {
        "keywords": ["bluetooth", "pair", "reconnect", "bt", "handsfree"],
        "text_fields": ["device_name", "pin_code"],
        "binary_fields": ["bt_enabled", "contact_sync_enabled"],
        "domain_specific": {
            "phone_types": ["iOS", "Samsung", "Android_Other", "China_OEM"],
            "profiles": ["HFP", "A2DP", "PBAP"],
            "reconnect_triggers": ["IGN_OFF_ON", "BT_OFF_ON", "Out_of_range"],
            "power_states": ["KL15", "ACC", "Crank"],
        },
    },

    "wifi": {
        "keywords": ["wifi", "hotspot", "wireless"],
        "text_fields": ["ssid", "password"],
        "binary_fields": ["hotspot_enabled", "autoconnect"],
    },

    "hmi": {
        "keywords": ["hmi", "ui", "screen", "menu", "touch"],
        "text_fields": ["screen_name", "button_id"],
        "binary_fields": ["touch_enabled", "gesture_enabled"],
    },

    "audio": {
        "keywords": ["audio", "volume", "routing", "media"],
        "text_fields": ["source", "target_output"],
        "binary_fields": ["nav_prompt_active", "phone_call_active"],
    },

    "navigation": {
        "keywords": ["navigation", "gps", "route", "reroute"],
        "text_fields": ["destination", "start_point", "route_type"],
        "binary_fields": ["traffic_enabled", "gps_signal_ok"],
    },

    "vehicle_integration": {
        "keywords": ["can", "lin", "vehicle", "signal"],
        "text_fields": ["signal_name", "value"],
        "binary_fields": ["ignition_on", "battery_present"],
    },

    "ota": {
        "keywords": ["ota", "update", "firmware"],
        "text_fields": ["version", "package_id"],
        "binary_fields": ["wifi_required", "rollback_available"],
    },

    "performance": {
        "keywords": ["performance", "boot", "latency", "loadtime"],
        "text_fields": ["component", "metric"],
        "binary_fields": ["cold_boot", "heavy_load"],
    },

    "security": {
        "keywords": ["security", "auth", "permissions"],
        "text_fields": ["user_role", "action"],
        "binary_fields": ["session_valid", "encryption_enabled"],
    },

    "robustness": {
        "keywords": ["robust", "stress", "fault", "recovery"],
        "text_fields": ["operation", "fault_type"],
        "binary_fields": ["power_cycle", "network_disruption"],
    },
}


def detect_scenario_fields(scenario: str):
    """Auto-detect what fields to use based on scenario name."""
    scenario_lower = scenario.lower()

    for name, config in AUTOMOTIVE_SCENARIOS.items():
        if any(keyword in scenario_lower for keyword in config["keywords"]):
            return config  # return full config block

    # Default fallback
    return {
        "text_fields": ["field1", "field2"],
        "binary_fields": ["toggle1"],
        "domain_specific": {},
    }

