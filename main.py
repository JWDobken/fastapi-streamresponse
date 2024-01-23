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
            chunk = json.dumps({chunk.__class__.__name__.lower(): chunk.model_dump()}) + "\n"
            if not isinstance(chunk, bytes):
                chunk = chunk.encode(self.charset)
            await send({"type": "http.response.body", "body": chunk, "more_body": True})
        await send({"type": "http.response.body", "body": b"", "more_body": False})


def union_response_models(base_models: List[Type[BaseModel]]) -> Type[BaseModel]:
    response_models = [create_model(f"Response{m.__name__}", **{m.__name__.lower(): (m, ...)}) for m in base_models]
    return Union[tuple(response_models)]


app = FastAPI()


class Item(BaseModel):
    name: str
    age: int


class Status(BaseModel):
    text: str


def generate_ndjson():
    data = [
        Item(name="Jane", age=25),
        Item(name="Bob", age=35),
        Status(text="process A"),
    ]
    try:
        for item in data:
            time.sleep(random.uniform(0.8, 1.7))
            yield item
    except:
        yield Status(text="Something is wrong")
    finally:
        time.sleep(random.uniform(0.8, 1.7))
        yield Status(text="done")


@app.get("/", response_model=union_response_models([Item, Status]))
def get_ndjson_stream():
    return JsonStreamingResponse(
        generate_ndjson(),
        media_type="application/x-ndjson",
    )
