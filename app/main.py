"""
Criacao, Edicao e Teste T3A - FastAPI Application
Standalone platform for T3A document editing with approval cards.
"""

import os
import json
import logging
import threading
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.database import init_db, Client, EditJob, EditChange, EditHistory, CreationProject, SessionLocal
from app.orchestrator import Orchestrator
from app.llm.cost_tracker import cost_tracker

logging.basicConfig(level=getattr(logging, settings.log_level), format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Database initialized")
    yield


app = FastAPI(title="Criacao, Edicao e Teste T3A", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "app", "static")), name="static")

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "app", "templates"))


# ============ AUTH ============

class AuthRedirect(Exception):
    pass


def require_auth(request: Request):
    if not request.session.get("authenticated"):
        raise AuthRedirect()
    return True


@app.exception_handler(AuthRedirect)
async def auth_redirect_handler(request: Request, exc: AuthRedirect):
    return RedirectResponse(url="/login", status_code=303)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if request.session.get("authenticated"):
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request, password: str = Form(...)):
    if password == settings.app_password:
        request.session["authenticated"] = True
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Senha incorreta"})


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


# ============ HEALTH ============

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


# ============ DASHBOARD ============

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, _=Depends(require_auth)):
    db = SessionLocal()
    try:
        clients = db.query(Client).order_by(Client.updated_at.desc()).all()
        return templates.TemplateResponse("dashboard.html", {"request": request, "clients": clients})
    finally:
        db.close()


# ============ CLIENT CRUD ============

@app.get("/clients/new", response_class=HTMLResponse)
async def client_new_form(request: Request, _=Depends(require_auth)):
    return templates.TemplateResponse("client_form.html", {"request": request, "client": None, "error": None})


@app.post("/clients/new", response_class=HTMLResponse)
async def client_create(request: Request, _=Depends(require_auth),
                        name: str = Form(...), description: str = Form(""),
                        prompt_content: str = Form(""), base_content: str = Form(""),
                        general_prompt_content: str = Form("")):
    db = SessionLocal()
    try:
        client = Client(name=name, description=description, prompt_content=prompt_content,
                        base_content=base_content, general_prompt_content=general_prompt_content)
        db.add(client)
        db.commit()
        db.refresh(client)
        return RedirectResponse(url=f"/clients/{client.id}", status_code=303)
    finally:
        db.close()


@app.get("/clients/{client_id}", response_class=HTMLResponse)
async def client_detail(request: Request, client_id: int, _=Depends(require_auth)):
    db = SessionLocal()
    try:
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Cliente nao encontrado")
        jobs = db.query(EditJob).filter(EditJob.client_id == client_id).order_by(EditJob.created_at.desc()).all()
        return templates.TemplateResponse("client_detail.html", {
            "request": request, "client": client, "jobs": jobs, "error": None, "success": None
        })
    finally:
        db.close()


@app.get("/clients/{client_id}/edit", response_class=HTMLResponse)
async def client_edit_form(request: Request, client_id: int, _=Depends(require_auth)):
    db = SessionLocal()
    try:
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Cliente nao encontrado")
        return templates.TemplateResponse("client_form.html", {"request": request, "client": client, "error": None})
    finally:
        db.close()


@app.post("/clients/{client_id}/edit", response_class=HTMLResponse)
async def client_update(request: Request, client_id: int, _=Depends(require_auth),
                        name: str = Form(...), description: str = Form(""),
                        prompt_content: str = Form(""), base_content: str = Form(""),
                        general_prompt_content: str = Form("")):
    db = SessionLocal()
    try:
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Cliente nao encontrado")
        client.name = name
        client.description = description
        client.prompt_content = prompt_content
        client.base_content = base_content
        client.general_prompt_content = general_prompt_content
        client.updated_at = datetime.utcnow()
        db.commit()
        return RedirectResponse(url=f"/clients/{client_id}", status_code=303)
    finally:
        db.close()


@app.post("/clients/{client_id}/delete")
async def client_delete(request: Request, client_id: int, _=Depends(require_auth)):
    db = SessionLocal()
    try:
        client = db.query(Client).filter(Client.id == client_id).first()
        if client:
            db.query(EditChange).filter(
                EditChange.job_id.in_(db.query(EditJob.id).filter(EditJob.client_id == client_id))
            ).delete(synchronize_session=False)
            db.query(EditJob).filter(EditJob.client_id == client_id).delete()
            db.query(EditHistory).filter(EditHistory.client_id == client_id).delete()
            db.delete(client)
            db.commit()
        return RedirectResponse(url="/", status_code=303)
    finally:
        db.close()


