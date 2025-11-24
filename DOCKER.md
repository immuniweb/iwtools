# iwtools — ImmuniWeb® Community Edition CLI

Simple CLI interface to leverage [ImmuniWeb® Community Edition](https://www.immuniweb.com/free/) free tools in CI/CD 
pipelines and DevOps.

## Usage

### Email Security Test

Test your email server security, encryption, configurations and privacy:

```sh
docker run immuniweb/iwtools email immuniweb.com
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
docker run immuniweb/iwtools websec https://www.immuniweb.com
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
docker run --volume /{path-to-your-app}/:/app/myapp/ immuniweb/iwtools mobile /app/myapp/myapp.apk
```

Remote mobile app check:

```sh
docker run immuniweb/iwtools mobile https://example.com/download/myapp.apk
```

Published mobile app check:

```sh
docker run immuniweb/iwtools mobile https://play.google.com/store/apps/details?id=com.app.my
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
docker run immuniweb/iwtools darkweb www.immuniweb.com
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
docker run immuniweb/iwtools ssl immuniweb.com:443
```

Mail Server check:

```sh
docker run immuniweb/iwtools ssl immuniweb.com:25
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
This can be done only when using `email`, `websec` and `ssl` services.
The result of the comparison can be viewed in the Exit Code of the script.

```sh
docker run immuniweb/iwtools email immuniweb.com -p
docker run immuniweb/iwtools websec https://www.immuniweb.com -p
docker run immuniweb/iwtools ssl www.immuniweb.com:443 -p
```

In order to use a custom configuration file, you need to mount volume, which will contain the new file.
If the name of the configuration file is different from the default `config/email.yaml`, `config/websec.yaml` or
`config/ssl.yaml` ones, then you need to specify the new name via the `-cfg config/{new-file-name}` parameter.

```sh
docker run --volume /{path-to-config}/:/app/config/ immuniweb/iwtools websec https://www.immuniweb.com -p -cfg config/websec-new.yaml
```

Curretly only `yaml` and `json` formats are supported.
[List of parameters](https://github.com/immuniweb/iwtools/blob/main/CONFIG.md) that can be configured.

The docker's Exit Code can return one of these 4 status codes:
- 0 - all checks have passed successfully.
- 1 - an error occured.
- 2 - an error occured in the input data.
- 3 - at least one of the checks has failed.

### API key's utilization

The API key can be prepared for using upon Docker's launch via the `--api-key API_KEY` parameter,
or by mounting volume, which will contain a file with the key.
In this case, you will need to use `--api-keyfile API_KEYFILE` parameter.

```sh
 docker run --volume /{path-to-key-folder}/:/app/config/ immuniweb/iwtools websec https://www.immuniweb.com -p -r --api-keyfile config/api-key.txt
```

Command line options: [documentation](https://github.com/immuniweb/iwtools/blob/main/CLI.md)
Read more: [ImmuniWeb® Community Edition](https://www.immuniweb.com/free/)

This software is provided "as is" without any warranty of any kind.
By using this software you agree to the Terms of Service: https://www.immuniweb.com/pages/legal.html
By using this software you accept the Privacy Policy: https://www.immuniweb.com/pages/privacy.html
