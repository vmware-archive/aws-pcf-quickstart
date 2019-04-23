package templates_test

import (
	"fmt"
	"io/ioutil"
	"path/filepath"
	"runtime"

	"github.com/cf-platform-eng/aws-pcf-quickstart/config"
	. "github.com/cf-platform-eng/aws-pcf-quickstart/templates"

	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
	"gopkg.in/yaml.v2"

	ompattern "github.com/starkandwayne/om-tiler/pattern"
)

func fixturesDir() string {
	_, filename, _, _ := runtime.Caller(0)
	return filepath.Join(filepath.Dir(filename), "fixtures")
}

func fixturePath(f string) string {
	return filepath.Join(fixturesDir(), f)
}

func readFixture(f string) []byte {
	in, err := ioutil.ReadFile(fixturePath(f))
	Expect(err).ToNot(HaveOccurred())

	return in
}

func readYAML(f string) map[string]interface{} {
	out := make(map[string]interface{})
	err := yaml.Unmarshal(readFixture(f), out)
	Expect(err).ToNot(HaveOccurred())

	return out
}

var _ = Describe("GetPattern", func() {
	var (
		pattern        ompattern.Pattern
		varsFile       string
		varsStore      string
		smallFootPrint bool
	)
	JustBeforeEach(func() {
		var err error
		deploymentSize := "Multi-AZ"
		if smallFootPrint {
			deploymentSize = "SmallFootPrint"
		}
		cfg := &config.Config{
			PcfDeploymentSize: deploymentSize,
			Raw:               readYAML(varsFile),
		}
		pattern, err = GetPattern(
			cfg, fixturePath(varsStore), true)
		Expect(err).ToNot(HaveOccurred())
		err = pattern.Validate(true)
		Expect(err).ToNot(HaveOccurred())
	})

	Context("when small-footprint is enabled", func() {
		BeforeEach(func() {
			varsFile = "vars.yml"
			varsStore = "creds.yml"
			smallFootPrint = true
		})
		It("renders tile configs", func() {
			director, err := pattern.Director.ToTemplate().Evaluate(true)
			Expect(err).ToNot(HaveOccurred())
			Expect(director).To(MatchYAML(readFixture("bosh-smallfootprint.yml")))
			for _, tile := range pattern.Tiles {
				template, err := tile.ToTemplate().Evaluate(true)
				Expect(err).ToNot(HaveOccurred())
				Expect(template).To(MatchYAML(readFixture(fmt.Sprintf("%s.yml", tile.Name))))
			}
		})
	})
	// Context("when small-footprint is Disabled", func() {
	// 	BeforeEach(func() {
	// 		varsFile = "vars.yml"
	// 		varsStore = "creds.yml"
	// 		smallFootPrint = false
	// 	})
	// 	It("renders tile configs", func() {
	// 		director, err := pattern.Director.ToTemplate().Evaluate(true)
	// 		Expect(err).ToNot(HaveOccurred())
	// 		Expect(director).To(MatchYAML(readFixture("bosh-full.yml")))
	// 		for _, tile := range pattern.Tiles {
	// 			template, err := tile.ToTemplate().Evaluate(true)
	// 			Expect(err).ToNot(HaveOccurred())
	// 			Expect(template).To(MatchYAML(readFixture(fmt.Sprintf("%s.yml", tile.Name))))
	// 		}
	// 	})
	// })
})
