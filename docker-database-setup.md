# Docker Database Setup Instructions

## Problem
Your Docker container can't connect to the PostgreSQL database because it's trying to connect to `localhost:5432`, but inside the container, `localhost` refers to the container itself, not your host machine.

## Solutions

### Option 1: Connect to PostgreSQL on Host Machine (Recommended)

Build and run your Docker container with database connectivity:

```bash
# Build the Docker image
docker build -t chatgpt-augmenter .

# Run the container with proper port mapping and database connection
docker run -p 3000:3000 -p 5001:5001 \
  --add-host=host.docker.internal:host-gateway \
  --name chatgpt-augmenter-container \
  chatgpt-augmenter
```

### Option 2: Override Database Host at Runtime

If you need to connect to a different database host:

```bash
docker run -p 3000:3000 -p 5001:5001 \
  -e DB_HOST=your-database-host \
  -e DB_PORT=5432 \
  -e DB_NAME=your-database-name \
  -e DB_USER=your-username \
  -e DB_PASSWORD=your-password \
  --name chatgpt-augmenter-container \
  chatgpt-augmenter
```

### Option 3: Use Docker Compose (Advanced)

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
      - "5001:5001"
    environment:
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_NAME=test
      - DB_USER=ayushpai
      - DB_PASSWORD=pai2004
    depends_on:
      - postgres

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=test
      - POSTGRES_USER=ayushpai
      - POSTGRES_PASSWORD=pai2004
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Then run:
```bash
docker-compose up --build
```

## Environment Variables

The application now supports these environment variables:

- `DB_HOST`: Database host (default: localhost, Docker: host.docker.internal)
- `DB_PORT`: Database port (default: 5432)
- `DB_NAME`: Database name (default: test)
- `DB_USER`: Database username (default: ayushpai)
- `DB_PASSWORD`: Database password (default: pai2004)

## Troubleshooting

1. **Ensure PostgreSQL is running on your host machine**:
   ```bash
   # Check if PostgreSQL is running
   pg_isready -h localhost -p 5432
   
   # Or check processes
   ps aux | grep postgres
   ```

2. **Check Docker container logs**:
   ```bash
   docker logs chatgpt-augmenter-container
   ```

3. **Test database connectivity from container**:
   ```bash
   # Get into the container
   docker exec -it chatgpt-augmenter-container bash
   
   # Test connection
   python -c "from backend.database.postgres import DatabaseService; print(DatabaseService.get_database_connection())"
   ```

4. **Check if PostgreSQL allows external connections**:
   - Edit `postgresql.conf`: `listen_addresses = '*'`
   - Edit `pg_hba.conf`: Add line for Docker network
   - Restart PostgreSQL service

## Key Changes Made

1. **Environment Variables**: Database connection now uses environment variables
2. **Host Resolution**: Docker container uses `host.docker.internal` to connect to host machine
3. **Flexible Configuration**: Can override database settings at runtime
