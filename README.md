
# Scratch

Random notes while iterating

```
pip download -r requirements.txt  --no-deps --dest ./vendor
pip download --no-deps --dest ./vendor pip
```

On ops manager vm
```
apt-get upgrade
apt-get install python3-pip
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


# Questions
* How are we doing DNS?
* How are we doing certs?
