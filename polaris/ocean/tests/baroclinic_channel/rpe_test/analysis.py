import cmocean  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np
import xarray

from polaris.ocean.rpe import compute_rpe
from polaris.step import Step


class Analysis(Step):
    """
    A step for plotting the results of a series of RPE runs in the baroclinic
    channel test group

    Attributes
    ----------
    nus : list
        A list of viscosities
    """
    def __init__(self, test_case, resolution, nus):
        """
        Create the step

        Parameters
        ----------
        test_case : polaris.TestCase
            The test case this step belongs to

        resolution : float
            The resolution of the test case in km

        nus : list
            A list of viscosities
        """
        super().__init__(test_case=test_case, name='analysis')
        self.nus = nus

        self.add_input_file(
            filename='initial_state.nc',
            target='../initial_state/initial_state.nc')

        for index, nu in enumerate(nus):
            self.add_input_file(
                filename=f'output_{index + 1}.nc',
                target=f'../rpe_test_{index + 1}_nu_{int(nu)}/output.nc')

        self.add_output_file(
            filename=f'sections_baroclinic_channel_{resolution}.png')
        self.add_output_file(filename='rpe_t.png')
        self.add_output_file(filename='rpe.csv')

    def run(self):
        """
        Run this step of the test case
        """
        section = self.config['baroclinic_channel']
        nx = section.getint('nx')
        ny = section.getint('ny')
        rpe = compute_rpe(initial_state_file_name=self.inputs[0],
                          output_files=self.inputs[1:])
        _plot(nx, ny, self.outputs[0], self.nus, rpe)


def _plot(nx, ny, filename, nus, rpe):
    """
    Plot section of the baroclinic channel at different viscosities

    Parameters
    ----------
    nx : int
        The number of cells in the x direction

    ny : int
        The number of cells in the y direction (before culling)

    filename : str
        The output file name

    nus : list
        The viscosity values

    rpe : numpy.ndarray
        The reference potential energy with size len(nu) x len(time)
    """

    plt.switch_backend('Agg')
    num_files = len(nus)
    time = 20

    ds = xarray.open_dataset('output_1.nc', decode_times=False)
    times = ds.daysSinceStartOfSim.values

    fig = plt.figure()
    for i in range(num_files):
        rpe_norm = np.divide((rpe[i, :] - rpe[i, 0]), rpe[i, 0])
        plt.plot(times, rpe_norm,
                 label=f"$\\nu_h=${nus[i]}")
    plt.xlabel('Time, days')
    plt.ylabel('RPE-RPE(0)/RPE(0)')
    plt.legend()
    plt.savefig('rpe_t.png')
    plt.close(fig)

    fig, axs = plt.subplots(1, num_files, figsize=(
        2.1 * num_files, 5.0), constrained_layout=True)

    for iCol in range(num_files):
        ds = xarray.open_dataset(f'output_{iCol + 1}.nc', decode_times=False)
        times = ds.daysSinceStartOfSim.values
        time_index = np.argmin(np.abs(times - time))
        var = ds.temperature.values
        var1 = np.reshape(var[time_index, :, 0], [ny, nx])
        # flip in y-dir
        var = np.flipud(var1)

        # Every other row in y needs to average two neighbors in x on
        # planar hex mesh
        var_avg = var
        for j in range(0, ny, 2):
            for i in range(1, nx - 2):
                var_avg[j, i] = (var[j, i + 1] + var[j, i]) / 2.0

        ax = axs[iCol]
        dis = ax.imshow(
            var_avg,
            extent=[0, 160, 0, 500],
            cmap='cmo.thermal',
            vmin=11.8,
            vmax=13.0)
        ax.set_title(f'day {times[time_index]}, '
                     f'$\\nu_h=${nus[iCol]}')
        ax.set_xticks(np.arange(0, 161, step=40))
        ax.set_yticks(np.arange(0, 501, step=50))

        ax.set_xlabel('x, km')
        if iCol == 0:
            ax.set_ylabel('y, km')
        if iCol == num_files - 1:
            fig.colorbar(dis, ax=axs[num_files - 1], aspect=40)

    plt.savefig(filename)
