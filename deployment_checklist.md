# Deployment Checklist

## Pre-deployment
- [ ] Backup current database (users.db)
- [ ] Backup leads data (leads_data.csv)
- [ ] Check current production configurations
- [ ] Test all features in development environment

## Files to Update
- [ ] main.py
- [ ] utils/data_handler.py
- [ ] utils/auth.py
- [ ] utils/pdf_generator.py
- [ ] assets/style.css
- [ ] .streamlit/config.toml

## Post-deployment Verification
- [ ] Verify login functionality
- [ ] Test lead creation
- [ ] Confirm lead deletion and trash feature
- [ ] Check followup tracking
- [ ] Verify PDF report generation
- [ ] Test admin console
- [ ] Confirm data persistence

## Rollback Plan
If issues occur after deployment:
1. Stop the Streamlit server
2. Restore backup files (users.db.backup, leads_data.csv.backup)
3. Revert code changes
4. Restart the server

## Production URLs
- Main application: https://lead.iamhari.in
- Admin portal: https://lead.iamhari.in/admin

## Server Commands
```bash
# Restart Streamlit server
sudo systemctl restart streamlit-server

# Check server status
sudo systemctl status streamlit-server

# View logs
sudo journalctl -u streamlit-server -f
```
