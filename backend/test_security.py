from aurora.modules.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

password = "Aurora123!"

hashed = hash_password(password)

print("Hash:", hashed)
print("Verify:", verify_password(password, hashed))

token = create_access_token("user@example.com")

print("Token:", token)

payload = decode_access_token(token)

print("Payload:", payload)
