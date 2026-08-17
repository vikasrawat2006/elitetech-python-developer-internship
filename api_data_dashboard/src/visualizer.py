"""
Visualizer Module
Generates custom publication-quality visualization dashboards using Seaborn and Matplotlib.
"""

import logging
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)

class DashboardVisualizer:
    """Generates multi-panel analytical dashboards."""

    @staticmethod
    def render_and_save(df: pd.DataFrame, output_path: str) -> None:
        """Builds a customized 4-panel meteorological dashboard and saves it locally.

        Args:
            df (pd.DataFrame): Processed meteorological dataframe.
            output_path (str): Destination file path for image export.
        """
        logger.info("Rendering visualization dashboard...")

        # Apply custom Seaborn theme
        sns.set_theme(style="whitegrid", palette="deep")
        fig, axes = plt.subplots(4, 1, figsize=(12, 14), sharex=True)
        fig.suptitle("Comprehensive 24-Hour Meteorological Analytics Dashboard", fontsize=16, fontweight="bold", y=0.95)

        x_indexes = range(len(df))
        time_labels = df["timestamp"].dt.strftime("%H:%M").tolist()

        # 1. Temperature & Rolling Average
        sns.lineplot(data=df, x=x_indexes, y="temperature", ax=axes[0], color="#e74c3c", linewidth=2.5, marker="o", label="Hourly Temp")
        sns.lineplot(data=df, x=x_indexes, y="temp_rolling_avg", ax=axes[0], color="#8e44ad", linewidth=2.0, linestyle="--", label="3-Hr Rolling Avg")
        axes[0].set_title("Temperature Trend & Smoothing", fontsize=11, fontweight="bold")
        axes[0].set_ylabel("Temp (°C)", fontsize=10)
        axes[0].legend(loc="upper left")
        axes[0].grid(True, linestyle=":", alpha=0.7)

        # 2. Relative Humidity
        sns.lineplot(data=df, x=x_indexes, y="humidity", ax=axes[1], color="#3498db", linewidth=2.5, marker="s")
        axes[1].set_title("Relative Humidity Profile", fontsize=11, fontweight="bold")
        axes[1].set_ylabel("Humidity (%)", fontsize=10)
        axes[1].grid(True, linestyle=":", alpha=0.7)

        # 3. Wind Speed Bar Chart
        axes[2].bar(x_indexes, df["wind_speed"], color="#2ecc71", alpha=0.85, edgecolor="black", linewidth=0.5)
        axes[2].set_title("Hourly Wind Velocity", fontsize=11, fontweight="bold")
        axes[2].set_ylabel("Wind (km/h)", fontsize=10)
        axes[2].grid(True, linestyle=":", alpha=0.7)

        # 4. Precipitation Bar Chart
        axes[3].bar(x_indexes, df["precipitation"], color="#34495e", alpha=0.85, edgecolor="black", linewidth=0.5)
        axes[3].set_title("Hourly Precipitation Accumulation", fontsize=11, fontweight="bold")
        axes[3].set_xlabel("Time (HH:MM)", fontsize=10)
        axes[3].set_ylabel("Precip (mm)", fontsize=10)
        
        # Format X-axis ticks once on the bottom subplot
        axes[3].set_xticks(list(x_indexes))
        axes[3].set_xticklabels(time_labels, rotation=45)
        axes[3].grid(True, linestyle=":", alpha=0.7)

        # Layout adjustment
        plt.tight_layout(rect=[0, 0.03, 1, 0.93])

        # Export image
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        logger.info("Dashboard successfully compiled and exported to: %s", output_path)
        plt.close()