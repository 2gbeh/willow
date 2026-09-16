# Willow

⚠️ **WIP :** RunPod Serverless Endpoint — AI image generation using [FLUX.1-dev](https://huggingface.co/black-forest-labs/FLUX.1-dev)

## Overview

Willow is a serverless worker that generates images from text prompts using Black Forest Labs' FLUX.1-dev model, deployed on RunPod's serverless GPU platform.

- **Base image:** `python:3.10-slim`
- **Runtime:** RunPod Serverless SDK (`runpod==1.7.12`)
- **Model:** FLUX.1-dev (Hugging Face)

## Project Structure

```
willow/
├── rp_handler.py       # Serverless request handler
├── requirements.txt    # Python dependencies
├── test_input.json     # Local test payload
├── Dockerfile
├── .dockerignore
└── README.md
```

## Setup

### Prerequisites

- Docker
- RunPod account + API key
- Hugging Face access token (for model download)

### Local Development

Clone the repo:

```sh
git clone https://github.com/2gbeh/willow.git
cd willow
```

Install dependencies locally (optional, for non-Docker testing):

```sh
pip install -r requirements.txt
```

### Build the Docker image

```sh
docker build --provenance=false --sbom=false -t willow:local .
```

### Run locally

The RunPod SDK automatically picks up `test_input.json` when run without an API server:

```sh
docker run --rm willow:local
```

## Deployment

1. Tag and push the image to Docker Hub:

   ```sh
   docker tag willow:local 2gbeh/runpod:latest
   docker push 2gbeh/runpod:latest
   ```

2. On the [RunPod Console](https://www.runpod.io/console/serverless), create a new Serverless Endpoint pointing to `2gbeh/runpod:latest`.
3. Set required environment variables (see below).
4. Deploy and note the generated endpoint URL + API key.

## Environment Variables

| Variable   | Description                                  | Default |
| ---------- | -------------------------------------------- | ------- |
| `HF_TOKEN` | Hugging Face access token for model download | —       |

## API

### Input

```json
{
  "input": {
    "prompt": "a red fox sitting in a snowy forest, cinematic lighting",
    "width": 1024,
    "height": 1024,
    "num_inference_steps": 28
  }
}
```

### Output

```json
{
  "output": {
    "image": "<base64-encoded PNG>"
  }
}
```

### Testing the deployed endpoint

```sh
curl -X POST https://api.runpod.ai/v2/<endpoint-id>/runsync \
  -H "Authorization: Bearer <RUNPOD_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"input": {"prompt": "a red fox in a snowy forest"}}'
```

## Notes

- Requires GPU runtime — FLUX.1-dev is compute-heavy and not runnable on CPU-only local builds.
- Local Docker builds without a GPU are for handler/logic testing only, not full image generation.

## License

MIT