# ============ EDIT REQUEST (NEW FLOW) ============

def _run_edit_job(job_id: int, client_id: int, edit_request: str, document_types: list[str]):
    """Run edit job in background thread."""
    db = SessionLocal()
    try:
        job = db.query(EditJob).filter(EditJob.id == job_id).first()
        client = db.query(Client).filter(Client.id == client_id).first()
        if not job or not client:
            return

        job.status = "processing"
        job.progress = 10
        db.commit()

        # Build edit history context
        past_jobs = db.query(EditJob).filter(
            EditJob.client_id == client_id, EditJob.status == "completed"
        ).order_by(EditJob.created_at.desc()).limit(15).all()

        edit_history_context = ""
        if past_jobs:
            history_parts = []
            for pj in past_jobs:
                changes = db.query(EditChange).filter(EditChange.job_id == pj.id, EditChange.status == "approved").all()
                if changes:
                    parts = [f"- {c.field}/{c.section}: {c.reason}" for c in changes[:5]]
                    history_parts.append(f"Edicao '{pj.edit_request[:80]}': " + "; ".join(parts))
            if history_parts:
                edit_history_context = "\n\nEDICOES ANTERIORES APROVADAS (contexto):\n" + "\n".join(history_parts)

        orchestrator = Orchestrator()
        result = orchestrator.generate_edit_changes(
            edit_request=edit_request + edit_history_context,
            prompt_content=client.prompt_content or "",
            base_content=client.base_content or "",
            general_prompt_content=client.general_prompt_content or "",
            document_types=document_types,
            job_id=str(job_id)
        )

        if result.get("success"):
            changes = result.get("changes", [])
            for change_data in changes:
                change = EditChange(
                    job_id=job_id,
                    field=change_data.get("field", "prompt"),
                    section=change_data.get("section", ""),
                    before_text=change_data.get("before", ""),
                    after_text=change_data.get("after", ""),
                    reason=change_data.get("reason", ""),
                    status="pending"
                )
                db.add(change)

            job.status = "completed"
            job.progress = 100
            job.summary = result.get("summary", "")
            db.commit()
        else:
            job.status = "failed"
            job.error_message = result.get("error", "Unknown error")
            job.progress = 100
            db.commit()

    except Exception as e:
        logger.error(f"Edit job {job_id} failed: {e}", exc_info=True)
        try:
            job = db.query(EditJob).filter(EditJob.id == job_id).first()
            if job:
                job.status = "failed"
                job.error_message = str(e)
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


