import time

from polaris.ocean.model import OceanModelStep


class Forward(OceanModelStep):
    """
    A step for performing forward ocean component runs as part of baroclinic
    channel test cases.

    Attributes
    ----------
    resolution : float
        The resolution of the test case in km

    resources_fixed : bool
        Whether resources were set already and shouldn't be updated
        algorithmically

    dt : float
        The model time step in seconds

    btr_dt : float
        The model barotropic time step in seconds

    run_time_steps : int or None
        Number of time steps to run for
    """
    def __init__(self, test_case, resolution, name='forward', subdir=None,
                 ntasks=None, min_tasks=None, openmp_threads=1, nu=None,
                 run_time_steps=None):
        """
        Create a new test case

        Parameters
        ----------
        test_case : polaris.TestCase
            The test case this step belongs to

        resolution : km
            The resolution of the test case in km

        name : str
            the name of the test case

        subdir : str, optional
            the subdirectory for the step.  The default is ``name``

        ntasks : int, optional
            the number of tasks the step would ideally use.  If fewer tasks
            are available on the system, the step will run on all available
            tasks as long as this is not below ``min_tasks``

        min_tasks : int, optional
            the number of tasks the step requires.  If the system has fewer
            than this number of tasks, the step will fail

        openmp_threads : int, optional
            the number of OpenMP threads the step will use

        nu : float, optional
            the viscosity (if different from the default for the test group)

        run_time_steps : int, optional
            Number of time steps to run for
        """
        self.resolution = resolution
        self.run_time_steps = run_time_steps
        super().__init__(test_case=test_case, name=name, subdir=subdir,
                         ntasks=ntasks, min_tasks=min_tasks,
                         openmp_threads=openmp_threads)

        if nu is not None:
            # update the viscosity to the requested value
            self.add_model_config_options(options=dict(config_mom_del2=nu))

        # make sure output is double precision
        self.add_yaml_file('polaris.ocean.config', 'output.yaml')

        self.add_input_file(filename='initial_state.nc',
                            target='../initial_state/initial_state.nc')
        self.add_input_file(filename='graph.info',
                            target='../initial_state/culled_graph.info')

        self.add_yaml_file('polaris.ocean.tests.baroclinic_channel',
                           'forward.yaml')

        self.add_output_file(filename='output.nc')

        self.resources_fixed = (ntasks is not None)

        self.dt = None
        self.btr_dt = None

    def compute_cell_count(self, at_setup):
        """
        Compute the approximate number of cells in the mesh, used to constrain
        resources

        Parameters
        ----------
        at_setup : bool
            Whether this method is being run during setup of the step, as
            opposed to at runtime

        Returns
        -------
        cell_count : int or None
            The approximate number of cells in the mesh
        """
        section = self.config['baroclinic_channel']
        nx = section.getint('nx')
        ny = section.getint('ny')
        # by setting the cell count, the resources will be computed
        # automatically
        cell_count = nx * ny
        return cell_count

    def dynamic_model_config(self, at_setup):
        """
        Add model config options, namelist, streams and yaml files using config
        options or template replacements that need to be set both during step
        setup and at runtime

        Parameters
        ----------
        at_setup : bool
            Whether this method is being run during setup of the step, as
            opposed to at runtime
        """
        super().dynamic_model_config(at_setup)

        config = self.config

        options = dict()

        # dt is proportional to resolution: default 30 seconds per km
        dt_per_km = config.getfloat('baroclinic_channel', 'dt_per_km')
        dt = dt_per_km * self.resolution
        # https://stackoverflow.com/a/1384565/7728169
        options['config_dt'] = \
            time.strftime('%H:%M:%S', time.gmtime(dt))

        if self.run_time_steps is not None:
            # default run duration is a few time steps
            run_seconds = self.run_time_steps * dt
            options['config_run_duration'] = \
                time.strftime('%H:%M:%S', time.gmtime(run_seconds))

        # btr_dt is also proportional to resolution: default 1.5 seconds per km
        btr_dt_per_km = config.getfloat('baroclinic_channel', 'btr_dt_per_km')
        btr_dt = btr_dt_per_km * self.resolution
        options['config_btr_dt'] = \
            time.strftime('%H:%M:%S', time.gmtime(btr_dt))

        self.dt = dt
        self.btr_dt = btr_dt

        self.add_model_config_options(options=options)
