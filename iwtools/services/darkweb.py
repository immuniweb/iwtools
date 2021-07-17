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


class Darkweb:
    """
    ImmuniWeb® Community Edition: Dark Web Exposure Test

    ✓ Dark Web Exposure Monitoring
    ✓ Phishing Detection and Monitoring
    ✓ Domain Squatting Monitoring
    ✓ Trademark Infringement Monitoring
    """

    API_URL = 'https://www.immuniweb.com/darkweb/api/v1'
    USER_AGENT = 'iwtools-0.1'


    def __init__(self, target, api_key=None, recheck=False, quiet=False):
        self.target = target
        self.api_key = api_key
        self.recheck = recheck
        self.quiet = quiet
        self.test_results = None
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.USER_AGENT})


    def get_cache_id_or_start_test(self):
        """Get cached test id if exists or start new test"""

        url = f"{self.API_URL}/scan/{str(time())}.html"

        data = {
            'domain': self.target,
            'recheck': self.recheck,
            'api_key': self.api_key,
            'no_limit': 1,
            'dnsr': 'on'
        }

        response = self.session.post(url, data)
        response.raise_for_status()

        return response.json()


    def get_result_by_test_id(self, test_id):
        """Get result by test id (from cache)"""

        url = f"{self.API_URL}/get_result/{str(time())}.html"

        data = {
            'id': test_id
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
            loader = asyncio.ensure_future(self.test_loader('Dark Web Exposure Test in progress', 'Test completed'))
            response = await loop.run_in_executor(None, self.wait_test_results, job_id)
            loader.cancel()

        self.test_results = response

        return response


    def start(self):
        """Start test"""

        logging.info(
            colored('\nImmuni', 'red', attrs=['bold']) + colored('Web®', 'blue', attrs=['bold']) +
            colored(' Community Edition: Dark Web Exposure Test\n', attrs=['bold'])
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


    def generate_banner(self, dark_web_color, phishing_color, cybersquatting_color, typosquatting_color, fake_accounts_color):
        """Generate beauty banner with test results"""

        return (
            "\n"
            f"{colored('╭───────────────────────────────╮', dark_web_color)} {colored('╭─────────────────────────────────╮', fake_accounts_color)}\n"
            f"{colored('│  Dark Web Security Incidents  │', dark_web_color)} {colored('│  Fake Accounts in Social Media  │', fake_accounts_color)}\n"
            f"{colored('╰───────────────────────────────╯', dark_web_color)} {colored('╰─────────────────────────────────╯', fake_accounts_color)}\n"
            f"{colored('╭───────────────────────────────╮', cybersquatting_color)} {colored('╭──────────────────────────────╮', typosquatting_color)}\n"
            f"{colored('│  Cybersquatting Domain Names  │', cybersquatting_color)} {colored('│  Typosquatting Domain Names  │', typosquatting_color)}\n"
            f"{colored('╰───────────────────────────────╯', cybersquatting_color)} {colored('╰──────────────────────────────╯', typosquatting_color)}\n"
            f"{colored('╭───────────────────────────────╮', phishing_color)}\n"
            f"{colored('│  Phishing Websites and Pages  │', phishing_color)}\n"
            f"{colored('╰───────────────────────────────╯', phishing_color)}\n"
        )


    def print_report(self, test_results=None):
        """Generate report"""

        if not test_results:
            test_results = self.test_results

        dark_web_color = self.normalize_color(test_results['internals']['scores']['dark_web']['class'])
        phishing_color = self.normalize_color(test_results['internals']['scores']['phishing']['class'])
        fake_accounts_color = self.normalize_color(test_results['internals']['scores']['social_networks']['class'])
        typosquatting_color = self.normalize_color(test_results['internals']['scores']['typosquatting']['class'])
        cybersquatting_color = self.normalize_color(test_results['internals']['scores']['cybersquatting']['class'])

        banner = self.generate_banner(dark_web_color, phishing_color, cybersquatting_color, typosquatting_color, fake_accounts_color)

        test_time = strftime('%B %d, %Y %H:%M:%S', localtime(test_results['assesment_date']))

        # Test is outdated if older than 1 week
        test_time_color = None
        if int(time()) - test_results['assesment_date'] > 604800:
            test_time_color = 'yellow'

        logging.info(colored("Tested Domain: ", attrs=['bold']) + test_results['orig_url'])
        logging.info(colored("Completed: ", attrs=['bold']) + test_time)
        logging.info(banner)
        logging.info(colored("Dark Web Security Incidents: ", attrs=['bold'])  + colored(test_results['internals']['scores']['dark_web']['description'].title(), dark_web_color))
        logging.info(colored("Phishing Websites and Pages: ", attrs=['bold'])  + colored(test_results['internals']['scores']['phishing']['description'].title(), phishing_color))
        logging.info(colored("Cybersquatting Domain Names: ", attrs=['bold'])  + colored(test_results['internals']['scores']['cybersquatting']['description'].title(), cybersquatting_color))
        logging.info(colored("Typosquatting Domain Names: ", attrs=['bold'])  + colored(test_results['internals']['scores']['typosquatting']['description'].title(), typosquatting_color))
        logging.info(colored("Fake Accounts in Social Media: ", attrs=['bold'])  + colored(test_results['internals']['scores']['social_networks']['description'].title(), fake_accounts_color))

        # Full Results
        logging.info(colored("\nCheck Details: ", attrs=['bold'])  + colored(f"https://www.immuniweb.com/darkweb/{test_results['unicode_orig_url']}/{test_results['internals']['id']}/", 'blue'))
