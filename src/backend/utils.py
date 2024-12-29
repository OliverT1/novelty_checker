from braintrust import current_span, traced
from litellm import acompletion


@traced(type="llm", name="LiteLLM acompletion", notrace_io=True)
async def braintrust_acompletion(
    model: str,
    messages: list[dict],
    response_format=None,
    **kwargs,
) -> str:
    """
    Wrapper around litellm.acompletion with Braintrust tracing.
    """
    result = await acompletion(model, messages, response_format, **kwargs)
    metrics = {
        "prompt_tokens": result.usage.prompt_tokens,
        "completion_tokens": result.usage.completion_tokens,
        "total_tokens": result.usage.total_tokens,
        "estimated_cost": (
            result._hidden_params.get("response_cost", 0)
            if hasattr(result, "_hidden_params")
            else 0
        ),
    }
    print(f"Logging with kwargs: {kwargs}")
    current_span().log(
        input=messages,
        output=result.choices[0].message.content,
        metrics=metrics,
        metadata=kwargs,
    )

    return result


# @traced(type="llm", name="LiteLLM completion", notrace_io=True)
# def braintrust_completion(
#     model: str,
#     messages: list[dict],
#     response_format: Any | None = None,
#     additional_metadata: Dict[str, Any] = {},
#     **kwargs,
# ) -> str:
#     """
#     Wrapper around litellm.completion_with_metadata with Braintrust tracing.

#     Args:
#         model (str): The model to use.
#         messages (list[dict]): The messages to send to the model.
#         response_format (Any): The format of the response.
#         additional_metadata (Dict[str, Any], optional): Additional metadata to include.
#         **kwargs: Additional arguments to pass to completion_with_metadata.

#     Returns:
#         str: The content of the LLM's response.
#     """
#     additional_metadata["model"] = model
#     # Call the LitellM completion function with metadata
#     result = completion_with_metadata(
#         model=model,
#         messages=messages,
#         response_format=response_format,
#         additional_metadata=additional_metadata,
#         **kwargs,
#     )

#     # Extract metrics from the response
#     metrics = {
#         "prompt_tokens": result.usage.prompt_tokens,
#         "completion_tokens": result.usage.completion_tokens,
#         "total_tokens": result.usage.total_tokens,
#         "estimated_cost": (
#             result._hidden_params.get("response_cost", 0)
#             if hasattr(result, "_hidden_params")
#             else 0
#         ),
#     }

#     # Log the interaction with Braintrust
#     current_span().log(
#         input=messages,
#         output=result.choices[0].message.content,
#         metrics=metrics,
#         metadata=additional_metadata,
#     )

#     return result
