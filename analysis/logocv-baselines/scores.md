## Summary: BO-framework surrogates against the reference baselines

### Spearman rho_s, held-out prediction vs measurement (two-sided permutation p in brackets)

| model | noise | t180, 6 orig. | t180, 6 orig. + sim | t180, 12 campaign | E_reb, 6 orig. | E_reb, 6 orig. + sim | E_reb, 12 campaign |
|---|---|--:|--:|--:|--:|--:|--:|
| SAASBO (Ax, 256/512) | SEMs as known noise (campaign) | +0.05 (0.731) | -0.14 (0.370) | +0.32 (0.036) | -0.42 (0.005) | -0.71 (<0.001) | -0.40 (0.008) |
| SAASBO, noise learned (256/512) | learned | +0.53 (<0.001) | +0.55 (<0.001) | +0.55 (<0.001) | +0.27 (0.071) | +0.33 (0.029) | +0.51 (<0.001) |
| Ax default (GP, MAP, SEMs as noise) | SEMs as known noise | +0.20 (0.204) | +0.19 (0.223) | +0.29 (0.055) | -0.20 (0.193) | -0.64 (<0.001) | -0.09 (0.570) |
| Ax default, noise learned | learned | +0.52 (<0.001) | +0.41 (0.007) | +0.53 (<0.001) | +0.19 (0.214) | +0.33 (0.027) | +0.54 (<0.001) |
| Ax GP without Winsorize (SEMs as noise) | SEMs as known noise | +0.02 (0.921) | -0.01 (0.936) | +0.39 (0.008) | -0.26 (0.084) | -0.64 (<0.001) | -0.09 (0.570) |
| BoFire default (GP, MAP, noise learned) | learned | +0.53 (<0.001) | +0.41 (0.006) | +0.48 (0.001) | +0.19 (0.227) | +0.28 (0.063) | +0.53 (<0.001) |
| GP, ARD Matern (ML-II) | learned (white-noise term) | +0.51 (<0.001) | +0.41 (0.006) | +0.55 (<0.001) | +0.24 (0.123) | +0.21 (0.172) | +0.41 (0.006) |
| random forest (tuned) | n/a | +0.59 (<0.001) | +0.65 (<0.001) | +0.52 (<0.001) | +0.13 (0.390) | +0.20 (0.191) | +0.27 (0.082) |
| training mean | n/a | mechanical | mechanical | mechanical | mechanical | mechanical | mechanical |

### R2_oos (1 - SSE / SSE of the per-fold training mean; 0 = the mean predictor)

| model | noise | t180, 6 orig. | t180, 6 orig. + sim | t180, 12 campaign | E_reb, 6 orig. | E_reb, 6 orig. + sim | E_reb, 12 campaign |
|---|---|--:|--:|--:|--:|--:|--:|
| SAASBO (Ax, 256/512) | SEMs as known noise (campaign) | +0.12 | +0.02 | +0.12 | -0.37 | -0.30 | -0.05 |
| SAASBO, noise learned (256/512) | learned | +0.41 | +0.44 | +0.40 | +0.09 | +0.12 | +0.23 |
| Ax default (GP, MAP, SEMs as noise) | SEMs as known noise | +0.12 | +0.08 | +0.08 | -0.48 | -0.66 | -0.01 |
| Ax default, noise learned | learned | +0.39 | +0.30 | +0.36 | -0.01 | +0.08 | +0.34 |
| Ax GP without Winsorize (SEMs as noise) | SEMs as known noise | +0.11 | +0.13 | -0.04 | -0.51 | -0.66 | -0.01 |
| BoFire default (GP, MAP, noise learned) | learned | +0.40 | +0.31 | +0.29 | -0.01 | +0.03 | +0.34 |
| GP, ARD Matern (ML-II) | learned (white-noise term) | +0.31 | +0.16 | +0.34 | +0.05 | -0.02 | +0.18 |
| random forest (tuned) | n/a | +0.40 | +0.49 | +0.33 | -0.08 | +0.04 | +0.08 |
| training mean | n/a | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 |

### MAPE

