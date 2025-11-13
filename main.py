"""
FastAPI entry point for ISA GetKeywords Service
Designed to be triggered by Cloud Scheduler
"""
from fastapi import FastAPI
from src.batch_generate_keywords import main as run_batch_job
from dotenv import load_dotenv

# Load environment variables for local development
load_dotenv()

app = FastAPI(
    title="ISA GetKeywords Service",
    description="Microservice to generate Hebrew keywords for stocks and finance industry using Gemini AI",
    version="1.0.1"
)


@app.get("/")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "isa-getkeywords-service",
        "version": "1.0.1"
    }


@app.post("/")
async def run_job():
    """
    Main endpoint to trigger keyword generation job.
    Designed to be called by Cloud Scheduler.

    Returns:
        Status response indicating job completion
    """
    try:
        print("Job triggered by Cloud Scheduler.")
        await run_batch_job()
        print("Job finished successfully.")
        return {"status": "OK"}
    except Exception as e:
        print(f"An error occurred during job execution: {e}")
        return {"status": "Error", "message": str(e)}, 500


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
