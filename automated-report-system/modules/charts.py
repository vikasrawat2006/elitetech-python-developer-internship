import matplotlib.pyplot as plt
import os
from modules.logger import setup_logger

logger = setup_logger()

class ChartGenerator:
    @staticmethod
    def generate_bar_chart(df, output_path="exports/department_performance.png"):
        os.makedirs("exports", exist_ok=True)
        logger.info("Generating analytical visualization charts...")
        
        fig, ax = plt.subplots(figsize=(7, 3.2))
        
        departments = df["Department"].unique()
        actuals = df.groupby("Department")["Actual_Value"].mean()
        targets = df.groupby("Department")["Target_Value"].mean()
        
        x = range(len(departments))
        width = 0.35
        
        ax.bar([p - width/2 for p in x], targets, width, label='Target Benchmark', color='#CBD5E0')
        ax.bar([p + width/2 for p in x], actuals, width, label='Actual Achieved', color='#2B6CB0')
        
        ax.set_ylabel('Score / Value', fontsize=9, fontweight='bold', color='#2D3748')
        ax.set_title('Departmental Benchmarks: Target vs Actual', fontsize=11, fontweight='bold', color='#1A365D')
        ax.set_xticks(x)
        ax.set_xticklabels(departments, rotation=10, fontsize=9)
        ax.legend(frameon=True, facecolor='#F7FAFC', edgecolor='none')
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300)
        plt.close()
        logger.info(f"Chart compiled and saved to {output_path}")
        return output_path