| model | noise | t180, 6 orig. | t180, 6 orig. + sim | t180, 12 campaign | E_reb, 6 orig. | E_reb, 6 orig. + sim | E_reb, 12 campaign |
|---|---|--:|--:|--:|--:|--:|--:|
| SAASBO (Ax, 256/512) | SEMs as known noise (campaign) | 5.2% | 5.4% | 4.8% | 43.6% | 43.5% | 38.8% |
| SAASBO, noise learned (256/512) | learned | 4.3% | 4.5% | 4.6% | 36.4% | 35.4% | 33.2% |
| Ax default (GP, MAP, SEMs as noise) | SEMs as known noise | 5.1% | 5.1% | 5.1% | 47.0% | 48.7% | 36.7% |
| Ax default, noise learned | learned | 4.2% | 4.6% | 4.6% | 38.8% | 35.5% | 30.2% |
| Ax GP without Winsorize (SEMs as noise) | SEMs as known noise | 5.3% | 5.2% | 5.4% | 48.8% | 48.7% | 36.7% |
| BoFire default (GP, MAP, noise learned) | learned | 4.1% | 4.7% | 4.9% | 38.8% | 36.7% | 30.3% |
| GP, ARD Matern (ML-II) | learned (white-noise term) | 4.6% | 5.2% | 4.4% | 36.2% | 35.9% | 33.9% |
| random forest (tuned) | n/a | 4.5% | 4.1% | 5.0% | 40.5% | 35.8% | 35.9% |
| training mean | n/a | 5.2% | 5.2% | 5.2% | 37.9% | 37.9% | 37.9% |

## Full scorecard

### t180 (transmissibility), held out over 35 design folds (44 articles)

