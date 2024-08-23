# -*- coding: utf-8 -*-
from fastapi import (
    FastAPI,
    Request,
    Depends,
    Response,
    Form,
    File,
    UploadFile,
    status,
    Cookie,
    HTTPException
)
from fastapi.responses import (
    RedirectResponse,
    StreamingResponse,
    HTMLResponse
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from passlib.hash import bcrypt
from google_auth_oauthlib.flow import InstalledAppFlow
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text
from .database import (
    SessionLocal,
    engine
)
from .models import (
    Base,
    Recipe,
    Batch,
    User,
    UserSession
)
from .google_docs import list_shared_files
from datetime import (datetime, timezone, timedelta)
from io import BytesIO
from pathlib import Path
from timeit import default_timer as timer
from typing import Any, Optional
import os
import secrets
import shutil
import subprocess

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

UPLOAD_DIRECTORY = "app/static/user_images"
Path(UPLOAD_DIRECTORY).mkdir(parents=True, exist_ok=True)

Base.metadata.create_all(bind=engine)

app.add_middleware(SessionMiddleware, secret_key="HoytIrcbOGRp7znytn0k1nwbUWZzTOBfy1ee2gbJCck")

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

app.add_middleware(HTTPSRedirectMiddleware)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    session = db.query(UserSession).filter_by(token=token).first()
    if not session or session.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return session.user

def create_session(user: User, db: Session) -> UserSession:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=30)
    session = UserSession(token=token, user=user, expires_at=expires_at)
    db.add(session)
    db.commit()
    return session

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    start = timer()
    utcnow = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    current_year = datetime.now().year
    end = timer()
    lt = end - start
    loadtime = format_time(lt)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "utcnow": utcnow,
        "current_year": current_year,
        "loadtime": loadtime
    })

