from uuid import uuid4
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse




from backend.database import (
    DatabaseError,
    get_analysis,
    update_alert_status,
)
from backend.ingestion import IngestionError
from backend.schemas import (
    ErrorResponse,
    UpdateAlertRequest,
    UploadResponse,
)
from backend.service import run_analysis


app = FastAPI(title="AMLens API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post(
    "/api/analyses",
    response_model=UploadResponse,
    status_code=201,
)
async def create_analysis(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=415,
            detail={
                "error": {
                    "code": "UNSUPPORTED_FILE",
                    "message": "A CSV file is required",
                    "row": None,
                    "field": None,
                }
            },
        )

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=415,
            detail={
                "error": {
                    "code": "UNSUPPORTED_FILE",
                    "message": "Only CSV files are supported",
                    "row": None,
                    "field": None,
                }
            },
        )

    content = await file.read()

    try:
        analysis_id = f"analysis-{uuid4().hex[:12]}"

        run_analysis(
            analysis_id=analysis_id,
            content=content,
        )

        return UploadResponse(
            analysis_id=analysis_id,
            status="COMPLETED",
            result_url=f"/api/analyses/{analysis_id}",
        )

    except IngestionError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "row": exc.row,
                    "field": exc.field,
                }
            },
        )

    except DatabaseError:
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "STORAGE_UNAVAILABLE",
                    "message": "Storage is temporarily unavailable",
                    "row": None,
                    "field": None,
                }
            },
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "ANALYSIS_FAILED",
                    "message": "Analysis failed",
                    "row": None,
                    "field": None,
                }
            },
        )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": str(exc.detail),
                "row": None,
                "field": None,
            }
        },
    )


@app.get("/api/analyses/{analysis_id}")
def read_analysis(analysis_id: str):
    try:
        result = get_analysis(analysis_id)

    except DatabaseError:
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "STORAGE_UNAVAILABLE",
                    "message": "Storage is temporarily unavailable",
                    "row": None,
                    "field": None,
                }
            },
        )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Analysis not found",
                    "row": None,
                    "field": None,
                }
            },
        )

    return result


@app.patch(
    "/api/analyses/{analysis_id}/alerts/{alert_id}"
)
def update_alert(
    analysis_id: str,
    alert_id: str,
    request: UpdateAlertRequest,
):
    try:
        updated = update_alert_status(
            analysis_id=analysis_id,
            alert_id=alert_id,
            status=request.status,
        )

    except DatabaseError:
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "STORAGE_UNAVAILABLE",
                    "message": "Storage is temporarily unavailable",
                    "row": None,
                    "field": None,
                }
            },
        )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Alert not found",
                    "row": None,
                    "field": None,
                }
            },
        )

    return {
        "id": alert_id,
        "analysis_id": analysis_id,
        "status": updated["status"],
        "updated_at": updated["updated_at"],
    }