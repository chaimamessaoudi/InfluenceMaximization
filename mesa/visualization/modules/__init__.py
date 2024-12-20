"""
Container for all built-in visualization modules.
"""

from mesa.visualization.modules.CanvasGridVisualization import CanvasGrid  # noqa
from mesa.visualization.modules.ChartVisualization import ChartModule  # noqa
from mesa.visualization.modules.PieChartVisualization import PieChartModule  # noqa
from mesa.visualization.modules.BarChartVisualization import BarChartModule  # noqa
from mesa.visualization.modules.HexGridVisualization import CanvasHexGrid  # noqa
from mesa.visualization.modules.NetworkVisualization import NetworkModule  # noqa

# Delete this line in the next major release, once the simpler namespace has
# become widely adopted.
from mesa.visualization.ModularVisualization import TextElement  # noqa
