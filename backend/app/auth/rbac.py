from typing import List, Dict, Any, Optional

ALL_ROLES = [
    "employee",
    "manager",
    "hr",
    "finance",
    "it_support",
    "it_admin",
    "executive",
    "system_admin",
]

ROLE_HIERARCHY_SCOPES: Dict[str, List[str]] = {
    "employee": ["all", "employee"],
    "manager": ["all", "employee", "manager"],
    "hr": ["all", "employee", "hr"],
    "finance": ["all", "employee", "finance"],
    "it_support": ["all", "employee", "it_support"],
    "it_admin": ["all", "employee", "it_support", "it_admin"],
    "executive": ["all", "employee", "manager", "executive"],
    "system_admin": ["all", "system_admin"],
}

CLASSIFICATION_LEVELS = {
    "public": 1,
    "internal": 2,
    "confidential": 3,
    "restricted": 4,
}

ROLE_MAX_CLASSIFICATION = {
    "employee": "internal",
    "manager": "internal",
    "hr": "confidential",
    "finance": "confidential",
    "it_support": "confidential",
    "it_admin": "restricted",
    "executive": "confidential",
    "system_admin": "internal", # system admin does not automatically see all secrets/restricted content
}

class RBACManager:
    @staticmethod
    def is_chunk_accessible(
        user_role: str,
        user_department: str,
        chunk_allowed_roles: List[str],
        chunk_allowed_departments: List[str],
        chunk_classification: str = "internal",
    ) -> bool:
        """
        Validates if a chunk is accessible by the specified user role and department.
        Enforces defense-in-depth:
        1. Role permission
        2. Department permission
        3. Classification ceiling
        """
        user_role = (user_role or "employee").lower()
        user_department = (user_department or "all").lower()
        chunk_classification = (chunk_classification or "internal").lower()

        # Check classification level
        max_allowed_class = ROLE_MAX_CLASSIFICATION.get(user_role, "internal")
        if CLASSIFICATION_LEVELS.get(chunk_classification, 2) > CLASSIFICATION_LEVELS.get(max_allowed_class, 2):
            return False

        # Check Role Access
        if chunk_allowed_roles:
            normalized_roles = [r.lower() for r in chunk_allowed_roles]
            user_scopes = ROLE_HIERARCHY_SCOPES.get(user_role, ["all", "employee"])
            has_role_access = any(scope in normalized_roles for scope in user_scopes)
            if not has_role_access:
                return False

        # Check Department Access
        if chunk_allowed_departments:
            normalized_depts = [d.lower() for d in chunk_allowed_departments]
            if "all" not in normalized_depts and user_department not in normalized_depts:
                # If specific department is required, check match
                if user_department != "all":
                    return False

        return True

    @staticmethod
    def build_rbac_filter(user_role: str, user_department: str) -> Dict[str, Any]:
        """
        Returns criteria for pre-filtering chunks in database before computing vector/keyword similarity.
        """
        user_role = (user_role or "employee").lower()
        user_department = (user_department or "all").lower()
        user_scopes = ROLE_HIERARCHY_SCOPES.get(user_role, ["all", "employee"])
        max_class = ROLE_MAX_CLASSIFICATION.get(user_role, "internal")

        allowed_classifications = [
            cls_name
            for cls_name, lvl in CLASSIFICATION_LEVELS.items()
            if lvl <= CLASSIFICATION_LEVELS.get(max_class, 2)
        ]

        return {
            "allowed_scopes": user_scopes,
            "user_department": user_department,
            "allowed_classifications": allowed_classifications,
        }
