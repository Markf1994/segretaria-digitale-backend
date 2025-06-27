from app.crud import user as user_crud


def test_create_user(db_session):
    new_user = user_crud.create_user(db_session, "user@example.com", "secret")
    assert new_user.email == "user@example.com"
    assert user_crud.verify_password("secret", new_user.hashed_password)
