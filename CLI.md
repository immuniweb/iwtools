# iwtools commandline options

```
usage: iwtools.py [-h] [--api-key API_KEY] [--api-keyfile API_KEYFILE] [-r] [-p] [-i IP] [-o OUTPUT] [-f FORMAT]
                  [--quick false] [-cfg CONFIG_FILE] TEST_TYPE TEST_TARGET
```

### --api-key API_KEY
Pass your API key for a higher number of daily tests.

### --api-keyfile API_KEYFILE
Use a file with your API keys (it’s more secure than using raw arguments).
[Find out more](https://www.immuniweb.com/free/).

Sample file content:

~~~
cloud ABCDE-FGHIJ-12345-67890
email 12345-ABCDE-67890-FGHIJ
websec ssl ABCDE-12345-FGHIJ-67890
darkweb 12345-ABCDE-67890-FGHIJ
mobile ABCDE-FGHIJ-12345-67890
~~~

### -r / --recheck
Force to refresh the test (API key required).

### -p / --pipeline
Compare test result with config (`websec`, `email` and `ssl` services only).

### -i / --ip IP
Force to use a specific IP address of the test's target (`websec` and `ssl` services only).

### --quick false
This parameter is for `cloud` service only. The default value (if ommited) is `true` - with it the test checks only in 
AWS, Azure and GCP only; in case of `false` - it performs full scan.

### -o / --output OUTPUT
Path to the output file.

### -f / --format {colorized_text, pretty_json, raw_json}
Output format.

- `colorized_text` — Colorful human-readable text (default value).
- `raw_json` — API response in JSON format.
- `pretty_json` — API response in pretty-printed JSON format.

### -cfg / --config-file CONFIG_FILE
Path to the configuration file. json or yaml. Default `config/email.yaml`, `config/websec.yaml` and `config/ssl.yaml`.

### TEST_TYPE (positional argument)
This parameter specifies the test's type.

- `cloud` - [Cloud Security Test](https://www.immuniweb.com/cloud/)
- `email` — [Email Security Test](https://www.immuniweb.com/email/)
- `websec` — [Website Security Test](https://www.immuniweb.com/websec/)
- `mobile` — [Mobile App Security Test](https://www.immuniweb.com/mobile/)
- `darkweb` — [Dark Web Exposure Test](https://www.immuniweb.com/darkweb/)
- `ssl` — [SSL Security Test](https://www.immuniweb.com/ssl/)

### TEST_TARGET (positional argument)
This parameter specifies the target of the test: URL of the tested website or mobile app (in application stores).
