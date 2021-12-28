print('Loading the required libraries')
import sys
from awsglue.utils import getResolvedOptions

print('Reading the AWS Glue job parameters')
args = getResolvedOptions(sys.argv, ['today','source_path','kms_key_id','days_observational_windows'])
for a in args.keys():
    print(args[a])
