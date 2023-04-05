(ocean-translating-low)=

# translating_low

The `translating_low'` test case implements the Forced Nonlinear System with a Translating Low
 test case as described in
 [Williamson et al. 1992](<https://doi.org/10.1016/S0021-9991(05)80016-6>). The flow field, 
described in [Browning et al. 1989](<https://doi.org/10.1175/1520-0493(1989)117<1058:ACOTNM>2.0.CO;2>), 
is a tranlating low pressure center superimposed on a zonal jet. 
It is meant to represent some of the characteristics of tropospheric flows (i.e. a trough in a westerly jet).

## Initial conditions (and forcing?)
The inital flow is given by:

$$
u = u_0 \sin^{14}(2\theta) -  \psi_{theta} / a
v = \psi_{\lambda} / (a \cos\theta)
gh = gh_0 - \int\limits_(-\pi/2)^\theta [a f(\tau) + u(\tau)\tan\tau]u(\tau) d\tau + f\psi 

with \psi(\lambda, \theta, t) = \psi_0 exp -\sigma ((1-C)/1+C))


$$

where $a$ = 6.37122 x 10 ^{6} m, $u_0$ = 40 m.s^{-1} 
and 
$$
C = \sin \theta_0 \sin \theta + \cos \theta_0 \cos \theta \cos (\lambda- u_0/a t - \lambda_0)
$$


## Initial conditions
The center of the low is initally located at (\laba_0, \theata_0)= (0, \pi/4). 


$$
\psi =
    \begin{cases}
        \left( \psi_0/2 \right) \left[ 1 + \cos(\pi r/R )\right] &
            \text{if } r < R \\
        0 & \text{if } r \ge R
    \end{cases}
$$

where $\psi_0 = 1$, the bell radius $R = a/3$, and $a$ is
the radius of the sphere.  The equatorial velocity
$u_0 = 2 \pi a/ (\text{24 days})$. The time step is proportional to the
grid-cell size.

By default, the resolution is varied from 60 km to 240 km in steps of 30 km.
The result of the `analysis` step of the test case is a plot like the
following showing the $l_2$ error as a function of time:

```{image} images/translating_low_initial.png
:align: center
:width: 500 px
```

### config options

The `translating_low` config options include:

```cfg
# options for translating low test case
[translating_low]

# the constant temperature of the domain
temperature = 15.0

# the constant salinity of the domain
salinity = 35.0

# the initial central latitude (rad) of the low 
lat_center = 3.14159265/4.

# the initial central longitude (rad) of the low
lon_center = 0.0

# the exponential spatial decay rate of the low
sigma = 2123666.6667

# max of the low geopotential perturbation
psi0 = 1.0

# bakground velocity maximum (m/s)
u0 = 40

## resolution

The default resolution used in the test case is 

## error

The error used by default is the $l_2$ norm. Other $l$ norms (suggested by
original paper) may be added adt a later stage.

