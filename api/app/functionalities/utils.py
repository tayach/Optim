from flask import current_app, has_app_context
from langchain_openai import ChatOpenAI
import os
import json


DEFAULT_MODEL_FALLBACK = "gpt-4o-mini"


def _resolve_model(override: str | None, config_key: str) -> str:
    if override:
        return override

    if has_app_context():
        configured = current_app.config.get(config_key)
        if configured:
            return configured

        fallback = current_app.config.get("OPENAI_DEFAULT_MODEL")
        if fallback:
            return fallback

    return DEFAULT_MODEL_FALLBACK


def get_structured_model(override: str | None = None) -> str:
    return _resolve_model(override, "OPENAI_STRUCTURED_MODEL")


def get_chat_model(override: str | None = None) -> str:
    return _resolve_model(override, "OPENAI_DEFAULT_MODEL")


class StructuredLLM:

    def __init__(
        self,
        schema,
        llm,
        structuring_model: str | None = None,
    ):
        self.schema = schema
        self.structuring_model = get_structured_model(structuring_model)
        self.schema_json = json.dumps(schema.schema(), indent=2)
        self.llm = llm
        self.structured_llm = ChatOpenAI(
            model=self.structuring_model
        ).with_structured_output(schema)

    def invoke(self, prompt):
        full_prompt = (
            prompt
            + "\n\n Your response must be in JSON format compatible with the following python object class schema:"
            + self.schema_json
        )

        print("full_prompt", full_prompt)

        initial_response = self.llm.invoke(full_prompt).content

        print("\n\n\ninitial_response", initial_response)

        structuring_prompt = "Given the following data, format it with the given response format: {initial_response}".format(
            initial_response=initial_response
        )

        print("structuring_prompt", structuring_prompt)

        structured_response = self.structured_llm.invoke(structuring_prompt)
        print("structured_response", structured_response)
        return structured_response


def get_structured_llm(schema, model: str | None = None):
    resolved_model = get_structured_model(model)

    print(f"[LLM] Using structured model: {resolved_model}")

    if resolved_model in ["gpt-4o", "gpt-4o-mini"]:
        return ChatOpenAI(model=resolved_model).with_structured_output(schema)
    elif resolved_model in ["o1-mini", "o1-preview"]:
        llm = ChatOpenAI(model=resolved_model, temperature=1.0)
        return StructuredLLM(schema, llm)
    elif resolved_model in [
        "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
    ]:
        api_key = os.environ.get("TOGETHER_API_KEY")
        if not api_key:
            raise ValueError("TOGETHER_API_KEY is not set")
        llm = ChatOpenAI(
            base_url="https://api.together.xyz/v1",
            api_key=api_key,
            model=resolved_model,
        )
        return StructuredLLM(schema, llm)
    else:
        raise ValueError(f"Model {resolved_model} not supported")
