#! /usr/bin/env python3

# Standard libraries
from time import time, strftime, localtime, sleep
import logging
import asyncio
import sys
import re

# Third-party libraries
from termcolor import colored
import requests

# Local libraries
from gui.loader import InfiniteLoader
from gui.scores import scores


class Websec:
    """
    ImmuniWeb® Community Edition: Website Security Test

    ✓ GDPR & PCI DSS Test
    ✓ Website CMS Security Test
    ✓ CSP & HTTP Headers Check
    ✓ WordPress & Drupal Scanning
    """

    API_URL = 'https://www.immuniweb.com/websec/api/v1'
    USER_AGENT = 'iwtools-0.1'

    # Check groups names
    groups = {
        'http_headers': 'HTTP Headers Security',
        'http_cookies': 'Cookies Security',
        'app_scan': 'Software Security',
    }

    test_results = None


    def __init__(self, target, ip='any', api_key=None, recheck=False, quiet=False):
        self.target = target
        self.ip = ip
        self.api_key = api_key
        self.recheck = recheck
        self.quiet = quiet


    def get_cache_id_or_start_test(self):
        """Get cached test id if exists or start new test"""

        url = f"{self.API_URL}/chsec/{str(time())}.html"

        data = {
            'tested_url': self.target,
            'choosen_ip': self.ip,
            'recheck': self.recheck,
            'api_key': self.api_key,
            'dnsr': 'on'
        }

        response = requests.post(url, data)
        response.raise_for_status()

        return response.json()


    def get_result_by_test_id(self, test_id):
        """Get result by test id (from cache)"""

        url = f"{self.API_URL}/get_result/{str(time())}.html"

        data = {
            'id': test_id
        }

        response = requests.post(url, data)
        response.raise_for_status()

        return response.json()


    def get_result_by_job_id(self, job_id):
        """Get result by job id (processing)"""

        url = f"{self.API_URL}/get_result/{str(time())}.html"

        data = {
            'job_id': job_id
        }

        response = requests.post(url, data)
        response.raise_for_status()

        return response.json()


    async def test_loader(self, start_message, cancel_message):
        """Print loading status while test rinning"""

        loader = InfiniteLoader(len(start_message))

        row_up = "\x1B[3A"
        row_clear = "\x1B[0K"
        step = 0

        logging.info(colored(start_message, 'blue'))

        # Draw loader
        print('\n\n\n')
        while True:
            print(row_up + loader.generate(step) + row_clear)
            print('\n' + row_clear)

            step += 1
            try:
                await asyncio.sleep(.1)
            except asyncio.CancelledError:
                logging.info(colored(row_up + row_clear + row_up + row_clear + '\n' + row_clear + cancel_message + '\n' , 'blue'))
                break


    def wait_test_results(self, job_id):
        """Wait until the completion of test"""

        response = {
            'status': 'in_progress'
        }

        while 'status' in response and response['status'] == 'in_progress':
            response = self.get_result_by_job_id(job_id)
            sleep(10)

        return response


    async def watch(self, job_id):
        """Check test status until complete"""

        if self.quiet or logging.root.level == logging.DEBUG:
            response = self.wait_test_results(job_id)
        else:
            loop = asyncio.get_event_loop()
            loader = asyncio.ensure_future(self.test_loader('Website Security Test in progress', 'Test completed'))
            response = await loop.run_in_executor(None, self.wait_test_results, job_id)
            loader.cancel()

        self.test_results = response

        return response


    def start(self):
        """Start test"""

        logging.info(
            colored('\nImmuni', 'red', attrs=['bold']) + colored('Web®', 'blue', attrs=['bold']) +
            colored(' Community Edition: Website Security Test\n', attrs=['bold'])
        )

        logging.info(colored('Target: ', attrs=['bold']) + self.target)
        logging.info(colored('IP Address: ', attrs=['bold']) + (self.ip if self.ip != 'any' else 'Not specified') + '\n')

        response = self.get_cache_id_or_start_test()

        if 'error' in response:
            raise Exception(response['error'])

        if 'multiple_ips' in response:
            raise Exception('Passed IP was not resolved')

        if response['status'] == 'test_started':
            loop = asyncio.get_event_loop()
            response = loop.run_until_complete(self.watch(response['job_id']))
            loop.close()

        elif response['status'] == 'test_cached':
            logging.info(colored('Result was found in cache, preparing the report…\n', 'blue'))

            try:
                response = self.get_result_by_test_id(response['test_id'])
            except:
                logging.error(colored('Error while HTTP request, aborting…', 'red'))
                raise

        self.test_results = response

        return response


    def parse_highlight(self, highlight):
        """Parse highlight status from string"""

        status_code = 4

        parsed = re.search('^(.+) \[(\d+)\]$', highlight)

        if parsed:
           status_code = int(parsed.group(2))
           highlight = parsed.group(1)

        if status_code == 0:
            result = {
                'title': 'Empty',
                'level': 'info',
                'color': 'green',
            }
        elif status_code == 1:
            result = {
                'title': 'Good configuration',
                'level': 'info',
                'color': 'green',
            }
        elif status_code == 4:
            result = {
                'title': 'Information',
                'level': 'info',
                'color': 'blue',
            }
        elif status_code in [2,3,5,6]:
            result = {
                'title': 'Misconfiguration or Weakness',
                'level': 'warning',
                'color': 'yellow',
            }

        result['text'] = highlight

        return result


    def get_grade_color(self, grade):
        """Get status color depend on grade"""

        if grade in ['a+', 'a', 'a-']:
            grade_color = 'green'
        elif grade in ['b+', 'b', 'b-']:
            grade_color = 'yellow'
        elif grade in ['c+', 'c', 'f']:
            grade_color = 'red'
        else:
            grade_color = 'blue'

        return grade_color


    def normalize_color(self, color):
        """Adapt color names to console palette"""

        if color == 'orange':
            return 'yellow'

        return color


    def generate_banner(self, grade, grade_color, pci_dss_color, eu_gdpr_color, csp_pol_color, appscan_color, headers_color):
        """Generate beauty banner with test results"""

        # Grade letter icon
        score = scores[grade]

        return (
            "\n"
            f"{colored('╭───────────────────╮', grade_color)} {colored('╭───────────╮', pci_dss_color)} {colored('╭───────────────────────────────╮', appscan_color)}\n"
            f"{colored('│   '+ score[0] +'  │', grade_color)} {colored('│  PCI DSS  │', pci_dss_color)} {colored('│    Software Security Test     │', appscan_color)}\n"
            f"{colored('│   '+ score[1] +'  │', grade_color)} {colored('╰───────────╯', pci_dss_color)} {colored('╰───────────────────────────────╯', appscan_color)}\n"
            f"{colored('│   '+ score[2] +'  │', grade_color)} {colored('╭───────────╮', eu_gdpr_color)} {colored('╭───────────────────────────────╮', headers_color)}\n"
            f"{colored('│   '+ score[3] +'  │', grade_color)} {colored('│  EU GDPR  │', eu_gdpr_color)} {colored('│     Headers Security Test     │', headers_color)}\n"
            f"{colored('│   '+ score[4] +'  │', grade_color)} {colored('╰───────────╯', eu_gdpr_color)} {colored('╰───────────────────────────────╯', headers_color)}\n"
            f"{colored('│   '+ score[5] +'  │', grade_color)} {colored('╭───────────╮', csp_pol_color)}\n"
            f"{colored('│                   │', grade_color)} {colored('│    CSP    │', csp_pol_color)}\n"
            f"{colored('╰───────────────────╯', grade_color)} {colored('╰───────────╯', csp_pol_color)}\n"
        )


    def print_report(self, test_results=None):
        """Generate report"""

        if not test_results:
            test_results = self.test_results

        grade = test_results['grade'].lower()
        grade_color = self.get_grade_color(grade)

        pci_dss_color = self.normalize_color(test_results['internals']['scores']['pci_dss']['class'])
        eu_gdpr_color = self.normalize_color(test_results['internals']['scores']['gdpr']['class'])
        csp_pol_color = self.normalize_color(test_results['internals']['scores']['csp']['class'])
        appscan_color = self.normalize_color(test_results['internals']['scores']['app_scan']['class'])
        headers_color = self.normalize_color(test_results['internals']['scores']['http_headers']['class'])

        banner = self.generate_banner(grade, grade_color, pci_dss_color, eu_gdpr_color, csp_pol_color, appscan_color, headers_color)

        test_time = strftime('%B %d, %Y %H:%M:%S', localtime(test_results['ts']))

        # Test is outdated if older than 1 week
        test_time_color = None
        if int(time()) - test_results['ts'] > 604800:
            test_time_color = 'yellow'

        logging.info(colored("Source URL: ", attrs=['bold']) + test_results['source_url'])
        logging.info(colored("Tested URL: ", attrs=['bold']) + test_results['tested_url'])
        logging.info(colored("Tested IP Address: ", attrs=['bold']) + test_results['server_ip'])
        logging.info(colored("Completed: ", attrs=['bold']) + test_time)
        logging.info(banner)
        logging.info(colored("Grade: ", attrs=['bold']) + colored(test_results['grade'], grade_color, attrs=['bold']))
        logging.info(colored("PCI DSS Compliance Test: ", attrs=['bold'])  + colored(test_results['internals']['scores']['pci_dss']['description'].title(), pci_dss_color))
        logging.info(colored("EU GDPR Compliance Test: ", attrs=['bold'])  + colored(test_results['internals']['scores']['gdpr']['description'].title(), eu_gdpr_color))
        logging.info(colored("Content Security Policy Test: ", attrs=['bold'])  + colored(test_results['internals']['scores']['csp']['description'].title(), csp_pol_color))
        logging.info(colored("Software Security Test: ", attrs=['bold'])  + colored(test_results['internals']['scores']['app_scan']['description'].title(), appscan_color))
        logging.info(colored("Headers Security Test: ", attrs=['bold'])  + colored(test_results['internals']['scores']['http_headers']['description'].title(), headers_color))

        if test_results['global_highlights']:
            logging.info(colored("\nNotes:", attrs=['bold']))

        # Global Highlights
        for highlight in test_results['global_highlights']:
            # A little bit messed. Global highlights may be dict with HTML-formatted text
            # TODO: print both types
            if not type(highlight) is str:
                continue
            highlight = self.parse_highlight(highlight)
            logging.info(colored(f"[{highlight['title']}]", highlight['color']) + ' ' + highlight['text'])


        # Local Highlights
        local_highlights = {}
        for highlight in test_results['highlights']:
            location = highlight['location']
            highlight = self.parse_highlight(highlight['highlight'])

            if not location in local_highlights:
                local_highlights[location] = []

            local_highlights[location].append(highlight)

        for group in local_highlights:
            logging.info(colored(f"\n{self.groups[group]} Notes:", attrs=['bold']))

            for highlight in local_highlights[group]:
                logging.info(colored(f"[{highlight['title']}]", highlight['color']) + f" {highlight['text']}")

        # Full Results
        logging.info(colored("\nCheck Details: ", attrs=['bold'])  + colored(f"https://www.immuniweb.com/websec/{test_results['unicode_hostname']}/{test_results['short_id']}/", 'blue'))
