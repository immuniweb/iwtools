#! /usr/bin/env python3

# Standard libraries
from time import time, strftime, localtime, sleep
import logging
import asyncio

# Third-party libraries
import requests

# Local libraries
from gui.loader import InfiniteLoader
from gui.termcolor import colored


class Email:
    """
    ImmuniWeb® Community Edition: Email Security Test

    ✓ Email Server Security
    ✓ Email Server Encryption
    ✓ DNS Misconfigurations
    ✓ Blacklists & Spam Reports
    ✓ Compromised Credentials
    ✓ Phishing Campaigns
    """

    API_URL = 'https://www.immuniweb.com/email/api/v1'
    USER_AGENT = 'iwtools-0.2'


    def __init__(self, target, api_key=None, recheck=False, quiet=False):
        self.target = target
        self.api_key = api_key
        self.recheck = recheck
        self.quiet = quiet
        self.test_results = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.USER_AGENT,
            'Connection':'close'
        })


    def get_cache_id_or_start_test(self):
        """Get cached test id if exists or start new test"""

        url = f"{self.API_URL}/check/{str(time())}.html"

        data = {
            'domain': self.target,
            'recheck': self.recheck,
            'api_key': self.api_key,
            'show_test_results': 'false'
        }

        response = self.session.post(url, data)
        response.raise_for_status()

        return response.json()


    def get_result_by_test_id(self, test_id):
        """Get result by test id (from cache)"""

        url = f"{self.API_URL}/get_result/{str(time())}.html"

        data = {
            'test_id': test_id
        }

        response = self.session.post(url, data)
        response.raise_for_status()

        return response.json()


    def get_result_by_job_id(self, job_id):
        """Get result by job id (processing)"""

        url = f"{self.API_URL}/get_result/{str(time())}.html"

        data = {
            'job_id': job_id
        }

        response = self.session.post(url, data)
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
            self.wait_test_results(job_id)
        else:
            loop = asyncio.get_event_loop()
            loader = asyncio.ensure_future(self.test_loader('Email Security Test in progress', 'Test completed'))
            response = await loop.run_in_executor(None, self.wait_test_results, job_id)
            loader.cancel()

        self.test_results = response

        return response


    def start(self):
        """Start test"""

        logging.info(
            colored('\nImmuni', 'red', attrs=['bold']) + colored('Web®', 'blue', attrs=['bold']) +
            colored(' Community Edition: Email Security Test\n', attrs=['bold'])
        )

        logging.info(colored('Target: ', attrs=['bold']) + self.target + '\n')

        response = self.get_cache_id_or_start_test()

        if 'error' in response:
            raise Exception(response['error'])

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

        if 'error' in response:
            raise Exception(response['error'])

        self.test_results = response

        return response


    def normalize_color(self, color):
        """Adapt color names to console palette"""

        if color == 'orange':
            return 'yellow'

        return color


    def generate_banner(self, server_color, ssl_color, dns_color, blacklists_color, darkweb_color, phishing_color):
        """Generate beauty banner with test results"""

        return (
            "\n"
            f"{colored('╭───────────────────────────────╮', server_color)} {colored('╭─────────────────────────────────╮', ssl_color)}\n"
            f"{colored('│  Email Server Security        │', server_color)} {colored('│  Email SSL/TLS Encryption       │', ssl_color)}\n"
            f"{colored('╰───────────────────────────────╯', server_color)} {colored('╰─────────────────────────────────╯', ssl_color)}\n"
            f"{colored('╭───────────────────────────────╮', dns_color)} {colored('╭─────────────────────────────────╮', blacklists_color)}\n"
            f"{colored('│  DNS Security                 │', dns_color)} {colored('│  Email Server Blacklists        │', blacklists_color)}\n"
            f"{colored('╰───────────────────────────────╯', dns_color)} {colored('╰─────────────────────────────────╯', blacklists_color)}\n"
            f"{colored('╭───────────────────────────────╮', darkweb_color)} {colored('╭─────────────────────────────────╮', phishing_color)}\n"
            f"{colored('│  Compromised Credentials      │', darkweb_color)} {colored('│  Phishing and Domain Squatting  │', phishing_color)}\n"
            f"{colored('╰───────────────────────────────╯', darkweb_color)} {colored('╰─────────────────────────────────╯', phishing_color)}\n"
        )


    def print_report(self, test_results=None):
        """Generate report"""

        if not test_results:
            test_results = self.test_results

        internals = test_results['internals']
        summary = test_results['summary']
        hostname = internals['hostname']

        server_color = self.normalize_color(summary['server']['color'])
        ssl_color = self.normalize_color(summary['ssl']['color'])
        dns_color = self.normalize_color(summary['dns']['color'])
        blacklists_color = self.normalize_color(summary['blacklists']['color'])
        darkweb_color = self.normalize_color(summary['darkweb']['color'])
        phishing_color = self.normalize_color(summary['phishing']['color'])

        server_text = summary['server']['text']
        ssl_text = summary['ssl']['text']
        dns_text = summary['dns']['text']
        blacklists_text = summary['blacklists']['text']
        darkweb_text = summary['darkweb']['text']
        phishing_text = summary['phishing']['text']

        banner = self.generate_banner(server_color, ssl_color, dns_color, blacklists_color, darkweb_color, phishing_color)

        ts = internals['ts']
        test_time = strftime('%B %d, %Y %H:%M:%S', localtime(ts))

        logging.info(colored("Tested Domain: ", attrs=['bold']) + hostname)
        logging.info(colored("Completed: ", attrs=['bold']) + test_time)
        logging.info(banner)
        logging.info(colored("Email Server Security: ", attrs=['bold']) + colored(server_text, server_color))
        logging.info(colored("Email SSL/TLS Encryption: ", attrs=['bold']) + colored(ssl_text, ssl_color))
        logging.info(colored("DNS Security: ", attrs=['bold']) + colored(dns_text, dns_color))
        logging.info(colored("Email Server Blacklists: ", attrs=['bold']) + colored(blacklists_text, blacklists_color))
        logging.info(colored("Compromised Credentials: ", attrs=['bold']) + colored(darkweb_text, darkweb_color))
        logging.info(colored("Phishing and Domain Squatting: ", attrs=['bold']) + colored(phishing_text, phishing_color))

        # Full Results
        link = self.get_test_link(test_results)
        logging.info(colored("\nCheck Details: ", attrs=['bold'])  + colored(link, 'blue'))


    def get_test_link(self, test_results):
        internals = test_results['internals']
        hostname = internals['hostname']
        short_id = internals['short_id']
        return f"https://www.immuniweb.com/email/{hostname}/{short_id}/"
