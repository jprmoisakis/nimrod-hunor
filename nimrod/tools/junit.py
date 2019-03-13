import os
import re
import sys
import time
import subprocess

from collections import namedtuple

from bs4 import BeautifulSoup

from nimrod.tools.bin import JUNIT, HAMCREST, JMOCKIT, EVOSUITE_RUNTIME
from nimrod.utils import generate_classpath, package_to_dir

TIMEOUT = 60 * 3


JUnitResult = namedtuple('JUnitResult', ['ok_tests', 'fail_tests', 
                                         'fail_test_set', 'run_time',
                                         'coverage'])


class JUnit:

    def __init__(self, java, classpath):
        self.java = java
        self.classpath = classpath
        
    def exec(self, suite_dir, suite_classes_dir, sut_class, test_class,
             timeout=TIMEOUT):
        classpath = generate_classpath([
            JMOCKIT, JUNIT, HAMCREST, EVOSUITE_RUNTIME,
            suite_classes_dir,
            self.classpath
        ])

        return self._exec(suite_dir, sut_class, test_class, classpath, '.',
                          timeout)

    def exec_with_mutant(self, suite_dir, suite_classes_dir, sut_class,
                         test_class, mutant, timeout=TIMEOUT):
        classpath = generate_classpath([
            JMOCKIT, JUNIT, HAMCREST, EVOSUITE_RUNTIME,
            suite_classes_dir,
            mutant.dir,
            self.classpath
        ])

        return self._exec(suite_dir, sut_class, test_class, classpath,
                          mutant.dir, timeout)

    def _exec(self, suite_dir, sut_class, test_class, classpath,
              cov_src_dirs='.', timeout=TIMEOUT):

        params = (
            '-classpath', classpath,
            '-Dcoverage-classes=' + sut_class,
            '-Dcoverage-output=html',
            '-Dcoverage-metrics=line',
            '-Dcoverage-srcDirs=' + cov_src_dirs,
            'org.junit.runner.JUnitCore', test_class
        )

        start = time.time()
        try:
            output = self.java.exec_java(suite_dir, self.java.get_env(),
                                         timeout, *params)
            return JUnitResult(
                *JUnit._extract_results_ok(output.decode('unicode_escape')),
                time.time() - start, None
            )
        except subprocess.CalledProcessError as e:
            return JUnitResult(
                *JUnit._extract_results(e.output.decode('unicode_escape')),
                time.time() - start, None
            )
        except subprocess.TimeoutExpired as e:
            elapsed_time = time.time() - start
            print("# ERROR: Run JUnit tests timed out. {0} seconds".format(
                elapsed_time
            ), file=sys.stderr)
            raise e

    @staticmethod
    def _extract_results_ok(output):
        result = re.findall(r'OK \([0-9]* tests?\)', output)
        if len(result) > 0:
            result = result[0].replace('(', '')
            r = [int(s) for s in result.split() if s.isdigit()]
            return r[0], 0, set()

        return 0, 0, set()

    @staticmethod
    def _extract_results(output):
        if len(re.findall(r'initializationError', output)) == 0:
            result = re.findall(r'Tests run: [0-9]*,[ ]{2}Failures: [0-9]*',
                                output)
            if len(result) > 0:
                result = result[0].replace(',', ' ')
                r = [int(s) for s in result.split() if s.isdigit()]
                return r[0], r[1], JUnit._extract_test_id(output)

        return 0, 0, set()

    @staticmethod
    def _extract_test_id(output):
        tests_fail = set()
        for test in re.findall(r'\.test[0-9]+\([A-Za-z0-9_]+\.java:[0-9]+\)',
                               output):
            i = re.findall('\d+', test)
            file = re.findall(r'\(.+?(?=\.)', test)[0][1:]
            test_case = re.findall(r'\..+?(?=\()', test)[0][1:]

            if len(i) > 0:
                tests_fail.add('{0}#{1}'.format(file, test_case, int(i[-1])))
            else:
                print("*** ERROR: Error in regex of junit output.")

        return tests_fail

    def run_with_mutant(self, suite, sut_class, mutant):
        ok_tests = 0
        fail_tests = 0
        fail_test_set = set()
        run_time = 0
        call_points = set()
        test_cases = set()
        executions = 0

        for test_class in suite.test_classes:
            result = self.exec_with_mutant(suite.suite_dir,
                                           suite.suite_classes_dir, sut_class,
                                           test_class, mutant)
            ok_tests += result.ok_tests
            fail_tests += result.fail_tests
            fail_test_set = fail_test_set.union(result.fail_test_set)
            run_time += run_time

            cov = self.run_coverage(suite.suite_dir, sut_class,
                                    mutant.line_number)

            call_points = call_points.union(cov.call_points)
            test_cases = test_cases.union(cov.test_cases)
            executions += cov.executions

        return JUnitResult(ok_tests, fail_tests, fail_test_set, run_time,
                           Coverage(call_points, test_cases, executions))

    @staticmethod
    def run_coverage( suite_dir, sut_class, mutation_line):
        jmockit = JMockit(suite_dir, sut_class)
        return jmockit.coverage(mutation_line)


Coverage = namedtuple('Coverage', ['call_points', 'test_cases', 'executions'])


class JMockit:

    def __init__(self, suite_dir, sut_class):
        self.suite_dir = suite_dir
        self.sut_class = sut_class

    def coverage(self, mutation_line):
        return self.get_coverage_report(mutation_line)

    def get_coverage_report(self, mutation_line):
        report_file = self.get_coverage_report_file()

        if report_file:
            with open(report_file, 'r') as html:
                soup = BeautifulSoup(html, 'html.parser')
                return JMockit._get_coverage_info(soup, mutation_line)

    def get_coverage_report_file(self):
        coverage_report = os.path.join(self.suite_dir, 'coverage-report',
                                       package_to_dir(self.sut_class) + '.html')

        return coverage_report if os.path.exists(coverage_report) else None

    @staticmethod
    def _get_coverage_info(soup, mutation_line):
        test_cases = set()
        call_points = set()
        executions = 0

        for tr in soup.find_all('tr'):
            td_line = tr.find_all('td', class_='line')
            td_executions = tr.find_all('td', class_='count')
            td_count = tr.find_all('td', class_='callpoints-count')
            if (td_line and td_count and td_executions
                    and mutation_line == int(td_line[0].string)):
                executions = int(td_executions[0].string.strip())
                for li in tr.find_all('li'):
                    info = JMockit._extract_li(li)
                    if info:
                        file, test_case, cps = info
                        test_cases.add((file, test_case))
                        for cp in cps:
                            call_points.add((file, test_case, cp))

        return Coverage(call_points, test_cases, executions)

    @staticmethod
    def _extract_li(li):
        li = li.string.split(':')
        if len(li) == 2:
            try:
                file = li[0].split('#')[0]
                test_case = li[0].split('#')[1]
                return (file, test_case,
                        [int(cp.split('x')[0].strip())
                         for cp in li[1].split(',')])
            except IndexError:
                return None

