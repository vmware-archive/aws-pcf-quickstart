# Scratch

Random notes while iterating

```
pip download -r requirements.txt  --no-deps --dest ./vendor
pip download --no-deps --dest ./vendor pip
```

On ops manager vm
```
apt-get upgrade
apt-get install python3-pip python3-dev
# get om on path somehow...
# get pivnet cli on machine somehow
```

Looks like pivnet download traffic *is* inside aws
```shell
ubuntu@ip-10-0-0-45:~$ time pivnet download-product-files -p elastic-runtime -r 1.10.4 --product-file-id=17937
2017/04/18 15:47:14 Downloading 'cf-1.10.4-build.1.pivotal' to 'cf-1.10.4-build.1.pivotal'
 5.96 GB / 5.96 GB [==============================================] 100.00% 3m1s

real	3m2.372s
user	0m15.970s
sys	0m32.127s
```

Iterating on ops manager vm
```bash
rsync -avzh --exclude=env --exclude=.git --exclude=.idea . ubuntu@ec2-....compute-1.amazonaws.com:~/quickstart
```


# Questions
* How are we doing DNS?
* How are we doing certs?
* How do we install pip / python3 / om / pivnet on ops manager vm?
* How are we reporting and elevating errors back to the user?
    - Before ops manager is ready
    - While it running
* How CI system outputs the versions of tiles (ERT, others)
    - Some config file outside of formation script?
    - Don't really want user to input, but want some tested / vetted version close to latest
* How will we grab the tile out of s3 bucket? Nervous about making it public. Also, bucket is in Jeenal's account. Some other place
* boto3.client - work out some failure modes and retry secenarios


# Docker

```bash
docker build ci -t cfplatformeng/quickstart-ci
docker tag cfplatformeng/quickstart-ci cfplatformeng/quickstart-ci:1 #where 1 is the tag version number
docker push cfplatformeng/quickstart-ci
```

# Changes to cloud-formation template:

* 11PivnetToken
* 12AdminEmail (used for mysql backups, for example)
* Didn't make change, but want: output load the 3 balancer names so we don't have to recreate logic
