# Deployment Checklist for Nubilum

## Pre-Deployment

- [ ] Replace placeholder logo with actual HL7 Portugal logo
  - File: `nubilum/static/hl7pt_logo.png`
  - Recommended size: 200x200px PNG format

- [ ] Review and update contact information in README.md
  - Add project repository URL
  - Verify HL7 Portugal website URL

- [ ] Review security settings
  - [ ] CORS configuration (currently allows all origins)
  - [ ] Nginx security headers
  - [ ] SSL/TLS certificate setup (if deploying with HTTPS)

- [ ] Test with real HL7 messages
  - [ ] ADT messages
  - [ ] ORM messages
  - [ ] Lab results (ORU)
  - [ ] Various HL7 v2 versions

## Build and Test

- [ ] Build the wheel package
  ```bash
  ./build.sh
  ```

- [ ] Verify wheel contents
  ```bash
  unzip -l dist/nubilum-1.0.0-py3-none-any.whl
  ```

- [ ] Build Docker image
  ```bash
  docker build -t nubilum:1.0.0 .
  ```

- [ ] Test Docker container locally
  ```bash
  docker run -d -p 8080:80 --name nubilum-test nubilum:1.0.0
  # Test at http://localhost:8080
  docker stop nubilum-test
  docker rm nubilum-test
  ```

## Production Deployment

### Option 1: Docker with External Nginx (HTTPS + Subdomain)

For deploying with an external nginx reverse proxy, HTTPS, and subdomain (e.g., `nubilum.yourdomain.pt`):

See [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) for complete instructions.

- [ ] Set up DNS for your subdomain
- [ ] Obtain SSL certificates (Let's Encrypt)
  ```bash
  sudo certbot certonly --nginx -d nubilum.yourdomain.pt
  ```

- [ ] Configure external nginx
  ```bash
  sudo cp docker/nginx-external.conf.example /etc/nginx/sites-available/nubilum
  # Edit to customize domain and SSL paths
  sudo ln -s /etc/nginx/sites-available/nubilum /etc/nginx/sites-enabled/
  sudo nginx -t && sudo systemctl reload nginx
  ```

- [ ] Set up log directory with proper permissions
  ```bash
  mkdir -p logs
  chmod 755 logs
  ```

- [ ] Deploy using production compose file
  ```bash
  docker-compose -f docker-compose.production.yml up -d --build
  ```

- [ ] Verify health
  ```bash
  curl https://nubilum.yourdomain.pt/api/health
  ```

### Option 2: Docker Compose (Development/Direct Access)

- [ ] Set up log directory with proper permissions
  ```bash
  mkdir -p /var/log/nubilum
  chmod 755 /var/log/nubilum
  ```

- [ ] Deploy
  ```bash
  docker-compose up -d
  ```

- [ ] Verify health
  ```bash
  curl http://localhost:8080/api/health
  ```

### Option 3: Kubernetes (Advanced)

- [ ] Create Kubernetes manifests (Deployment, Service, Ingress)
- [ ] Configure persistent volume for logs
- [ ] Set up ingress with SSL/TLS
- [ ] Deploy and verify

### Option 4: Manual Installation

- [ ] Set up Python 3.9+ environment
- [ ] Install wheel
  ```bash
  pip install dist/nubilum-1.0.0-py3-none-any.whl
  ```

- [ ] Configure nginx separately
- [ ] Set up systemd service for Gunicorn
- [ ] Configure log rotation

## Post-Deployment

- [ ] Verify application is accessible
- [ ] Test all functionality
  - [ ] Load example message
  - [ ] Anonymize message
  - [ ] Edit fields
  - [ ] Copy to clipboard
  - [ ] Clear all

- [ ] Check logs
  ```bash
  # Docker
  docker logs nubilum
  docker exec nubilum tail -f /var/log/nubilum/nubilum_*.log

  # Manual
  tail -f /var/log/nubilum/nubilum_*.log
  ```

- [ ] Monitor resource usage
  ```bash
  docker stats nubilum
  ```

- [ ] Set up log rotation (if not using Docker)
  ```bash
  # Create /etc/logrotate.d/nubilum
  ```

- [ ] Configure monitoring/alerting (optional)
  - [ ] Health check endpoint monitoring
  - [ ] Error rate tracking
  - [ ] Resource usage alerts

## Security Review

- [ ] Verify no sensitive data in logs
- [ ] Review CORS settings for production
- [ ] Ensure HTTPS is enabled (if applicable)
- [ ] Review nginx security headers
- [ ] Verify file permissions
- [ ] Check that no debug mode is enabled

## Documentation

- [ ] Update README.md with production URL
- [ ] Document any custom configuration
- [ ] Create runbook for operations team
- [ ] Document backup/restore procedures (if applicable)

## Maintenance

- [ ] Set up automated backups (logs only)
- [ ] Schedule regular updates
- [ ] Monitor for security vulnerabilities
  ```bash
  pip list --outdated
  docker scan nubilum:1.0.0
  ```

- [ ] Plan for log archival/cleanup

## Rollback Plan

In case of issues:

1. Stop the new deployment
   ```bash
   docker-compose down
   # or
   docker stop nubilum
   ```

2. Deploy previous version
   ```bash
   docker run -d -p 8080:80 nubilum:previous-version
   ```

3. Investigate issues in logs

4. Fix and redeploy

## Contact and Support

- Technical issues: [Add your support contact]
- HL7 Portugal: https://hl7.pt
- Documentation: See README.md in project

---

**Deployment Date**: ________________
**Deployed By**: ________________
**Version**: 1.0.0
**Environment**: ________________ (Development / Staging / Production)
