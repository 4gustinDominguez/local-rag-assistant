import os

import ollama
from dotenv import load_dotenv

from core.logging import setup_logger

logger = setup_logger("LLM")

# Load OLLAMA_API_KEY from .env (only needed for cloud models)
load_dotenv()

CLOUD_HOST = "https://ollama.com"


# A cloud model is identified by its name:
#   gemma4:31b-cloud  -> suffix "-cloud"
#   gemma4:cloud      -> tag "cloud"
def is_cloud_model(model: str) -> bool:
    return model.endswith("-cloud") or model.split(":")[-1] == "cloud"


def get_client(model: str) -> ollama.Client:
    """Return the right client: cloud or local server."""
    if is_cloud_model(model):
        if not os.getenv("OLLAMA_API_KEY"):
            raise RuntimeError(
                f"'{model}' is a cloud model and OLLAMA_API_KEY is missing "
                "from .env. Add it at https://ollama.com/settings/keys"
            )
        return ollama.Client(host=CLOUD_HOST)

    return ollama.Client()


def ask_llm(
    prompt: str,
    model: str,
    temperature: float = None,
    max_tokens: int = None,
) -> str:
    cloud = is_cloud_model(model)
    logger.info(f"Calling model={model} cloud={cloud}")

    options = {}
    if temperature is not None:
        options["temperature"] = temperature
    if max_tokens is not None:
        options["num_predict"] = max_tokens

    try:
        response = get_client(model).generate(
            model=model,
            prompt=prompt,
            options=options or None,
        )
    except ollama.ResponseError as exc:
        logger.error(f"LLM call failed: {exc}")
        raise RuntimeError(f"LLM call failed: {exc}") from exc

    return response.response
