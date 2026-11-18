#!/usr/bin/env python3
"""Measure download speed by making ten sequential HTTP requests."""

import argparse
import math
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


REQUEST_COUNT = 10
CHUNK_SIZE = 64 * 1024


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Измеряет скорость скачивания для десяти последовательных запросов."
    )
    parser.add_argument("url", help="Адрес ресурса, который нужно скачать")
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Таймаут одного запроса в секундах, по умолчанию: 30",
    )
    return parser.parse_args()


def validate_url(url: str) -> None:
    parsed_url = urlsplit(url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise ValueError("URL должен начинаться с http:// или https://")


def download_once(url: str, timeout: float) -> tuple[float, int]:
    request = Request(url, headers={"User-Agent": "internet-speed-test/1.0"})
    started_at = time.perf_counter()
    downloaded_bytes = 0

    with urlopen(request, timeout=timeout) as response:
        while chunk := response.read(CHUNK_SIZE):
            downloaded_bytes += len(chunk)

    elapsed_seconds = time.perf_counter() - started_at
    return elapsed_seconds, downloaded_bytes


def format_mib(byte_count: int) -> float:
    return byte_count / (1024 * 1024)


def main() -> int:
    args = parse_args()

    try:
        validate_url(args.url)
        if not math.isfinite(args.timeout) or args.timeout <= 0:
            raise ValueError("Таймаут должен быть больше нуля")
    except ValueError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 2

    total_bytes = 0
    total_elapsed_seconds = 0.0

    print(f"Запускаю {REQUEST_COUNT} последовательных запросов к {args.url}")

    try:
        for request_number in range(1, REQUEST_COUNT + 1):
            elapsed_seconds, downloaded_bytes = download_once(args.url, args.timeout)
            total_bytes += downloaded_bytes
            total_elapsed_seconds += elapsed_seconds
            print(
                f"Запрос {request_number:2d}/{REQUEST_COUNT}: "
                f"{elapsed_seconds:.3f} с, {format_mib(downloaded_bytes):.2f} MiB"
            )
    except (HTTPError, URLError, TimeoutError, OSError) as error:
        print(f"Ошибка запроса: {error}", file=sys.stderr)
        return 1

    average_elapsed_seconds = total_elapsed_seconds / REQUEST_COUNT
    average_speed_mib_per_second = format_mib(total_bytes) / total_elapsed_seconds

    print("\nРезультат:")
    print(f"Среднее время запроса: {average_elapsed_seconds:.3f} с")
    print(f"Скачано всего: {format_mib(total_bytes):.2f} MiB")
    print(f"Средняя скорость скачивания: {average_speed_mib_per_second:.2f} MiB/s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
