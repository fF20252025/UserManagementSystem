ROLES = {
    "superadmin",
    "admin",
    "operator",
    "user"
}


def is_valid_role(role: str) -> bool:
    return role in ROLES