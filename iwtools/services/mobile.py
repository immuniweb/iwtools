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


class Mobile:
    """
    ImmuniWeb® Community Edition: Mobile App Security Test

    ✓ iOS/Android Security Test
    ✓ OWASP Mobile Top 10 Test
    ✓ Mobile App Privacy Check
    ✓ Static & Dynamic Mobile Sca
    """

    API_URL = 'https://www.immuniweb.com/mobile/api'
    USER_AGENT = 'iwtools-0.1'

    test_results = None


    def __init__(self, target, api_key=None, recheck=False, quiet=False):
        self.target = target
        self.api_key = api_key
        self.recheck = recheck
        self.quiet = quiet


    def get_cache_id_or_start_test(self):
        """Get cached test id if exists or start new test"""

        url = f"{self.API_URL}/download_apk"

        files = None
        data = {
            'api_key': self.api_key,
            'hide_in_statistics': 1
        }

        if urlparse(self.target).scheme in ['http', 'https']:
            data['app'] = self.target
        else:
            files = {'file': open(self.target,'rb')}
            url = f"{self.API_URL}/upload"

        response = requests.post(url, data=data, files=files)
        response.raise_for_status()

        logging.debug(response.text)

        return response.json()


    def get_result_by_test_id(self, test_id):
        """Get result by test id (from cache)"""

        url = f"{self.API_URL}/test_info/id/{test_id}"

        response = requests.get(url)
        response.raise_for_status()

        logging.debug(response.text)

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

        logging.debug(response.text)

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


    def wait_test_results(self, test_id):
        """Wait until the completion of test"""

        response = {
            'status': 'unprocessed'
        }

        while 'status' in response and response['status'] in ['in_progress', 'unprocessed', 'doesnt_exist']:
            response = self.get_result_by_test_id(test_id)
            sleep(10)

        return response


    async def watch(self, test_id):
        """Check test status until complete"""

        if self.quiet or logging.root.level == logging.DEBUG:
            response = self.wait_test_results(test_id)
        else:
            loop = asyncio.get_event_loop()
            loader = asyncio.ensure_future(self.test_loader('Mobile App Security Test in progress', 'Test completed'))
            response = await loop.run_in_executor(None, self.wait_test_results, test_id)
            loader.cancel()

        self.test_results = response

        return response


    def start(self):
        """Start test"""

        logging.info(
            colored('\nImmuni', 'red', attrs=['bold']) + colored('Web®', 'blue', attrs=['bold']) +
            colored(' Community Edition: Mobile App Security Test\n', attrs=['bold'])
        )

        logging.info(colored('Target: ', attrs=['bold']) + self.target + '\n')

        response = self.get_cache_id_or_start_test()

        error = None
        for task in response:
            if 'status' and 'id' in task and task['status'] == 'success':
                loop = asyncio.get_event_loop()
                response = loop.run_until_complete(self.watch(task['id']))
                loop.close()
                error = None
                break

            elif 'error_id' in task and task['error_id'] == 0:
                response = self.get_result_by_test_id(task['id'])

                if response['status'] in ['in_progress', 'unprocessed', 'doesnt_exist']:
                    loop = asyncio.get_event_loop()
                    response = loop.run_until_complete(self.watch(task['id']))
                    loop.close()
                    error = None
                    break

                error = None
                break

            if 'error' in task:
                error = task['error']

        if error:
            raise Exception(error)

        self.test_results = response

        return response


    def normalize_color(self, color):
        """Adapt color names to console palette"""

        if color == 'orange':
            return 'yellow'

        return color


    def generate_banner(self, owasp_color, behaviour_color, sca_color, apis_color):
        """Generate beauty banner with test results"""

        return (
            "\n"
            f"{colored('╭──────────────────────────────────╮', owasp_color)} {colored('╭──────────────────────────────────────╮', apis_color)}\n"
            f"{colored('│   OWASP Mobile Top 10 Security   │', owasp_color)} {colored('│  Mobile App External Communications  │', apis_color)}\n"
            f"{colored('╰──────────────────────────────────╯', owasp_color)} {colored('╰──────────────────────────────────────╯', apis_color)}\n"
            f"{colored('╭──────────────────────────────────╮', sca_color)} {colored('╭──────────────────────────────────────╮', behaviour_color)}\n"
            f"{colored('│   Software Composition Analysis  │', sca_color)} {colored('│    Mobile App Privacy and Behavior   │', behaviour_color)}\n"
            f"{colored('╰──────────────────────────────────╯', sca_color)} {colored('╰──────────────────────────────────────╯', behaviour_color)}\n"
        )


    def print_report(self, test_results=None):
        """Generate report"""

        if not test_results:
            test_results = self.test_results

        owasp_color = self.normalize_color(test_results['scores']['owasp_top_10']['class'])
        behaviour_color = self.normalize_color(test_results['scores']['behaviour']['class'])
        sca_color = self.normalize_color(test_results['scores']['sca']['class'])
        apis_color = self.normalize_color(test_results['scores']['apis']['class'])

        banner = self.generate_banner(owasp_color, behaviour_color, sca_color, apis_color)

        test_time = strftime('%B %d, %Y %H:%M:%S', localtime(test_results['data']['app_info']['ts_stop']))

        # Test is outdated if older than 1 week
        test_time_color = None
        if int(time()) - test_results['data']['app_info']['ts_stop'] > 604800:
            test_time_color = 'yellow'

        logging.info(colored("App Name: ", attrs=['bold']) + test_results['data']['app_info']['app_name'])
        logging.info(colored("App ID: ", attrs=['bold']) + test_results['data']['app_info']['app_id'])
        logging.info(colored("Version: ", attrs=['bold']) + test_results['data']['app_info']['app_version'])
        logging.info(colored("Developer: ", attrs=['bold']) + test_results['data']['app_info']['app_developer'])
        logging.info(colored("OS: ", attrs=['bold']) + test_results['data']['app_info']['device_type'].title())
        logging.info(colored("Completed: ", attrs=['bold']) + colored(test_time, test_time_color))
        logging.info(banner)
        logging.info(colored("OWASP Mobile Top 10 Security Test: ", attrs=['bold'])  + colored(test_results['scores']['owasp_top_10']['description'].title(), owasp_color))
        logging.info(colored("Mobile App Privacy and Behavior: ", attrs=['bold'])  + colored(test_results['scores']['behaviour']['description'].title(), behaviour_color))
        logging.info(colored("Software Composition Analysis Test: ", attrs=['bold'])  + colored(test_results['scores']['sca']['description'].title(), sca_color))
        logging.info(colored("Mobile App External Communications: ", attrs=['bold'])  + colored(test_results['scores']['apis']['description'].title(), apis_color))


        # Full Results
        logging.info(colored("\nCheck Details: ", attrs=['bold']) + colored(f"https://www.immuniweb.com/mobile/{test_results['data']['app_info']['app_id']}/{test_results['data']['app_info']['test_short_id']}/", 'blue'))
