# Episode 2: Model Training of the Incidence Operator

---

## Description

Thank you very much for tuning in to the second issue. In the previous tutorial, we covered Step 1: Sampling. In this tutorial, we now move on to **Step 2.1: Model training of the incidence operator $\eta$**.

---

📹 [**Enjoy watching!**](https://youtu.be/KxqmIYTPojU)

---

The incidence operator $\eta_i$ is defined for a specific incidence direction ($\theta_i$, $\varphi_i$) and material-specific (or geometric) configuration of the scene ($u_1$, $u_2$, $u_3$). The scene is sampled for a defined radiance/luminance value of $L=1.5e7$ and a solar half-angle of $\alpha_{sun}=0.2665^\circ$ using the [RADIANCE](https://doi.org/10.1145/192161.192286) ray-tracer. The incidence operator $\eta_i$ is derived from the determined irradiance/illuminance value $q_i$ using $\eta_i = \frac{q_i}{L2\pi(1-\cos(\alpha_{sun}))}$.

Using the presented [Grasshopper script](./src/02_ModelTraining_TheIncidenceOperator/design.gh) and custom components, we have generated the training data consisting of the [Feature Matrix](src/02_ModelTraining_TheIncidenceOperator/X.npy) and the [Targets](src/02_ModelTraining_TheIncidenceOperator/y.npy). The feature matrix contains the variables `{zen, azi, u1, u2, u3}`. These correspond to the zenith and azimuth angles of 3000 Fibonacci-distributed incidence directions, analyzed for tuples of `(u1, u2, u3)` describing the tint states of regions 1, 2, and 3 (from 0/transparent to 100/opaque). The material data were taken from Table 1 of the [study](https://doi.org/10.1016/j.jobe.2021.102535).

The training data was generated for a uniform 5x5x5 meshgrid of tint states, resulting in a total of 375,000 data points. In this tutorial, we will create a continuous model from this data using the `sklearn` routine `DecisionTreeRegressor`.

Feel free to click through the jupyter [notebook](src/02_ModelTraining_TheIncidenceOperator/tutorial.ipynb) to understand the code and try it out yourself!

---

## Feedback

How did you like it? Do you have a suggestion for the next newsletter?

Then simply leave a comment.

---

Best regards from  
*sweet and serious Simon from Stuttgart in southern Germany*