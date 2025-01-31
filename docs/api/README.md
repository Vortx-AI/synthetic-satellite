# API Documentation

This directory contains comprehensive API documentation for the Vortx Earth Memory System.

## Contents

### [REST API](rest/overview.md)
- API endpoints
- Authentication
- Request/response formats
- Rate limiting
- Error handling

### [Python SDK](python/overview.md)
- Installation
- Basic usage
- Advanced features
- Best practices
- Error handling

## API Architecture

```mermaid
graph TD
    A[Client] --> B[API Gateway]
    B --> C[Authentication]
    C --> D[Rate Limiter]
    D --> E[Request Handler]
    E --> F1[Memory Service]
    E --> F2[Inference Service]
    E --> F3[Synthetic Service]
    
    F1 --> G[Response Handler]
    F2 --> G
    F3 --> G
    G --> H[Client Response]
```

## Authentication

```mermaid
graph LR
    A[API Key] --> B[JWT Token]
    B --> C[Request]
    C --> D[Validation]
    D --> E[Response]
```

## Quick Links

- [API Reference](rest/overview.md)
- [Python SDK Guide](python/overview.md)
- [Code Examples](../guides/examples/)
- [API Changelog](../meta/changelog.md)

## Support

For API support:
- Email: api-support@vortx.ai
- Documentation: https://vortx.ai/docs/api
- Status: https://status.vortx.ai 