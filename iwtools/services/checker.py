from services.services import Services


class Checker:
    """
    Check test results according to configurations.
    Results of the checks are written to the log.
    """

    def __init__(self, service: str):
        self.service = service
        self.logs = []

    def check(self, config: dict, result: dict):
        if self.service == Services.WEBSEC:
            CheckerWebsec().check(config, result, self.logs)
        elif self.service == Services.SSL:
            CheckerSsl().check(config, result, self.logs)
        elif self.service == Services.MOBILE:
            CheckerMobile().check(config, result, self.logs)

    def get_log(self):
        return self.logs


class CheckerWebsec:
    """
    Check Websec test results according to configurations.
    """

    """
    Configuration file keys.
    """
    KEY_MINIMAL_GRADE = 'minimal_grade'  # str
    KEY_PCI_DSS = 'compliance_pci_dss'  # boolean
    KEY_GDPR = 'compliance_gdpr'  # boolean
    KEY_SOFT_OUTDATED = 'max_soft_outdated'  # int
    KEY_SOFT_VULNERABILITIES = 'max_soft_vulnerabilities'  # int
    KEY_HEADERS_ISSUES = 'max_headers_issue'  # int
    KEY_CSP = 'csp_is_set'  # boolean

    ALL_KEYS = [
        KEY_MINIMAL_GRADE,
        KEY_PCI_DSS,
        KEY_GDPR,
        KEY_SOFT_OUTDATED,
        KEY_SOFT_VULNERABILITIES,
        KEY_HEADERS_ISSUES,
        KEY_CSP,
    ]

    def check(self, config: dict, result: dict, logs: list):

        CheckerUtils.check_grade(config, self.KEY_MINIMAL_GRADE, result['grade'], logs)

        if self.KEY_PCI_DSS in config:
            pci_dss = result['compliance_pci_dss']
            config_value = config[self.KEY_PCI_DSS]
            passed = (pci_dss == config_value)
            log = {'key': self.KEY_PCI_DSS, 'passed': passed}
            if not passed:
                log['msg'] = "Compliance PCI DSS: expected '{}' insted of '{}'".format(config_value, pci_dss)
            logs.append(log)

        if self.KEY_GDPR in config:
            gdpr = result['compliance_gdpr']
            config_value = config[self.KEY_GDPR]
            passed = (gdpr == config_value)
            log = {'key': self.KEY_GDPR, 'passed': passed}
            if not passed:
                log['msg'] = "Compliance GDPR: expected '{}' insted of '{}'".format(config_value, gdpr)
            logs.append(log)

        if self.KEY_SOFT_OUTDATED in config:
            outdated = result['http_additional_info']['app_scan']['result']['stats']['outdated']
            config_value = config[self.KEY_SOFT_OUTDATED]
            passed = (outdated <= config_value)
            log = {'key': self.KEY_SOFT_OUTDATED, 'passed': passed}
            if not passed:
                log['msg'] = "Web Software Outdated: {} found, expected no more than {}".format(outdated, config_value)
            logs.append(log)

        if self.KEY_SOFT_VULNERABILITIES in config:
            vulnerabilities = result['http_additional_info']['app_scan']['result']['stats']['vulnerabilities']
            config_value = config[self.KEY_SOFT_VULNERABILITIES]
            passed = (vulnerabilities <= config_value)
            log = {'key': self.KEY_SOFT_VULNERABILITIES, 'passed': passed}
            if not passed:
                log['msg'] = "Web Software Vulnerabilities: {} found, expected no more than {}"\
                    .format(vulnerabilities, config_value)
            logs.append(log)

        headers_issues = result['internals']['scores']['http_headers']['description'].lower()
        CheckerUtils.check_issue_cnt(config, self.KEY_HEADERS_ISSUES, headers_issues, logs, 'Headers Security Test')

        if self.KEY_CSP in config:
            csp_status = result['internals']['scores']['csp']['description'].lower()
            csp_is_set = not (csp_status == 'missing')
            config_value = config[self.KEY_CSP]
            passed = csp_is_set == config_value
            log = {'key': self.KEY_CSP, 'passed': passed}
            if not passed:
                is_str = 'is not' if config_value else 'is'
                log['msg'] = "CSP {} set".format(is_str)
            logs.append(log)


