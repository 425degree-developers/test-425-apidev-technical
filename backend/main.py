## paths and credentials related
import os
from pathlib import Path
from dotenv import load_dotenv

## main packages
from fastapi import Body, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from linebot import *
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import logging
import uvicorn

### loading credentials
try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass
ENV_PATH = "."  ### for .py use; project-based .env
LOG_PATH = "./.logs/"
CRED_PATH = "./.credentials"
env_path = Path(ENV_PATH) / ".env"
load_dotenv(dotenv_path=env_path)

## -------- Line App Setup --------
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
line_channel_name = os.getenv("LINE_CHANNEL_NAME", "test-425-apidev-technical")
log_replies_db_name = f"log_replies_{line_channel_name}"

## Line Stickers shorthand
BEAR_BOWING = {"package_id": "11537", "sticker_id": "52002739"}

## -------- Fast API's --------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

## Example from https://github.com/line/line-bot-sdk-python
@app.post("/callback")
async def line_callback(request: Request):
    """
    Main webhook url: For receiving line's messages
    """
    ## Safe guard
    body = await request.body()
    signature = request.headers["x-line-signature"]
    try:
        handler.handle(body.decode(), signature)
    except InvalidSignatureError:
        raise InvalidSignatureError("Invalid signature. Please check your channel access token/channel secret.")

    data = await request.json()
    events = data['events']

    ## Data Validation
    if len(events) != 1:
        logging.info("line_callback() -> len(events) != 1")
        logging.info("line_callback() -> data:", data)
        return
    
    print(data) ## or: logging.info(data)
    reply_token = events[0]['replyToken']
    ## TODO:
    # 1. create CRUD operation for each `data` recieve from line
    # 2. insert those "data element" to Database
    try:
        line_bot_api.reply_message(reply_token, StickerSendMessage(**BEAR_BOWING))
    except Exception as e:
        logging.exception(e)
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    return "OK"

@app.post("/line-push-message-api")
async def line_push_message_api(
    body: dict = Body(..., description="{'text': ...}")
    ):
    """
    Push message to customer line chat

    Request format
    --------
    body: {"to": ..., "text": ...}
    """
    to = body.get("to")
    text = body.get("text")
    if not to or not text:
        logging.error(body)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f'expecting body={{"to": ..., "text": ...}} but got {body}')
    try:
        print(body)## or: logging.info(body)
        ## TODO:
        # 1. create CRUD operation for each `body` sent to line
        # 2. insert those "body element" to Database
        line_bot_api.push_message(to, TextSendMessage(text=text))
    except Exception as e:
        raise e
        
if __name__ == "__main__":
    uvicorn.run(
        f"{__file__.replace('.py', '').rpartition('/')[-1]}:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
