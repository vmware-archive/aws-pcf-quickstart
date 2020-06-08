module github.com/cf-platform-eng/aws-pcf-quickstart

go 1.12

require (
	github.com/alecthomas/template v0.0.0-20160405071501-a0175ee3bccc // indirect
	github.com/alecthomas/units v0.0.0-20151022065526-2efee857e7cf // indirect
	github.com/aws/aws-sdk-go v1.23.4
	github.com/go-sql-driver/mysql v1.4.1
	github.com/google/uuid v1.1.1
	github.com/onsi/ginkgo v1.9.0
	github.com/onsi/gomega v1.6.0
	github.com/shurcooL/httpfs v0.0.0-20190707220628-8d4bc4ba7749 // indirect
	github.com/shurcooL/vfsgen v0.0.0-20181202132449-6a9ea43bcacd
	github.com/starkandwayne/om-tiler v0.0.0-20190820103743-86c0a1263e12
	gopkg.in/alecthomas/kingpin.v2 v2.2.6
	gopkg.in/yaml.v2 v2.2.2
)

replace (
	github.com/cheggaaa/pb => github.com/cheggaaa/pb v1.0.28 // from bosh-cli Gopkg.lock
	github.com/golang/lint => golang.org/x/lint v0.0.0-20190409202823-959b441ac422 // https://github.com/golang/lint/issues/446#issuecomment-483638233
	github.com/jessevdk/go-flags => github.com/cppforlife/go-flags v0.0.0-20170707010757-351f5f310b26 // from bosh-cli Gopkg.lock
)
