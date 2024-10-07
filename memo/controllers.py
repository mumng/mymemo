from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from models import User, Memo
from schemas import UserCreate, UserLogin, MemoCreate, MemoUpdate
from dependencies import get_db, get_password_hash, verify_password
from sqlalchemy.orm import Session

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# 회원 가입
@router.post("/signup/")
async def signup(signup_data: UserCreate, db: Session = Depends(get_db)):
  existing_user = db.query(User).filter(signup_data.username == User.username).first()
  if existing_user:
    raise HTTPException(status_code=400, detail="이미 동일한 username 존재!")
  hashed_password = get_password_hash(signup_data.password)
  new_user = User(username=signup_data.username, email=signup_data.email, hashed_password=hashed_password)
  db.add(new_user)
  try:
    db.commit()
  except Exception as e:
    print(e)
    raise HTTPException(status_code=500, detail="회원가입시 DB 접속에러")
  db.refresh(new_user)
  return {"message": "회원가입 완료!"}

# 로그인
@router.post("/login")
async def login(request: Request, signin_data: UserLogin, db: Session = Depends(get_db)):
  user = db.query(User).filter(signin_data.username == User.username).first()
  if user and verify_password(signin_data.password, user.hashed_password):
    request.session["username"] = user.username
    return {"message": "Logged in successfully!"}
  else:
    raise HTTPException(status_code=401, detail="Invalid condentials")

@router.post("/logout")
async def logout(request: Request):
  request.session.pop("username", None)
  return {"message":"Logout successfully!"}

# 메모 생성
@router.post("/memos/")
async def create_user(request: Request, memo:MemoCreate, db:Session = Depends(get_db)):
  username = request.session.get("username")
  if username is None:
    raise HTTPException(status_code=401, detail="Not authorized")
  user = db.query(User).filter(User.username == username).first()
  if user is None:
    raise HTTPException(status_code=404, detail="User not found")
  new_memo = Memo(user_id = user.id, title=memo.title, content = memo.content)
  db.add(new_memo)
  db.commit()
  db.refresh(new_memo)  
  return new_memo

# 메모 조회
@router.get("/memos/")
async def list_memos(request:Request, db:Session = Depends(get_db)):
  username = request.session.get("username")
  if username is None:
    raise HTTPException(status_code=401, detail="Not authorized")
  user = db.query(User).filter(User.username == username).first()
  if user is None:
    raise HTTPException(status_code=404, detail="User not found")
  
  memos = db.query(Memo).filter(Memo.user_id == user.id).all()
  return templates.TemplateResponse("memos.html", {"request":request, "memos":memos})

# 메모 수정
@router.put("/memos/{memo_id}")
async def update_memo(request:Request, memo_id: int, memo:MemoUpdate, db:Session = Depends(get_db)):
  username = request.session.get("username")
  if username is None:
    raise HTTPException(status_code=401, detail="로그인 하십시오")
  user = db.query(User).filter(User.username == username).first()
  if user is None:
    raise HTTPException(status_code=404, detail="DB에 기록되어 있지 않은 유저 입니다")
  db_memo = db.query(Memo).filter(Memo.user_id == user.id, Memo.id == memo_id).first()
  if db_memo is None:
    return ({"error": "Memo is not found"})
  
  if memo.title is not None:
    db_memo.title = memo.title
  if memo.content is not None:
    db_memo.content = memo.content

  db.commit()
  db.refresh(db_memo)
  return db_memo

# 메모 삭제
@router.delete("/memos/{memo_id}")
async def delete_memo(request:Request, memo_id: int, db:Session = Depends(get_db)):
  username = request.session.get("username")
  if username is None:
    raise HTTPException(status_code=401, detail="로그인 하십시오")
  user = db.query(User).filter(User.username == username).first()
  if user is None:
    raise HTTPException(status_code=404, detail="DB에 기록되어 있지 않은 유저 입니다")
  db_memo = db.query(Memo).filter(user.id == Memo.user_id, Memo.id == memo_id).first()
  if db_memo is None:
    return ({"error": "Memo is not found"})
  db.delete(db_memo)
  db.commit()
  return({"message": "Memo deleted"})

@router.get("/")
async def read_root(request: Request):
  return templates.TemplateResponse("home.html", {"request": request})

@router.get("/about")
async def about():
  return {"message": "이것은 마이메모 앱의 소개페이지 입니다."}