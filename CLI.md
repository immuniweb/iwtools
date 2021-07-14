# iwtools commandline options

```
usage: iwtools.py [-h] [--api-key API_KEY] [--api-keyfile API_KEYFILE] [-q] [-r] [-i IP] [-o OUTPUT] [-f FORMAT]
                  TEST_TYPE TEST_TARGET
```

### --api-key API_KEY
Pass your API key for a higher number of daily tests.

### --api-keyfile API_KEYFILE
Use a file with your API keys (it’s more secure than using raw arguments). [Find out more](https://www.immuniweb.com/free/).

### -r / --recheck
Force to refresh the test (API key required).

### -i / --ip IP
Force to use a specific IP address of the test's target.

### -o / --output OUTPUT
Path to the output file.

### -f / --format {colorized_text, pretty_json, raw_json}
Output format.

- colorized_text — Colorful human-readable text.
- raw_json — API response in JSON format.
- pretty_json — API response in pretty-printed JSON format.

### websec / mobile / darkweb / ssl
This parameter specifies the test's type.

websec — [Website Security Test](https://www.immuniweb.com/websec/)  
mobile — [Mobile App Security Test](https://www.immuniweb.com/mobile/)  
darkweb — [Dark Web Exposure Test](https://www.immuniweb.com/darkweb/)  
ssl — [SSL Security Test](https://www.immuniweb.com/ssl/)

### target (positional argument)
This parameter specifies the target of the test: URL of the tested website or mobile app (in application stores).
