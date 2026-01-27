"""
Gemini SDK helper utilities.
"""
from __future__ import annotations

import asyncio
from typing import Iterable, Optional, Sequence


DEFAULT_GEMINI_FALLBACK_MODELS: Sequence[str] = (
    "gemini-2.0-flash",
    "gemini-1.5-flash",
)


def build_model_candidates(preferred: Optional[str]) -> list[str]:
    """Return ordered, de-duplicated model candidates."""
    candidates: list[str] = []
    if preferred:
        candidates.append(preferred)
    for model in DEFAULT_GEMINI_FALLBACK_MODELS:
        if model not in candidates:
            candidates.append(model)
    return candidates


def is_model_not_found_error(err: Exception) -> bool:
    """Best-effort detection for invalid Gemini model errors."""
    status_code = getattr(err, "status_code", None)
    if status_code == 404:
        return True
    message = str(err)
    return "NOT_FOUND" in message or "not found" in message or "is not found" in message


async def generate_content_with_fallback(
    *,
    client,
    model: str,
    contents: str,
    config: Optional[dict] = None,
    logger=None,
) -> object:
    """Call generate_content with model fallback and config/no-config retry."""
    loop = asyncio.get_event_loop()
    last_error: Optional[Exception] = None
    for candidate in build_model_candidates(model):
        try:
            if logger and candidate != model:
                logger.warning(f"GEMINI_MODEL fallback 사용: {candidate}")
            if config is None:
                return await loop.run_in_executor(
                    None,
                    lambda: client.models.generate_content(
                        model=candidate,
                        contents=contents,
                    ),
                )
            try:
                return await loop.run_in_executor(
                    None,
                    lambda: client.models.generate_content(
                        model=candidate,
                        contents=contents,
                        config=config,
                    ),
                )
            except TypeError as type_error:
                # 일부 SDK 버전은 config 파라미터를 지원하지 않음
                if logger:
                    logger.warning(f"config 파라미터 미지원, 일반 모드로 재시도: {type_error}")
                return await loop.run_in_executor(
                    None,
                    lambda: client.models.generate_content(
                        model=candidate,
                        contents=contents,
                    ),
                )
        except Exception as err:
            last_error = err
            if is_model_not_found_error(err):
                continue
            raise
    if last_error:
        raise last_error
    raise RuntimeError("Gemini API 호출 실패: 모델 후보가 비어 있습니다.")


async def generate_content_stream_with_fallback(
    *,
    client,
    model: str,
    contents: str,
    config: Optional[dict] = None,
    logger=None,
) -> Iterable:
    """Call generate_content_stream with model fallback and config/no-config retry."""
    loop = asyncio.get_event_loop()
    last_error: Optional[Exception] = None
    for candidate in build_model_candidates(model):
        try:
            if logger and candidate != model:
                logger.warning(f"GEMINI_MODEL fallback 사용: {candidate}")
            if config is None:
                return await loop.run_in_executor(
                    None,
                    lambda: client.models.generate_content_stream(
                        model=candidate,
                        contents=contents,
                    ),
                )
            try:
                return await loop.run_in_executor(
                    None,
                    lambda: client.models.generate_content_stream(
                        model=candidate,
                        contents=contents,
                        config=config,
                    ),
                )
            except TypeError as type_error:
                if logger:
                    logger.warning(f"config 파라미터 미지원, 일반 모드로 재시도: {type_error}")
                return await loop.run_in_executor(
                    None,
                    lambda: client.models.generate_content_stream(
                        model=candidate,
                        contents=contents,
                    ),
                )
        except Exception as err:
            last_error = err
            if is_model_not_found_error(err):
                continue
            raise
    if last_error:
        raise last_error
    raise RuntimeError("Gemini API 스트리밍 호출 실패: 모델 후보가 비어 있습니다.")
