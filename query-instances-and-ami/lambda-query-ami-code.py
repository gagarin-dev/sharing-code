import logging
import boto3

# Description: Queries information about EC2 instances in the current region

# Set up 'logger'. DEBUG for debugging, INFO for informational messages.
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
#logger.setLevel(logging.INFO)

ec2_resource = boto3.resource('ec2')


def f_get_ami_details(ami_id,instance_id):
    """Given AMI ID, pools AMI details
    """
    ami_details = {}

    # Get the image by the ID
    # Available image filters: https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeImages.html#query-DescribeImages-filters 
    filters = [{'Name': 'image-id', 'Values': [ami_id]}]
    try:
        ami_object = list(ec2_resource.images.filter(Filters=filters))[0] # This will give us the filtered-out image object
        # Construct the function response
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#image
        ami_details["ImageDescription"] = ami_object.description
        ami_details["ImageName"] = ami_object.name
        ami_details["ImageLocation"] = ami_object.image_location
        ami_details["OwnerId"] = ami_object.owner_id
        ami_details["InstanceIds"] = [instance_id]

    except Exception as e:
        logger.error(e)
        ami_details["ImageDescription"] = None
        ami_details["ImageName"] = None
        ami_details["ImageLocation"] = None
        ami_details["OwnerId"] = None
        ami_details["InstanceIds"] = [instance_id]

    return ami_details


def f_analyze_instances(ec2_instances):
    """Given the collection of the instances, perform the analysis
    """
    ami_list = {} # Empty dict to accumulate AMIs used by the instances

    for instance in ec2_instances:
        instance_ami = instance.image_id
        instance_id = instance.id
        logger.debug(f"DEBUG: Analyzing the instance {instance_id} with AMI {instance_ami}...")

        if instance_ami not in ami_list:  # Have not seen this AMI yet
            logger.debug(f"DEBUG: Have not seen {instance_ami} yet.") # debug
            ami_details = f_get_ami_details(instance_ami, instance_id)
            ami_list[instance_ami] = ami_details
            
        else:  # Already seen this AMI, just need to add the instance
            logger.debug(f"DEBUG: Seen {instance_ami} already!") # debug
            ami_list[instance_ami]["InstanceIds"].append(instance_id)

    return ami_list



def lambda_handler(event, context):
    """The Main Lambda function handler
    """
    # Get all instances
    try:
        ec2_instances = ec2_resource.instances.all()
    except Exception as e:
        logger.error(e)

    # Check if any instances are present
    if not ec2_instances:
        return 'No instances found in the current region. Nothing to do.'
    else:
        result = f_analyze_instances(ec2_instances)  # Calling f_analyze_instances function

    return(result)


if __name__ == "__main__":
    lambda_handler("na","na")