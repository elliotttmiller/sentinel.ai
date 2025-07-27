from fastapi import APIRouter
from loguru import logger

router = APIRouter(prefix="/genai", tags=["GenAI"])

@router.get("/status")
async def get_genai_status():
    """Get the status of Google GenAI integration."""
    try:
        from main import llm_client
        model_info = llm_client.get_model_info()
        return {"success": True, "genai_status": model_info}
    except Exception as e:
        logger.error(f"GenAI status check failed: {e}")
        return {"success": False, "error": str(e)}

@router.post("/test")
async def test_genai():
    """Test Google GenAI integration with a simple prompt."""
    try:
        from main import llm_client
        test_prompt = "Hello! Can you tell me about your capabilities?"
        response = await llm_client.generate_response(test_prompt)
        return {
            "message": "GenAI test completed successfully",
            "prompt": test_prompt,
            "response": response,
            "success": True
        }
    except Exception as e:
        logger.error(f"GenAI test failed: {e}")
        return {
            "message": "GenAI test failed",
            "error": str(e),
            "success": False
        } 