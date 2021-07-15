#! /usr/bin/env python3

# Standard libraries
from time import time, strftime, localtime, sleep
from urllib.parse import urlparse
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


class Ssl:
    """
    ImmuniWeb® Community Edition: SSL Security Test

    ✓ Web Server SSL Test
    ✓ Email Server SSL Test
    ✓ SSL Certificate Test
    ✓ PCI DSS, HIPAA & NIST Test
    """

    API_URL = 'https://www.immuniweb.com/ssl/api/v1'
    USER_AGENT = 'iwtools-0.1'

    highlight_titles = [
        'Empty',
        'Good configuration',
        'Non-compliant with NIST guidelines',
        'Misconfiguration or weakness',
        'Information',
        'Non-compliant with PCI DSS requirements',
        'Non-compliant with PCI DSS and NIST',
        'Not vulnerable',
        'Deprecated. Dropped since June 2018',
        'Non-compliant with HIPAA guidance',
        'Non-compliant with HIPAA and NIST',
        'Non-compliant with PCI DSS and HIPAA',
        'Non-compliant with PCI DSS, HIPAA and NIST',
        'No Encryption'
    ]

    test_results = None


    def __init__(self, target, ip='any', api_key=None, recheck=False, quiet=False):
        self.target = target
        self.ip = ip
        self.api_key = api_key
        self.recheck = recheck
        self.quiet = quiet


    def get_cache_id_or_start_test(self):
        """Get cached test id if exists or start new test"""

        url = f"{self.API_URL}/check/{str(time())}.html"

        data = {
            'domain': self.target,
            'choosen_ip': self.ip,
            'recheck': self.recheck,
            'api_key': self.api_key,
            'show_test_results': 'false'
        }

        response = requests.post(url, data)
        response.raise_for_status()

        return response.json()


    def get_result_by_test_id(self, test_id):
        """Get result by test id (from cache)"""

        url = f"{self.API_URL}/get_result/{str(time())}.html"

        data = {
            'id': test_id,
            'verbosity': 1
        }

        response = requests.post(url, data)
        response.raise_for_status()

        return response.json()


    def get_result_by_job_id(self, job_id):
        """Get result by job id (processing)"""

        url = f"{self.API_URL}/get_result/{str(time())}.html"

        data = {
            'job_id': job_id,
            'verbosity': 1
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

        return response


    async def watch(self, job_id):
        """Check test status until complete"""

        if self.quiet:
            response = self.wait_test_results(job_id)
        else:
            loop = asyncio.get_event_loop()
            loader = asyncio.ensure_future(self.test_loader('SSL Security Test in progress', 'Test completed'))
            response = await loop.run_in_executor(None, self.wait_test_results, job_id)
            loader.cancel()

        self.test_results = response

        return response


    def start(self):
        """Start test"""

        logging.info(
            colored('\nImmuni', 'red', attrs=['bold']) + colored('Web®', 'blue', attrs=['bold']) +
            colored(' Community Edition: SSL Security Test\n', attrs=['bold'])
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
        """Parse highlight status from dict"""

        result = {}

        tag = highlight['tag']

        if tag == 4:
            result['level'] = 'info'
            result['color'] = 'blue'
        if tag in [0, 1, 7, 8]:
            result['level'] = 'info'
            result['color'] = 'green'
        elif tag in [12, 11, 6, 5, 10, 9, 2, 3, 13]:
            result['level'] = 'warning'
            result['color'] = 'yellow'

        result['title'] = self.highlight_titles[tag]
        result['text'] = highlight['highlight']

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


    def generate_banner(self, grade, grade_color, hipaa_color, nist_color, pci_dss_color, ibp_color):
        """Generate beauty banner with test results"""

        # Grade letter icon
        score = scores[grade]

        return (
            "\n"
            f"{colored('╭───────────────────╮', grade_color)} {colored('╭───────────╮', hipaa_color)} {colored('╭───────────────────────────────╮', ibp_color)}\n"
            f"{colored('│   '+ score[0] +'  │', grade_color)} {colored('│   HIPAA   │', hipaa_color)} {colored('│    Industry Best Practices    │', ibp_color)}\n"
            f"{colored('│   '+ score[1] +'  │', grade_color)} {colored('╰───────────╯', hipaa_color)} {colored('╰───────────────────────────────╯', ibp_color)}\n"
            f"{colored('│   '+ score[2] +'  │', grade_color)} {colored('╭───────────╮', nist_color)}\n"
            f"{colored('│   '+ score[3] +'  │', grade_color)} {colored('│    NIST   │', nist_color)}\n"
            f"{colored('│   '+ score[4] +'  │', grade_color)} {colored('╰───────────╯', nist_color)}\n"
            f"{colored('│   '+ score[5] +'  │', grade_color)} {colored('╭───────────╮', pci_dss_color)}\n"
            f"{colored('│                   │', grade_color)} {colored('│  PCI DSS  │', pci_dss_color)}\n"
            f"{colored('╰───────────────────╯', grade_color)} {colored('╰───────────╯', pci_dss_color)}\n"
        )


    def print_report(self, test_results=None):
        """Generate report"""

        if not test_results:
            test_results = self.test_results

        grade = test_results['results']['grade'].lower()
        grade_color = self.get_grade_color(grade)

        hipaa_color = self.normalize_color(test_results['internals']['scores']['hipaa']['class'])
        nist_color = self.normalize_color(test_results['internals']['scores']['nist']['class'])
        pci_dss_color = self.normalize_color(test_results['internals']['scores']['pci_dss']['class'])
        ibp_color = self.normalize_color(test_results['internals']['scores']['industry_best_practices']['class'])

        banner = self.generate_banner(grade, grade_color, hipaa_color, nist_color, pci_dss_color, ibp_color)

        test_time = strftime('%B %d, %Y %H:%M:%S', localtime(test_results['internals']['ts']))

        # Test is outdated if older than 1 week
        test_time_color = None
        if int(time()) - test_results['internals']['ts'] > 604800:
            test_time_color = 'yellow'

        logging.info(colored("Tested Hostname: ", attrs=['bold']) + test_results['server_info']['unicode_hostname']['value'])
        logging.info(colored("Tested IP Address: ", attrs=['bold']) + test_results['server_info']['ip']['value'])
        logging.info(colored("Completed: ", attrs=['bold']) + colored(test_time, test_time_color))
        logging.info(banner)
        logging.info(colored("Grade: ", attrs=['bold']) + colored(test_results['results']['grade'], grade_color, attrs=['bold']))
        logging.info(colored("HIPAA Compliance Test: ", attrs=['bold'])  + colored(test_results['internals']['scores']['hipaa']['description'].title(), hipaa_color))
        logging.info(colored("NIST Compliance Test: ", attrs=['bold'])  + colored(test_results['internals']['scores']['nist']['description'].title(), hipaa_color))
        logging.info(colored("PCI DSS Compliance Test: ", attrs=['bold'])  + colored(test_results['internals']['scores']['pci_dss']['description'].title(), hipaa_color))
        logging.info(colored("Industry Best Practices: ", attrs=['bold'])  + colored(test_results['internals']['scores']['industry_best_practices']['description'].title(), nist_color))

        # Clean system highlights
        highlights = []

        for highlight in test_results['highlights']:
            if highlight['highlight_id'] == 32:
                continue
            highlights.append(highlight)

        if highlights:
            logging.info(colored("\nNotes:", attrs=['bold']))

        # Global Highlights
        for highlight in highlights:
            highlight = self.parse_highlight(highlight)
            logging.info(colored(f"[{highlight['title']}]", highlight['color']) + ' ' + highlight['text'])

        # Full Results
        logging.info(colored("\nCheck Details: ", attrs=['bold']) + colored(f"https://www.immuniweb.com/ssl/{test_results['server_info']['unicode_hostname']['value']}/{test_results['internals']['short_id']}/", 'blue'))
