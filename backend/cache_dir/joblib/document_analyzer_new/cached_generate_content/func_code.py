# first line: 259
@memory.cache
def cached_generate_content(prompt):
    logger.info("Calling Gemini API (cached_generate_content)")
    
    try:
        prompt_str = _ensure_str(prompt)
        logger.info("Sending request to Gemini model...")
        response = gemini_model.generate_content(prompt_str)
        logger.info("Received response from Gemini model")
        
        result = response.text if response.text else ""
        return result
    except Exception as e:
        logger.error(f"Error in cached_generate_content: {str(e)}", exc_info=True)
        raise
