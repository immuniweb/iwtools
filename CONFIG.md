# iwtools pipeline configuration file parameters

## Websec

```yaml
---
  minimal_grade: "A-"
  compliance_pci_dss: true
  compliance_gdpr: true
  max_soft_outdated: 0
  max_soft_vulnerabilities: 0
  max_headers_issue: 0
  csp_is_set: true
```

`minimal_grade` - indicates the minimal expected grade of the test. Possible values are: 'N', 'F', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A', 'A+'.

`compliance_pci_dss` - indicates the expected compliance with PCI DSS. Boolean value.

`compliance_gdpr` - indicates the expected compliance with PCI DSS. Boolean value.

`max_soft_outdated` - indicates the maximal expected number of outdated software. Can be either zero or a positive number.

`max_soft_vulnerabilities` - indicates the maximal expected number of vulnerable software. Can be either zero or a positive number.

`max_headers_issue` - indicates the maximal expected number of HTTP header-related issues. Can be either zero or a positive number.

`csp_is_set` - indicates whether Content-Security-Policy header is expected to be set by the tested website. Boolean value.

## SSL

```yaml
---
  minimal_grade: "C"
  max_pci_dss_issues: 1
  max_hipaa: 1
  max_nist: 1
  max_best_practises_issues: 1
```

`minimal_grade` - indicates the minimal expected grade of the test. Possible values are: 'N', 'F', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A', 'A+'.

`max_pci_dss_issues` - indicates the maximal expected number of PCI DSS compliance-related issues. Can be either zero or a positive number.

`max_hipaa` - indicates the maximal expected number of HIPAA compliance-related issues. Can be either zero or a positive number.

`max_nist` - indicates the maximal expected number of NIST compliance-related issues. Can be either zero or a positive number.

`max_best_practises_issues` - indicates the maximal expected number of Industrt Best Practice-related issues. Can be either zero or a positive number.