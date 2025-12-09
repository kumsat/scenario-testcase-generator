from typing import List, Tuple


def detect_fields_for_scenario(scenario: str) -> Tuple[List[str], List[str]]:
    """
    Best-effort heuristic to choose sensible text and binary fields
    for common scenarios. For unknown scenarios we return empty lists
    and let the caller decide defaults.

    This now includes:
    - Web/app flows (login, logout, checkout, etc.)
    - Automotive / infotainment scenarios (HMI, audio, BT, Wi-Fi, navigation, CAN/LIN, OTA, etc.)
    """
    s = scenario.strip().lower()

    # ---------------- Web / generic app flows ----------------

    # Login / authentication style
    if "login" in s or "sign in" in s.replace("-", " ") or "authenticate" in s:
        text_fields = ["username", "password", "otp"]
        binary_fields = ["remember_me", "show_password"]
        return text_fields, binary_fields

    # Logout
    if "logout" in s or "sign out" in s.replace("-", " "):
        text_fields = ["session_id"]
        binary_fields = ["is_network_connected"]
        return text_fields, binary_fields

    # Checkout / payment
    if "checkout" in s or "payment" in s or "purchase" in s:
        text_fields = ["shipping_address", "zipcode", "card_number", "cvv"]
        binary_fields = ["save_address", "accept_terms"]
        return text_fields, binary_fields

    # Registration / signup
    if "registration" in s or "sign up" in s.replace("-", " ") or "signup" in s:
        text_fields = ["full_name", "email", "password", "confirm_password"]
        binary_fields = ["accept_terms", "subscribe_newsletter"]
        return text_fields, binary_fields

    # Reset password / forgot password
    if "reset password" in s or "forgot password" in s or "password_reset" in s:
        text_fields = ["email", "otp", "new_password"]
        binary_fields = ["remember_device"]
        return text_fields, binary_fields

    # Add to cart
    if "add to cart" in s or "add_to_cart" in s.replace("-", " "):
        text_fields = ["product_id", "quantity"]
        binary_fields = ["is_logged_in"]
        return text_fields, binary_fields

    # Generic API operation guess
    if "api" in s or "endpoint" in s or "request" in s:
        text_fields = ["payload", "auth_token"]
        binary_fields = ["is_authenticated"]
        return text_fields, binary_fields

    # ---------------- Automotive / ECU style ----------------

    if "ecu" in s or "firmware" in s or "diagnostic" in s or "can" in s and "door" not in s:
        text_fields = ["request_id", "checksum", "ecu_id"]
        binary_fields = ["is_vehicle_running", "is_ignition_on"]
        return text_fields, binary_fields

    # ---------------- Infotainment / HMI scenarios ----------------

    # HMI / UI
    if "hmi" in s or "ui" in s or "user interface" in s:
        text_fields = ["screen_id", "language", "theme", "brightness_level"]
        binary_fields = ["is_touch_enabled", "is_night_mode"]
        return text_fields, binary_fields

    # Audio routing
    if "audio" in s and ("routing" in s or "source" in s or "output" in s):
        text_fields = ["audio_source", "output_target", "volume_level", "balance_setting"]
        binary_fields = ["is_nav_prompt_active", "is_phone_call_active"]
        return text_fields, binary_fields

    # Bluetooth
    if "bluetooth" in s or "bt " in s or s.startswith("bt "):
        text_fields = [
            "phone_bucket",       # iOS/Android category
            "bt_profile",         # HFP/A2DP/PBAP
            "reconnect_trigger",  # ignition / bt toggle / out-of-range / hu reboot
            "power_state",        # engine/accessory/crank
            "hu_state",           # idle/media/call
        ]
        binary_fields = ["is_device_paired_before", "is_auto_reconnect_enabled"]
        return text_fields, binary_fields

    # Wi-Fi / hotspot
    if "wifi" in s or "wi-fi" in s or "hotspot" in s:
        text_fields = ["ssid", "wifi_password", "signal_strength", "client_profile"]
        binary_fields = ["is_hotspot_enabled", "is_client_mode_enabled"]
        return text_fields, binary_fields

    # Navigation / GNSS
    if "navigation" in s or "nav " in s or "gnss" in s or "route" in s:
        text_fields = ["start_location", "destination", "route_type", "traffic_condition"]
        binary_fields = ["is_gps_locked", "is_online_services_available"]
        return text_fields, binary_fields

    # Vehicle integration (CAN/LIN) – infotainment context
    if "vehicle integration" in s or ("can" in s or "lin" in s) and "door" not in s:
        text_fields = ["signal_name", "signal_value", "bus_load"]
        binary_fields = ["is_ignition_on", "is_vehicle_moving"]
        return text_fields, binary_fields

    # OTA update
    if "ota" in s or "over-the-air" in s or "software update" in s:
        text_fields = ["package_version", "package_size", "current_sw_version"]
        binary_fields = ["is_wifi_connected", "is_battery_ok"]
        return text_fields, binary_fields

    # Performance / responsiveness
    if "performance" in s or "latency" in s or "response time" in s:
        text_fields = ["operation_type", "data_volume", "concurrent_sessions"]
        binary_fields = ["is_logging_enabled", "is_debug_mode"]
        return text_fields, binary_fields

    # Security / access control
    if "security" in s or "access control" in s or "authorization" in s:
        text_fields = ["user_role", "auth_method", "resource_name"]
        binary_fields = ["is_mfa_enabled", "is_account_locked"]
        return text_fields, binary_fields

    # Robustness / faults / power cycling
    if "robustness" in s or "power cycle" in s or "fault" in s or "stress" in s:
        text_fields = ["fault_type", "recovery_attempts", "test_duration"]
        binary_fields = ["is_network_available", "is_backup_path_available"]
        return text_fields, binary_fields

    # Door warning (special CAN use-case, if you ever use 'door warning' in scenario)
    if "door warning" in s or ("door" in s and "warning" in s):
        text_fields = ["door_signal", "vehicle_speed", "voltage_profile"]
        binary_fields = ["is_ignition_on", "cluster_active"]
        return text_fields, binary_fields

    # Fallback: unknown scenario → let caller decide defaults
    return [], []

