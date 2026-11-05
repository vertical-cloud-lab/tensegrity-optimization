### t180 (transmissibility), held out over 35 design folds (44 articles)

| feature space | model | MAPE | RMSE | R2_oos | rho_s (perm p) | design-mean rho_s | r | spread / data sd | 95% cov |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 6 original parameters (shape + mass) | SAASBO (Ax, 256/512) | 5.2% | 0.0827 | +0.12 | +0.05 (0.731) | +0.06 | +0.32 | 0.47 | 84% |
| 6 original parameters (shape + mass) | training mean | 5.2% | 0.0881 | +0.00 | -0.86 (<0.001) | -0.99 | -0.92 | 0.03 | 91% |
| 6 original parameters (shape + mass) | print-session mean | 6.0% | 0.0871 | +0.02 | +0.03 (0.855) | +0.06 | +0.20 | 0.45 | 89% |
| 6 original parameters (shape + mass) | ridge (linear) | 5.2% | 0.0802 | +0.17 | +0.51 (<0.001) | +0.53 | +0.40 | 0.55 | 93% |
| 6 original parameters (shape + mass) | k-nearest neighbours | 4.4% | 0.0777 | +0.22 | +0.44 (0.003) | +0.49 | +0.53 | 0.69 | 93% |
| 6 original parameters (shape + mass) | GP, ARD Matern (ML-II) | 4.6% | 0.0734 | +0.31 | +0.51 (<0.001) | +0.56 | +0.56 | 0.77 | 75% |
| 6 original + 6 sim features | SAASBO (Ax, 256/512) | 5.4% | 0.0872 | +0.02 | -0.14 (0.370) | -0.14 | -0.04 | 0.13 | 86% |
| 6 original + 6 sim features | training mean | 5.2% | 0.0881 | +0.00 | -0.86 (<0.001) | -0.99 | -0.92 | 0.03 | 91% |
| 6 original + 6 sim features | print-session mean | 6.0% | 0.0871 | +0.02 | +0.03 (0.855) | +0.06 | +0.20 | 0.45 | 89% |
| 6 original + 6 sim features | ridge (linear) | 5.2% | 0.0792 | +0.19 | +0.54 (<0.001) | +0.58 | +0.45 | 0.65 | 89% |
| 6 original + 6 sim features | k-nearest neighbours | 4.4% | 0.0706 | +0.36 | +0.53 (<0.001) | +0.54 | +0.59 | 0.67 | 93% |
| 12 campaign parameters | SAASBO (Ax, 256/512) | 4.8% | 0.0824 | +0.12 | +0.32 (0.036) | +0.37 | +0.29 | 0.32 | 89% |
| 12 campaign parameters | training mean | 5.2% | 0.0881 | +0.00 | -0.86 (<0.001) | -0.99 | -0.92 | 0.03 | 91% |
| 12 campaign parameters | print-session mean | 6.0% | 0.0871 | +0.02 | +0.03 (0.855) | +0.06 | +0.20 | 0.45 | 89% |
| 12 campaign parameters | ridge (linear) | 5.4% | 0.084 | +0.09 | +0.41 (0.005) | +0.43 | +0.31 | 0.53 | 93% |
| 12 campaign parameters | k-nearest neighbours | 4.7% | 0.0761 | +0.25 | +0.52 (<0.001) | +0.58 | +0.51 | 0.71 | 95% |

### E_reb (mJ per drop), held out over 35 design folds (44 articles)

| feature space | model | MAPE | RMSE | R2_oos | rho_s (perm p) | design-mean rho_s | r | spread / data sd | 95% cov |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 6 original parameters (shape + mass) | SAASBO (Ax, 256/512) | 43.6% | 4.4 | -0.37 | -0.42 (0.005) | -0.31 | -0.41 | 0.37 | 84% |
| 6 original parameters (shape + mass) | training mean | 37.9% | 3.76 | -0.00 | -0.79 (<0.001) | -0.97 | -0.81 | 0.03 | 93% |
| 6 original parameters (shape + mass) | print-session mean | 38.9% | 3.96 | -0.11 | -0.20 (0.183) | -0.07 | -0.08 | 0.32 | 86% |
| 6 original parameters (shape + mass) | ridge (linear) | 36.2% | 3.57 | +0.10 | +0.28 (0.064) | +0.25 | +0.28 | 0.41 | 91% |
| 6 original parameters (shape + mass) | k-nearest neighbours | 37.2% | 3.75 | +0.00 | +0.23 (0.140) | +0.14 | +0.16 | 0.41 | 89% |
| 6 original parameters (shape + mass) | GP, ARD Matern (ML-II) | 36.2% | 3.67 | +0.05 | +0.24 (0.123) | +0.17 | +0.18 | 0.32 | 36% |
| 6 original + 6 sim features | SAASBO (Ax, 256/512) | 43.5% | 4.28 | -0.30 | -0.71 (<0.001) | -0.67 | -0.44 | 0.30 | 89% |
| 6 original + 6 sim features | training mean | 37.9% | 3.76 | -0.00 | -0.79 (<0.001) | -0.97 | -0.81 | 0.03 | 93% |
| 6 original + 6 sim features | print-session mean | 38.9% | 3.96 | -0.11 | -0.20 (0.183) | -0.07 | -0.08 | 0.32 | 86% |
| 6 original + 6 sim features | ridge (linear) | 35.1% | 3.51 | +0.13 | +0.35 (0.021) | +0.33 | +0.31 | 0.38 | 91% |
| 6 original + 6 sim features | k-nearest neighbours | 38.7% | 3.87 | -0.06 | +0.06 (0.716) | -0.07 | +0.04 | 0.38 | 91% |
| 12 campaign parameters | SAASBO (Ax, 256/512) | 38.8% | 3.84 | -0.05 | -0.40 (0.008) | -0.30 | -0.36 | 0.11 | 93% |
| 12 campaign parameters | training mean | 37.9% | 3.76 | -0.00 | -0.79 (<0.001) | -0.97 | -0.81 | 0.03 | 93% |
| 12 campaign parameters | print-session mean | 38.9% | 3.96 | -0.11 | -0.20 (0.183) | -0.07 | -0.08 | 0.32 | 86% |
| 12 campaign parameters | ridge (linear) | 34.9% | 3.57 | +0.10 | +0.37 (0.014) | +0.41 | +0.30 | 0.47 | 91% |
| 12 campaign parameters | k-nearest neighbours | 39.6% | 3.85 | -0.05 | +0.14 (0.359) | +0.09 | +0.14 | 0.49 | 89% |
