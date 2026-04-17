from fastapi import APIRouter, Depends, HTTPException, status
from psycopg2.extras import RealDictCursor
from ..database import get_db
from ..schemas.auth import Token, LoginRequest, UserCreate, UserOut
from ..auth.password import verify_password, hash_password
from ..auth.jwt_handler import create_access_token
from ..auth.rbac import require_admin, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
def login(body: LoginRequest, db=Depends(get_db)):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            "SELECT * FROM users WHERE username = %s LIMIT 1", (body.username,)
        )
        user = cursor.fetchone()
    finally:
        cursor.close()

    if not user or not verify_password(body.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled"
        )

    token = create_access_token(
        {"sub": user["username"], "user_id": user["user_id"], "role": user["role"]}
    )
    return Token(
        access_token=token,
        token_type="bearer",
        role=user["role"],
        username=user["username"],
        user_id=user["user_id"],
        linked_id=user["linked_id"],
    )


@router.get("/me", response_model=UserOut)
def get_me(current_user: UserOut = Depends(get_current_user)):
    return current_user


@router.get("/users", response_model=list[UserOut])
def list_users(db=Depends(get_db), _: UserOut = Depends(require_admin)):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        return [UserOut(**u) for u in users]
    finally:
        cursor.close()


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(
    body: UserCreate, db=Depends(get_db), _: UserOut = Depends(require_admin)
):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            "SELECT * FROM users WHERE username = %s LIMIT 1", (body.username,)
        )
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already taken")

        hashed_pw = hash_password(body.password)
        cursor.execute(
            """
            INSERT INTO users (username, email, password, role, linked_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
            """,
            (body.username, body.email, hashed_pw, body.role, body.linked_id),
        )
        user = cursor.fetchone()
        db.commit()
        return UserOut(**user)
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db=Depends(get_db), _: UserOut = Depends(require_admin)):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            "DELETE FROM users WHERE user_id = %s RETURNING user_id", (user_id,)
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="User not found")
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()
