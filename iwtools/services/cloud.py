#! /usr/bin/env python3
import math
from datetime import datetime
# Standard libraries
from time import sleep
import logging
import asyncio

# Third-party libraries
import requests

# Local libraries
from gui.loader import InfiniteLoader
from gui.termcolor import colored

class Cloud:
    """
    ImmuniWeb® Community Edition: Cloud Security Test
    """

    USER_AGENT = 'iwtools-0.2'

    def __init__(self, target: str, api_key: str = None, recheck: bool = False, quick: bool = True,
                 quiet: bool = False):
        self.target = target
        self.api_key = api_key
        self.recheck = recheck
        self.quick = quick
        self.quiet = quiet
        self.private = True
        self.test_results = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.USER_AGENT,
            'Connection':'close'
        })


    def get_result(self):

        url = f"https://www.immuniweb.com/cloud/api/v2/tests/{self.target}/"
        headers = {}
        if self.api_key:
            headers['Authorization'] = f"Bearer {self.api_key}"
        response = self.session.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


    def get_test_status(self):

        url = f"https://www.immuniweb.com/cloud/api/v2/tests/{self.target}/status/?quick={str(self.quick)}"
        response = self.session.get(url)
        response.raise_for_status()

        return response.json()


    async def test_loader(self, start_message, cancel_message):
        """Print loading status while test rinning"""

        loader = InfiniteLoader(len(start_message))

        row_up = "\x1B[3A"
        row_clear = "\x1B[0K"
        step = 0

        logging.info(colored(start_message, "blue"))

        # Draw loader
        print("\n\n\n")
        while True:
            print(row_up + loader.generate(step) + row_clear)
            print("\n" + row_clear)

            step += 1
            try:
                await asyncio.sleep(.1)
            except asyncio.CancelledError:
                msg = row_up + row_clear + row_up + row_clear + "\n" + row_clear + cancel_message + "\n"
                logging.info(colored(msg, "blue"))
                break


    def wait_test_results(self):
        """Wait until the completion of test"""

        response = {
            'status': "in_progress"
        }

        while 'status' in response and response['status'] != "finished":
            response = self.get_test_status()
            sleep(10)

        return response


    def start_test(self):

        url = "https://www.immuniweb.com/cloud/api/v2/tests/"
        data = {
            'target': self.target,
            'quick': self.quick,
            'private': True,
            'api_key': self.api_key,
        }

        req = self.session.post(url, None, data)
        result = req.json()

        if 'error' in result:
            error_data = result['error']['detail'][0]['msg']
            error_msg = "unknown error format"
            if type(error_data) is str:
                error_msg = error_data
            elif 'error' in error_data:
                error_msg = error_data['error']
                if 'recommendation' in error_data:
                    prefix = " " if self.quiet else "\n"
                    error_msg += prefix + "Recommendation: " + error_data['recommendation']

            raise Exception(error_msg)

        return result


    async def watch(self):
        """Check test status until complete"""

        if self.quiet or logging.root.level == logging.DEBUG:
            response = self.wait_test_results()
        else:
            loop = asyncio.get_event_loop()
            loader = asyncio.ensure_future(self.test_loader("Cloud Security Test in progress", "Test completed"))
            response = await loop.run_in_executor(None, self.wait_test_results)
            loader.cancel()

        self.test_results = response

        return response


    def start(self):
        """Start test"""

        logging.info(
            colored("\nImmuni", "red", attrs=['bold']) + colored("Web®", "blue", attrs=['bold']) +
            colored(" Community Edition: Cloud Security Test\n", attrs=['bold'])
        )

        logging.info("Input parameters:")
        logging.info(colored("  Target: ", attrs=['bold']) + self.target)
        logging.info(colored("  Recheck: ", attrs=['bold']) + str(self.recheck))
        logging.info(colored("  Quick: ", attrs=['bold']) + str(self.quick) + "\n")

        start_test_res = None

        if self.recheck:
            start_test_res = self.start_test()
        else:
            try:
                self.test_results = self.get_result()
            except Exception as error:
                code = str(error).split(" ", 1)[0]
                if code == "404":
                    logging.info(colored("Test not found\n", attrs=['bold']))
                    start_test_res = self.start_test()
                else:
                    raise Exception(error)

        if start_test_res and 'status' in start_test_res:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.watch())
            loop.close()
            self.test_results = self.get_result()

        return self.test_results


    def generate_banner(self):
        """Generate beauty banner with test results"""
        
        stats = self.test_results['result']['cloud']['stats']

        tBuckets = stats['buckets_total']
        pBuckets = stats['public_buckets']
        pFiles = stats['files_total']

        maxNum = max(tBuckets, pBuckets, pFiles)
        maxNumLen = len(str(maxNum))
        tBucketsStr = str(tBuckets).rjust(maxNumLen, ' ')
        pBucketsStr = str(pBuckets).rjust(maxNumLen, ' ')
        pFilesStr = str(pFiles).rjust(maxNumLen, ' ')
        line = "─" * maxNumLen

        tBucketsColored = colored(tBucketsStr, "yellow")
        pBucketsColored = colored(pBucketsStr, "yellow")
        if pBuckets > 0:
            pBucketsColored = colored(pBucketsStr, "red")
        pFilesColored = colored(pFilesStr, "yellow")
        if pFiles > 0:
            pFilesColored = colored(pFilesStr, "red")

        return (
            "\n"
            "╭─────────────────" + line            + "─╮\n"
            "│ Total buckets   " + tBucketsColored + " │\n"
            "│ Public buckets  " + pBucketsColored + " │\n"
            "│ Public files    " + pFilesColored   + " │\n"
            "╰─────────────────" + line            + "─╯\n"
        )


    def print_report(self, test_results=None):
        """Generate report"""

        if not test_results:
            test_results = self.test_results

        target = test_results['parameters']['target']
        logging.info(colored("Tested Domain: ", attrs=['bold']) + target)

        brand = self.test_results['result']['brand']
        if brand:
            logging.info("Domain name {} seems to be operated by {}.".format(target, brand))

        finished_at = datetime.fromisoformat(test_results['finished_at'])
        test_time = finished_at.strftime('%B %d, %Y %H:%M:%S')
        logging.info(colored("Test Date: ", attrs=['bold']) + test_time)

        created_at = datetime.fromisoformat(test_results['created_at'])
        delta = math.floor((finished_at - created_at).total_seconds() / 60)
        delta_unit = " minute"
        if delta > 1:
            delta_unit = " minutes"
        logging.info(colored("Test Runtime: ", attrs=['bold']) + str(delta) + delta_unit)

        logging.info(colored("Quick: ", attrs=['bold']) + str(test_results['parameters']['quick']))

        banner = self.generate_banner()
        logging.info(banner)

        buckets = self.test_results['result']['cloud']['buckets']
        maxNameLen = 0
        bucketsLogging = []
        for key in buckets:
            name = buckets[key][0]['type']
            if len(name) > maxNameLen:
                maxNameLen = len(name)
            subTBuckets = len(buckets[key])
            subPBuckets = sum(1 for item in buckets[key] if item['status'] == "public")
            subPFiles = sum(item['total_files'] for item in buckets[key])
            bucketsLogging.append((name, subTBuckets, subPBuckets, subPFiles))

        if len(buckets) > 0:
            logging.info(" " * maxNameLen + "     Total    Public    Public")
            logging.info(" " * maxNameLen + "   buckets   buckets     files")

        column_len = 9
        for bucketLog in bucketsLogging:

            subTBuckets = bucketLog[1]
            subTBucketsStr = str(subTBuckets).rjust(column_len)
            subTBucketsStr = colored(subTBucketsStr, "yellow")

            subPBuckets = bucketLog[2]
            subPBucketsStr = str(subPBuckets).rjust(column_len)
            color = "yellow"
            if subPBuckets > 0:
                color = "red"
            subPBucketsStr = colored(subPBucketsStr, color)

            subPFiles = bucketLog[3]
            subPFilesStr = str(subPFiles).rjust(column_len)
            color = "yellow"
            if subPFiles > 0:
                color = "red"
            subPFilesStr = colored(subPFilesStr, color)

            logging.info(f"{bucketLog[0].ljust(maxNameLen)} {subTBucketsStr} {subPBucketsStr} {subPFilesStr}")

        if test_results['parameters']['quick']:
            if len(buckets) > 0:
                logging.info("")

            logging.info("A quick test was performed, refresh test with parameter '--quick false' to check for "
                         "exposure in more clouds")

        # Link to full results
        logging.info(colored("\nCheck Details: ", attrs=['bold']) + colored(self.get_test_link(test_results), 'blue'))


    def get_test_link(self, test_results):
        return f"https://www.immuniweb.com/cloud/{test_results['parameters']['target']}/"
