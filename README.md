# fastapi-streamresponse

Simple demo how Stream Response should work with [FastAPI](https://fastapi.tiangolo.com/)

Key features

- New line delimited json: https://ndjson.org/
- [StreamResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- With [response model](https://fastapi.tiangolo.com/tutorial/response-model/)

## How to run

Install the reqs:

```cmd
pip install -r requirements.txt
```

Run the server:

```cmd
uvicorn main:app --reload
```

## Read the stream

For example with curl

```cmd
curl --raw "http://localhost:8000"
```
