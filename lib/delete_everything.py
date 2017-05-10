from settings import Settings
import om_manager
import boto3


def delete_everything(my_settings: Settings):
    cmd = "{om_with_auth} delete-installation".format(
        om_with_auth=om_manager.get_om_with_auth(my_settings)
    )

    return_code = om_manager.exponential_backoff(cmd, my_settings.debug)
    if return_code != 0:
        print("OM cmd failed to delete installation {}".format(return_code))
        return return_code

    s3 = boto3.client(
        service_name='s3', region_name=my_settings.region,
        aws_access_key_id=my_settings.pcf_iamuseraccesskey,
        aws_secret_access_key=my_settings.pcf_iamusersecretaccesskey
    )

    buckets = [
        my_settings.pcf_elasticruntimes3buildpacksbucket,
        my_settings.pcf_elasticruntimes3dropletsbucket,
        my_settings.pcf_elasticruntimes3packagesbucket,
        my_settings.pcf_elasticruntimes3resourcesbucket
    ]

    for bucket in buckets:
        try:
            s3.delete_bucket(Bucket=bucket)
        except Exception as e:
            print(e)
            return 1

    return 0
