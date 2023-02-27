# iwtools — ImmuniWeb® Community Edition CLI

<p align="center">
  <img src="logo.png" alt="iwtools logo">
</p>

Simple CLI interface to leverage [ImmuniWeb® Community Edition](https://www.immuniweb.com/free/) free tools in CI/CD pipelines and DevOps.

## Prepare

Create virtual enviroment and install dependencies. Python >= 3.7 required.

```sh
git clone https://github.com/ImmuniwebSA/iwtools.git
cd iwtools/iwtools
python3 -m venv env
source ./env/bin/activate
pip install -r requirements.txt
```

Instead of preparing and configuring the environment yourself, you can use our [Docker Image](https://hub.docker.com/r/immuniweb/iwtools).

## Usage

### Website Security Test

Check your website for GDPR and PCI DSS compliance, test CMS and CSP security, verify web server hardening and privacy:

```sh
./iwtools.py websec https://www.immuniweb.com
```

#### Main features:

- GDPR & PCI DSS Test
- Website CMS Security Test
- CSP & HTTP Headers Check
- WordPress & Drupal Scanning

### Mobile App Security Test

Audit your iOS or Android apps for OWASP Mobile Top 10 and other vulnerabilities:

Local mobile app check:

```sh
./iwtools.py mobile /home/user/myapp/build/myapp.apk
```

Remote mobile app check:

```sh
./iwtools.py mobile https://example.com/download/myapp.apk
```

Published mobile app check:

```sh
./iwtools.py mobile https://play.google.com/store/apps/details?id=com.app.my
```

#### Main features:

- iOS/Android Security Test
- OWASP Mobile Top 10 Test
- Mobile App Privacy Check
- Static & Dynamic Mobile Scan

### Dark Web Exposure Test

Monitor and detect your Dark Web exposure, phishing and domain squatting:

```sh
./iwtools.py darkweb https://www.immuniweb.com
```

#### Main features:

- Dark Web Exposure Monitoring
- Phishing Detection and Monitoring
- Domain Squatting Monitoring
- Trademark Infringement Monitoring

### SSL Security Test

Test your servers for security and compliance with PCI DSS, HIPAA & NIST:

Web Server check:

```sh
./iwtools.py ssl immuniweb.com
```

Mail Server check:

```sh
./iwtools.py ssl immuniweb.com:25
```

#### Main features:

- Web Server SSL Test
- Email Server SSL Test
- SSL Certificate Test
- PCI DSS, HIPAA & NIST Test

## Utilization in CI/CD

When executing the script you can specify option `-p` or `--pipeline` parameter, which will compare the results of the 
test with pre-determined results in a configuration file.
This can be done only when using `websec` and `ssl` services.
The result of the comparison can be viewed in the Exit Code of the script.

```sh
./iwtools.py websec https://www.immuniweb.com -p
./iwtools.py ssl https://www.immuniweb.com -p
```

By default, iwtools uses configuration file `config/websec.yaml` for `websec` service, and `config/ssl.yaml` for `ssl`.
You can change the values in these 2 files, or use your own configuration file.
The path to the file will need to be specified upon iwtools' launch:

```sh
./iwtools.py websec https://www.immuniweb.com -cfg config/websec-new.yaml
```

Curretly only `yaml` and `json` formats are supported.
[List of parameters](CONFIG.md) that can be configured.

The script's Exit Code can return one of these 4 status codes:
- 0 - all checks have passed successfully.
- 1 - an error occured.
- 2 - an error occured in the input data.
- 3 - at least one of the checks has failed.

Command line options: [Wiki](https://github.com/ImmuniwebSA/iwtools/blob/main/CLI.md)  
Read more: [ImmuniWeb® Community Edition](https://www.immuniweb.com/free/)

This software is provided "as is" without any warranty of any kind.
By using this software you agree to the Terms of Service: https://www.immuniweb.com/pages/legal.html
By using this software you accept the Privacy Policy: https://www.immuniweb.com/pages/privacy.html