| feature space | model | MAPE | RMSE | R2_oos | rho_s (perm p) | design-mean rho_s | r | spread / data sd | 95% cov |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 6 original parameters (shape + mass) | SAASBO (Ax, 256/512) | 5.2% | 0.0827 | +0.12 | +0.05 (0.731) | +0.06 | +0.32 | 0.47 | 84% |
| 6 original parameters (shape + mass) | Ax default (GP, MAP, SEMs as noise) | 5.1% | 0.0825 | +0.12 | +0.20 (0.204) | +0.22 | +0.35 | 0.53 | 75% |
| 6 original parameters (shape + mass) | BoFire default (GP, MAP, noise learned) | 4.1% | 0.0682 | +0.40 | +0.53 (<0.001) | +0.58 | +0.62 | 0.66 | 89% |
| 6 original parameters (shape + mass) | training mean | 5.2% | 0.0881 | +0.00 | -0.86 (<0.001) | -0.99 | -0.92 | 0.03 | 91% |
| 6 original parameters (shape + mass) | print-session mean | 6.0% | 0.0871 | +0.02 | +0.03 (0.855) | +0.06 | +0.20 | 0.45 | 89% |
| 6 original parameters (shape + mass) | ridge (linear) | 5.2% | 0.0802 | +0.17 | +0.51 (<0.001) | +0.53 | +0.40 | 0.55 | 93% |
| 6 original parameters (shape + mass) | k-nearest neighbours | 4.4% | 0.0777 | +0.22 | +0.44 (0.003) | +0.49 | +0.53 | 0.69 | 93% |
| 6 original parameters (shape + mass) | random forest (tuned) | 4.5% | 0.0682 | +0.40 | +0.59 (<0.001) | +0.63 | +0.61 | 0.60 | 93% |
| 6 original parameters (shape + mass) | GP, ARD Matern (ML-II) | 4.6% | 0.0734 | +0.31 | +0.51 (<0.001) | +0.56 | +0.56 | 0.77 | 75% |
| 6 original parameters (shape + mass) | Ax GP without Winsorize (SEMs as noise) | 5.3% | 0.0832 | +0.11 | +0.02 (0.921) | +0.00 | +0.34 | 0.56 | 80% |
| 6 original parameters (shape + mass) | Ax default, noise learned | 4.2% | 0.0689 | +0.39 | +0.52 (<0.001) | +0.55 | +0.62 | 0.61 | 77% |
| 6 original parameters (shape + mass) | SAASBO, noise learned (256/512) | 4.3% | 0.0675 | +0.41 | +0.53 (<0.001) | +0.60 | +0.63 | 0.71 | 91% |
| 6 original + 6 sim features | SAASBO (Ax, 256/512) | 5.4% | 0.0872 | +0.02 | -0.14 (0.370) | -0.14 | -0.04 | 0.13 | 86% |
| 6 original + 6 sim features | Ax default (GP, MAP, SEMs as noise) | 5.1% | 0.0846 | +0.08 | +0.19 (0.223) | +0.09 | +0.20 | 0.26 | 77% |
| 6 original + 6 sim features | BoFire default (GP, MAP, noise learned) | 4.7% | 0.0733 | +0.31 | +0.41 (0.006) | +0.44 | +0.55 | 0.70 | 84% |
| 6 original + 6 sim features | training mean | 5.2% | 0.0881 | +0.00 | -0.86 (<0.001) | -0.99 | -0.92 | 0.03 | 91% |
| 6 original + 6 sim features | print-session mean | 6.0% | 0.0871 | +0.02 | +0.03 (0.855) | +0.06 | +0.20 | 0.45 | 89% |
| 6 original + 6 sim features | ridge (linear) | 5.2% | 0.0792 | +0.19 | +0.54 (<0.001) | +0.58 | +0.45 | 0.65 | 89% |
| 6 original + 6 sim features | k-nearest neighbours | 4.4% | 0.0706 | +0.36 | +0.53 (<0.001) | +0.54 | +0.59 | 0.67 | 93% |
| 6 original + 6 sim features | random forest (tuned) | 4.1% | 0.0627 | +0.49 | +0.65 (<0.001) | +0.71 | +0.69 | 0.66 | 91% |
| 6 original + 6 sim features | GP, ARD Matern (ML-II) | 5.2% | 0.0807 | +0.16 | +0.41 (0.006) | +0.44 | +0.48 | 0.81 | 70% |
| 6 original + 6 sim features | Ax GP without Winsorize (SEMs as noise) | 5.2% | 0.0821 | +0.13 | -0.01 (0.936) | -0.13 | +0.34 | 0.50 | 82% |
| 6 original + 6 sim features | Ax default, noise learned | 4.6% | 0.0736 | +0.30 | +0.41 (0.007) | +0.42 | +0.54 | 0.58 | 73% |
| 6 original + 6 sim features | SAASBO, noise learned (256/512) | 4.5% | 0.0659 | +0.44 | +0.55 (<0.001) | +0.60 | +0.64 | 0.66 | 91% |
| 12 campaign parameters | SAASBO (Ax, 256/512) | 4.8% | 0.0824 | +0.12 | +0.32 (0.036) | +0.37 | +0.29 | 0.32 | 89% |
| 12 campaign parameters | Ax default (GP, MAP, SEMs as noise) | 5.1% | 0.0847 | +0.08 | +0.29 (0.055) | +0.32 | +0.31 | 0.52 | 82% |
| 12 campaign parameters | BoFire default (GP, MAP, noise learned) | 4.9% | 0.0742 | +0.29 | +0.48 (0.001) | +0.54 | +0.54 | 0.74 | 89% |
| 12 campaign parameters | training mean | 5.2% | 0.0881 | +0.00 | -0.86 (<0.001) | -0.99 | -0.92 | 0.03 | 91% |
| 12 campaign parameters | print-session mean | 6.0% | 0.0871 | +0.02 | +0.03 (0.855) | +0.06 | +0.20 | 0.45 | 89% |
| 12 campaign parameters | ridge (linear) | 5.4% | 0.084 | +0.09 | +0.41 (0.005) | +0.43 | +0.31 | 0.53 | 93% |
| 12 campaign parameters | k-nearest neighbours | 4.7% | 0.0761 | +0.25 | +0.52 (<0.001) | +0.58 | +0.51 | 0.71 | 95% |
| 12 campaign parameters | random forest (tuned) | 5.0% | 0.0722 | +0.33 | +0.52 (<0.001) | +0.58 | +0.56 | 0.67 | 93% |
| 12 campaign parameters | GP, ARD Matern (ML-II) | 4.4% | 0.0714 | +0.34 | +0.55 (<0.001) | +0.61 | +0.59 | 0.77 | 77% |
| 12 campaign parameters | Ax GP without Winsorize (SEMs as noise) | 5.4% | 0.0896 | -0.04 | +0.39 (0.008) | +0.42 | +0.22 | 0.58 | 80% |
| 12 campaign parameters | Ax default, noise learned | 4.6% | 0.0705 | +0.36 | +0.53 (<0.001) | +0.58 | +0.59 | 0.64 | 77% |
| 12 campaign parameters | SAASBO, noise learned (256/512) | 4.6% | 0.0683 | +0.40 | +0.55 (<0.001) | +0.62 | +0.61 | 0.70 | 93% |

