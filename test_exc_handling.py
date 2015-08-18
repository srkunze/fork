# -*- coding: utf-8 -*-

# that is necessary to activate hook before the relevant try blocks are imported
import fork

from _test_exc_handling import test_result_proxy_evaluation_when_entering_a_try_statement, ExitTestException, \
    test_result_proxy_evaluation_when_exiting_a_try_statement




try:
    test_result_proxy_evaluation_when_entering_a_try_statement()
except ExitTestException:
    pass

try:
    test_result_proxy_evaluation_when_exiting_a_try_statement()
except ExitTestException:
    pass
