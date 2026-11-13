import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Налаштування стилю графіків для звіту та презентації
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "figure.autolayout": True,
})


def perform_sensitivity_analysis(df, base_tariff=40.0, base_expense_per_floor=50000.0):
    """
    Проводить аналіз чутливості оптимальної кількості поверхів K
    при зміні погодинного тарифу (30, 40, 50 грн/год)
    та при зміні витрат на утримання (+20% до витрат).
    """
    tariffs = [30.0, 40.0, 50.0]
    sensitivity_results = {}

    # Відновлюємо середню кількість оплачених авто-годин за місяць з базового доходу
    # monthly_revenue = monthly_paid_hours * base_tariff
    monthly_paid_hours = df["monthly_revenue"] / base_tariff

    for tariff in tariffs:
        net_profit = (monthly_paid_hours * tariff) - df["monthly_expenses"]
        sensitivity_results[f"Тариф {int(tariff)} грн/год"] = net_profit

    # Додатковий сценарій: інфляція витрат (+20% до утримання поверху) при базовому тарифі
    high_expenses = df["K_floors"] * (base_expense_per_floor * 1.2)
    sensitivity_results["Тариф 40 грн + 20% витрат"] = (
        monthly_paid_hours * base_tariff
    ) - high_expenses

    return pd.DataFrame(sensitivity_results, index=df["K_floors"])


