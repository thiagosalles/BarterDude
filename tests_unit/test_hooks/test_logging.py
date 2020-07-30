import logging
from asynctest import TestCase, Mock, patch
from barterdude.hooks import logging as hook_log
from barterdude.conf import BARTERDUDE_DEFAULT_APP_NAME


class TestLogging(TestCase):
    maxDiff = None

    def setUp(self):
        self.message = Mock()
        self.logging = hook_log.Logging()

    async def test_should_access_default_logger(self):
        log = hook_log.Logging("my_log", logging.DEBUG)
        logger = log.logger
        self.assertEqual(
            type(logger),
            logging.Logger
        )
        self.assertEqual(
            type(logger.handlers[0]),
            logging.StreamHandler
        )
        self.assertEqual(
            logger.name, f"{BARTERDUDE_DEFAULT_APP_NAME}.my_log")
        self.assertEqual(logger.level, logging.DEBUG)

    @patch("barterdude.hooks.logging.Logging.logger")
    @patch("barterdude.hooks.logging.format_tb")
    async def test_should_log_on_connection_fail(
        self, format_tb, logger
    ):
        retries = Mock()
        exception = Exception()
        await self.logging.on_connection_fail(exception, retries)
        format_tb.assert_called_once_with(exception.__traceback__)
        logger.error.assert_called_once_with({
            "message": "Failed to connect to the broker",
            "retries": retries,
            "exception": repr(exception),
            "traceback": format_tb.return_value,
        })


class TestLoggingNotRedacted(TestCase):
    maxDiff = None

    def setUp(self):
        hook_log.BARTERDUDE_LOG_REDACTED = False
        self.message = Mock()
        self.logging = hook_log.Logging()

    @patch("barterdude.hooks.logging.Logging.logger")
    @patch("barterdude.hooks.logging.json.dumps")
    async def test_should_log_before_consume(self, dumps, logger):
        await self.logging.before_consume(self.message)
        dumps.assert_called_once_with(self.message.body)
        logger.info.assert_called_once_with({
            "message": "Before consume message",
            "delivery_tag": self.message.delivery_tag,
            "message_body": dumps.return_value,
        })

    @patch("barterdude.hooks.logging.Logging.logger")
    @patch("barterdude.hooks.logging.json.dumps")
    async def test_should_log_on_success(self, dumps, logger):
        await self.logging.on_success(self.message)
        dumps.assert_called_once_with(self.message.body)
        logger.info.assert_called_once_with({
            "message": "Successfully consumed message",
            "delivery_tag": self.message.delivery_tag,
            "message_body": dumps.return_value,
        })

    @patch("barterdude.hooks.logging.Logging.logger")
    @patch("barterdude.hooks.logging.json.dumps")
    @patch("barterdude.hooks.logging.format_tb")
    async def test_should_log_on_fail(self, format_tb, dumps, logger):
        exception = Exception()
        await self.logging.on_fail(self.message, exception)
        dumps.assert_called_once_with(self.message.body)
        format_tb.assert_called_once_with(exception.__traceback__)
        logger.error.assert_called_once_with({
            "message": "Failed to consume message",
            "delivery_tag": self.message.delivery_tag,
            "message_body": dumps.return_value,
            "exception": repr(exception),
            "traceback": format_tb.return_value,
        })


class TestLoggingRedacted(TestCase):
    maxDiff = None

    def setUp(self):
        hook_log.BARTERDUDE_LOG_REDACTED = True
        self.message = Mock()
        self.logging = hook_log.Logging()

    @patch("barterdude.hooks.logging.Logging.logger")
    @patch("barterdude.hooks.logging.json.dumps")
    async def test_should_log_before_consume(self, dumps, logger):
        await self.logging.before_consume(self.message)
        dumps.assert_not_called()
        logger.info.assert_called_once_with({
            "message": "Before consume message",
            "delivery_tag": self.message.delivery_tag
        })

    @patch("barterdude.hooks.logging.Logging.logger")
    @patch("barterdude.hooks.logging.json.dumps")
    async def test_should_log_on_success(self, dumps, logger):
        await self.logging.on_success(self.message)
        dumps.assert_not_called()
        logger.info.assert_called_once_with({
            "message": "Successfully consumed message",
            "delivery_tag": self.message.delivery_tag
        })

    @patch("barterdude.hooks.logging.Logging.logger")
    @patch("barterdude.hooks.logging.json.dumps")
    @patch("barterdude.hooks.logging.format_tb")
    async def test_should_log_on_fail(self, format_tb, dumps, logger):
        exception = Exception()
        await self.logging.on_fail(self.message, exception)
        dumps.assert_not_called()
        format_tb.assert_called_once_with(exception.__traceback__)
        logger.error.assert_called_once_with({
            "message": "Failed to consume message",
            "delivery_tag": self.message.delivery_tag,
            "exception": repr(exception),
            "traceback": format_tb.return_value,
        })