@app.post("/login")
async def login_post(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter_by(username=username).first()
    if not user or not user.verify_password(password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    session_token = secrets.token_hex(32)
    session = UserSession(user_id=user.id, token=session_token, expires_at=datetime.utcnow() + timedelta(days=30))
    db.add(session)
    db.commit()

    if user.username == "admin":
        response = RedirectResponse(url="/create-user", status_code=status.HTTP_303_SEE_OTHER)
    else:
        response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    response.set_cookie(key="session_token", value=session_token, httponly=True, max_age=60*60*24*30)
    return response

@app.middleware("http")
async def enforce_authentication(request: Request, call_next):
    if not request.url.path.startswith(("/login", "/static", "/open-endpoints")):
        session_token = request.cookies.get("session_token")
        if not session_token:
            return RedirectResponse(url="/login")
        db = SessionLocal()
        session = db.query(UserSession).filter_by(token=session_token).first()
        if not session or session.expires_at < datetime.utcnow():
            return RedirectResponse(url="/login")
        db.close()
    response = await call_next(request)
    return response

@app.post("/token", response_class=HTMLResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=form_data.username).first()
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    session = create_session(user, db)
    response = RedirectResponse(url="/")
    response.set_cookie(key="session_token", value=session.token, httponly=True, max_age=60*60*24*30)
    return response

@app.get("/logout", response_class=RedirectResponse)
async def logout(response: Response):
    response.delete_cookie("session_token")
    return RedirectResponse(url="/login")

@app.get("/me")
async def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    return user

@app.get("/create-user", response_class=HTMLResponse)
async def create_user_form(request: Request, db: Session = Depends(get_db)):
    session_token = request.cookies.get("session_token")
    if not session_token:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    session = db.query(UserSession).filter_by(token=session_token).first()
    if not session or session.expires_at < datetime.utcnow():
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    user = db.query(User).filter_by(id=session.user_id).first()
    if not user or user.username != "admin":
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("create_user.html", {"request": request})

@app.post("/create-user")
async def create_user(
    request: Request,
    username: str = Form(...),
    realname: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    session_token = request.cookies.get("session_token")
    if not session_token:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    session = db.query(UserSession).filter_by(token=session_token).first()
    if not session or session.expires_at < datetime.utcnow():
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    user = db.query(User).filter_by(id=session.user_id).first()
    if not user or user.username != "admin":
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    new_user = User(username=username, realname=realname, hashed_password=User.hash_password(password))
    db.add(new_user)
    db.commit()

    db.delete(user)
    db.commit()

    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

def format_time(lt):
    microseconds = lt * 1_000_000
    milliseconds = lt * 1000
    seconds = lt
    minutes = lt / 60
    if lt >= 60:
        elapsed_minutes = int(lt // 60)
        elapsed_seconds = lt % 60
        if elapsed_seconds >= 1:
            loadtime = f'{elapsed_minutes} minutes and {elapsed_seconds:.2f} seconds'
        else:
            loadtime = f'{elapsed_minutes} minutes'
    elif lt >= 1:
        loadtime = f'{seconds:.2f} seconds'
    elif lt >= 0.001:
        loadtime = f'{milliseconds:.2f} milliseconds'
    else:
        loadtime = f'{microseconds:.2f} microseconds'
    return loadtime

@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    if db.query(User).count() == 0:
        default_user = User(
            username="admin",
            realname="Default Admin",
            hashed_password=User.hash_password("password123")
        )
        db.add(default_user)
        db.commit()
    db.close()

@app.get("/restricted", response_class=HTMLResponse)
async def restricted_view(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("restricted.html", {"request": request, "user": user})

@app.get("/")
async def read_root(request: Request, db: Session = Depends(get_db)):
    start = timer()
    session_token = request.cookies.get("session_token")
    realname = "Guest"
    if session_token:
        session = db.query(UserSession).filter_by(token=session_token).first()
        if session and session.expires_at > datetime.utcnow():
            user = db.query(User).filter_by(id=session.user_id).first()
            if user:
                realname = user.realname

    utcnow = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    current_year = datetime.now().year
    end = timer()
    lt = end - start
    loadtime = format_time(lt)

    return templates.TemplateResponse("main.html", {
        "request": request,
        "utcnow": utcnow,
        "current_year": current_year,
        "loadtime": loadtime,
        "realname": realname
    })

@app.get("/tilt/callback")
async def callback(request: Request):
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json',
        SCOPES,
        redirect_uri='https://localhost:8080/tilt/callback'
    )
    flow.fetch_token(authorization_response=str(request.url))
    creds = flow.credentials

    with open('token.json', 'w') as token:
        token.write(creds.to_json())

    return RedirectResponse(url="/tilt")

@app.get("/oauth2callback")
async def oauth2callback(request: Request):
    code = request.query_params.get('code')
    state = request.query_params.get('state')

    if code:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        flow.fetch_token(code=code)
        creds = flow.credentials
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        return RedirectResponse(url="/tilt")

    return HTMLResponse(content="Authorization failed.")

@app.get("/tilt/callback")
async def callback(request: Request):
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json',
        SCOPES,
        redirect_uri='https://localhost:8080/tilt/callback'
    )
    flow.fetch_token(authorization_response=str(request.url))
    creds = flow.credentials

    with open('token.json', 'w') as token:
        token.write(creds.to_json())

    return RedirectResponse(url="/tilt")

@app.get("/oauth2callback")
async def oauth2callback(request: Request):
    code = request.query_params.get('code')
    state = request.query_params.get('state')

    if code:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        flow.fetch_token(code=code)
        creds = flow.credentials
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        return RedirectResponse(url="/tilt")

    return HTMLResponse(content="Authorization failed.")

@app.get("/tilt", response_class=HTMLResponse)
async def select_document(request: Request):
    start = timer()
    utcnow = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    current_year = datetime.now().year
    end = timer()
    lt = end - start
    loadtime = format_time(lt)
    user_email = "noah@baronbrew.com"

    result = list_shared_files(user_email=user_email)

    if isinstance(result, RedirectResponse):
        redirect_url = result.headers.get('location')
        return HTMLResponse(content=f"""
        <html>
        <body>
            <p>Please follow this link to authenticate: <a href="{redirect_url}" target="_blank">{redirect_url}</a></p>
        </body>
        </html>
        """)

    files = result

    return templates.TemplateResponse("tilt.html", {
        "request": request,
        "files": files,
        "utcnow": utcnow,
        "current_year": current_year,
        "loadtime": loadtime
    })


@app.post("/tilt/view", response_class=RedirectResponse)
async def view_document(doc_id: str = Form(...)):
    return RedirectResponse(url=f"/tilt/view/{doc_id}", status_code=303)

@app.get("/tilt/upload_credentials", response_class=HTMLResponse)
async def upload_credentials(request: Request):
    start = timer()
    utcnow = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    current_year = datetime.now().year
    end = timer()
    lt = end - start
    loadtime = format_time(lt)
    return templates.TemplateResponse("upload_credentials.html", {
        "request": request,
        "utcnow": utcnow,
        "current_year": current_year,
        "loadtime": loadtime
    })

@app.post("/tilt/upload_credentials")
async def handle_upload_credentials(file: UploadFile = File(...)):
    credentials_path = "credentials.json"
    with open(credentials_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return RedirectResponse(url="/tilt", status_code=303)

@app.get("/abv-calculator", response_class=HTMLResponse)
async def abv_calculator_view(request: Request):
    start = timer()
    utcnow = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    current_year = datetime.now().year
    end = timer()
    lt = end - start
    loadtime = format_time(lt)
    return templates.TemplateResponse("abv-calculator.html", {
        "request": request,
        "utcnow": utcnow,
        "current_year": current_year,
        "loadtime": loadtime
    })

@app.get("/batches", response_class=HTMLResponse)
async def get_batch_form(request: Request):
    recipes = session.query(Recipe).all()

    return templates.TemplateResponse("create_batch.html", {"request": request, "recipes": recipes})

@app.get("/batches/{batch_id}/image")
async def get_batch_image(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(Batch).filter_by(id=batch_id).first()
    if batch and batch.image:
        return Response(content=batch.image, media_type="image/jpeg")
    else:
        raise HTTPException(status_code=404, detail="Image not found")

@app.post("/batches")
async def create_batch(request: Request,
                       recipe_id: Optional[int] = Form(None),
                       primary_fermentation: str = Form(None),
                       secondary_fermentation: str = Form(None),
                       bottled: str = Form(None),
                       batch_size: str = Form("5 gallons"),
                       notes: str = Form(None),
                       osg: str = Form(None),
                       fsg: str = Form(None),
                       abv: str = Form(None),
                       image: UploadFile = File(None),
                       db: Session = Depends(get_db)):

    primary_fermentation_date = (
        datetime.strptime(primary_fermentation, "%Y-%m-%d").date()
        if primary_fermentation else None
    )
    secondary_fermentation_date = (
        datetime.strptime(secondary_fermentation, "%Y-%m-%d").date()
        if secondary_fermentation else None
    )
    bottled_date = (
        datetime.strptime(bottled, "%Y-%m-%d").date()
        if bottled else None
    )

    image_data = None
    if image and hasattr(image, 'filename') and image.filename:
        image_data = await image.read()  # Read image data as bytes

    new_batch = Batch(
        recipe_id=recipe_id,
        primary_fermentation=primary_fermentation_date,
        secondary_fermentation=secondary_fermentation_date,
        bottled=bottled_date,
        batch_size=batch_size,
        notes=notes,
        osg=osg,
        fsg=fsg,
        abv=abv,
        image=image_data
    )

    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)

    return RedirectResponse(url="/recipes", status_code=303)

@app.get("/recipes", response_class=HTMLResponse)
async def recipes_view(request: Request, db: Session = Depends(get_db)):
    start = timer()
    try:
        batches = db.query(Batch).options(joinedload(Batch.recipe)).all()
        recipes = db.query(Recipe).all()
    except Exception as e:
        print(f"Error fetching recipes: {e}")
        recipes = "ERROR"
        batches = "ERROR"
    utcnow = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    current_year = datetime.now().year
    end = timer()
    lt = end - start
    loadtime = format_time(lt)
    return templates.TemplateResponse("recipes.html", {
        "request": request,
        "recipes": recipes,
        "batches": batches,
        "utcnow": utcnow,
        "current_year": current_year,
        "loadtime": loadtime
    })

@app.post("/recipes")
async def create_recipe(
    recipe_name: str = Form(...),
    rec_size: Optional[str] = Form(None),
    ingredients: str = Form(...),
    instructions: str = Form(...),
    db: Session = Depends(get_db)
):
    new_recipe = Recipe(
        recipe_name=recipe_name,
        rec_size=rec_size,
        ingredients=ingredients,
        instructions=instructions
    )
    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)

    return RedirectResponse(url="/recipes", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/recipes/{recipe_id}/edit")
async def edit_recipe(recipe_id: int, recipe_name: str = Form(...), rec_size: str = Form(...), ingredients: str = Form(...), instructions: str = Form(...), db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if recipe:
        recipe.recipe_name = recipe_name
        recipe.rec_size = rec_size
        recipe.ingredients = ingredients
        recipe.instructions = instructions
        db.commit()
    return RedirectResponse(url="/recipes", status_code=303)

@app.post("/batches/{batch_id}/edit")
async def edit_batch(batch_id: int,
                     batch_size: str = Form(...),
                     primary_fermentation: str = Form(...),
                     secondary_fermentation: str = Form(...),
                     bottled: str = Form(...),
                     notes: str = Form(...),
                     osg: str = Form(...),
                     fsg: str = Form(...),
                     abv: str = Form(...),
                     db: Session = Depends(get_db)):

    try:
        primary_fermentation_date = (
            datetime.strptime(primary_fermentation, "%Y-%m-%d").date()
            if primary_fermentation else None
        )
        secondary_fermentation_date = (
            datetime.strptime(secondary_fermentation, "%Y-%m-%d").date()
            if secondary_fermentation else None
        )
        bottled_date = (
            datetime.strptime(bottled, "%Y-%m-%d").date()
            if bottled else None
        )
    except ValueError as e:
        return {"error": f"Invalid date format: {e}"}

    batch = db.query(Batch).filter(Batch.id == batch_id).first()

    if batch:
        batch.batch_size = batch_size
        batch.primary_fermentation = primary_fermentation_date
        batch.secondary_fermentation = secondary_fermentation_date
        batch.bottled = bottled_date
        batch.notes = notes
        batch.osg = osg
        batch.fsg = fsg
        batch.abv = abv

        db.commit()

    return RedirectResponse(url="/recipes", status_code=303)

@app.post("/recipes/{recipe_id}/delete")
def delete_recipe(recipe_id: int,
                  db: Session = Depends(get_db)
                  ):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    db.delete(recipe)

    db.commit()


    return RedirectResponse(url="/recipes", status_code=303)

@app.post("/batches/{batch_id}/delete")
def delete_batch(batch_id: int,
                  db: Session = Depends(get_db)
                 ):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()

    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")

    db.delete(batch)

    db.commit()


    return RedirectResponse(url="/recipes", status_code=303)


@app.get("/about", response_class=HTMLResponse)
async def settings_view(
    request: Request,
    db: Session = Depends(get_db),
    session_token: str = Cookie(None)
):
    user_session = db.query(UserSession).filter_by(token=session_token).first()
    if not user_session:
        return RedirectResponse(url="/login")

    user = db.query(User).filter_by(id=user_session.user_id).first()

    if user:
        user_id = user.id
        username = user.username
        realname = user.realname
    else:
        username = ""
        realname = ""
        user_id = ""

    start = timer()
    utcnow = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    current_year = datetime.now().year
    end = timer()
    lt = end - start
    loadtime = format_time(lt)

    return templates.TemplateResponse("about.html", {
        "request": request,
        "utcnow": utcnow,
        "current_year": current_year,
        "loadtime": loadtime,
        "user_id": user_id,
        "username": username,
        "realname": realname
    })

@app.post("/backup-database")
async def backup_database():
    db_file_path = "app/skal.db"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"skal_backup_{timestamp}.db"

    with open(db_file_path, "rb") as db_file:
        db_content = db_file.read()

    headers = {
        "Content-Disposition": f"attachment; filename={file_name}"
    }
    return Response(db_content, headers=headers, media_type="application/octet-stream")

@app.post("/import-database")
async def import_database(file: UploadFile = File(...)):
    db_file_path = "app/skal.db"
    backup_dir = "app/backups"
    os.makedirs(backup_dir, exist_ok=True)

    # Backup the existing database
    if os.path.exists(db_file_path):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_file_path = os.path.join(backup_dir, f"skal_backup_{timestamp}.db")
        shutil.copy(db_file_path, backup_file_path)

    # Import the new database
    with open(db_file_path, "wb") as db_file:
        shutil.copyfileobj(file.file, db_file)

    return RedirectResponse(url="/about", status_code=303)

@app.post("/update-user")
async def update_user(
    username: str = Form(...),
    realname: str = Form(...),
    password: str = Form(None),
    confirm_password: str = Form(None),
    user_id: int = Form(...),
    db: Session = Depends(get_db)
):
    if password and password != confirm_password:
        return {"error": "Passwords do not match"}

    query = "UPDATE users SET username = :username, realname = :realname"
    params = {"username": username, "realname": realname, "user_id": user_id}

    if password:
        hashed_password = bcrypt.hash(password)
        query += ", hashed_password = :hashed_password"
        params["hashed_password"] = hashed_password

    query += " WHERE id = :user_id"

    db.execute(text(query), params)
    db.commit()
    db.close()

    return RedirectResponse(url="/about", status_code=303)

@app.get("/license")
async def get_license():
    license_path = os.path.join(os.getcwd(), "LICENSE")
    if os.path.exists(license_path):
        with open(license_path, "r") as file:
            license_content = file.read()
        return Response(content=license_content, media_type="text/plain")
    return Response(content="LICENSE file not found", media_type="text/plain", status_code=404)

@app.get("/info", response_class=HTMLResponse)
async def info(request: Request):
    start = timer()
    utcnow = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    current_year = datetime.now().year
    end = timer()
    lt = end - start
    loadtime = format_time(lt)
    return templates.TemplateResponse("info.html", {"request": request,
        "utcnow": utcnow,
        "current_year": current_year,
        "loadtime": loadtime
    })

#@app.post("/generate-cert")
#async def generate_cert(request: Request, domain: str = Form(...)):
#    # Trigger Certbot to generate certificates
#    certbot_command = (
#        f"sudo certbot certonly --standalone -d {domain} "
#        f"--non-interactive --agree-tos --email admin@{domain} "
#        f"--config-dir app/static/certbot/config "
#        f"--work-dir app/static/certbot/work "
#        f"--logs-dir app/static/certbot/logs"
#    )
#
#    process = subprocess.run(certbot_command.split(), capture_output=True)
#
#    if process.returncode == 0:
#        # Certbot succeeded, link new certs to the app's cert files
#        subprocess.run(["ln", "-sf", f"app/static/certbot/{domain}/fullchain.pem", "cert.pem"])
#        subprocess.run(["ln", "-sf", f"app/static/certbot/{domain}/privkey.pem", "key.pem"])
#
#
#        # Create the Nginx configuration file
#        nginx_config = f"""
#        server {{
#            listen 80;
#            server_name {domain};
#
#            location / {{
#                return 301 https://$host$request_uri;
#            }}
#        }}
#
#        server {{
#            listen 443 ssl;
#            server_name {domain};
#
#            ssl_certificate app/static/certbot/live/{domain}/fullchain.pem;
#            ssl_certificate_key /etc/letsencrypt/live/{domain}/privkey.pem;
#
#            location / {{
#                proxy_pass https://127.0.0.1:8080;
#            }}
#        }}
#        """
#
#        # Write the Nginx configuration to the appropriate location
#        nginx_config_path = f"/etc/nginx/sites-available/{domain}.conf"
#        with open(nginx_config_path, "w") as config_file:
#            config_file.write(nginx_config)
#
#        # Enable the configuration by creating a symlink in sites-enabled
#        subprocess.run(["ln", "-sf", nginx_config_path, f"/etc/nginx/sites-enabled/{domain}.conf"])
#
#        # Reload or restart Nginx to apply the changes
#        nginx_reload = subprocess.run(["systemctl", "reload", "nginx"], capture_output=True)
#
#        if nginx_reload.returncode == 0:
#            return {"message": "Certificate generated and Nginx reloaded successfully"}
#        else:
#            return {"error": "Failed to reload Nginx", "details": nginx_reload.stderr.decode()}
#        cron_command = f"(crontab -l; echo '0 0 * * * certbot renew --quiet --post-hook \"systemctl reload nginx\"') | crontab -"
#        cron_process = subprocess.run(cron_command, shell=True, capture_output=True)
#
#        if cron_process.returncode == 0:
#            return {"message": "Certificate generated, Nginx reloaded, and renewal cron job created successfully"}
#        else:
#            return {"error": "Failed to create cron job", "details": cron_process.stderr.decode()}
#    else:
#        return {"error": "Failed to generate certificate", "details": process.stderr.decode()}
#
#@app.get("/cert-form")
#async def cert_form(request: Request):
#    return templates.TemplateResponse("generate_cert.html", {"request": request})