def run_analytics(csv_file="simulation_results.csv"):
    # 1. Завантаження та перевірка даних
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Помилка: Файл '{csv_file}' не знайдено. Переконайтеся, що він у поточній директорії.")
        return

    # 2. Базовий економічний розрахунок та пошук оптимуму
    best_idx = df["monthly_net_profit"].idxmax()
    best_row = df.loc[best_idx]
    best_k = int(best_row["K_floors"])
    max_profit = best_row["monthly_net_profit"]

    # Розрахунок маржинального прибутку (приріст прибутку при додаванні кожного наступного поверху)
    df["marginal_profit"] = df["monthly_net_profit"].diff().fillna(df["monthly_net_profit"])

    print("=" * 65)
    print("       АНАЛІТИЧНИЙ ЗВІТ STEM-ПРОЄКТУ (ЕКОНОМІЧНИЙ МОДУЛЬ)")
    print("=" * 65)
    print(df[["K_floors", "total_capacity", "reject_percentage", "monthly_revenue", "monthly_expenses", "monthly_net_profit"]].to_string(index=False))
    print("-" * 65)
    print(f"ОПТИМАЛЬНА КІЛЬКІСТЬ ПОВЕРХІВ: K = {best_k} поверхів ({int(best_row['total_capacity'])} місць)")
    print(f"Максимальний чистий прибуток:   {max_profit:,.2f} грн/місяць")
    print(f"Очікуваний місячний дохід:      {best_row['monthly_revenue']:,.2f} грн/місяць")
    print(f"Очікувані місячні витрати:      {best_row['monthly_expenses']:,.2f} грн/місяць")
    print(f"Відсоток відмов при K={best_k}:        {best_row['reject_percentage']:.2f}%")
    print("=" * 65)

    # ---------------------------------------------------------
    # ГРАФІК 1: Залежність чистого прибутку NP(K) від кількості поверхів
    # ---------------------------------------------------------
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(
        df["K_floors"],
        df["monthly_net_profit"] / 1000,
        marker="o",
        markersize=8,
        linewidth=2.5,
        color="#2ca02c",
        label="Чистий прибуток NP(K) (тис. грн)",
    )
    ax1.axhline(0, color="black", linewidth=1, linestyle=":")
    ax1.axvline(
        x=best_k,
        color="#d62728",
        linestyle="--",
        linewidth=1.5,
        label=f"Оптимум: K = {best_k} пов. ({max_profit/1000:,.1f} тис. грн)",
    )
    ax1.scatter([best_k], [max_profit / 1000], color="#d62728", s=160, zorder=5)

    # Анотація точки оптимуму
    ax1.annotate(
        f"Максимум: {max_profit/1000:,.1f} тис. грн",
        xy=(best_k, max_profit / 1000),
        xytext=(best_k + 0.4, (max_profit / 1000) * 0.92),
        arrowprops=dict(arrowstyle="->", color="#d62728", lw=1.5),
        fontweight="bold",
        color="#d62728",
    )

    ax1.set_title("Графік 1. Залежність чистого щомісячного прибутку від кількості поверхів")
    ax1.set_xlabel("Кількість поверхів підземного паркінгу (K)")
    ax1.set_ylabel("Чистий прибуток (тис. грн / місяць)")
    ax1.set_xticks(df["K_floors"])
    ax1.legend(loc="lower right")
    plt.savefig("graph1_net_profit.png", dpi=300)
    plt.close()

    # ---------------------------------------------------------
    # ГРАФІК 2: Залежність відсотка відмов P_rej(K)
    # ---------------------------------------------------------
    fig, ax2 = plt.subplots(figsize=(10, 6))
    ax2.plot(
        df["K_floors"],
        df["reject_percentage"],
        marker="s",
        markersize=8,
        linewidth=2.5,
        color="#d62728",
        label="Відсоток втрачених клієнтів P_rej (%)",
    )
    ax2.axvline(
        x=best_k,
        color="#1f77b4",
        linestyle="--",
        linewidth=1.5,
        label=f"Економічний оптимум (K = {best_k}, відмов {best_row['reject_percentage']:.1f}%)",
    )
    ax2.scatter([best_k], [best_row["reject_percentage"]], color="#1f77b4", s=140, zorder=5)

    for x_val, y_val in zip(df["K_floors"], df["reject_percentage"]):
        ax2.text(x_val, y_val + 1.8, f"{y_val:.1f}%", ha="center", fontsize=9)

    ax2.set_title("Графік 2. Залежність імовірності відмови від кількості поверхів")
    ax2.set_xlabel("Кількість поверхів (K)")
    ax2.set_ylabel("Відсоток відмов (%)")
    ax2.set_ylim(0, max(df["reject_percentage"]) * 1.15)
    ax2.set_xticks(df["K_floors"])
    ax2.legend(loc="upper right")
    plt.savefig("graph2_rejection_rate.png", dpi=300)
    plt.close()

    # ---------------------------------------------------------
    # ГРАФІК 3: Порівняння Доходів та Витрат
    # ---------------------------------------------------------
    fig, ax3 = plt.subplots(figsize=(10, 6))
    x = np.arange(len(df["K_floors"]))
    width = 0.36

    rects1 = ax3.bar(
        x - width / 2,
        df["monthly_revenue"] / 1000,
        width,
        label="Щомісячний дохід (тис. грн)",
        color="#1f77b4",
    )
    rects2 = ax3.bar(
        x + width / 2,
        df["monthly_expenses"] / 1000,
        width,
        label="Витрати на утримання (тис. грн)",
        color="#ff7f0e",
    )

    ax3.set_title("Графік 3. Порівняння щомісячних доходів та витрат на утримання")
    ax3.set_xlabel("Кількість поверхів (K)")
    ax3.set_ylabel("Сума (тис. грн / місяць)")
    ax3.set_xticks(x)
    ax3.set_xticklabels(df["K_floors"])
    ax3.legend(loc="upper left")
    plt.savefig("graph3_revenue_vs_expenses.png", dpi=300)
    plt.close()

    # ---------------------------------------------------------
    # ГРАФІК 4: Аналіз чутливості (Sensitivity Analysis)
    # ---------------------------------------------------------
    sens_df = perform_sensitivity_analysis(df)

    print("\n=== АНАЛІЗ ЧУТЛИВОСТІ (ОПТИМАЛЬНЕ K ЗА РІЗНИХ СЦЕНАРІЇВ) ===")
    for col in sens_df.columns:
        opt_k_scen = sens_df[col].idxmax()
        opt_val_scen = sens_df[col].max()
        print(f"• {col:<28} -> Оптимум: K = {opt_k_scen} пов. (Прибуток: {opt_val_scen:,.2f} грн)")

    fig, ax4 = plt.subplots(figsize=(10, 6))
    styles = ["--", "-", "-.", ":"]
    markers = ["v", "o", "^", "d"]

    for idx, col in enumerate(sens_df.columns):
        ax4.plot(
            sens_df.index,
            sens_df[col] / 1000,
            linestyle=styles[idx],
            marker=markers[idx],
            linewidth=2.2,
            label=col,
        )

    ax4.axhline(0, color="black", linewidth=1, linestyle=":")
    ax4.set_title("Графік 4. Аналіз чутливості чистого прибутку до зміни тарифів та витрат")
    ax4.set_xlabel("Кількість поверхів (K)")
    ax4.set_ylabel("Чистий прибуток (тис. грн / місяць)")
    ax4.set_xticks(df["K_floors"])
    ax4.legend(loc="best")
    plt.savefig("graph4_sensitivity_analysis.png", dpi=300)
    plt.close()

    print("\nУсі 4 графіки успішно збережено у поточну директорію!")


if __name__ == "__main__":
    run_analytics()