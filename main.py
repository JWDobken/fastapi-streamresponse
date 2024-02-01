import json
import random
import time
from typing import List, Type, Union

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, create_model
from starlette.types import Send


class JsonStreamingResponse(StreamingResponse):
    async def stream_response(self, send: Send) -> None:
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self.raw_headers,
            }
        )
        chunk: BaseModel
        async for chunk in self.body_iterator:
            chunk = json.dumps(chunk.model_dump()) + "\n"
            if not isinstance(chunk, bytes):
                chunk = chunk.encode(self.charset)
            await send({"type": "http.response.body", "body": chunk, "more_body": True})
        await send({"type": "http.response.body", "body": b"", "more_body": False})


app = FastAPI()


class Item(BaseModel):
    name: str
    age: int


class Status(BaseModel):
    status: str


def generate_ndjson():
    data = [
        Item(name="Jane", age=25),
        Item(name="Bob", age=35),
        Status(status="process A"),
    ]
    try:
        for item in data:
            time.sleep(random.uniform(0.8, 1.7))
            yield item
    except:
        yield Status(status="Something is wrong")
    finally:
        time.sleep(random.uniform(0.8, 1.7))
        yield Status(status="done")


@app.get("/", response_model=Union[Item, Status])
def get_ndjson_stream():
    return JsonStreamingResponse(
        generate_ndjson(),
        media_type="application/x-ndjson",
    )
