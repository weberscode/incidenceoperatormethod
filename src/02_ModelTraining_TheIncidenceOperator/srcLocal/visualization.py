import numpy as np
import plotly.graph_objects as go
import ipywidgets as widgets
from IPython.display import display

# %% Functions and Classes
class ScatterVisualizer:
    """
    A class to visualize model predictions as a 3D surface.
    All controls (sliders) are aligned in a single column.
    """

    def __init__(self, X, y):
        """
        Initialize the visualizer.

        Parameters:
        -----------
        X : The feature matrix
        y : The target matrix
        """
        self.X = X
        self.y = y

        # Create widgets
        self.s1 = widgets.FloatSlider(
            value=0, min=0, max=100, step=25,
            description='Tint reg. 1', continuous_update=False
        )
        self.s2 = widgets.FloatSlider(
            value=0, min=0, max=100, step=25,
            description='Tint reg. 2', continuous_update=False
        )
        self.s3 = widgets.FloatSlider(
            value=0, min=0, max=100, step=25,
            description='Tint reg. 3', continuous_update=False
        )

        # Output container
        self.out = widgets.Output()

        # Build UI
        self.controls = widgets.VBox([
            self.s1, self.s2, self.s3
        ])

        self.app = widgets.VBox([self.out, self.controls])

        # Connect sliders → update on change
        for slider in [self.s1, self.s2, self.s3]:
            slider.observe(self._update_surface, names='value')

        # Initial render
        self._update_surface()


    # -------------------------------------------------
    # Core Logic
    # -------------------------------------------------
    def _predict(self, u1, u2, u3):
        """
        Extract 3D scatter data from all data
        """
        # Identify indices matching current slider values
        ids = np.where(
            (self.X[:,2] == u1) &
            (self.X[:,3] == u2) &
            (self.X[:,4] == u3)
        )[0]
        # Extract spherical coordinates
        zens = self.X[ids,0]
        azis = self.X[ids,1]

        # Extract targets
        r = self.y[ids,:]

        # Convert to Cartesian coordinates
        x = np.zeros_like(r)
        y = np.zeros_like(r)
        z = np.zeros_like(r)
        for i in range(x.shape[1]):
            x[:, i], y[:, i], z[:, i] = sph2cart(zens, azis, r[:, i])

        # Reshape to 2D grid
        return (x, y, z)


    def _make_figure(self, u1, u2, u3):
        """Create Plotly figure for current parameters."""
        X, Y, Z = self._predict(u1, u2, u3)

        fig = go.Figure()
        for i in range(X.shape[1]):
            # add 3D scatter plot with label
            fig.add_trace(go.Scatter3d(x=X[:, i], y=Y[:, i], z=Z[:, i], mode='markers', marker=dict(size=2), name='Sensor ' + str(i + 1)))

        fig.update_layout(
            width=700,
            height=500,
            margin=dict(l=0, r=0, t=30, b=0),
            title=f'Incidence operator of all sensors',
            scene=dict(
                aspectmode='cube',
                xaxis=dict(range=[-0.4, 0.4]),
                yaxis=dict(range=[-.4, 0]),
                zaxis=dict(range=[0, .4]),
                camera=dict(eye=dict(x=1.2, y=-1.8, z=0.9))
            ),
        )
        return fig

    # -------------------------------------------------
    # Update Handler
    # -------------------------------------------------
    def _update_surface(self, change=None):
        """Update the 3D plot when any slider changes."""
        with self.out:
            self.out.clear_output(wait=True)
            fig = self._make_figure(
                self.s1.value,
                self.s2.value,
                self.s3.value
            )
            display(fig)

    # -------------------------------------------------
    # Display the UI
    # -------------------------------------------------
    def show(self):
        """Render the widget in the notebook."""
        display(self.app)

