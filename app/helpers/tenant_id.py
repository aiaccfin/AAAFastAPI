from uuid import UUID

TENANT_ID = UUID("550e8400-e29b-41d4-a716-446655440000")

def get_tenant_id() -> UUID:
    # later: extract from JWT / header / Azure AD
    return TENANT_ID
