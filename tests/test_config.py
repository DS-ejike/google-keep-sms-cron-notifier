from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from keep_sms_cron.config import Config


class ConfigTests(unittest.TestCase):
    def test_defaults_are_safe_for_demo(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            config = Config.from_env()

        self.assertEqual(config.keep_backend, "mock")
        self.assertTrue(config.dry_run)
        config.validate()

    def test_real_sms_requires_twilio_settings(self) -> None:
        with patch.dict(os.environ, {"DRY_RUN": "false"}, clear=True):
            config = Config.from_env()

        with self.assertRaises(ValueError):
            config.validate()


if __name__ == "__main__":
    unittest.main()

