"""TODO_doc."""

import os
from pathlib import Path

import numpy as np
import pytest

from pqueens.external_geometry import from_config_create_external_geometry
from pqueens.main import get_config_dict
from pqueens.utils import injector


def test_geometry_from_dat(
    inputdir, tmpdir, third_party_inputs, expected_node_coordinates, expected_surface_topology
):
    """TODO_doc."""
    # generate json input file from template
    third_party_input_file = Path(
        third_party_inputs, "baci_input_files", "bending_wall_channel_flow_fsi_lofi.dat"
    )
    dir_dict = {
        'baci_input': third_party_input_file,
    }
    template = Path(inputdir, "baci_mc_randomfields_from_geometry_template.yml")
    input_file = Path(tmpdir, "baci_mc_randomfields_from_geometry.yml")
    injector.inject(dir_dict, template, input_file)

    # get json file as config dictionary
    config = get_config_dict(Path(input_file), Path(tmpdir))

    # create pre-processing module form config
    preprocessor_obj = from_config_create_external_geometry(config, 'pre_processing')
    preprocessor_obj.main_run()

    # Check if we got the expected results
    assert preprocessor_obj.surface_topology == expected_surface_topology
    assert preprocessor_obj.node_coordinates['node_mesh'] == expected_node_coordinates['node_mesh']
    np.testing.assert_allclose(
        preprocessor_obj.node_coordinates['coordinates'],
        expected_node_coordinates['coordinates'],
        rtol=1.0e-3,
    )


# some lengthy result data as fixtures
@pytest.fixture()
def expected_surface_topology():
    """TODO_doc."""
    expected_topology = [
        {
            'node_mesh': [
                2242,
                2243,
                2244,
                2245,
                2250,
                2251,
                2254,
                2255,
                2258,
                2259,
                2262,
                2263,
                2266,
                2268,
                2270,
                2272,
                2273,
                2276,
                2278,
                2280,
                2282,
                2283,
                2286,
                2288,
                2290,
                2292,
                2293,
                2296,
                2298,
                2300,
                2302,
                2303,
                2306,
                2308,
                2310,
                2312,
                2313,
                2316,
                2318,
                2320,
                2322,
                2323,
                2326,
                2328,
                2330,
                2332,
                2333,
                2336,
                2338,
                2340,
                2342,
                2343,
                2346,
                2348,
                2350,
                2352,
                2353,
                2356,
                2358,
                2360,
                2362,
                2363,
                2366,
                2368,
                2370,
                2372,
                2373,
                2376,
                2378,
                2380,
                2382,
                2383,
                2386,
                2388,
                2390,
                2392,
                2393,
                2396,
                2398,
                2400,
                2402,
                2403,
                2406,
                2408,
                2410,
                2412,
                2413,
                2416,
                2418,
                2420,
                2422,
                2423,
                2426,
                2428,
                2430,
                2432,
                2433,
                2436,
                2438,
                2440,
                2442,
                2443,
                2446,
                2448,
                2450,
                2452,
                2453,
                2456,
                2458,
                2460,
                2462,
                2463,
                2466,
                2468,
                2470,
                2472,
                2473,
                2476,
                2478,
                2480,
                2482,
                2483,
                2486,
                2488,
                2490,
                2492,
                2493,
                2494,
                2495,
                2500,
                2501,
                2504,
                2505,
                2508,
                2509,
                2512,
                2513,
                2516,
                2518,
                2520,
                2522,
                2523,
                2526,
                2528,
                2530,
                2532,
                2533,
                2536,
                2538,
                2540,
                2542,
                2543,
                2546,
                2548,
                2550,
                2552,
                2553,
                2556,
                2558,
                2560,
                2562,
                2563,
                2566,
                2568,
                2570,
                2572,
                2573,
                2576,
                2578,
                2580,
                2582,
                2583,
                2586,
                2588,
                2590,
                2594,
                2595,
                2597,
                2599,
                2601,
                2604,
                2605,
                2607,
                2609,
                2611,
                2614,
                2615,
                2617,
                2619,
                2621,
                2624,
                2625,
                2627,
                2629,
                2631,
                2634,
                2635,
                2637,
                2639,
                2641,
                2644,
                2645,
                2647,
                2649,
                2651,
                2654,
                2655,
                2657,
                2659,
                2661,
                3800,
                3801,
                3802,
                3803,
                3806,
                3807,
                3810,
                3811,
                3814,
                3815,
                3818,
                3819,
                3822,
                3823,
                3826,
                3827,
                3830,
                3831,
                3834,
                3835,
                3838,
                3839,
                3842,
                3843,
                3846,
                3847,
                3850,
                3851,
                3854,
                3855,
                3858,
                3859,
                3862,
                3863,
                3866,
                3867,
                3870,
                3871,
                3874,
                3875,
                3878,
                3879,
                3882,
                3883,
                3886,
                3887,
                3890,
                3891,
                3894,
                3895,
                3898,
                3899,
                3901,
                3903,
                3905,
                3907,
                3909,
                3911,
                3913,
                3915,
                3917,
                3919,
                3921,
                3923,
                3925,
                3927,
                3929,
                3931,
                3933,
                3935,
                3937,
                3939,
                3941,
                3943,
                3945,
                3950,
                3951,
                3952,
                3953,
                3956,
                3957,
                3960,
                3961,
                3964,
                3965,
                3968,
                3969,
                3972,
                3973,
                3976,
                3977,
                3980,
                3981,
                3984,
                3985,
                3987,
                3989,
                3991,
                3993,
                3995,
                3997,
                3999,
                4002,
                4003,
                4005,
                4008,
                4009,
                4012,
                4013,
                4016,
                4017,
                4020,
                4021,
                4024,
                4025,
                4028,
                4029,
                4032,
                4033,
                4035,
                4037,
                4039,
                4041,
                4043,
                4045,
                4047,
            ],
            'surface_topology': [
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
            ],
            'topology_name': 'DSURFACE 9',
        }
    ]
    return expected_topology


