
# AWS Cost Estimator Bot

A lightweight Python bot that estimates your AWS EC2, S3, and RDS usage costs in real-time — and emails you a **daily cost report** using AWS SNS.

> ❌ Tired of the clunky AWS Billing Console?  
> ✅ Build your own cost-tracking solution that’s clean, automated, and under your control.

---

## Features

-  **Real-time pricing** pulled from AWS Pricing API
-  Smart cost calculations for:
  - EC2 (by instance type and region)
  - S3 (based on used storage)
  - RDS (by instance type and region)
-  **Daily email reports** via AWS SNS
- ⏱ Run with AWS Lambda or a simple local **cron job**
-  Shows both **hourly** and **monthly** estimates

---

##  Demo Output

```text
AWS Daily Cost Report:

EC2:
    Hourly: $0.0496
    Monthly: $35.71

S3:
    Size: 0.00010 GB
    Monthly: $0.00

RDS:
    Hourly: $0.02
    Monthly: $15.12

Total:
    Hourly: $0.07
    Monthly: $50.83
```

---

##  How It Works

1. Extracts metadata from your running AWS resources (EC2, S3, RDS)
2. Queries the Pricing API to fetch live cost per resource
3. Estimates hourly + monthly totals
4. Sends the summary via email using AWS SNS

---

##  Deployment Options

### Option 1: Cron Job (Local)
- Clone the repo
- Setup Python environment and AWS credentials
- Add to crontab: `python3 Cost_Estimator_Bot.sns_msg.py`

### Option 2: AWS Lambda (Cloud)
- Upload script as Lambda function
- Use EventBridge rule to trigger daily
- Grant Lambda permission to publish SNS

---

##  Tech Stack

- Python 
- Boto3 SDK
- AWS Pricing API
- AWS SNS (for email alerts)

---

## 🙋 Author

Made with ❤️ by [Daksh Sawhney](https://www.linkedin.com/in/dakshsawhneyy/)  
If you like it, connect or follow me for more DevOps 🔧 + Cloud ☁️ projects.

---
