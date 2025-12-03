# Production Deployment Guide

This guide explains how to deploy Nubilum behind an external nginx reverse proxy with HTTPS on a subdomain (e.g., `nubilum.yourdomain.pt`).

## Prerequisites

- Linux server with Docker and Docker Compose installed
- External nginx installed on the host system
- A domain name with DNS configured (e.g., `nubilum.yourdomain.pt`)
- SSL certificates (e.g., from Let's Encrypt)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Internet                              │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTPS :443
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 Host Server                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              External Nginx                           │   │
│  │   - SSL termination                                   │   │
│  │   - Subdomain routing (nubilum.yourdomain.pt)        │   │
│  │   - Reverse proxy to Docker container                 │   │
│  └──────────────────────────┬───────────────────────────┘   │
│                             │ HTTP :8080 (localhost only)    │
│                             ▼                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Docker Container                         │   │
│  │   - Internal nginx                                    │   │
│  │   - Gunicorn + Flask app                             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Step 1: Set Up DNS

Configure your DNS to point your subdomain to your server's IP address:

```
nubilum.yourdomain.pt  A  YOUR_SERVER_IP
```

Wait for DNS propagation (can take a few minutes to 48 hours).

## Step 2: Obtain SSL Certificate

### Using Let's Encrypt (Recommended)

Install Certbot if not already installed:

```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx
```

Obtain a certificate:

```bash
sudo certbot certonly --nginx -d nubilum.yourdomain.pt
```

Or using standalone mode (if nginx isn't running yet):

```bash
sudo certbot certonly --standalone -d nubilum.yourdomain.pt
```

Certificates will be stored in `/etc/letsencrypt/live/nubilum.yourdomain.pt/`.

## Step 3: Configure External Nginx

1. Copy the example configuration:

```bash
sudo cp docker/nginx-external.conf.example /etc/nginx/sites-available/nubilum
```

2. Edit the configuration to match your domain:

```bash
sudo nano /etc/nginx/sites-available/nubilum
```

Replace all occurrences of `nubilum.example.pt` with your actual domain (e.g., `nubilum.yourdomain.pt`).

Update the SSL certificate paths if needed:

```nginx
ssl_certificate /etc/letsencrypt/live/nubilum.yourdomain.pt/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/nubilum.yourdomain.pt/privkey.pem;
```

3. Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/nubilum /etc/nginx/sites-enabled/
```

4. Test the nginx configuration:

```bash
sudo nginx -t
```

5. Reload nginx:

```bash
sudo systemctl reload nginx
```

## Step 4: Deploy the Docker Container

1. Navigate to the Nubilum directory:

```bash
cd /path/to/nubilum
```

2. Create the logs directory:

```bash
mkdir -p logs
chmod 755 logs
```

3. Build and start the container:

```bash
docker-compose -f docker-compose.production.yml up -d --build
```

4. Verify the container is running:

```bash
docker-compose -f docker-compose.production.yml ps
```

5. Check container health:

```bash
docker-compose -f docker-compose.production.yml logs
```

## Step 5: Verify Deployment

1. Test HTTPS access:

```bash
curl -I https://nubilum.yourdomain.pt/
```

2. Test API endpoint:

```bash
curl https://nubilum.yourdomain.pt/api/health
```

Expected response:
```json
{"status": "healthy", "version": "1.0.0", "timestamp": "..."}
```

3. Open in browser: `https://nubilum.yourdomain.pt`

## Troubleshooting

### Common Issues

#### 502 Bad Gateway

- Ensure the Docker container is running: `docker-compose -f docker-compose.production.yml ps`
- Check container logs: `docker-compose -f docker-compose.production.yml logs`
- Verify port 8080 is listening: `ss -tlnp | grep 8080`

#### SSL Certificate Errors

- Check certificate paths in nginx configuration
- Verify certificates exist: `ls -la /etc/letsencrypt/live/yourdomain/`
- Check certificate expiration: `sudo certbot certificates`

#### Mixed Content Errors

- Ensure all API calls use relative URLs (the app is configured for this)
- Check browser console for specific errors

### View Logs

```bash
# Container logs
docker-compose -f docker-compose.production.yml logs -f

# External nginx logs
sudo tail -f /var/log/nginx/nubilum_access.log
sudo tail -f /var/log/nginx/nubilum_error.log

# Application logs
tail -f logs/nubilum_*.log
```

## Updating the Application

1. Pull the latest code:

```bash
git pull origin main
```

2. Rebuild and restart:

```bash
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml up -d --build
```

## SSL Certificate Renewal

Let's Encrypt certificates expire every 90 days. Certbot usually sets up auto-renewal. To test:

```bash
sudo certbot renew --dry-run
```

To manually renew:

```bash
sudo certbot renew
sudo systemctl reload nginx
```

## Running with Other Applications

When running Nubilum alongside other applications on the same server:

1. Each application should use a different port (Nubilum uses 8080 by default)
2. Each application needs its own nginx server block with its own subdomain
3. Make sure there are no port conflicts

Example for multiple applications:

```
nubilum.yourdomain.pt  -> 127.0.0.1:8080 (Nubilum)
app2.yourdomain.pt     -> 127.0.0.1:8081 (Other App)
app3.yourdomain.pt     -> 127.0.0.1:8082 (Another App)
```

To change Nubilum's port, edit `docker-compose.production.yml`:

```yaml
ports:
  - "127.0.0.1:YOUR_PORT:80"
```

And update the external nginx configuration:

```nginx
proxy_pass http://127.0.0.1:YOUR_PORT;
```