@pytest.fixture()
def expected_node_coordinates():
    """TODO_doc."""
    node_coordinates = {
        'node_mesh': [
            2242,
            2243,
            2244,
            2245,
            2250,
            2251,
            2254,
            2255,
            2258,
            2259,
            2262,
            2263,
            2266,
            2268,
            2270,
            2272,
            2273,
            2276,
            2278,
            2280,
            2282,
            2283,
            2286,
            2288,
            2290,
            2292,
            2293,
            2296,
            2298,
            2300,
            2302,
            2303,
            2306,
            2308,
            2310,
            2312,
            2313,
            2316,
            2318,
            2320,
            2322,
            2323,
            2326,
            2328,
            2330,
            2332,
            2333,
            2336,
            2338,
            2340,
            2342,
            2343,
            2346,
            2348,
            2350,
            2352,
            2353,
            2356,
            2358,
            2360,
            2362,
            2363,
            2366,
            2368,
            2370,
            2372,
            2373,
            2376,
            2378,
            2380,
            2382,
            2383,
            2386,
            2388,
            2390,
            2392,
            2393,
            2396,
            2398,
            2400,
            2402,
            2403,
            2406,
            2408,
            2410,
            2412,
            2413,
            2416,
            2418,
            2420,
            2422,
            2423,
            2426,
            2428,
            2430,
            2432,
            2433,
            2436,
            2438,
            2440,
            2442,
            2443,
            2446,
            2448,
            2450,
            2452,
            2453,
            2456,
            2458,
            2460,
            2462,
            2463,
            2466,
            2468,
            2470,
            2472,
            2473,
            2476,
            2478,
            2480,
            2482,
            2483,
            2486,
            2488,
            2490,
            2492,
            2493,
            2494,
            2495,
            2500,
            2501,
            2504,
            2505,
            2508,
            2509,
            2512,
            2513,
            2516,
            2518,
            2520,
            2522,
            2523,
            2526,
            2528,
            2530,
            2532,
            2533,
            2536,
            2538,
            2540,
            2542,
            2543,
            2546,
            2548,
            2550,
            2552,
            2553,
            2556,
            2558,
            2560,
            2562,
            2563,
            2566,
            2568,
            2570,
            2572,
            2573,
            2576,
            2578,
            2580,
            2582,
            2583,
            2586,
            2588,
            2590,
            2594,
            2595,
            2597,
            2599,
            2601,
            2604,
            2605,
            2607,
            2609,
            2611,
            2614,
            2615,
            2617,
            2619,
            2621,
            2624,
            2625,
            2627,
            2629,
            2631,
            2634,
            2635,
            2637,
            2639,
            2641,
            2644,
            2645,
            2647,
            2649,
            2651,
            2654,
            2655,
            2657,
            2659,
            2661,
            3800,
            3801,
            3802,
            3803,
            3806,
            3807,
            3810,
            3811,
            3814,
            3815,
            3818,
            3819,
            3822,
            3823,
            3826,
            3827,
            3830,
            3831,
            3834,
            3835,
            3838,
            3839,
            3842,
            3843,
            3846,
            3847,
            3850,
            3851,
            3854,
            3855,
            3858,
            3859,
            3862,
            3863,
            3866,
            3867,
            3870,
            3871,
            3874,
            3875,
            3878,
            3879,
            3882,
            3883,
            3886,
            3887,
            3890,
            3891,
            3894,
            3895,
            3898,
            3899,
            3901,
            3903,
            3905,
            3907,
            3909,
            3911,
            3913,
            3915,
            3917,
            3919,
            3921,
            3923,
            3925,
            3927,
            3929,
            3931,
            3933,
            3935,
            3937,
            3939,
            3941,
            3943,
            3945,
            3950,
            3951,
            3952,
            3953,
            3956,
            3957,
            3960,
            3961,
            3964,
            3965,
            3968,
            3969,
            3972,
            3973,
            3976,
            3977,
            3980,
            3981,
            3984,
            3985,
            3987,
            3989,
            3991,
            3993,
            3995,
            3997,
            3999,
            4002,
            4003,
            4005,
            4008,
            4009,
            4012,
            4013,
            4016,
            4017,
            4020,
            4021,
            4024,
            4025,
            4028,
            4029,
            4032,
            4033,
            4035,
            4037,
            4039,
            4041,
            4043,
            4045,
            4047,
        ],
        'coordinates': [
            [1.5, 0.25, -0.3],
            [1.5, 0.25, -0.225],
            [1.41875, 0.25, -0.225],
            [1.41875, 0.25, -0.3],
            [1.5, 0.25, -0.15],
            [1.41875, 0.25, -0.15],
            [1.5, 0.25, -0.075],
            [1.41875, 0.25, -0.075],
            [1.5, 0.25, 0.0],
            [1.41875, 0.25, 0.0],
            [1.3375, 0.25, -0.225],
            [1.3375, 0.25, -0.3],
            [1.3375, 0.25, -0.15],
            [1.3375, 0.25, -0.075],
            [1.3375, 0.25, 0.0],
            [1.25625, 0.25, -0.225],
            [1.25625, 0.25, -0.3],
            [1.25625, 0.25, -0.15],
            [1.25625, 0.25, -0.075],
            [1.25625, 0.25, 0.0],
            [1.175, 0.25, -0.225],
            [1.175, 0.25, -0.3],
            [1.175, 0.25, -0.15],
            [1.175, 0.25, -0.075],
            [1.175, 0.25, 0.0],
            [1.09375, 0.25, -0.225],
            [1.09375, 0.25, -0.3],
            [1.09375, 0.25, -0.15],
            [1.09375, 0.25, -0.075],
            [1.09375, 0.25, 0.0],
            [1.0125, 0.25, -0.225],
            [1.0125, 0.25, -0.3],
            [1.0125, 0.25, -0.15],
            [1.0125, 0.25, -0.075],
            [1.0125, 0.25, 0.0],
            [0.93125, 0.25, -0.225],
            [0.93125, 0.25, -0.3],
            [0.93125, 0.25, -0.15],
            [0.93125, 0.25, -0.075],
            [0.93125, 0.25, 0.0],
            [0.85, 0.25, -0.225],
            [0.85, 0.25, -0.3],
            [0.85, 0.25, -0.15],
            [0.85, 0.25, -0.075],
            [0.85, 0.25, 0.0],
            [0.76875, 0.25, -0.225],
            [0.76875, 0.25, -0.3],
            [0.76875, 0.25, -0.15],
            [0.76875, 0.25, -0.075],
            [0.76875, 0.25, 0.0],
            [0.6875, 0.25, -0.225],
            [0.6875, 0.25, -0.3],
            [0.6875, 0.25, -0.15],
            [0.6875, 0.25, -0.075],
            [0.6875, 0.25, 0.0],
            [0.60625, 0.25, -0.225],
            [0.60625, 0.25, -0.3],
            [0.60625, 0.25, -0.15],
            [0.60625, 0.25, -0.075],
            [0.60625, 0.25, 0.0],
            [0.525, 0.25, -0.225],
            [0.525, 0.25, -0.3],
            [0.525, 0.25, -0.15],
            [0.525, 0.25, -0.075],
            [0.525, 0.25, 0.0],
            [0.44375, 0.25, -0.225],
            [0.44375, 0.25, -0.3],
            [0.44375, 0.25, -0.15],
            [0.44375, 0.25, -0.075],
            [0.44375, 0.25, 0.0],
            [0.3625, 0.25, -0.225],
            [0.3625, 0.25, -0.3],
            [0.3625, 0.25, -0.15],
            [0.3625, 0.25, -0.075],
            [0.3625, 0.25, 0.0],
            [0.28125, 0.25, -0.225],
            [0.28125, 0.25, -0.3],
            [0.28125, 0.25, -0.15],
            [0.28125, 0.25, -0.075],
            [0.28125, 0.25, 0.0],
            [0.2, 0.25, -0.225],
            [0.2, 0.25, -0.3],
            [0.2, 0.25, -0.15],
            [0.2, 0.25, -0.075],
            [0.2, 0.25, 0.0],
            [0.11875, 0.25, -0.225],
            [0.11875, 0.25, -0.3],
            [0.11875, 0.25, -0.15],
            [0.11875, 0.25, -0.075],
            [0.11875, 0.25, 0.0],
            [0.0375, 0.25, -0.225],
            [0.0375, 0.25, -0.3],
            [0.0375, 0.25, -0.15],
            [0.0375, 0.25, -0.075],
            [0.0375, 0.25, 0.0],
            [-0.04375, 0.25, -0.225],
            [-0.04375, 0.25, -0.3],
            [-0.04375, 0.25, -0.15],
            [-0.04375, 0.25, -0.075],
            [-0.04375, 0.25, 0.0],
            [-0.125, 0.25, -0.225],
            [-0.125, 0.25, -0.3],
            [-0.125, 0.25, -0.15],
            [-0.125, 0.25, -0.075],
            [-0.125, 0.25, 0.0],
            [-0.20625, 0.25, -0.225],
            [-0.20625, 0.25, -0.3],
            [-0.20625, 0.25, -0.15],
            [-0.20625, 0.25, -0.075],
            [-0.20625, 0.25, 0.0],
            [-0.2875, 0.25, -0.225],
            [-0.2875, 0.25, -0.3],
            [-0.2875, 0.25, -0.15],
            [-0.2875, 0.25, -0.075],
            [-0.2875, 0.25, 0.0],
            [-0.36875, 0.25, -0.225],
            [-0.36875, 0.25, -0.3],
            [-0.36875, 0.25, -0.15],
            [-0.36875, 0.25, -0.075],
            [-0.36875, 0.25, 0.0],
            [-0.45, 0.25, -0.225],
            [-0.45, 0.25, -0.3],
            [-0.45, 0.25, -0.15],
            [-0.45, 0.25, -0.075],
            [-0.45, 0.25, 0.0],
            [-1.0, 0.25, -0.3],
            [-1.0, 0.25, -0.225],
            [-1.0625, 0.25, -0.225],
            [-1.0625, 0.25, -0.3],
            [-1.0, 0.25, -0.15],
            [-1.0625, 0.25, -0.15],
            [-1.0, 0.25, -0.075],
            [-1.0625, 0.25, -0.075],
            [-1.0, 0.25, 0.0],
            [-1.0625, 0.25, 0.0],
            [-1.125, 0.25, -0.225],
            [-1.125, 0.25, -0.3],
            [-1.125, 0.25, -0.15],
            [-1.125, 0.25, -0.075],
            [-1.125, 0.25, 0.0],
            [-1.1875, 0.25, -0.225],
            [-1.1875, 0.25, -0.3],
            [-1.1875, 0.25, -0.15],
            [-1.1875, 0.25, -0.075],
            [-1.1875, 0.25, 0.0],
            [-1.25, 0.25, -0.225],
            [-1.25, 0.25, -0.3],
            [-1.25, 0.25, -0.15],
            [-1.25, 0.25, -0.075],
            [-1.25, 0.25, 0.0],
            [-1.3125, 0.25, -0.225],
            [-1.3125, 0.25, -0.3],
            [-1.3125, 0.25, -0.15],
            [-1.3125, 0.25, -0.075],
            [-1.3125, 0.25, 0.0],
            [-1.375, 0.25, -0.225],
            [-1.375, 0.25, -0.3],
            [-1.375, 0.25, -0.15],
            [-1.375, 0.25, -0.075],
            [-1.375, 0.25, 0.0],
            [-1.4375, 0.25, -0.225],
            [-1.4375, 0.25, -0.3],
            [-1.4375, 0.25, -0.15],
            [-1.4375, 0.25, -0.075],
            [-1.4375, 0.25, 0.0],
            [-1.5, 0.25, -0.225],
            [-1.5, 0.25, -0.3],
            [-1.5, 0.25, -0.15],
            [-1.5, 0.25, -0.075],
            [-1.5, 0.25, 0.0],
            [-0.95, 0.25, -0.3],
            [-0.95, 0.25, -0.225],
            [-0.95, 0.25, -0.15],
            [-0.95, 0.25, -0.075],
            [-0.95, 0.25, 0.0],
            [-0.8875, 0.25, -0.3],
            [-0.8875, 0.25, -0.225],
            [-0.8875, 0.25, -0.15],
            [-0.8875, 0.25, -0.075],
            [-0.8875, 0.25, 0.0],
            [-0.825, 0.25, -0.3],
            [-0.825, 0.25, -0.225],
            [-0.825, 0.25, -0.15],
            [-0.825, 0.25, -0.075],
            [-0.825, 0.25, 0.0],
            [-0.7625, 0.25, -0.3],
            [-0.7625, 0.25, -0.225],
            [-0.7625, 0.25, -0.15],
            [-0.7625, 0.25, -0.075],
            [-0.7625, 0.25, 0.0],
            [-0.7, 0.25, -0.3],
            [-0.7, 0.25, -0.225],
            [-0.7, 0.25, -0.15],
            [-0.7, 0.25, -0.075],
            [-0.7, 0.25, 0.0],
            [-0.6375, 0.25, -0.3],
            [-0.6375, 0.25, -0.225],
            [-0.6375, 0.25, -0.15],
            [-0.6375, 0.25, -0.075],
            [-0.6375, 0.25, 0.0],
            [-0.575, 0.25, -0.3],
            [-0.575, 0.25, -0.225],
            [-0.575, 0.25, -0.15],
            [-0.575, 0.25, -0.075],
            [-0.575, 0.25, 0.0],
            [-0.5125, 0.25, -0.3],
            [-0.5125, 0.25, -0.225],
            [-0.5125, 0.25, -0.15],
            [-0.5125, 0.25, -0.075],
            [-0.5125, 0.25, 0.0],
            [1.5, 0.25, -0.5],
            [1.41875, 0.25, -0.5],
            [1.5, 0.25, -0.43333333],
            [1.41875, 0.25, -0.43333333],
            [1.3375, 0.25, -0.5],
            [1.3375, 0.25, -0.43333333],
            [1.25625, 0.25, -0.5],
            [1.25625, 0.25, -0.43333333],
            [1.175, 0.25, -0.5],
            [1.175, 0.25, -0.43333333],
            [1.09375, 0.25, -0.5],
            [1.09375, 0.25, -0.43333333],
            [1.0125, 0.25, -0.5],
            [1.0125, 0.25, -0.43333333],
            [0.93125, 0.25, -0.5],
            [0.93125, 0.25, -0.43333333],
            [0.85, 0.25, -0.5],
            [0.85, 0.25, -0.43333333],
            [0.76875, 0.25, -0.5],
            [0.76875, 0.25, -0.43333333],
            [0.6875, 0.25, -0.5],
            [0.6875, 0.25, -0.43333333],
            [0.60625, 0.25, -0.5],
            [0.60625, 0.25, -0.43333333],
            [0.525, 0.25, -0.5],
            [0.525, 0.25, -0.43333333],
            [0.44375, 0.25, -0.5],
            [0.44375, 0.25, -0.43333333],
            [0.3625, 0.25, -0.5],
            [0.3625, 0.25, -0.43333333],
            [0.28125, 0.25, -0.5],
            [0.28125, 0.25, -0.43333333],
            [0.2, 0.25, -0.5],
            [0.2, 0.25, -0.43333333],
            [0.11875, 0.25, -0.5],
            [0.11875, 0.25, -0.43333333],
            [0.0375, 0.25, -0.5],
            [0.0375, 0.25, -0.43333333],
            [-0.04375, 0.25, -0.5],
            [-0.04375, 0.25, -0.43333333],
            [-0.125, 0.25, -0.5],
            [-0.125, 0.25, -0.43333333],
            [-0.20625, 0.25, -0.5],
            [-0.20625, 0.25, -0.43333333],
            [-0.2875, 0.25, -0.5],
            [-0.2875, 0.25, -0.43333333],
            [-0.36875, 0.25, -0.5],
            [-0.36875, 0.25, -0.43333333],
            [-0.45, 0.25, -0.5],
            [-0.45, 0.25, -0.43333333],
            [1.5, 0.25, -0.36666667],
            [1.41875, 0.25, -0.36666667],
            [1.3375, 0.25, -0.36666667],
            [1.25625, 0.25, -0.36666667],
            [1.175, 0.25, -0.36666667],
            [1.09375, 0.25, -0.36666667],
            [1.0125, 0.25, -0.36666667],
            [0.93125, 0.25, -0.36666667],
            [0.85, 0.25, -0.36666667],
            [0.76875, 0.25, -0.36666667],
            [0.6875, 0.25, -0.36666667],
            [0.60625, 0.25, -0.36666667],
            [0.525, 0.25, -0.36666667],
            [0.44375, 0.25, -0.36666667],
            [0.3625, 0.25, -0.36666667],
            [0.28125, 0.25, -0.36666667],
            [0.2, 0.25, -0.36666667],
            [0.11875, 0.25, -0.36666667],
            [0.0375, 0.25, -0.36666667],
            [-0.04375, 0.25, -0.36666667],
            [-0.125, 0.25, -0.36666667],
            [-0.20625, 0.25, -0.36666667],
            [-0.2875, 0.25, -0.36666667],
            [-0.36875, 0.25, -0.36666667],
            [-0.45, 0.25, -0.36666667],
            [-1.0, 0.25, -0.5],
            [-1.0625, 0.25, -0.5],
            [-1.0, 0.25, -0.43333333],
            [-1.0625, 0.25, -0.43333333],
            [-1.125, 0.25, -0.5],
            [-1.125, 0.25, -0.43333333],
            [-1.1875, 0.25, -0.5],
            [-1.1875, 0.25, -0.43333333],
            [-1.25, 0.25, -0.5],
            [-1.25, 0.25, -0.43333333],
            [-1.3125, 0.25, -0.5],
            [-1.3125, 0.25, -0.43333333],
            [-1.375, 0.25, -0.5],
            [-1.375, 0.25, -0.43333333],
            [-1.4375, 0.25, -0.5],
            [-1.4375, 0.25, -0.43333333],
            [-1.5, 0.25, -0.5],
            [-1.5, 0.25, -0.43333333],
            [-1.0, 0.25, -0.36666667],
            [-1.0625, 0.25, -0.36666667],
            [-1.125, 0.25, -0.36666667],
            [-1.1875, 0.25, -0.36666667],
            [-1.25, 0.25, -0.36666667],
            [-1.3125, 0.25, -0.36666667],
            [-1.375, 0.25, -0.36666667],
            [-1.4375, 0.25, -0.36666667],
            [-1.5, 0.25, -0.36666667],
            [-0.95, 0.25, -0.5],
            [-0.95, 0.25, -0.43333333],
            [-0.95, 0.25, -0.36666667],
            [-0.5125, 0.25, -0.5],
            [-0.5125, 0.25, -0.43333333],
            [-0.575, 0.25, -0.5],
            [-0.575, 0.25, -0.43333333],
            [-0.6375, 0.25, -0.5],
            [-0.6375, 0.25, -0.43333333],
            [-0.7, 0.25, -0.5],
            [-0.7, 0.25, -0.43333333],
            [-0.7625, 0.25, -0.5],
            [-0.7625, 0.25, -0.43333333],
            [-0.825, 0.25, -0.5],
            [-0.825, 0.25, -0.43333333],
            [-0.8875, 0.25, -0.5],
            [-0.8875, 0.25, -0.43333333],
            [-0.5125, 0.25, -0.36666667],
            [-0.575, 0.25, -0.36666667],
            [-0.6375, 0.25, -0.36666667],
            [-0.7, 0.25, -0.36666667],
            [-0.7625, 0.25, -0.36666667],
            [-0.825, 0.25, -0.36666667],
            [-0.8875, 0.25, -0.36666667],
        ],
    }
    # node_coordinates['coordinates'] = [ele.strip() for ele in node_coordinates['coordinates']]
    return node_coordinates
