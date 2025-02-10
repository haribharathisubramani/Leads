pip install streamlit pandas reportlab
```

2. Create necessary directories:
```bash
mkdir -p .streamlit assets
```

3. Project structure:
```
├── .streamlit/
│   └── config.toml
├── assets/
│   └── style.css
├── utils/
│   ├── auth.py
│   ├── data_handler.py
│   └── pdf_generator.py
└── main.py
```

4. Run the application:
```bash
streamlit run main.py
```

## Deployment Instructions

1. Backup your existing data:
```bash
# Backup your database and leads data
cp users.db users.db.backup
cp leads_data.csv leads_data.csv.backup
```

2. Update production files:
```bash
# Copy all updated files to your production server
scp -r * username@lead.iamhari.in:/path/to/your/app/
```

3. Install or update dependencies:
```bash
pip install -r requirements.txt
```

4. Restart the Streamlit server:
```bash
sudo systemctl restart streamlit-server
```

## Production Configuration

For production deployment (lead.iamhari.in), ensure:

1. Server configuration in `.streamlit/config.toml`:
```toml
[server]
headless = true
enableCORS = false
enableXsrfProtection = false
port = 5000
address = "0.0.0.0"
```

2. Proper file permissions:
```bash
chmod 644 leads_data.csv
chmod 644 users.db