# iwtools — ImmuniWeb® Community Edition CLI

<p align="center">
  <img src="logo.png" alt="iwtools logo">
</p>

Simple CLI interface to leverage [ImmuniWeb® Community Edition](https://www.immuniweb.com/free/) free tools in CI/CD
pipelines and DevOps.

## Prepare

Create virtual environment and install dependencies. Python >= 3.7 required.

```sh
git clone https://github.com/immuniweb/iwtools.git
cd iwtools/iwtools
python3 -m venv env
source ./env/bin/activate
pip install -r requirements.txt
```

Instead of preparing and configuring the environment yourself, you can use our
[Docker Image](https://hub.docker.com/r/immuniweb/iwtools).

## Usage

### Email Security Test

Test your email server security, encryption, configurations and privacy:

```sh
./iwtools.py email immuniweb.com
```

#### Main features:

- Email Server Security Test
- Email Server Encryption Test
- DNS Misconfigurations Test
- Phishing Campaigns Detection
- Compromised Credentials Detection
- Black & Spam Lists Presence Detection

### Website Security Test

Test your website security vulnerabilities, privacy issues, GDPR and PCI DSS compliance:

```sh
./iwtools.py websec https://www.immuniweb.com
```

#### Main features:

- Web Software Detection
- Website Vulnerability Scan
- WordPress & Drupal Scanning
- Website Privacy Check
- HTTP Headers & CSP Test
- AI Bot Protection Test

### Mobile App Security Test

Test your iOS or Android mobile apps for OWASP Mobile Top 10 and other vulnerabilities:

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

- iOS App Security Test
- Android App Security Test
- OWASP Mobile Top 10 Scan
- Mobile Security Test
- Mobile App Privacy Test
- Software Composition Analysis

### Dark Web and Threat Exposure Test

Discover your data leaks on the Dark Web and get your cyber threat exposure report:

```sh
./iwtools.py darkweb www.immuniweb.com
```

#### Main features:

- Dark Web Exposure Monitoring
- Phishing & Scam Websites Detection
- Cloud Exposure & Incidents Monitoring
- Trademark Infringement Monitoring
- Cyber & Typo Squatting Domains Detection
- Fake Accounts in Social Networks Detection

### SSL Security Test

Test SSL/TLS of your web or email servers for security, PCI DSS, HIPAA & NIST compliance:

Web Server check:

```sh
./iwtools.py ssl immuniweb.com:443
```

Mail Server check:

```sh
./iwtools.py ssl immuniweb.com:25
```

#### Main features:

- Web Server SSL/TLS Security
- Email Server SSL/TLS Security
- SSL Certificate Test Validity
- Post-Quantum Cryptography (PQC) Readiness
- PCI DSS, HIPAA & NIST Compliance
- Best-Practices Compliance

## Utilization in CI/CD

When executing the script you can specify option `-p` or `--pipeline` parameter, which will compare the results of the
test with pre-determined results in a configuration file.
This can be done only when using `websec`, `ssl` and `email` services.
The result of the comparison can be viewed in the Exit Code of the script.

```sh
./iwtools.py email immuniweb.com -p
./iwtools.py websec https://www.immuniweb.com -p
./iwtools.py ssl www.immuniweb.com:443 -p
```

By default, iwtools uses configuration file `config/email.yaml` for `email` service,
`config/websec.yaml` for `websec` service, and `config/ssl.yaml` for `ssl`.
You can change the values in these 3 files, or use your own configuration file.
The path to the file will need to be specified upon iwtools' launch:

```sh
./iwtools.py websec https://www.immuniweb.com -cfg config/websec-new.yaml
```

Currently only `yaml` and `json` formats are supported.
[List of parameters](CONFIG.md) that can be configured.

The script's Exit Code can return one of these 4 status codes:
- 0 - all checks have passed successfully.
- 1 - an error occured.
- 2 - an error occured in the input data.
- 3 - at least one of the checks has failed.

Command line options: [documentation](https://github.com/immuniweb/iwtools/blob/main/CLI.md)
Read more: [ImmuniWeb® Community Edition](https://www.immuniweb.com/free/)

This software is provided "as is" without any warranty of any kind.
By using this software you agree to the Terms of Service: https://www.immuniweb.com/pages/legal.html
By using this software you accept the Privacy Policy: https://www.immuniweb.com/pages/privacy.html
