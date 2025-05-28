import boto3
import json
from fetch_resources import get_running_S3
from fetch_resources import get_running_instances
from fetch_resources import get_running_rds

def get_ec2_price(instance_type, region_name):
    # Zone-1 Make a connection to AWS Pricing service (works only in us-east-1)
    pricing = boto3.client('pricing', region_name='us-east-1')
    
    # Zone 2: Translate region name into AWS’s pricing language
    region_mapping = {
        'ap-south-1': 'Asia Pacific (Mumbai)'
    }
    location = region_mapping.get(region_name, region_name) # extract full name used in pricing api

    # Zone-3 Ask AWS Pricing Api - “How much for this type of machine in this region?”
    response = pricing.get_products(
        ServiceCode='AmazonEC2',
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
            {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': location},
            {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
            {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'},  # No extra software like SQL Server or Windows pre-installed. Just a clean Linux VM.
        ],
        MaxResults=1
    )
    # print(response)
    
    # Zone-4 Read the nested JSON response
    # Its output is dictionary but it has one key 'Pricelist' which is in json - need to convert it
    price_item = json.loads(response['PriceList'][0])   # converts into dictionary
    # print(price_item)
    on_demand = price_item['terms']['OnDemand'] 
    # print(on_demand)
    
    # Zone 5 - Final Boss Fight — Get the actual price
    prices = []
    for term_id, term in on_demand.items():  # term_id is instance types under and term is object liked with that key
        price_dimentions = term['priceDimensions'] # i want this from value object
        for pd_id, pd in price_dimentions.items():
            price_per_hour = pd['pricePerUnit']['USD']
            prices.append(float(price_per_hour))

    return prices


def get_s3_price(buckets, target_region):
    s3 = boto3.resource('s3') # set up S3 Resource
    # print(s3)
    total_size = 0  # total size initially 0
    
    # Loop through each bucket
    for bucket in buckets:
        name = bucket['BucketName']
        region = bucket['Region']
        
        # if bucket is not of specific region, skip it
        if region != target_region:
            continue
        
        bucket_obj = s3.Bucket(name)
        # print(bucket_obj)
        for obj in bucket_obj.objects.all(): # List all objects
            # print(obj)
            total_size += obj.size  # Add file size to toal size
        
    total_size_gb = total_size / (1024 ** 3)
    return total_size_gb
    

def get_rds_price(instance_class, engine, region_name):
    # Zone 1 - Make a connection for AWS Pricing
    pricing = boto3.client('pricing', region_name='us-east-1')

    # Zone 2 - Translate region into AWS can understand
    region_mapping = {
        'ap-south-1': 'Asia Pacific (Mumbai)'
    }
    location = region_mapping.get(region_name, region_name)

    # Map your engine name to AWS pricing API expected values because capitalise wont work
    engine_mapping = {
        'mysql': 'MySQL',
        'postgres': 'PostgreSQL',
        'postgresql': 'PostgreSQL',
        'oracle-se1': 'Oracle SE1',
        'oracle-se2': 'Oracle SE2',
        'oracle-ee': 'Oracle EE',
        'sqlserver-web': 'SQL Server Web',
        'sqlserver-standard': 'SQL Server Standard',
        'sqlserver-ee': 'SQL Server Enterprise',
        'mariadb': 'MariaDB',
        # add more as needed
    }
    engine_proper = engine_mapping.get(engine.lower(), engine)

    # Zone 3 - Ask AWS pricing by filtering things
    response = pricing.get_products(
        ServiceCode='AmazonRDS',
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_class},
            {'Type': 'TERM_MATCH', 'Field': 'databaseEngine', 'Value': engine_proper},
            {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': location},
            {'Type': 'TERM_MATCH', 'Field': 'deploymentOption', 'Value': 'Single-AZ'},
            {'Type': 'TERM_MATCH', 'Field': 'licenseModel', 'Value': 'No License required'},
        ],
        MaxResults=1
    )

    if not response['PriceList']:
        return [0.0]

    # Zone 4 - Read the nested JSON response
    price_item = json.loads(response['PriceList'][0])
    on_demand = price_item['terms']['OnDemand']
    
    # Zone 5 - Fetch the actual Price
    prices = []
    for term_id, term in on_demand.items():
        for pd_id, pd in term['priceDimensions'].items():
            price_per_hour = pd['pricePerUnit']['USD']
            prices.append(float(price_per_hour))
    return prices


def get_total_cost():
    region = 'ap-south-1'
        
    instances = get_running_instances()
    total_price_ec2_per_hour = 0
    total_price_ec2_per_month = 0
    for instance in instances:
        instance_type = instance['Instance_Type']
        # print(instance_type)
        hourly_price = get_ec2_price(instance_type, region)
        total_price_ec2_per_hour += hourly_price[0]
        monthly_price = [price* 720 for price in hourly_price]
        total_price_ec2_per_month += monthly_price[0]
    #print(f"Hourly Price for EC2: ${total_price_ec2_per_hour:.3f}")
    #print(f"Monthly Price for EC2: ${total_price_ec2_per_month:.2f}")
    
    s3_buckets = get_running_S3()
    total_size = get_s3_price(s3_buckets, region)
    price_per_gb = 0.023
    estimated_cost = total_size * price_per_gb
    #print(f"Total S3 Size in GB: {float(total_size):.5f}GB") # Round to 2 decimal places
    #print(f"Estimated Cost for S3 Storage: ${estimated_cost:.2f} per month")
    
    databases = get_running_rds()
    total_price = 0
    for database in databases:
        engine = database['Engine']
        db_type = database['DbInstanceType']
        rds = get_rds_price(db_type, engine, region)
        total_price = rds[0]
    #print(f"Estimated Cost for RDS: ${total_price:.2f} per hour")    
    rds_monthly = (total_price * 720)
    #print(f"Estimated Cost for RDS: ${rds_monthly:.2f} per month")
    
    total_hourly_cost = total_price_ec2_per_hour + total_price
    total_monthly_cost = total_price_ec2_per_month + rds_monthly + estimated_cost
    #print(f"Total Estimated Cost per Hour: ${total_hourly_cost:.2f}")
    #print(f"Total Estimated Cost per Month: ${total_monthly_cost:.2f}")
    
    return {
        'ec2_hourly': total_price_ec2_per_hour,
        'ec2_monthly': total_price_ec2_per_month,
        's3_size': total_size,
        's3_monthly': estimated_cost,
        'rds_hourly': total_price,
        'rds_monthly': rds_monthly,
        'total_hourly': total_hourly_cost,
        'total_monthly': total_monthly_cost
    }