import asyncio

from config import Config
from telegram_factory import TelegramClientFactory
import re
import logging

logger = logging.getLogger(__name__)

async def handle_message(client, event, condition_func):
    logger.info("Checking conditions")
    if await condition_func(event.message):
        try:
            # Check if client is authorized before processing using factory method
            if not await TelegramClientFactory.check_authorization(client):
                logger.error("Cannot process message - client not authorized")
                return
            
            # First, check if the message has a button and click it
            if event.message.buttons:
                logger.info("Found buttons in message, preparing to click 'Забрать заказ'")
                try:
                    # Random delay before clicking
                    #delay = random.uniform(0.0, 0.1)
                    #logger.info(f"Waiting {delay:.2f} seconds before clicking...")
                    #await asyncio.sleep(delay)

                    await event.message.click(text="Забрать заказ")
                    logger.info("Successfully clicked button")
                    # Add a small delay to ensure the button click is processed
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"Error clicking button: {str(e)}")
            else:
                logger.info("No buttons found in message")

            # Then proceed with forwarding
            logger.info("Starting message forwarding")
            target_entity = await client.get_input_entity(Config.TARGET_USER_NICKNAME)
            await client.forward_messages(target_entity, event.message)
            logger.info("Message forwarded successfully!")

        except Exception as e:
            logger.error(f"Error in message handling: {str(e)}")

    logger.info("Message processing completed.")

async def text_contains_test(message):
    logger.info("Checking message: " + message.text)
    logger.info(f"DEBUG: Message length is {len(message.text)} characters.")

    # Check if the message contains excluded keywords
    excluded_keywords = await Config.get_excluded_keywords()
    for keyword in excluded_keywords:
        if keyword.strip() and keyword.strip().lower() in message.text.lower():
            logger.warning(f"Message contains excluded keyword: {keyword}")
            return False

    # Check the summ of order
    match1 = re.search(r"\*\*Сумма заказа:\*\*\s*(\d+)", message.text)
    match2 = re.search(r"Сумма заказа:\s*(\d+)", message.text)

    if match1:
        order_amount = int(match1.group(1))
        return order_amount > Config.ORDER_AMOUNT_THRESHOLD
    if match2:
        order_amount = int(match2.group(1))
        return order_amount > Config.ORDER_AMOUNT_THRESHOLD
    else:
        logger.info("Message does not contain order amount")
        return False
