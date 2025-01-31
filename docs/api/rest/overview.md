# REST API Reference

## Overview

The Vortx Synthetic Satellite REST API provides HTTP endpoints for interacting with the system. The API follows RESTful principles and uses JSON for request and response payloads.

## Base URL

```
https://api.vortx.ai/v1
```

## Authentication

All API requests require authentication using an API key. Include your API key in the request header:

```http
Authorization: Bearer your-api-key
```

## Endpoints

### Memory Formation

#### Create Memory
```http
POST /memories
Content-Type: application/json
Authorization: Bearer your-api-key

{
    "location": {
        "lat": 37.7749,
        "lon": -122.4194
    },
    "time_range": {
        "start": "2020-01-01",
        "end": "2024-01-01"
    },
    "modalities": ["satellite", "climate", "social"]
}
```

Response:
```json
{
    "memory_id": "mem_123abc",
    "status": "processing",
    "estimated_completion": "2024-01-20T15:30:00Z"
}
```

#### Get Memory Status
```http
GET /memories/{memory_id}
Authorization: Bearer your-api-key
```

Response:
```json
{
    "memory_id": "mem_123abc",
    "status": "completed",
    "created_at": "2024-01-20T15:00:00Z",
    "completed_at": "2024-01-20T15:30:00Z",
    "metadata": {
        "location": {
            "lat": 37.7749,
            "lon": -122.4194
        },
        "time_range": {
            "start": "2020-01-01",
            "end": "2024-01-01"
        },
        "modalities": ["satellite", "climate", "social"]
    }
}
```

### Synthetic Data Generation

#### Generate Data
```http
POST /synthetic
Content-Type: application/json
Authorization: Bearer your-api-key

{
    "base_location": {
        "lat": 37.7749,
        "lon": -122.4194
    },
    "scenario": "urban_development",
    "time_steps": 10,
    "climate_factors": true
}
```

Response:
```json
{
    "job_id": "job_456def",
    "status": "processing",
    "estimated_completion": "2024-01-20T16:00:00Z"
}
```

#### Get Generation Status
```http
GET /synthetic/{job_id}
Authorization: Bearer your-api-key
```

Response:
```json
{
    "job_id": "job_456def",
    "status": "completed",
    "created_at": "2024-01-20T15:30:00Z",
    "completed_at": "2024-01-20T16:00:00Z",
    "results_url": "https://storage.vortx.ai/synthetic/job_456def.zip"
}
```

### Inference

#### Run Inference
```http
POST /inference
Content-Type: application/json
Authorization: Bearer your-api-key

{
    "query": "Analyze urban development patterns and environmental impact",
    "context": {
        "memory_id": "mem_123abc",
        "synthetic_data_id": "job_456def"
    },
    "models": ["reasoning", "vision"]
}
```

Response:
```json
{
    "inference_id": "inf_789ghi",
    "status": "processing",
    "estimated_completion": "2024-01-20T16:15:00Z"
}
```

## Error Handling

The API uses standard HTTP response codes:

- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error

Error Response Format:
```json
{
    "error": {
        "code": "invalid_request",
        "message": "Invalid location coordinates",
        "details": {
            "field": "location.lat",
            "reason": "Must be between -90 and 90"
        }
    }
}
```

## Rate Limits

- 100 requests per minute per API key
- 1000 requests per hour per API key
- Larger limits available for enterprise plans

## Webhooks

Configure webhooks to receive real-time updates:

```http
POST /webhooks
Content-Type: application/json
Authorization: Bearer your-api-key

{
    "url": "https://your-server.com/webhook",
    "events": ["memory.completed", "synthetic.completed", "inference.completed"],
    "secret": "your-webhook-secret"
}
```

## SDKs

Official SDKs are available for:
- Python: [vortx-python](https://github.com/vortx-ai/vortx-python)
- JavaScript: Coming Soon
- Java: Coming Soon
- Go: Coming Soon

## Support

For API support:
- Email: api-support@vortx.ai
- Documentation: https://vortx.ai/docs/api
- Status: https://status.vortx.ai 