@app.post("/clients/{client_id}/edit-request")
async def submit_edit_request(request: Request, client_id: int, _=Depends(require_auth),
                              edit_request: str = Form(...),
                              doc_prompt: str = Form(""),
                              doc_base: str = Form(""),
                              doc_geral: str = Form("")):
    db = SessionLocal()
    try:
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404)

        document_types = []
        if doc_prompt:
            document_types.append("prompt")
        if doc_base:
            document_types.append("base_de_dados")
        if doc_geral:
            document_types.append("prompt_geral")
        if not document_types:
            document_types = ["prompt", "base_de_dados", "prompt_geral"]

        job = EditJob(
            client_id=client_id,
            edit_request=edit_request,
            document_types=json.dumps(document_types),
            status="pending",
            progress=0
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        # Run in background thread
        thread = threading.Thread(
            target=_run_edit_job,
            args=(job.id, client_id, edit_request, document_types)
        )
        thread.start()

        return RedirectResponse(url=f"/clients/{client_id}/jobs/{job.id}/review", status_code=303)
    finally:
        db.close()


# ============ JOB STATUS & REVIEW ============

@app.get("/api/clients/{client_id}/jobs/{job_id}/status")
async def job_status_api(request: Request, client_id: int, job_id: int, _=Depends(require_auth)):
    db = SessionLocal()
    try:
        job = db.query(EditJob).filter(EditJob.id == job_id, EditJob.client_id == client_id).first()
        if not job:
            return JSONResponse({"error": "not found"}, status_code=404)
        changes = []
        if job.status == "completed":
            changes = [
                {"id": c.id, "field": c.field, "section": c.section,
                 "before": c.before_text, "after": c.after_text,
                 "reason": c.reason, "status": c.status}
                for c in db.query(EditChange).filter(EditChange.job_id == job_id).all()
            ]
        return JSONResponse({
            "id": job.id, "status": job.status, "progress": job.progress,
            "error_message": job.error_message, "summary": job.summary,
            "changes": changes, "total_changes": len(changes)
        })
    finally:
        db.close()


@app.get("/clients/{client_id}/jobs/{job_id}/review", response_class=HTMLResponse)
async def review_changes(request: Request, client_id: int, job_id: int, _=Depends(require_auth)):
    db = SessionLocal()
    try:
        client = db.query(Client).filter(Client.id == client_id).first()
        job = db.query(EditJob).filter(EditJob.id == job_id, EditJob.client_id == client_id).first()
        if not client or not job:
            raise HTTPException(status_code=404)
        changes = db.query(EditChange).filter(EditChange.job_id == job_id).all()
        return templates.TemplateResponse("edit_review.html", {
            "request": request, "client": client, "job": job, "changes": changes
        })
    finally:
        db.close()


# ============ APPROVE / REJECT / APPLY ============

@app.post("/api/clients/{client_id}/jobs/{job_id}/changes/{change_id}/approve")
async def approve_change(request: Request, client_id: int, job_id: int, change_id: int, _=Depends(require_auth)):
    db = SessionLocal()
    try:
        change = db.query(EditChange).filter(EditChange.id == change_id, EditChange.job_id == job_id).first()
        if not change:
            return JSONResponse({"error": "not found"}, status_code=404)
        change.status = "approved"
        db.commit()

        # Check if all changes resolved
        all_changes = db.query(EditChange).filter(EditChange.job_id == job_id).all()
        all_resolved = all(c.status in ("approved", "rejected") for c in all_changes)
        approved_count = sum(1 for c in all_changes if c.status == "approved")
        rejected_count = sum(1 for c in all_changes if c.status == "rejected")

        return JSONResponse({
            "status": "approved", "all_resolved": all_resolved,
            "approved_count": approved_count, "rejected_count": rejected_count,
            "total": len(all_changes)
        })
    finally:
        db.close()


@app.post("/api/clients/{client_id}/jobs/{job_id}/changes/{change_id}/reject")
async def reject_change(request: Request, client_id: int, job_id: int, change_id: int, _=Depends(require_auth)):
    db = SessionLocal()
    try:
        change = db.query(EditChange).filter(EditChange.id == change_id, EditChange.job_id == job_id).first()
        if not change:
            return JSONResponse({"error": "not found"}, status_code=404)
        change.status = "rejected"
        db.commit()

        all_changes = db.query(EditChange).filter(EditChange.job_id == job_id).all()
        all_resolved = all(c.status in ("approved", "rejected") for c in all_changes)
        approved_count = sum(1 for c in all_changes if c.status == "approved")
        rejected_count = sum(1 for c in all_changes if c.status == "rejected")

        return JSONResponse({
            "status": "rejected", "all_resolved": all_resolved,
            "approved_count": approved_count, "rejected_count": rejected_count,
            "total": len(all_changes)
        })
    finally:
        db.close()


@app.post("/api/clients/{client_id}/jobs/{job_id}/apply")
async def apply_approved_changes(request: Request, client_id: int, job_id: int, _=Depends(require_auth)):
    """Apply all approved changes to the client's documents."""
    db = SessionLocal()
    try:
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return JSONResponse({"error": "client not found"}, status_code=404)

        approved = db.query(EditChange).filter(
            EditChange.job_id == job_id, EditChange.status == "approved"
        ).all()

        if not approved:
            return JSONResponse({"error": "no approved changes"}, status_code=400)

        # Apply changes by field
        field_map = {
            "prompt": "prompt_content",
            "base_de_dados": "base_content",
            "prompt_geral": "general_prompt_content"
        }

        applied = 0
        for change in approved:
            attr = field_map.get(change.field)
            if not attr:
                continue
            content = getattr(client, attr, "") or ""
            if change.before_text and change.before_text.strip() in content:
                content = content.replace(change.before_text.strip(), change.after_text, 1)
                setattr(client, attr, content)
                applied += 1
            elif change.after_text and not change.before_text:
                # Pure addition
                content += "\n\n" + change.after_text
                setattr(client, attr, content)
                applied += 1

        client.updated_at = datetime.utcnow()
        db.commit()

        return JSONResponse({"applied": applied, "total_approved": len(approved)})
    finally:
        db.close()


# ============ TEST SIMULATION ============

@app.post("/api/clients/{client_id}/jobs/{job_id}/changes/{change_id}/test")
async def test_change(request: Request, client_id: int, job_id: int, change_id: int, _=Depends(require_auth)):
    """Test a specific change by simulating a chatbot conversation."""
    db = SessionLocal()
    try:
        client = db.query(Client).filter(Client.id == client_id).first()
        change = db.query(EditChange).filter(EditChange.id == change_id, EditChange.job_id == job_id).first()
        if not client or not change:
            return JSONResponse({"error": "not found"}, status_code=404)

        # Get model from request body
        try:
            body = await request.json()
            model_choice = body.get("model", "deepseek")
        except Exception:
            model_choice = "deepseek"

        from app.llm.test_simulator import run_change_test

        result = run_change_test(
            change={
                "field": change.field,
                "section": change.section,
                "before_text": change.before_text,
                "after_text": change.after_text,
                "reason": change.reason,
            },
            client_prompt=client.prompt_content or "",
            client_base=client.base_content or "",
            client_geral=client.general_prompt_content or "",
            model_choice=model_choice
        )

        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return JSONResponse({"error": str(e), "conversation": []}, status_code=500)
    finally:
        db.close()


# ============ LEGACY EDIT HISTORY ============

@app.get("/clients/{client_id}/history/{history_id}", response_class=HTMLResponse)
async def view_edit_result(request: Request, client_id: int, history_id: int, _=Depends(require_auth)):
    db = SessionLocal()
    try:
        client = db.query(Client).filter(Client.id == client_id).first()
        record = db.query(EditHistory).filter(EditHistory.id == history_id, EditHistory.client_id == client_id).first()
        if not client or not record:
            raise HTTPException(status_code=404)
        analysis = {}
        validation = {}
        try:
            analysis = json.loads(record.analysis_json) if record.analysis_json else {}
        except Exception:
            pass
        try:
            validation = json.loads(record.validation_json) if record.validation_json else {}
        except Exception:
            pass
        return templates.TemplateResponse("edit_result.html", {
            "request": request, "client": client, "record": record,
            "analysis": analysis, "validation": validation
        })
    finally:
        db.close()


# ============ CREATION PIPELINE ============

@app.get("/create", response_class=HTMLResponse)
async def creation_list(request: Request, _=Depends(require_auth)):
    db = SessionLocal()
    try:
        projects = db.query(CreationProject).order_by(CreationProject.created_at.desc()).all()
        clients = db.query(Client).order_by(Client.name).all()
        return templates.TemplateResponse("creation_list.html", {
            "request": request, "projects": projects, "clients": clients
        })
    finally:
        db.close()


@app.post("/create/new")
async def creation_new(request: Request, _=Depends(require_auth),
                       name: str = Form(...), client_id: str = Form("")):
    db = SessionLocal()
    try:
        project = CreationProject(
            name=name,
            client_id=int(client_id) if client_id else None,
            status="collecting"
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return RedirectResponse(url=f"/create/{project.id}", status_code=303)
    finally:
        db.close()


@app.get("/create/{project_id}", response_class=HTMLResponse)
async def creation_detail(request: Request, project_id: int, _=Depends(require_auth)):
    db = SessionLocal()
    try:
        project = db.query(CreationProject).filter(CreationProject.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404)
        gap_sections = []
        try:
            gap_sections = json.loads(project.gap_analysis_json) if project.gap_analysis_json else []
        except Exception:
            pass
        gap_answers = {}
        try:
            gap_answers = json.loads(project.gap_answers_json) if project.gap_answers_json else {}
        except Exception:
            pass
        return templates.TemplateResponse("creation_detail.html", {
            "request": request, "project": project,
            "gap_sections": gap_sections, "gap_answers": gap_answers
        })
    finally:
        db.close()


def _add_log(db, project, msg: str):
    """Add a log entry to the project."""
    import json as _json
    logs = []
    try:
        logs = _json.loads(project.collection_log) if project.collection_log else []
    except Exception:
        logs = []
    logs.append({"time": datetime.utcnow().strftime("%H:%M:%S"), "msg": msg})
    project.collection_log = _json.dumps(logs, ensure_ascii=False)


@app.post("/create/{project_id}/upload")
async def creation_upload(request: Request, project_id: int, _=Depends(require_auth)):
    db = SessionLocal()
    try:
        project = db.query(CreationProject).filter(CreationProject.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404)

        form = await request.form()
        files = form.getmulti("files")

        from app.creation.parsers.file_parser import parse_file
        parsed_texts = []
        upload_dir = os.path.join(BASE_DIR, "uploads", str(project_id))
        os.makedirs(upload_dir, exist_ok=True)

        for file in files:
            if not file.filename:
                continue
            filepath = os.path.join(upload_dir, file.filename)
            content = await file.read()
            with open(filepath, 'wb') as f:
                f.write(content)

            result = parse_file(filepath, file.filename)
            if result.is_whatsapp:
                project.whatsapp_text = (project.whatsapp_text or "") + "\n\n" + result.text
                _add_log(db, project, f"WhatsApp detectado em {file.filename} ({len(result.text)} chars)")
            else:
                parsed_texts.append(f"## Arquivo: {result.filename}\n\n{result.text}")
                _add_log(db, project, f"Arquivo processado: {file.filename} ({len(result.text)} chars, tipo: {result.file_type})")
                if result.warnings:
                    for w in result.warnings:
                        _add_log(db, project, f"⚠ {file.filename}: {w}")

        if parsed_texts:
            project.uploaded_files_text = (project.uploaded_files_text or "") + "\n\n".join(parsed_texts)
        project.updated_at = datetime.utcnow()
        db.commit()

        return RedirectResponse(url=f"/create/{project_id}", status_code=303)
    finally:
        db.close()


@app.post("/create/{project_id}/save-notes")
async def creation_save_notes(request: Request, project_id: int, _=Depends(require_auth),
                              user_notes: str = Form("")):
    db = SessionLocal()
    try:
        project = db.query(CreationProject).filter(CreationProject.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404)
        project.user_notes = user_notes
        project.updated_at = datetime.utcnow()
        _add_log(db, project, f"Anotacoes salvas ({len(user_notes)} chars)")
        db.commit()
        return RedirectResponse(url=f"/create/{project_id}", status_code=303)
    finally:
        db.close()


def _run_scraping(project_id: int, url: str):
    """Run web scraping in background thread."""
    import asyncio
    db = SessionLocal()
    try:
        project = db.query(CreationProject).filter(CreationProject.id == project_id).first()
        if not project:
            return
        _add_log(db, project, f"Iniciando scraping de {url}...")
        db.commit()

        from app.creation.web_scraper import scrape_website
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(scrape_website(url))
        loop.close()

        project.scraping_url = url
        project.scraping_text = result.consolidated_text
        project.updated_at = datetime.utcnow()
        _add_log(db, project, f"Scraping concluido: {result.pages_scraped} paginas, {len(result.consolidated_text)} chars")
        if result.warnings:
            for w in result.warnings:
                _add_log(db, project, f"⚠ Scraping: {w}")
        db.commit()
    except Exception as e:
        logger.error(f"Scraping failed: {e}", exc_info=True)
        try:
            _add_log(db, project, f"❌ Scraping falhou: {str(e)}")
            db.commit()
        except Exception:
            pass
    finally:
        db.close()


@app.post("/create/{project_id}/scrape")
async def creation_scrape(request: Request, project_id: int, _=Depends(require_auth),
                          url: str = Form(...)):
    db = SessionLocal()
    try:
        project = db.query(CreationProject).filter(CreationProject.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404)
        project.scraping_url = url
        db.commit()
        thread = threading.Thread(target=_run_scraping, args=(project_id, url))
        thread.start()
        return RedirectResponse(url=f"/create/{project_id}", status_code=303)
    finally:
        db.close()


@app.post("/create/{project_id}/upload-whatsapp")
async def creation_upload_whatsapp(request: Request, project_id: int, _=Depends(require_auth)):
    """Handle WhatsApp export uploads (ZIP files with conversations)."""
    db = SessionLocal()
    try:
        project = db.query(CreationProject).filter(CreationProject.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404)

        form = await request.form()
        files = form.getmulti("wa_files")

        upload_dir = os.path.join(BASE_DIR, "uploads", str(project_id), "whatsapp")
        os.makedirs(upload_dir, exist_ok=True)

        wa_texts = []
        for file in files:
            if not file.filename:
                continue
            filepath = os.path.join(upload_dir, file.filename)
            content = await file.read()
            with open(filepath, 'wb') as f:
                f.write(content)

            ext = os.path.splitext(file.filename)[1].lower()
            if ext == '.zip':
                from app.creation.parsers.whatsapp_processor import process_whatsapp_zip
                result = process_whatsapp_zip(filepath)
                wa_texts.append(result)
            elif ext == '.txt':
                from app.creation.parsers.file_parser import parse_txt
                result = parse_txt(filepath, file.filename)
                if result.is_whatsapp:
                    wa_texts.append(result.text)

        if wa_texts:
            project.whatsapp_text = (project.whatsapp_text or "") + "\n\n---\n\n".join(wa_texts)
        project.updated_at = datetime.utcnow()
        db.commit()

        return RedirectResponse(url=f"/create/{project_id}", status_code=303)
    finally:
        db.close()


@app.post("/create/{project_id}/save-onboarding")
async def creation_save_onboarding(request: Request, project_id: int, _=Depends(require_auth)):
    db = SessionLocal()
    try:
        project = db.query(CreationProject).filter(CreationProject.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404)

        form = await request.form()
        onboarding = {}
        for key in form:
            if key.startswith("onb_"):
                onboarding[key[4:]] = form[key]

        project.onboarding_data = json.dumps(onboarding, ensure_ascii=False)
        project.updated_at = datetime.utcnow()
        db.commit()

        return RedirectResponse(url=f"/create/{project_id}", status_code=303)
    finally:
        db.close()


def _consolidate_project(project: CreationProject) -> str:
    """Consolidate all collected data into a single text."""
    parts = []
    # Onboarding
    try:
        onb = json.loads(project.onboarding_data) if project.onboarding_data else {}
        if onb:
            parts.append("## DADOS DO ONBOARDING\n\n" + "\n".join(f"- **{k}**: {v}" for k, v in onb.items() if v))
    except Exception:
        pass
    # Scraping
    if project.scraping_text and project.scraping_text.strip():
        parts.append(f"## DADOS DO SITE ({project.scraping_url})\n\n{project.scraping_text[:8000]}")
    # Uploads
    if project.uploaded_files_text and project.uploaded_files_text.strip():
        parts.append(f"## DOCUMENTOS ENVIADOS\n\n{project.uploaded_files_text[:8000]}")
    # WhatsApp
    if project.whatsapp_text and project.whatsapp_text.strip():
        parts.append(f"## CONVERSAS WHATSAPP\n\n{project.whatsapp_text[:8000]}")
    return "\n\n---\n\n".join(parts) if parts else ""


def _run_gap_analysis(project_id: int):
    """Run gap analysis in background thread."""
    db = SessionLocal()
    try:
        project = db.query(CreationProject).filter(CreationProject.id == project_id).first()
        if not project:
            return
        consolidated = _consolidate_project(project)
        if not consolidated.strip():
            project.status = "collecting"
            _add_log(db, project, "❌ Nenhum dado coletado para analisar")
            db.commit()
            return

        project.consolidated_text = consolidated
        project.status = "analyzing"
        project.progress = 5
        _add_log(db, project, "Iniciando Gap Analyzer...")
        db.commit()

        from app.creation.gap_analyzer import run_gap_analysis, SECTIONS, analyze_section, _load_templates
        manual, padrao = _load_templates()

        sections_results = []
        total = len(SECTIONS)
        for i, section_def in enumerate(SECTIONS):
            project.progress = int(10 + (i / total) * 80)
            _add_log(db, project, f"Analisando secao {i+1}/{total}: {section_def['name']}...")
            db.commit()

            gap = analyze_section(section_def, consolidated, manual, padrao)
            sections_results.append(gap)

        # Deduplicate
        seen = set()
        for s in sections_results:
            unique = []
            for q in s.questions:
                norm = q.lower().strip()[:80]
                if norm not in seen:
                    seen.add(norm)
                    unique.append(q)
            s.questions = unique

        sections_data = [
            {"number": s.section_number, "name": s.section_name, "level": s.gap_level,
             "coverage": s.coverage_percent, "questions": s.questions, "reasoning": s.reasoning}
            for s in sections_results
        ]

        total_q = sum(len(s.questions) for s in sections_results)
        project.gap_analysis_json = json.dumps(sections_data, ensure_ascii=False)
        project.status = "gaps" if total_q > 0 else "ready"
        project.progress = 100
        _add_log(db, project, f"Gap Analyzer concluido: {total_q} perguntas geradas")
        db.commit()
    except Exception as e:
        logger.error(f"Gap analysis failed: {e}", exc_info=True)
        project.status = "collecting"
        _add_log(db, project, f"❌ Gap Analyzer falhou: {str(e)}")
        db.commit()
    finally:
        db.close()


@app.post("/create/{project_id}/analyze")
async def creation_analyze(request: Request, project_id: int, _=Depends(require_auth)):
    """Save all form data + run scraping + gap analysis in one go."""
    db = SessionLocal()
    try:
        project = db.query(CreationProject).filter(CreationProject.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404)

        # Save all inline form fields
        form = await request.form()

        # Save URL
        url = form.get("url", "")
        if url:
            project.scraping_url = url

        # Save notes
        notes = form.get("user_notes", "")
        if notes:
            project.user_notes = notes

        # Save onboarding fields
        onboarding = {}
        for key in form:
            if key.startswith("onb_"):
                val = form[key]
                if val:
                    onboarding[key[4:]] = val
        if onboarding:
            project.onboarding_data = json.dumps(onboarding, ensure_ascii=False)

        project.status = "analyzing"
        project.progress = 0
        db.commit()

        thread = threading.Thread(target=_run_full_analysis, args=(project_id,))
        thread.start()
        return RedirectResponse(url=f"/create/{project_id}", status_code=303)
    finally:
        db.close()


def _run_full_analysis(project_id: int):
    """Run scraping (if URL) + gap analysis in sequence."""
    import asyncio
    db = SessionLocal()
    try:
        project = db.query(CreationProject).filter(CreationProject.id == project_id).first()
        if not project:
            return

        # Step 1: Scraping (if URL provided and not already scraped)
        if project.scraping_url and not project.scraping_text:
            project.progress = 5
            _add_log(db, project, f"Iniciando scraping de {project.scraping_url}...")
            db.commit()
            try:
                from app.creation.web_scraper import scrape_website
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(scrape_website(project.scraping_url))
                loop.close()
                project.scraping_text = result.consolidated_text
                _add_log(db, project, f"Scraping OK: {result.pages_scraped} paginas, {len(result.consolidated_text)} chars")
                if result.warnings:
                    for w in result.warnings:
                        _add_log(db, project, f"⚠ Scraping: {w}")
                db.commit()
            except Exception as e:
                _add_log(db, project, f"⚠ Scraping falhou: {str(e)} - continuando sem scraping")
                db.commit()

        # Step 2: Consolidate
        project.progress = 15
        _add_log(db, project, "Consolidando dados...")
        db.commit()
        consolidated = _consolidate_project(project)
        if not consolidated.strip():
            project.status = "collecting"
            _add_log(db, project, "❌ Nenhum dado para analisar. Envie arquivos, URL ou preencha onboarding.")
            db.commit()
            return
        project.consolidated_text = consolidated

        # Step 3: Gap Analysis
        from app.creation.gap_analyzer import SECTIONS, analyze_section, _load_templates
        manual, padrao = _load_templates()

        sections_results = []
        total = len(SECTIONS)
        for i, section_def in enumerate(SECTIONS):
            project.progress = int(20 + (i / total) * 70)
            _add_log(db, project, f"Analisando {i+1}/{total}: {section_def['name']}...")
            db.commit()
            gap = analyze_section(section_def, consolidated, manual, padrao)
            sections_results.append(gap)

        # Deduplicate questions
        seen = set()
        for s in sections_results:
            unique = []
            for q in s.questions:
                norm = q.lower().strip()[:80]
                if norm not in seen:
                    seen.add(norm)
                    unique.append(q)
            s.questions = unique

        sections_data = [
            {"number": s.section_number, "name": s.section_name, "level": s.gap_level,
             "coverage": s.coverage_percent, "questions": s.questions, "reasoning": s.reasoning}
            for s in sections_results
        ]

        total_q = sum(len(s.questions) for s in sections_results)
        project.gap_analysis_json = json.dumps(sections_data, ensure_ascii=False)
        project.status = "gaps" if total_q > 0 else "ready"
        project.progress = 100
        _add_log(db, project, f"Analise concluida: {total_q} perguntas, dados consolidados: {len(consolidated)} chars")
        db.commit()
    except Exception as e:
        logger.error(f"Full analysis failed: {e}", exc_info=True)
        try:
            project.status = "collecting"
            _add_log(db, project, f"❌ Analise falhou: {str(e)}")
            db.commit()
        except Exception:
            pass
    finally:
        db.close()


@app.post("/create/{project_id}/save-gap-answers")
async def creation_save_gaps(request: Request, project_id: int, _=Depends(require_auth)):
    db = SessionLocal()
    try:
        project = db.query(CreationProject).filter(CreationProject.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404)

        form = await request.form()
        answers = {}
        for key in form:
            if key.startswith("gap_"):
                answers[key] = form[key]

        project.gap_answers_json = json.dumps(answers, ensure_ascii=False)
        project.status = "ready"
        project.updated_at = datetime.utcnow()
        db.commit()

        return RedirectResponse(url=f"/create/{project_id}", status_code=303)
    finally:
        db.close()


def _run_generation(project_id: int):
    """Run prompt generation in background thread."""
    db = SessionLocal()
    try:
        project = db.query(CreationProject).filter(CreationProject.id == project_id).first()
        if not project:
            return

        project.status = "generating"
        project.progress = 5
        _add_log(db, project, "Iniciando geracao de Prompt e Base...")
        db.commit()

        consolidated = project.consolidated_text or _consolidate_project(project)
        # Add user notes to consolidated
        if project.user_notes and project.user_notes.strip():
            consolidated += f"\n\n## ANOTACOES DO CRIADOR\n\n{project.user_notes}"

        gap_answers = ""
        try:
            answers = json.loads(project.gap_answers_json) if project.gap_answers_json else {}
            gap_answers = "\n".join(f"- {k}: {v}" for k, v in answers.items() if v)
        except Exception:
            pass

        from app.creation.prompt_generator import generate_prompt_cliente, generate_base_dados

        project.progress = 20
        _add_log(db, project, "Gerando PROMPT_CLIENTE...")
        db.commit()
        project.generated_prompt = generate_prompt_cliente(consolidated, gap_answers)

        project.progress = 60
        _add_log(db, project, "Prompt gerado. Gerando BASE_DE_DADOS...")
        db.commit()
        project.generated_base = generate_base_dados(consolidated, gap_answers)

        project.status = "completed"
        project.progress = 100
        project.updated_at = datetime.utcnow()
        _add_log(db, project, f"Geracao concluida! Prompt: {len(project.generated_prompt)} chars, Base: {len(project.generated_base)} chars")
        db.commit()

        if project.client_id:
            client = db.query(Client).filter(Client.id == project.client_id).first()
            if client:
                client.prompt_content = project.generated_prompt
                client.base_content = project.generated_base
                client.updated_at = datetime.utcnow()
                _add_log(db, project, f"Salvo automaticamente no cliente: {client.name}")
                db.commit()

    except Exception as e:
        logger.error(f"Generation failed: {e}", exc_info=True)
        project.status = "ready"
        _add_log(db, project, f"❌ Geracao falhou: {str(e)}")
        db.commit()
    finally:
        db.close()


@app.post("/create/{project_id}/generate")
async def creation_generate(request: Request, project_id: int, _=Depends(require_auth)):
    thread = threading.Thread(target=_run_generation, args=(project_id,))
    thread.start()
    return RedirectResponse(url=f"/create/{project_id}", status_code=303)


@app.get("/api/create/{project_id}/status")
async def creation_status(request: Request, project_id: int, _=Depends(require_auth)):
    db = SessionLocal()
    try:
        project = db.query(CreationProject).filter(CreationProject.id == project_id).first()
        if not project:
            return JSONResponse({"error": "not found"}, status_code=404)
        logs = []
        try:
            logs = json.loads(project.collection_log) if project.collection_log else []
        except Exception:
            pass
        return JSONResponse({
            "status": project.status,
            "progress": project.progress or 0,
            "logs": logs[-10:],  # last 10 entries
            "has_scraping": bool(project.scraping_text),
            "has_files": bool(project.uploaded_files_text),
            "has_whatsapp": bool(project.whatsapp_text),
            "has_onboarding": bool(project.onboarding_data and project.onboarding_data != "{}"),
        })
    finally:
        db.close()


@app.post("/create/{project_id}/save-to-client")
async def creation_save_to_client(request: Request, project_id: int, _=Depends(require_auth),
                                   client_id: str = Form("")):
    """Save generated prompt/base to a client."""
    db = SessionLocal()
    try:
        project = db.query(CreationProject).filter(CreationProject.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404)

        cid = int(client_id) if client_id else project.client_id
        if not cid:
            return RedirectResponse(url=f"/create/{project_id}", status_code=303)

        client = db.query(Client).filter(Client.id == cid).first()
        if client:
            if project.generated_prompt:
                client.prompt_content = project.generated_prompt
            if project.generated_base:
                client.base_content = project.generated_base
            client.updated_at = datetime.utcnow()
            db.commit()

        return RedirectResponse(url=f"/clients/{cid}", status_code=303)
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.port, reload=True)
