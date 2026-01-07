# LiteLLM Proxy Project Context

## Architecture

Docker Compose setup running:
- CCProxy (Claude proxy with hooks) on port 4000
- PostgreSQL database for LiteLLM on port 5432
- Prometheus metrics on port 9090

## Key Files

- `Dockerfile`: Custom image with libatomic1 for Prisma, generates Prisma client at build time
- `docker-compose.yml`: Service definitions (db commented out for optional use)
- `config.yaml`: LiteLLM model routing configuration
- `ccproxy.yaml`: Hook configurations (rule_evaluator, model_router, forward_oauth)
- `.env`: Credentials (API keys, master key)

## Important Notes

- Prisma client must be generated during Docker build using LiteLLM's schema
- libatomic1 required for Prisma to work in slim Python image
- Database migrations run automatically on startup
- Master key: `<YOUR_MASTER_KEY>` (configured in .env as LITELLM_MASTER_KEY)
