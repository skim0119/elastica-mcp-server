import numpy as np

from elastica_mcp_server.simulation.manager import Manager
from elastica_mcp_server.material import MaterialParams, material_factory
from elastica_mcp_server.simulation.environment import compute_projected_velocity
from elastica_mcp_server.simulation.rod_strategy import StraightRodParams


def test_snake():
    """
    Integration test for composing a simulation with fixed timesteps.
    """
    manager = Manager()
    manager.create_simulation("snake")

    simulator = manager["snake"]

    material = MaterialParams(**material_factory("MuscleHydrostat"))
    rod_params = StraightRodParams(
        start_position=(0.0, 0.0, 0.0),
        direction=(0.0, 0.0, 1.0),
        normal=(0.0, 1.0, 0.0),
        base_length=0.35,
        base_radius=0.35 * 0.011,
    )

    simulator.create_rod("rod", rod_params, material)
    simulator.mimic_snake_motion("rod", rod_params)
    simulator.finalize()

    total_time = 0.1
    step_skip = simulator.step_skip
    simulator.run_simulation(total_time)

    data = simulator.callbacks["rod"]

    assert len(data["time"]) == np.ceil(
        int(total_time / simulator.time_step) / step_skip
    )
    return

    # Below is a plot of the velocity of the snake.
    # Enable to manually inspect the velocity of the snake.
    import matplotlib.pyplot as plt
    from matplotlib.colors import to_rgb

    time_per_period = np.array(data["time"]) / period
    avg_velocity = np.array(data["avg_velocity"])

    [
        velocity_in_direction_of_rod,
        velocity_in_rod_roll_dir,
        _,
        _,
    ] = compute_projected_velocity(data, period)

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    ax.grid(which="minor", color="k", linestyle="--")
    ax.grid(which="major", color="k", linestyle="-")
    ax.plot(
        time_per_period[:], velocity_in_direction_of_rod[:, 2], "r-", label="forward"
    )
    ax.plot(
        time_per_period[:],
        velocity_in_rod_roll_dir[:, 0],
        c=to_rgb("xkcd:bluish"),
        label="lateral",
    )
    ax.plot(time_per_period[:], avg_velocity[:, 1], "k-", label="normal")
    ax.set_ylabel("Velocity [m/s]")
    ax.set_xlabel("Time [s]")
    fig.legend(prop={"size": 20})
    plt.show()
    plt.close(plt.gcf())

    import matplotlib.animation as manimation
    from tqdm import tqdm

    fps = 15
    video_name = "snake.mp4"
    xlim = (0.0, 4.0)
    ylim = (-1.0, 1.0)
    positions_over_time = np.array(data["position"])

    print("plot video")
    FFMpegWriter = manimation.writers["ffmpeg"]
    metadata = dict(title="Movie Test", artist="Matplotlib", comment="Movie support!")
    writer = FFMpegWriter(fps=fps, metadata=metadata)
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_xlabel("z [m]")
    ax.set_ylabel("x [m]")
    rod_lines_2d = ax.plot(positions_over_time[0][2], positions_over_time[0][0])[0]
    # plt.axis("equal")
    with writer.saving(fig, video_name, dpi=150):
        for time in tqdm(range(1, len(data["time"]))):
            rod_lines_2d.set_xdata(positions_over_time[time][2])
            rod_lines_2d.set_ydata(positions_over_time[time][0])
            writer.grab_frame()
    plt.close(plt.gcf())
