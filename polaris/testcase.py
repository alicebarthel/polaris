import logging
import os

from polaris.config import PolarisConfigParser


class TestCase:
    """
    The base class for test cases---such as a decomposition, threading or
    restart test---that are made up of one or more steps

    Attributes
    ----------
    name : str
        the name of the test case

    test_group : polaris.TestGroup
        The test group the test case belongs to

    component : polaris.Component
        The component the test group belongs to

    steps : dict
        A dictionary of steps in the test case with step names as keys

    steps_to_run : list
        A list of the steps to run when ``run()`` gets called.  This list
        includes all steps by default but can be replaced with a list of only
        those tests that should run by default if some steps are optional and
        should be run manually by the user.

    subdir : str
        the subdirectory for the test case

    path : str
        the path within the base work directory of the test case, made up of
        ``component``, ``test_group``, and the test case's ``subdir``

    config : polaris.config.PolarisConfigParser
        Configuration options for this test case, a combination of the defaults
        for the machine, core and configuration

    config_filename : str
        The local name of the config file that ``config`` has been written to
        during setup and read from during run

    work_dir : str
        The test case's work directory, defined during setup as the combination
        of ``base_work_dir`` and ``path``

    base_work_dir : str
        The base work directory

    baseline_dir : str, optional
        Location of the same test case within the baseline work directory,
        for use in comparing variables and timers

    stdout_logger : logging.Logger
        A logger for output from the test case that goes to stdout regardless
        of whether ``logger`` is a log file or stdout

    logger : logging.Logger
        A logger for output from the test case

    log_filename : str
        At run time, the name of a log file where output/errors from the test
        case are being logged, or ``None`` if output is to stdout/stderr

    new_step_log_file : bool
        Whether to create a new log file for each step or to log output to a
        common log file for the whole test case.  The latter is used when
        running the test case as part of a test suite

    validation : dict
        A dictionary with the status of internal and baseline comparisons, used
        by the ``polaris`` framework to determine whether the test case passed
        or failed internal and baseline validation.
    """

    def __init__(self, test_group, name, subdir=None):
        """
        Create a new test case

        Parameters
        ----------
        test_group : polaris.TestGroup
            the test group that this test case belongs to

        name : str
            the name of the test case

        subdir : str, optional
            the subdirectory for the test case.  The default is ``name``
        """
        self.name = name
        self.component = test_group.component
        self.test_group = test_group
        if subdir is not None:
            self.subdir = subdir
        else:
            self.subdir = name

        self.path = os.path.join(self.component.name, test_group.name,
                                 self.subdir)

        # steps will be added by calling add_step()
        self.steps = dict()
        self.steps_to_run = list()

        # these will be set during setup, dummy values for now
        self.config = PolarisConfigParser()
        self.config_filename = ''
        self.work_dir = ''
        self.base_work_dir = ''
        # may be set during setup if there is a baseline for comparison
        self.baseline_dir = None

        # these will be set when running the test case, dummy values for now
        self.new_step_log_file = True
        self.stdout_logger = None
        self.logger = logging.getLogger('dummy')
        self.log_filename = None
        self.validation = None

    def configure(self):
        """
        Modify the configuration options for this test case. Test cases should
        override this method if they want to add config options specific to
        the test case, e.g. from a config file stored in the test case's python
        package.  If a test case overrides this method, it should assume that
        the ``<self.name>.cfg`` file in its package has already been added
        to the config options prior to calling ``configure()``.
        """
        pass

    def validate(self):
        """
        Test cases can override this method to perform validation of variables
        and timers
        """
        pass

    def add_step(self, step, run_by_default=True):
        """
        Add a step to the test case

        Parameters
        ----------
        step : polaris.Step
            The step to add

        run_by_default : bool, optional
            Whether to add this step to the list of steps to run when the
            ``run()`` method gets called.  If ``run_by_default=False``, users
            would need to run this step manually.
        """
        self.steps[step.name] = step
        if run_by_default:
            self.steps_to_run.append(step.name)

    def check_validation(self):
        """
        Check the test case's "validation" dictionary to see if validation
        failed.
        """
        validation = self.validation
        logger = self.logger
        if validation is not None:
            internal_pass = validation['internal_pass']
            baseline_pass = validation['baseline_pass']

            both_pass = True
            if internal_pass is not None and not internal_pass:
                if logger is not None:
                    logger.error('Comparison failed between files within the '
                                 'test case.')
                both_pass = False

            if baseline_pass is not None and not baseline_pass:
                if logger is not None:
                    logger.error('Comparison failed between the test case and '
                                 'the baseline.')
                both_pass = False

            if both_pass:
                raise ValueError('Comparison failed, see above.')