### E_reb (mJ per drop), held out over 35 design folds (44 articles)

| feature space | model | MAPE | RMSE | R2_oos | rho_s (perm p) | design-mean rho_s | r | spread / data sd | 95% cov |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 6 original parameters (shape + mass) | SAASBO (Ax, 256/512) | 43.6% | 4.4 | -0.37 | -0.42 (0.005) | -0.31 | -0.41 | 0.37 | 84% |
| 6 original parameters (shape + mass) | Ax default (GP, MAP, SEMs as noise) | 47.0% | 4.58 | -0.48 | -0.20 (0.193) | -0.04 | -0.16 | 0.60 | 73% |
| 6 original parameters (shape + mass) | BoFire default (GP, MAP, noise learned) | 38.8% | 3.78 | -0.01 | +0.19 (0.227) | +0.14 | +0.16 | 0.45 | 52% |
| 6 original parameters (shape + mass) | training mean | 37.9% | 3.76 | +0.00 | -0.79 (<0.001) | -0.97 | -0.81 | 0.03 | 93% |
| 6 original parameters (shape + mass) | print-session mean | 38.9% | 3.96 | -0.11 | -0.20 (0.183) | -0.07 | -0.08 | 0.32 | 86% |
| 6 original parameters (shape + mass) | ridge (linear) | 36.2% | 3.57 | +0.10 | +0.28 (0.064) | +0.25 | +0.28 | 0.41 | 91% |
| 6 original parameters (shape + mass) | k-nearest neighbours | 37.2% | 3.75 | +0.00 | +0.23 (0.140) | +0.14 | +0.16 | 0.41 | 89% |
| 6 original parameters (shape + mass) | random forest (tuned) | 40.5% | 3.9 | -0.08 | +0.13 (0.390) | +0.10 | -0.02 | 0.34 | 89% |
| 6 original parameters (shape + mass) | GP, ARD Matern (ML-II) | 36.2% | 3.67 | +0.05 | +0.24 (0.123) | +0.17 | +0.18 | 0.32 | 36% |
| 6 original parameters (shape + mass) | Ax GP without Winsorize (SEMs as noise) | 48.8% | 4.62 | -0.51 | -0.26 (0.084) | -0.15 | -0.21 | 0.57 | 73% |
| 6 original parameters (shape + mass) | Ax default, noise learned | 38.8% | 3.78 | -0.01 | +0.19 (0.214) | +0.14 | +0.16 | 0.45 | 52% |
| 6 original parameters (shape + mass) | SAASBO, noise learned (256/512) | 36.4% | 3.59 | +0.09 | +0.27 (0.071) | +0.23 | +0.25 | 0.37 | 50% |
| 6 original + 6 sim features | SAASBO (Ax, 256/512) | 43.5% | 4.28 | -0.30 | -0.71 (<0.001) | -0.67 | -0.44 | 0.30 | 89% |
| 6 original + 6 sim features | Ax default (GP, MAP, SEMs as noise) | 48.7% | 4.83 | -0.66 | -0.64 (<0.001) | -0.59 | -0.35 | 0.57 | 77% |
| 6 original + 6 sim features | BoFire default (GP, MAP, noise learned) | 36.7% | 3.7 | +0.03 | +0.28 (0.063) | +0.23 | +0.23 | 0.48 | 61% |
| 6 original + 6 sim features | training mean | 37.9% | 3.76 | +0.00 | -0.79 (<0.001) | -0.97 | -0.81 | 0.03 | 93% |
| 6 original + 6 sim features | print-session mean | 38.9% | 3.96 | -0.11 | -0.20 (0.183) | -0.07 | -0.08 | 0.32 | 86% |
| 6 original + 6 sim features | ridge (linear) | 35.1% | 3.51 | +0.13 | +0.35 (0.021) | +0.33 | +0.31 | 0.38 | 91% |
| 6 original + 6 sim features | k-nearest neighbours | 38.7% | 3.87 | -0.06 | +0.06 (0.716) | -0.07 | +0.04 | 0.38 | 91% |
| 6 original + 6 sim features | random forest (tuned) | 35.8% | 3.67 | +0.04 | +0.20 (0.191) | +0.18 | +0.20 | 0.39 | 91% |
| 6 original + 6 sim features | GP, ARD Matern (ML-II) | 35.9% | 3.79 | -0.02 | +0.21 (0.172) | +0.12 | +0.12 | 0.39 | 34% |
| 6 original + 6 sim features | Ax GP without Winsorize (SEMs as noise) | 48.7% | 4.83 | -0.66 | -0.64 (<0.001) | -0.59 | -0.35 | 0.57 | 77% |
| 6 original + 6 sim features | Ax default, noise learned | 35.5% | 3.61 | +0.08 | +0.33 (0.027) | +0.29 | +0.27 | 0.46 | 64% |
| 6 original + 6 sim features | SAASBO, noise learned (256/512) | 35.4% | 3.53 | +0.12 | +0.33 (0.029) | +0.28 | +0.29 | 0.39 | 55% |
| 12 campaign parameters | SAASBO (Ax, 256/512) | 38.8% | 3.84 | -0.05 | -0.40 (0.008) | -0.30 | -0.36 | 0.11 | 93% |
| 12 campaign parameters | Ax default (GP, MAP, SEMs as noise) | 36.7% | 3.78 | -0.01 | -0.09 (0.570) | +0.16 | +0.08 | 0.33 | 91% |
| 12 campaign parameters | BoFire default (GP, MAP, noise learned) | 30.3% | 3.06 | +0.34 | +0.53 (<0.001) | +0.61 | +0.56 | 0.53 | 77% |
| 12 campaign parameters | training mean | 37.9% | 3.76 | +0.00 | -0.79 (<0.001) | -0.97 | -0.81 | 0.03 | 93% |
| 12 campaign parameters | print-session mean | 38.9% | 3.96 | -0.11 | -0.20 (0.183) | -0.07 | -0.08 | 0.32 | 86% |
| 12 campaign parameters | ridge (linear) | 34.9% | 3.57 | +0.10 | +0.37 (0.014) | +0.41 | +0.30 | 0.47 | 91% |
| 12 campaign parameters | k-nearest neighbours | 39.6% | 3.85 | -0.05 | +0.14 (0.359) | +0.09 | +0.14 | 0.49 | 89% |
| 12 campaign parameters | random forest (tuned) | 35.9% | 3.61 | +0.08 | +0.27 (0.082) | +0.41 | +0.24 | 0.39 | 91% |
| 12 campaign parameters | GP, ARD Matern (ML-II) | 33.9% | 3.4 | +0.18 | +0.41 (0.006) | +0.46 | +0.39 | 0.47 | 57% |
| 12 campaign parameters | Ax GP without Winsorize (SEMs as noise) | 36.7% | 3.78 | -0.01 | -0.09 (0.570) | +0.16 | +0.08 | 0.33 | 91% |
| 12 campaign parameters | Ax default, noise learned | 30.2% | 3.04 | +0.34 | +0.54 (<0.001) | +0.62 | +0.56 | 0.54 | 77% |
| 12 campaign parameters | SAASBO, noise learned (256/512) | 33.2% | 3.3 | +0.23 | +0.51 (<0.001) | +0.55 | +0.44 | 0.41 | 73% |