class SurfaceVisualizer:
    """
    A class to visualize model predictions as a 3D surface.
    All controls (sliders) are aligned in a single column.
    """

    def __init__(self, model, res=50):
        """
        Initialize the visualizer.

        Parameters:
        -----------
        model : trained model
            Model used for prediction.
        res : int, optional
            Resolution of the spherical grid (default=50).
        """
        self.model = model
        self.res = res

        # Create widgets
        self.s1 = widgets.FloatSlider(
            value=0, min=0, max=100, step=1,
            description='Tint reg. 1', continuous_update=False
        )
        self.s2 = widgets.FloatSlider(
            value=0, min=0, max=100, step=1,
            description='Tint reg. 2', continuous_update=False
        )
        self.s3 = widgets.FloatSlider(
            value=0, min=0, max=100, step=1,
            description='Tint reg. 3', continuous_update=False
        )
        self.s4 = widgets.IntSlider(
            value=1, min=1, max=2, step=1,
            description='Sensor', continuous_update=False
        )

        # Output container
        self.out = widgets.Output()

        # Build UI
        self.controls = widgets.VBox([
            self.s1, self.s2, self.s3, self.s4
        ])

        self.app = widgets.VBox([self.out, self.controls])

        # Connect sliders → update on change
        for slider in [self.s1, self.s2, self.s3, self.s4]:
            slider.observe(self._update_surface, names='value')

        # Initial render
        self._update_surface()


    # -------------------------------------------------
    # Core Logic
    # -------------------------------------------------
    def _predict(self, u1, u2, u3, target):
        """
        Generate 3D surface data from model prediction.
        """
        # Spherical grid
        zens = np.linspace(0, np.pi/2, self.res)
        azis = np.linspace(0, 2*np.pi, self.res)
        zens, azis = np.meshgrid(zens, azis)

        # Flatten & build feature matrix
        z_flat = zens.flatten()
        a_flat = azis.flatten()
        features = np.column_stack((z_flat, a_flat,
                                   np.full(len(z_flat), u1),
                                   np.full(len(z_flat), u2),
                                   np.full(len(z_flat), u3)))

        # Predict
        r = self.model.predict(features)[:, target-1]

        # Convert to Cartesian coordinates
        X, Y, Z = sph2cart(z_flat, a_flat, r)
        X = X.reshape(zens.shape)
        Y = Y.reshape(zens.shape)
        Z = Z.reshape(zens.shape)

        return X, Y, Z

    def _make_figure(self, u1, u2, u3, target):
        """Create Plotly figure for current parameters."""
        X, Y, Z = self._predict(u1, u2, u3, target)

        fig = go.Figure()
        # add 3D scatter plot with label
        fig.add_trace(go.Surface(x=X, y=Y, z=Z,
                                 colorscale='Viridis',
                                 cmin=0, cmax=0.2,
                                 colorbar=dict(title='Value')))

        fig.update_layout(
            width=700,
            height=500,
            margin=dict(l=0, r=0, t=30, b=0),
            title=f'Incidence operator of all sensors',
            scene=dict(
                aspectmode='cube',
                xaxis=dict(range=[-0.4, 0.4]),
                yaxis=dict(range=[-.4, 0]),
                zaxis=dict(range=[0, .4]),
                camera=dict(eye=dict(x=1.2, y=-1.8, z=0.9))
            ),
        )
        return fig

    # -------------------------------------------------
    # Update Handler
    # -------------------------------------------------
    def _update_surface(self, change=None):
        """Update the 3D plot when any slider changes."""
        with self.out:
            self.out.clear_output(wait=True)
            fig = self._make_figure(
                self.s1.value,
                self.s2.value,
                self.s3.value,
                self.s4.value
            )
            display(fig)

    # -------------------------------------------------
    # Display the UI
    # -------------------------------------------------
    def show(self):
        """Render the widget in the notebook."""
        display(self.app)

def sph2cart(zen, azi, r):
    """
    Convert spherical coordinates to cartesian coordinates.
    :param r: radius
    :param zen: zenith angle in radians
    :param azi: azimuth angle in radians
    :return: x, y, z: cartesian coordinates
    """
    x = r * np.sin(zen) * np.cos(azi)
    y = r * np.sin(zen) * np.sin(azi)
    z = r * np.cos(zen)

    return x, y, z