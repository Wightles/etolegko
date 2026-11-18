import io
import sys
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import download_speed


class FakeResponse:
    def __init__(self, chunks):
        self._chunks = iter(chunks)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self, _size):
        return next(self._chunks)


class DownloadSpeedTests(unittest.TestCase):
    def test_download_once_reads_response_until_end(self):
        response = FakeResponse([b"abc", b"defgh", b""])

        with patch.object(download_speed, "urlopen", return_value=response) as urlopen:
            elapsed_seconds, downloaded_bytes = download_speed.download_once(
                "https://example.test/file.bin", 5
            )

        self.assertGreaterEqual(elapsed_seconds, 0)
        self.assertEqual(downloaded_bytes, 8)
        urlopen.assert_called_once()
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 5)

    def test_main_makes_ten_requests(self):
        results = [(0.2, 1024)] * download_speed.REQUEST_COUNT
        output = io.StringIO()

        with patch.object(download_speed, "download_once", side_effect=results) as download:
            with patch.object(
                sys,
                "argv",
                ["download_speed.py", "https://example.test/file.bin"],
            ):
                with redirect_stdout(output):
                    exit_code = download_speed.main()

        self.assertEqual(exit_code, 0)
        self.assertEqual(download.call_count, download_speed.REQUEST_COUNT)
        self.assertIn("Среднее время запроса: 0.200 с", output.getvalue())
        self.assertIn("Скачано всего: 0.01 MiB", output.getvalue())

    def test_main_rejects_invalid_url(self):
        with patch.object(download_speed, "urlopen") as urlopen:
            with patch.object(sys, "argv", ["download_speed.py", "ftp://example.test"]):
                exit_code = download_speed.main()

        self.assertEqual(exit_code, 2)
        urlopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
