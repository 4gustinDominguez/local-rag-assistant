import pytest

from llm import is_cloud_model


@pytest.mark.parametrize("model", [
    "gemma4:31b-cloud",
    "gemma4:cloud",
    "gemma4:12b-cloud",
])
def test_cloud_models_are_detected(model):
    assert is_cloud_model(model) is True


@pytest.mark.parametrize("model", [
    "llama3.2:latest",
    "qwen2.5:7b",
    "gemma4:12b",
    "mistral:latest",
])
def test_local_models_are_detected(model):
    assert is_cloud_model(model) is False
