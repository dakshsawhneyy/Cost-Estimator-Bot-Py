import boto3

def get_running_instances():
    ec2 = boto3.client('ec2', region_name="ap-south-1")
    
    # Filter running instances
    response = ec2.describe_instances(
        Filters=[
            {
            'Name': 'instance-state-name',
            'Values': ['running']
            }
        ]
    )
    
    # Create an empty list for storing instances
    instances = []
    # print(response)
    
    # Accessing Instances
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            # Get instance id and type
            instance_info = {
                'Instance_Id': instance['InstanceId'],
                'Instance_Type': instance['InstanceType']
            }
            instances.append(instance_info)
    return instances

def get_running_S3():
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    #print(response)
    buckets = []
    
    for bucket in response['Buckets']:
        # Need to fetch locations of indvijual buckets
        location = s3.get_bucket_location(Bucket=bucket['Name'])
        # print(location)
        region = location.get('LocationConstraint') or 'ap-south-1' # Default for none
        buckets.append({
            'BucketName': bucket['Name'],
            'Region': region
        })
    return buckets

def get_running_rds():
    rds = boto3.client('rds', region_name='ap-south-1')
    response = rds.describe_db_instances()
    # print(response)
    running_db = []
    
    for db in response['DBInstances']:
        # print(db)
        if db['DBInstanceStatus'] == 'available':
            running_db.append({
                'DBInstanceIdentifier': db['DBInstanceIdentifier'],
                'DbInstanceType': db['DBInstanceClass'],
                'Engine': db['Engine'],
                'Region': 'ap-south-1'
            })
    return running_db



if __name__ == "__main__":
    print('\n')
    running_instances = get_running_instances()
    print("Printing Running Instances:")
    for i in running_instances:
        print(f"{i}")
        
    buckets = get_running_S3()
    print("\n")
    print("Printing Running S3 Buckets:")
    for i in buckets:
        print(f"{i}")
        
    print('\n')
    rds_db = get_running_rds()
    print("Printing Running RDS Instances:")
    for i in rds_db:
        print(i)