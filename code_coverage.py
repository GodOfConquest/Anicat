"""
Test runner with code coverage.
Falls back to django simple runner if coverage-lib not installed
Found in internets
"""
import os

from django.test import simple
from django.conf import settings


try:
    from coverage import coverage as Coverage
except ImportError:
    run_tests = simple.run_tests
else:
    coverage = Coverage()
    def run_tests(test_labels, verbosity=1, interactive=True, extra_tests=[]):

        coverage.start()
        test_results = simple.run_tests(test_labels, verbosity, interactive, extra_tests)
        coverage.stop()

        coverage_modules = []
        for app in test_labels:
            try:
                module = __import__(app, globals(), locals(), [''])
            except ImportError:
                coverage_modules = None
                break
            if module:
                base_path = os.path.join(os.path.split(module.__file__)[0], "")
                for root, dirs, files in os.walk(base_path):
                    for fname in files:
                        if fname.endswith(".py") and os.path.getsize(os.path.join(root, fname)) > 1:
                            try:
                                mname = os.path.join(app, os.path.join(root, fname).replace(base_path, ""))
                                coverage_modules.append(mname)
                            except ImportError:
                                pass #do nothing

        if coverage_modules or not test_labels:
            coverage.html_report(coverage_modules, directory=settings.COVERAGE_REPORT_PATH)

        return test_results