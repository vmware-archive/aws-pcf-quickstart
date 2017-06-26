import boto3
import botocore.exceptions

import om_manager
from settings import Settings


def delete_everything(my_settings: Settings, delete_buckets=False):
    if om_manager.is_opsman_configured(my_settings):
        cmd = "{om_with_auth} delete-installation".format(
            om_with_auth=om_manager.get_om_with_auth(my_settings)
        )
        # todo: call delete twice
        return_code = om_manager.exponential_backoff(cmd, my_settings.debug)
        if return_code != 0:
            print("OM cmd failed to delete installation {}".format(return_code))
            return return_code

    buckets = [
        my_settings.pcf_opsmanagers3bucket,
        my_settings.pcf_elasticruntimes3buildpacksbucket,
        my_settings.pcf_elasticruntimes3dropletsbucket,
        my_settings.pcf_elasticruntimes3packagesbucket,
        my_settings.pcf_elasticruntimes3resourcesbucket
    ]

    # todo: should we delete the keypair...?

    for bucket_name in buckets:
        try:
            if delete_buckets:
                delete_bucket(my_settings, bucket_name)
            else:
                expire_bucket(my_settings, bucket_name)
        except Exception as e:
            print(e)
            return 1
    return 0


def delete_bucket(my_settings: Settings, bucket_name: str):
    try:
        s3 = boto3.client(
            service_name='s3', region_name=my_settings.region,
            aws_access_key_id=my_settings.pcf_iamuseraccesskey,
            aws_secret_access_key=my_settings.pcf_iamusersecretaccesskey
        )
        contents = s3.list_objects_v2(Bucket=bucket_name).get('Contents')
        while contents is not None:
            delete_keys = [{'Key': o.get('Key')} for o in contents]
            s3.delete_objects(Bucket=bucket_name, Delete={
                'Objects': delete_keys
            })
            contents = s3.list_objects_v2(Bucket=bucket_name).get('Contents')
        s3.delete_bucket(Bucket=bucket_name)
    except botocore.exceptions.ClientError as e:
        error = e.response.get('Error')
        if not error or error.get('Code') != 'NoSuchBucket':
            raise e


def expire_bucket(my_settings: Settings, bucket_name: str):
    s3 = boto3.client(
        service_name='s3', region_name=my_settings.region,
        aws_access_key_id=my_settings.pcf_iamuseraccesskey,
        aws_secret_access_key=my_settings.pcf_iamusersecretaccesskey
    )
    s3.put_bucket_lifecycle_configuration(
        Bucket=bucket_name,
        LifecycleConfiguration={
            'Rules': [
                {
                    'Expiration': {
                        'Date': '2000-01-01'
                    },
                    'Prefix': "",
                    'Status': 'Enabled'
                }
            ]
        }
    )
