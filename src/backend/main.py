from fastapi import FastAPI, HTTPException
from backend.models import NoveltyCheckRequest, NoveltyCheckResponse
from backend.business_logic import NoveltyChecker
from backend.logger import logger

app = FastAPI(title="Novelty Checker API")
novelty_checker = NoveltyChecker()


@app.post("/novelty-check", response_model=NoveltyCheckResponse)
async def check_novelty(request: NoveltyCheckRequest) -> NoveltyCheckResponse:
    """
    Check if a research question has been addressed in existing literature
    """
    try:
        logger.info(
            f"Received novelty check request: {request.research_question[:50]}..."
        )
        response = await novelty_checker.check_novelty(request.research_question)
        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
