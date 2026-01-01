import os
import logging
from typing import Optional

import requests

# Set up logging
logger = logging.getLogger(__name__)


def call(
	prompt: str,
	model_name: str = "gpt-4o-mini",
	system_prompt: Optional[str] = None,
	temperature: float = 0.7,
	max_tokens: Optional[int] = None,
) -> str:
	"""
	Send a chat completion request to OpenRouter and return the assistant reply.

	Args:
		prompt: User message to send to the model
		model_name: Valid OpenRouter model ID (default: mistral-7b)
		system_prompt: Optional system message to set context/behavior
		temperature: Sampling temperature 0-2 (default 0.7, lower = deterministic)
		max_tokens: Optional max tokens in response

	Returns:
		Assistant's text response

	Raises:
		ValueError: If OPENROUTER_API_KEY not set
		requests.RequestException: If API request fails
	"""
	api_key = os.environ.get("OPENROUTER_API_KEY")
	
	if not api_key:
		raise ValueError(
			"OpenRouter API key not provided. "
			"Set OPENROUTER_API_KEY environment variable."
		)

	url = "https://openrouter.ai/api/v1/chat/completions"
	headers = {
		"Authorization": f"Bearer {api_key}",
		"Content-Type": "application/json"
	}

	messages = []
	if system_prompt:
		messages.append({"role": "system", "content": system_prompt})
	messages.append({"role": "user", "content": prompt})

	payload = {
		"model": model_name,
		"messages": messages,
		"temperature": temperature,
	}
	
	if max_tokens is not None:
		payload["max_tokens"] = max_tokens
	
	logger.debug(f"Calling OpenRouter with model: {model_name}")

	try:
		resp = requests.post(url, json=payload, headers=headers, timeout=30)
		
		# Log status code and raw response for debugging
		logger.debug(f"OpenRouter response status: {resp.status_code}")
		
		# Check for HTTP errors
		if resp.status_code != 200:
			error_text = resp.text[:500]  # First 500 chars
			logger.error(f"OpenRouter HTTP error {resp.status_code}: {error_text}")
			resp.raise_for_status()
		
		# Try to parse JSON
		try:
			data = resp.json()
		except ValueError as json_err:
			# Response is not valid JSON
			raw_response = resp.text[:1000]
			logger.error(f"Invalid JSON response from OpenRouter: {raw_response}")
			raise ValueError(
				f"OpenRouter returned invalid JSON. Status: {resp.status_code}. "
				f"Response: {raw_response}"
			) from json_err
		
		# Extract assistant message from chat completion response
		if "choices" in data and len(data["choices"]) > 0:
			choice = data["choices"][0]
			if "message" in choice and "content" in choice["message"]:
				content = choice["message"]["content"]
				logger.debug(f"Successfully got response from OpenRouter")
				return content
			elif "text" in choice:
				logger.debug(f"Got text response from OpenRouter")
				return choice["text"]
		
		# Check for error in response
		if "error" in data:
			error_msg = data["error"].get("message", str(data["error"]))
			logger.error(f"OpenRouter error: {error_msg}")
			raise ValueError(f"OpenRouter error: {error_msg}")
		
		# Fallback if response structure is unexpected
		logger.error(f"Unexpected response format: {data}")
		raise ValueError(f"Unexpected OpenRouter response format: {data}")
	
	except requests.RequestException as e:
		logger.error(f"Request error: {str(e)}")
		raise requests.RequestException(f"OpenRouter API request error: {str(e)}") from e
	except (KeyError, ValueError) as e:
		logger.error(f"Response parsing error: {str(e)}")
		raise ValueError(f"Failed to parse OpenRouter response: {str(e)}") from e


if __name__ == "__main__":
	print("open_router module loaded — ready to call `call(prompt, ...)`.")