class CheckerSsl:
    """
    Check SSL test results according to configurations.
    """

    """
    Configuration file keys.
    """
    KEY_MINIMAL_GRADE = 'minimal_grade'  # str
    KEY_PCI_DSS = 'max_pci_dss_issues'  # int
    KEY_HIPAA = 'max_hipaa'  # int
    KEY_NIST = 'max_nist'  # int
    KEY_PRACTISES = 'max_best_practises_issues'  # int
    ALL_KEYS = [
        KEY_MINIMAL_GRADE,
        KEY_PCI_DSS,
        KEY_HIPAA,
        KEY_NIST,
        KEY_PRACTISES,
    ]

    def check(self, config: dict, result: dict, logs: list):
        CheckerUtils.check_grade(config, self.KEY_MINIMAL_GRADE, result['results']['grade'], logs)

        scores = result['internals']['scores']

        pci_dss = scores['pci_dss']['description']
        CheckerUtils.check_issue_cnt(config, self.KEY_PCI_DSS, pci_dss, logs, 'PCI DSS')

        hipaa = scores['hipaa']['description']
        CheckerUtils.check_issue_cnt(config, self.KEY_HIPAA, hipaa, logs, 'HIPAA')

        nist = scores['nist']['description']
        CheckerUtils.check_issue_cnt(config, self.KEY_NIST, nist, logs, 'NIST')

        practices = scores['industry_best_practices']['description']
        CheckerUtils.check_issue_cnt(config, self.KEY_PRACTISES, practices, logs, 'Industry Best Practices')


class CheckerMobile:
    """
    Check Mobile App test results according to configurations.
    """

    """
    Configuration file keys.
    """
    KEY_PRIVACY_NORMAL = 'max_privacy_normal'  # int
    KEY_PRIVACY_DANGEROUS = 'max_pci_dss_issues'  # int

    KEY_CRITICAL_RISK = 'max_critical'  # int
    KEY_HIGH_RISK = 'max_high'  # int
    KEY_MEDIUM_RISK = 'max_medium'  # int
    KEY_LOW_RISK = 'max_low'  # int
    KEY_WARNING = 'max_warning'  # int
    KEY_RISK_TOTAL = 'max_risk_total'  # int

    ALL_KEYS = [
        KEY_PRIVACY_NORMAL,
        KEY_PRIVACY_DANGEROUS,
        KEY_CRITICAL_RISK,
        KEY_HIGH_RISK,
        KEY_MEDIUM_RISK,
        KEY_LOW_RISK,
        KEY_WARNING,
        KEY_RISK_TOTAL
    ]

    def check(self, config: dict, result: dict, logs: list):
        pass
        # risks = self.calc_risk(result)

    def calc_risk(self, data):
        try:
            sastVulns = data['data']['test_sast']['vulns']
            dastVulns = data['data']['test_dast']['vulns']
        except Exception:
            raise Exception('Incorrect response format for risk calculation')

        risk = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'warning': 0,
            'low': 0,
            # 'intel':  0,
        }

        for key in sastVulns:
            level = sastVulns[key]['information']['level']
            risk[level] += 1

        for key in dastVulns:
            level = dastVulns[key]['information']['level']
            risk[level] += 1

        return risk


class CheckerUtils:
    """
    Common methods for checking test result.
    """
    @staticmethod
    def check_grade(config: dict, key: str, grade: str, logs: list):
        if key in config:
            grades = ['N', 'F', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A', 'A+']
            config_value = config[key]
            min_grade_i = grades.index(config_value)
            grade_i = grades.index(grade)
            passed = grade_i >= min_grade_i
            log = {'key': key, 'passed': passed}
            if not passed:
                log['msg'] = "Grade: '{}' is less than '{}'".format(grade, config_value)
            logs.append(log)

    @staticmethod
    def check_issue_cnt(config: dict, key: str, value: str, logs: list, title: str):
        if key not in config:
            return

        value_num = 0
        if value.find('issue found') != -1 or value.find('issues found') != -1:
            try:
                value_num = int(value[0:value.find(' ')])
            except ValueError:
                pass
        expected = config[key]
        passed = value_num <= expected
        log = {'key': key, 'passed': passed}

        if not passed:
            issues_str = 'issue'
            if value_num > 0:
                issues_str = 'issues'
            log['msg'] = "{}: {} {} found, expected no more than {}".format(title, value_num, issues_str, expected)
        logs.append(log)
