module github.com/cf-platform-eng/aws-pcf-quickstart

go 1.12

require (
	github.com/aws/aws-sdk-go v1.17.12
	github.com/google/uuid v1.1.1
	github.com/onsi/ginkgo v1.7.0
	github.com/onsi/gomega v1.4.3
	github.com/shurcooL/httpfs v0.0.0-20181222201310-74dc9339e414 // indirect
	github.com/shurcooL/vfsgen v0.0.0-20181202132449-6a9ea43bcacd // indirect
	github.com/starkandwayne/om-tiler v0.0.0-20190415123844-4a98c354d8f1
	gopkg.in/alecthomas/kingpin.v2 v2.2.6
	gopkg.in/yaml.v2 v2.2.2
	launchpad.net/goamz v0.0.0-20140813150539-000000000049 // indirect
)

replace (
	github.com/graymeta/stow => github.com/jtarchie/stow v0.0.0-20190209005554-0bff39424d5b
	github.com/jessevdk/go-flags => github.com/cppforlife/go-flags v0.0.0-20170707010757-351f5f310b26
	gopkg.in/mattn/go-colorable.v0 => github.com/mattn/go-colorable v0.1.1
)
