import boto3
import time
from price_api import get_total_cost

client = boto3.client('sns', region_name='ap-south-1')

# Create Topic
response = client.create_topic(Name='Cost_Estimator_Bot')
# print(response)
topic_arn = response['TopicArn']

# Subscribe to topic
client.subscribe(
    TopicArn = topic_arn,
    Protocol = 'email',
    Endpoint = 'youremail@gmail.com'
)
print("\nSubscription request sent. Please check your email to confirm the subscription.")

# Wait for confirmation Loop
while True:
    subs = client.list_subscriptions_by_topic(TopicArn=topic_arn)
    # print(subs)
    subs_arn_status = subs['Subscriptions'][0]['SubscriptionArn']
    if subs_arn_status != 'PendingConfirmation':
        print("\nSubscription Confirmed")
        break
    else:
        print("\nWaiting for subscription confirmation...")
        time.sleep(5)
        
# Publish A Message
costs = get_total_cost()

print("\n=== AWS Daily Cost Report Preview ===")
print(f"EC2 Hourly Cost: ${costs['ec2_hourly']:.3f}")
print(f"EC2 Monthly Cost: ${costs['ec2_monthly']:.2f}")
print(f"S3 Total Size (GB): {costs['s3_size']:.5f}")
print(f"S3 Monthly Cost: ${costs['s3_monthly']:.2f}")
print(f"RDS Hourly Cost: ${costs['rds_hourly']:.2f}")
print(f"RDS Monthly Cost: ${costs['rds_monthly']:.2f}")
print(f"Total Hourly Cost: ${costs['total_hourly']:.2f}")
print(f"Total Monthly Cost: ${costs['total_monthly']:.2f}")
print("=== End of Report ===\n")

message = client.publish(
    TopicArn = topic_arn,
    Subject = "AWS Daily Cost Report",
    Message = f"""
    AWS Daily Cost Report:

    EC2:
        Hourly: ${costs['ec2_hourly']}
        Monthly: ${costs['ec2_monthly']:.2f}

    S3:
        Size: {costs['s3_size']:.5f} GB
        Monthly: ${costs['s3_monthly']:.2f}

    RDS:
        Hourly: ${costs['rds_hourly']:.2f}
        Monthly: ${costs['rds_monthly']:.2f}

    Total:
        Hourly: ${costs['total_hourly']:.2f}
        Monthly: ${costs['total_monthly']:.2f}
    """
)
# print(f"\n Message Sent: {message}\n")