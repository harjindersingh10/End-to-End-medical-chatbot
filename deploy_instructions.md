# Deploy ClinixAI to AWS

## Option 1: AWS Elastic Beanstalk (Recommended)

### Prerequisites:
1. Install AWS CLI: `pip install awscli`
2. Install EB CLI: `pip install awsebcli`
3. Configure AWS credentials: `aws configure`

### Steps:
1. **Initialize EB application:**
   ```bash
   eb init
   ```
   - Choose region (e.g., us-east-1)
   - Select "Create new application"
   - Name: clinixai-medical-chatbot
   - Platform: Python 3.9+
   - Choose "No" for CodeCommit

2. **Set environment variables:**
   ```bash
   eb setenv GEMINI_API="your_actual_gemini_api_key" PINECONE_API="your_actual_pinecone_api_key"
   ```

3. **Create and deploy:**
   ```bash
   eb create clinixai-prod
   eb deploy
   ```

4. **Open your app:**
   ```bash
   eb open
   ```

## Option 2: AWS EC2 (Manual)

### Steps:
1. Launch EC2 instance (Ubuntu 22.04)
2. SSH into instance
3. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install python3-pip nginx
   pip3 install -r requirements.txt
   ```
4. Upload your files
5. Configure nginx
6. Run with gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 application:application
   ```

## Option 3: AWS Lambda + API Gateway

### Steps:
1. Install Zappa: `pip install zappa`
2. Initialize: `zappa init`
3. Deploy: `zappa deploy production`

## Environment Variables Needed:
- GEMINI_API: Your Gemini API key
- PINECONE_API: Your Pinecone API key

## Files for Deployment:
- ✅ application.py (main Flask app)
- ✅ requirements.txt (dependencies)
- ✅ .ebextensions/01_flask.config (EB config)
- ✅ index.html, styles.css, script.js (frontend)
- ✅ .env (with placeholder keys)